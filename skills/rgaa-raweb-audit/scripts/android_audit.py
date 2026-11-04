#!/usr/bin/env python3
"""Android app accessibility evidence for RAAM 1.1 audits, through adb (physical device or emulator).

  android_audit.py devices                                  # list adb devices
  android_audit.py capture --screen "Accueil" --out audit/  # dump the current screen: view hierarchy, screenshot, activity, settings
  android_audit.py analyse audit/accueil/                   # findings mapped to RAAM 1.1 criteria (works offline on a saved capture)
  android_audit.py analyse audit/accueil/ --json
  android_audit.py font-scale 2.0 | 1.0                     # change the system font scale (test 8.2: 200 %)
  android_audit.py rotate landscape | portrait | auto       # force orientation (criterion 11.9)
  android_audit.py talkback on | off                        # toggle TalkBack (needs it installed)
  android_audit.py compare audit/accueil/ audit/accueil-x2/ # texts truncated or lost between two captures (font scale, orientation)
  android_audit.py annotate audit/accueil/ [--out shots/]   # one cropped PNG per FAIL/REVIEW finding, element outlined in red, plus findings.json
  android_audit.py walk --screen "Accueil" --out audit/     # capture at scale 1.0, 2.0 and in landscape, then compare and analyse

What it proves: the view hierarchy exposed to assistive technologies (uiautomator dump): elements without a
name, clickable elements without a role or not focusable, image elements without alternative, form fields,
text that disappears or truncates at 200 %, orientation lock, estimated text contrast from the screenshot.
What it cannot prove: how TalkBack announces things, heading navigation, status messages, gestures, time
limits. Those criteria stay NT until tested with TalkBack and a keyboard, as the RAAM methodology requires.
"""
import argparse, json, os, re, struct, subprocess, sys, time, zlib
import xml.etree.ElementTree as ET
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    from contrast import check as contrast_check
except Exception:  # pragma: no cover
    contrast_check = None

IMAGE_CLASSES = ("android.widget.ImageView", "android.widget.ImageButton", "androidx.appcompat.widget.AppCompatImageView")
TEXT_CLASSES = ("android.widget.TextView", "android.widget.Button", "android.widget.EditText", "android.widget.CheckBox", "android.widget.RadioButton", "android.widget.Switch", "android.widget.CheckedTextView", "android.widget.ToggleButton")
CONTAINER_CLASSES = ("android.view.View", "android.view.ViewGroup", "android.widget.LinearLayout", "android.widget.RelativeLayout", "android.widget.FrameLayout", "androidx.cardview.widget.CardView", "androidx.constraintlayout.widget.ConstraintLayout", "android.widget.ScrollView", "androidx.recyclerview.widget.RecyclerView", "android.widget.ListView", "android.widget.GridView", "androidx.viewpager.widget.ViewPager", "android.widget.HorizontalScrollView", "androidx.compose.ui.platform.ComposeView")
ROLE_CLASSES = ("android.widget.Button", "android.widget.ImageButton", "android.widget.CheckBox", "android.widget.RadioButton", "android.widget.Switch", "android.widget.ToggleButton", "android.widget.EditText", "android.widget.Spinner", "android.widget.SeekBar", "android.widget.CheckedTextView", "android.widget.Tab", "android.widget.TabWidget")


# ---------------------------------------------------------------- adb
def adb(args, serial=None, binary=False, check=True, timeout=120):
    cmd = ["adb"] + (["-s", serial] if serial else []) + args
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout)
    except FileNotFoundError:
        sys.exit("adb not found. Install Android platform-tools (https://developer.android.com/tools/releases/platform-tools) and put adb on the PATH; start an emulator or plug a device with USB debugging enabled.")
    if check and r.returncode != 0:
        sys.exit(f"adb {' '.join(args)} failed: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout if binary else r.stdout.decode(errors="replace")


def cmd_devices(a):
    out = adb(["devices", "-l"])
    print(out.strip() or "no device")
    lines = [l for l in out.splitlines()[1:] if l.strip()]
    if not lines:
        print("Start an emulator (emulator -avd <name>) or connect a device with USB debugging, then run again.")


def shell(args, serial=None, **kw):
    return adb(["shell"] + args, serial, **kw)


def current_activity(serial=None):
    out = shell(["dumpsys", "window"], serial, check=False)
    m = re.search(r"mCurrentFocus=Window\{[^ ]+ [^ ]+ ([^/ ]+)/([^ }]+)", out) or re.search(r"mFocusedApp=.*?([A-Za-z0-9_.]+)/([A-Za-z0-9_.$]+)", out)
    return {"package": m.group(1), "activity": m.group(2)} if m else {}


def settings(serial=None):
    def get(ns, key):
        v = shell(["settings", "get", ns, key], serial, check=False).strip()
        return None if v in ("null", "") else v
    return {"font_scale": get("system", "font_scale"), "accelerometer_rotation": get("system", "accelerometer_rotation"),
            "user_rotation": get("system", "user_rotation"), "enabled_accessibility_services": get("secure", "enabled_accessibility_services"),
            "display_density": shell(["wm", "density"], serial, check=False).strip(), "display_size": shell(["wm", "size"], serial, check=False).strip(),
            "android_version": shell(["getprop", "ro.build.version.release"], serial, check=False).strip(),
            "model": shell(["getprop", "ro.product.model"], serial, check=False).strip()}


def capture(screen, out_dir, serial=None, label=None):
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", (label or screen).strip().lower()).strip("-") or "screen"
    d = os.path.join(out_dir, name)
    os.makedirs(d, exist_ok=True)
    shell(["uiautomator", "dump", "/sdcard/window_dump.xml"], serial)
    adb(["pull", "/sdcard/window_dump.xml", os.path.join(d, "window_dump.xml")], serial)
    png = adb(["exec-out", "screencap", "-p"], serial, binary=True, check=False)
    if png[:8] == b"\x89PNG\r\n\x1a\n":
        open(os.path.join(d, "screen.png"), "wb").write(png)
    meta = {"screen": screen, "captured_at": time.strftime("%Y-%m-%d %H:%M:%S"), "serial": serial, **current_activity(serial), "settings": settings(serial)}
    json.dump(meta, open(os.path.join(d, "meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"captured '{screen}' -> {d} ({meta.get('package', '?')}/{meta.get('activity', '?')}, font_scale={meta['settings'].get('font_scale')}, rotation={meta['settings'].get('user_rotation')})")
    return d


def cmd_capture(a):
    capture(a.screen, a.out, a.serial)


def cmd_font_scale(a):
    shell(["settings", "put", "system", "font_scale", str(a.value)], a.serial)
    print(f"font_scale set to {a.value} (give the app a second to relayout, then capture again)")


def cmd_rotate(a):
    if a.mode == "auto":
        shell(["settings", "put", "system", "accelerometer_rotation", "1"], a.serial); print("auto-rotate restored")
        return
    shell(["settings", "put", "system", "accelerometer_rotation", "0"], a.serial)
    shell(["settings", "put", "system", "user_rotation", "1" if a.mode == "landscape" else "0"], a.serial)
    time.sleep(1.5)
    rot = re.search(r"mCurRotation=(\d)|mRotation=(\d)|rotation=(\d)", shell(["dumpsys", "window", "displays"], a.serial, check=False))
    rot = next((g for g in rot.groups() if g), None) if rot else None
    print(f"requested {a.mode}; display rotation now {rot} (0 = portrait, 1 = landscape). If it stayed at 0 after asking for landscape, the app or screen locks the orientation (11.9: NC unless essential).")


TALKBACK = "com.google.android.marvin.talkback/com.google.android.marvin.talkback.TalkBackService"


def cmd_talkback(a):
    if a.mode == "on":
        shell(["settings", "put", "secure", "enabled_accessibility_services", TALKBACK], a.serial)
        shell(["settings", "put", "secure", "accessibility_enabled", "1"], a.serial)
        print("TalkBack requested (install 'Android Accessibility Suite' on the device/emulator first; on a physical device, explore by touch is now active: use two-finger swipes to scroll).")
    else:
        shell(["settings", "put", "secure", "enabled_accessibility_services", ""], a.serial)
        shell(["settings", "put", "secure", "accessibility_enabled", "0"], a.serial)
        print("TalkBack disabled")


# ---------------------------------------------------------------- analysis
class N:
    __slots__ = ("attrs", "children", "parent", "idx")

    def __init__(self, attrs, parent=None):
        self.attrs, self.children, self.parent, self.idx = attrs, [], parent, 0

    def g(self, k, default=""):
        return self.attrs.get(k, default)

    def b(self, k):
        return self.g(k) == "true"

    @property
    def cls(self):
        return self.g("class")

    @property
    def bounds(self):
        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", self.g("bounds"))
        return tuple(int(x) for x in m.groups()) if m else (0, 0, 0, 0)

    def iter(self):
        yield self
        for c in self.children:
            yield from c.iter()

    def own_text(self):
        return (self.g("text") or "").strip()

    def name(self):
        """Accessible name as TalkBack would compute it: content-desc, else text, else descendants' text/content-desc."""
        if self.g("content-desc").strip():
            return self.g("content-desc").strip()
        if self.own_text():
            return self.own_text()
        parts = [n.name() for n in self.children]
        return " ".join(p for p in parts if p).strip()

    def short(self):
        rid = self.g("resource-id").split("/")[-1]
        return f"{self.cls.split('.')[-1]}{('#' + rid) if rid else ''} {self.g('bounds')}" + (f' "{self.name()[:40]}"' if self.name() else "")


def load_tree(path):
    root = ET.parse(path).getroot()
    def build(el, parent):
        n = N(dict(el.attrib), parent)
        for c in el:
            if c.tag == "node":
                n.children.append(build(c, n))
        return n
    top = N({"class": "#root"})
    for c in root:
        if c.tag == "node":
            top.children.append(build(c, top))
    i = 0
    for n in top.iter():
        n.idx = i; i += 1
    return top


def dp(px, density):
    return px * 160 / density if density else px


# -- PNG decoding (8-bit RGB/RGBA, non-interlaced), stdlib only -----------------
def read_png(path):
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    pos, idat, w = 8, [], None
    while pos < len(data):
        ln, typ = struct.unpack(">I4s", data[pos:pos + 8]); chunk = data[pos + 8:pos + 8 + ln]; pos += 12 + ln
        if typ == b"IHDR":
            w, h, bit, ct, _, _, inter = struct.unpack(">IIBBBBB", chunk)
            if bit != 8 or ct not in (2, 6) or inter:
                return None
            ch = 3 if ct == 2 else 4
        elif typ == b"IDAT":
            idat.append(chunk)
        elif typ == b"IEND":
            break
    raw = zlib.decompress(b"".join(idat)); stride = w * ch; rows = []; prev = bytearray(stride); p = 0
    for y in range(h):
        f = raw[p]; p += 1; cur = bytearray(raw[p:p + stride]); p += stride
        for i in range(stride):
            a = cur[i - ch] if i >= ch else 0; bb = prev[i]; c = prev[i - ch] if i >= ch else 0
            if f == 1: cur[i] = (cur[i] + a) & 255
            elif f == 2: cur[i] = (cur[i] + bb) & 255
            elif f == 3: cur[i] = (cur[i] + ((a + bb) >> 1)) & 255
            elif f == 4:
                pa, pb, pc = abs(bb - c), abs(a - c), abs(a + bb - 2 * c)
                cur[i] = (cur[i] + (a if pa <= pb and pa <= pc else bb if pb <= pc else c)) & 255
        rows.append(bytes(cur)); prev = cur
    return {"w": w, "h": h, "ch": ch, "rows": rows}


def dominant_colours(img, bounds, limit=2, step=2):
    x1, y1, x2, y2 = bounds; x2 = min(x2, img["w"]); y2 = min(y2, img["h"]); ch = img["ch"]
    cnt = Counter()
    for y in range(max(0, y1), y2, step):
        row = img["rows"][y]
        for x in range(max(0, x1), x2, step):
            o = x * ch; cnt[(row[o] >> 3 << 3, row[o + 1] >> 3 << 3, row[o + 2] >> 3 << 3)] += 1
    return [c for c, _ in cnt.most_common(limit)]


def hexc(c):
    return "#%02x%02x%02x" % c


def analyse(capture_dir):
    xml_path = os.path.join(capture_dir, "window_dump.xml")
    if not os.path.exists(xml_path):
        sys.exit(f"no window_dump.xml in {capture_dir}")
    meta = json.load(open(os.path.join(capture_dir, "meta.json"), encoding="utf-8")) if os.path.exists(os.path.join(capture_dir, "meta.json")) else {}
    density = 0
    m = re.search(r"(\d+)", (meta.get("settings") or {}).get("display_density") or "")
    if m:
        density = int(m.group(1))
    tree = load_tree(xml_path)
    nodes = [n for n in tree.iter() if n.cls != "#root"]
    F = []
    def add(status, crit, msg, node=None):
        F.append({"status": status, "criterion": crit, "message": msg, "element": node.short() if node else None, "index": node.idx if node else None})
    inv = Counter()
    clickables = [n for n in nodes if n.b("clickable") or n.b("long-clickable") or n.b("checkable")]
    inv["nodes"] = len(nodes); inv["interactive"] = len(clickables)
    inv["webviews"] = sum(1 for n in nodes if "WebView" in n.cls)
    inv["edit_texts"] = sum(1 for n in nodes if "EditText" in n.cls or n.b("password"))
    inv["images"] = sum(1 for n in nodes if n.cls in IMAGE_CLASSES)
    inv["texts"] = sum(1 for n in nodes if n.own_text())
    # 5.1 name and role of interactive components
    def is_form_field(n):
        return "EditText" in n.cls or n.b("password") or n.b("checkable") or n.cls.endswith(("Spinner", "SeekBar", "RadioButton", "CheckBox", "Switch", "ToggleButton"))
    for n in clickables:
        if not n.name():
            if is_form_field(n):
                add("fail", "9.2", f"{n.cls.split('.')[-1]} without any label exposed to TalkBack (no text, content-desc, hint or labelFor relation visible in the dump): the field is announced by its type only. Also needs a visible label (9.1).", n)
            else:
                add("fail", "5.1", "Interactive element without accessible name (no text, content-desc or labelled descendant): TalkBack announces only the role or 'unlabelled'." + (" uiautomator flagged it NAF (not accessibility friendly)." if n.g("NAF") == "true" else ""), n)
        if n.cls in CONTAINER_CLASSES or (n.cls == "android.widget.TextView" and n.b("clickable")) or (n.cls in IMAGE_CLASSES and n.cls != "android.widget.ImageButton" and n.b("clickable")):
            add("review", "5.1", f"Clickable {n.cls.split('.')[-1]} exposes no control role (not a Button/CheckBox/...): TalkBack will not announce it as a button unless the accessibility class name or role description is set. NC 5.1 if no role is announced.", n)
        if n.b("clickable") and not n.b("focusable"):
            add("fail", "5.2", "Clickable but not focusable: unreachable with an external keyboard or switch access (also breaks TalkBack linear navigation).", n)
        if n.b("checkable"):
            add("review", "5.5", f"Toggle control ({'checked' if n.b('checked') else 'unchecked'}): check that TalkBack announces the state and each change of state, and that the state is visually perceptible.", n)
    # 1.x graphic elements
    for n in nodes:
        if n.cls in IMAGE_CLASSES:
            if n.g("content-desc").strip():
                add("review", "1.3", f'Image with alternative "{n.g("content-desc")[:50]}": check it conveys the information (not a file name or "image").', n)
            elif n.b("clickable") or (n.parent and n.parent.b("clickable") and not n.parent.name()):
                pass  # already reported under 5.1
            else:
                add("review", "1.1", "Image without content-desc: if decorative it must be hidden from TalkBack (importantForAccessibility=no); if informative it needs a contentDescription (1.2). The dump cannot tell which: check with TalkBack whether it is reachable.", n)
    # 9.x forms
    for n in nodes:
        if ("EditText" in n.cls or n.b("password")) and n.name():
            add("review", "9.1", f'Field announced as "{n.name()[:40]}": if that text is a hint it disappears once typed, so a visible persistent label is still required (9.1); check mandatory indication (9.7) and format help (9.8).', n)
    # 10.2 reading / focus order heuristic: interactive elements sorted by index vs by position
    seq = [n for n in clickables if n.b("focusable") or n.b("clickable")]
    if len(seq) >= 3:
        rows = sorted(seq, key=lambda n: (round(n.bounds[1] / 40), n.bounds[0]))
        if [n.idx for n in rows] != [n.idx for n in seq]:
            add("review", "10.2", "The hierarchy order of interactive elements differs from their visual top-to-bottom, left-to-right order: check TalkBack's reading order (swipe right through the screen) and the keyboard focus order (10.1).")
    # web views
    for n in nodes:
        if "WebView" in n.cls:
            add("info", "0", "WebView present: its content is evaluated with the web criteria (RAWeb 1.1); the dump exposes little of it. Use scan_html.py on the page it loads and test with TalkBack.", n)
    # text contrast estimate from screenshot (2.2)
    png = os.path.join(capture_dir, "screen.png")
    if os.path.exists(png) and contrast_check:
        img = read_png(png)
        if img:
            measured = 0
            for n in nodes:
                if n.own_text() and n.cls in TEXT_CLASSES and len(n.own_text()) >= 2:
                    x1, y1, x2, y2 = n.bounds
                    if x2 - x1 < 4 or y2 - y1 < 4 or (x2 - x1) * (y2 - y1) > 2_000_000:
                        continue
                    cols = dominant_colours(img, n.bounds, 2)
                    if len(cols) < 2:
                        continue
                    bg, fg = cols[0], cols[1]
                    v = contrast_check(hexc(fg), hexc(bg), size=dp(y2 - y1, density) * 0.7 if density else None)
                    measured += 1
                    if v["ratio"] < 4.5:
                        add("review", "2.2", f'Estimated text contrast {v["ratio"]}:1 ({hexc(fg)} on {hexc(bg)}) for "{n.own_text()[:35]}": below 4.5:1 (3:1 for large text). Estimate from dominant colours; confirm with a contrast analyser.', n)
            inv["texts_contrast_measured"] = measured
        else:
            add("info", "2.2", "screen.png could not be decoded (not 8-bit RGB/RGBA): contrast not estimated.")
    # small targets (good practice, not a RAAM criterion)
    small = [n for n in clickables if density and (dp(n.bounds[2] - n.bounds[0], density) < 24 or dp(n.bounds[3] - n.bounds[1], density) < 24)]
    if small:
        add("info", "0", f"{len(small)} interactive element(s) smaller than 24x24 dp (48x48 dp recommended). Not a RAAM 1.1 criterion (WCAG 2.5.5/2.5.8), report as a recommendation.", small[0])
    # always-manual reminders
    add("info", "0", "Not decidable from a dump: headings (7.1, TalkBack 'headings' navigation), lists (7.2), language (6.1), status messages (5.4), context changes (5.3), gestures (11.10, 11.11), motion (11.13), time limits (11.1, 11.2), moving content (11.8), flashes (11.7), focus visibility with a keyboard (8.5). Test them with TalkBack and an external keyboard.")
    return {"capture": capture_dir, "meta": meta, "inventory": dict(inv), "findings": F}


# -- PNG writing and drawing (stdlib) ------------------------------------------
def write_png(path, w, h, ch, rows):
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    raw = b"".join(b"\x00" + r for r in rows)
    ct = 2 if ch == 3 else 6
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, ct, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


DIGITS = {"0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"], "2": ["111", "001", "111", "100", "111"], "3": ["111", "001", "111", "001", "111"], "4": ["101", "101", "111", "001", "001"],
          "5": ["111", "100", "111", "001", "111"], "6": ["111", "100", "111", "101", "111"], "7": ["111", "001", "001", "001", "001"], "8": ["111", "101", "111", "101", "111"], "9": ["111", "101", "111", "001", "111"]}


def crop_annotate(img, bounds, label, margin=80, colour=(208, 2, 27)):
    """Crop the screenshot around bounds (with margin), draw a red rectangle on the element and a numbered label."""
    x1, y1, x2, y2 = bounds; ch = img["ch"]
    cx1, cy1 = max(0, x1 - margin), max(0, y1 - margin); cx2, cy2 = min(img["w"], x2 + margin), min(img["h"], y2 + margin)
    W, H = cx2 - cx1, cy2 - cy1
    rows = [bytearray(img["rows"][y][cx1 * ch:cx2 * ch]) for y in range(cy1, cy2)]
    def put(x, y, c):
        if 0 <= x < W and 0 <= y < H:
            o = x * ch; rows[y][o:o + 3] = bytes(c)
    t = 4
    for d in range(t):
        for x in range(x1 - cx1 - d, x2 - cx1 + d):
            put(x, y1 - cy1 - d, colour); put(x, y2 - cy1 + d, colour)
        for y in range(y1 - cy1 - d, y2 - cy1 + d):
            put(x1 - cx1 - d, y, colour); put(x2 - cx1 + d, y, colour)
    # label: white digits on a red box, scale 4
    sc = 4; lx = max(0, x1 - cx1 - t); ly = max(0, y1 - cy1 - t - 5 * sc - 10)
    bw = len(label) * 4 * sc + 8
    for y in range(ly, ly + 5 * sc + 8):
        for x in range(lx, lx + bw):
            put(x, y, colour)
    for i, chr_ in enumerate(label):
        pat = DIGITS.get(chr_)
        if not pat:
            continue
        for r, line in enumerate(pat):
            for c, bit in enumerate(line):
                if bit == "1":
                    for dy in range(sc):
                        for dx in range(sc):
                            put(lx + 4 + i * 4 * sc + c * sc + dx, ly + 4 + r * sc + dy, (255, 255, 255))
    return W, H, [bytes(r) for r in rows]


def cmd_annotate(a):
    res = analyse(a.capture_dir)
    png = os.path.join(a.capture_dir, "screen.png")
    img = read_png(png) if os.path.exists(png) else None
    out = a.out or os.path.join(a.capture_dir, "shots")
    os.makedirs(out, exist_ok=True)
    tree = load_tree(os.path.join(a.capture_dir, "window_dump.xml"))
    by_idx = {n.idx: n for n in tree.iter()}
    n = 0; findings = []
    for i, f in enumerate([x for x in res["findings"] if x["status"] in ("fail", "review")], 1):
        f = dict(f); f["id"] = f"A{i:02d}"; f["url"] = res["meta"].get("screen"); f["standard"] = "raam"
        node = by_idx.get(f.get("index"))
        if img and node is not None and node.bounds != (0, 0, 0, 0):
            W, H, rows = crop_annotate(img, node.bounds, str(i))
            path = os.path.join(out, f"{f['id']}.png"); write_png(path, W, H, img["ch"], rows); f["screenshot"] = path; n += 1
        findings.append(f)
    meta = res["meta"]
    doc = {"site": meta.get("package", ""), "standard": "raam", "lang": "en", "title": f"Écran « {meta.get('screen', a.capture_dir)} »",
           "sample": [{"id": "E01", "title": meta.get("screen", ""), "url": f"{meta.get('package', '')}/{meta.get('activity', '')}"}],
           "environment": [f"Android {(meta.get('settings') or {}).get('android_version', '?')}, {(meta.get('settings') or {}).get('model', '')}, font scale {(meta.get('settings') or {}).get('font_scale', '?')}; static view-hierarchy analysis, no TalkBack"],
           "findings": findings}
    fp = os.path.join(out, "findings.json"); json.dump(doc, open(fp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{n} annotated screenshot(s) in {out}; findings written to {fp} (edit problem/impact/fix, then build_report.py)")


def cmd_analyse(a):
    res = analyse(a.capture_dir)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1)); return
    meta = res["meta"]; F = res["findings"]
    fails = [f for f in F if f["status"] == "fail"]; reviews = [f for f in F if f["status"] == "review"]
    print(f"# Android screen analysis — {meta.get('screen', a.capture_dir)} ({meta.get('package', '?')}/{meta.get('activity', '?')}, Android {(meta.get('settings') or {}).get('android_version', '?')}, font_scale {(meta.get('settings') or {}).get('font_scale', '?')})")
    print(f"\nRAAM 1.1. {len(fails)} likely non-conformities, {len(reviews)} points to review. Static view-hierarchy analysis: TalkBack and keyboard tests are still required.\n")
    print("## Inventory"); [print(f"- {k}: {v}") for k, v in res["inventory"].items()]
    by = {}
    for f in F:
        by.setdefault(f["criterion"], []).append(f)
    def key(c):
        try: return tuple(int(x) for x in c.split("."))
        except ValueError: return (99,)
    for c in sorted(by, key=key):
        print(f"\n## {'Criterion ' + c if c != '0' else 'Other'}")
        for f in sorted(by[c], key=lambda x: {"fail": 0, "review": 1, "info": 2}[x["status"]]):
            print(f"- **{f['status'].upper()}**" + (f" `{f['element']}`" if f["element"] else "") + f": {f['message']}")


def texts_of(capture_dir):
    tree = load_tree(os.path.join(capture_dir, "window_dump.xml"))
    return {(n.g("resource-id"), n.idx): n.own_text() for n in tree.iter() if n.own_text()}


def cmd_compare(a):
    ta, tb = texts_of(a.before), texts_of(a.after)
    ra = {t for t in ta.values()}; rb = {t for t in tb.values()}
    lost = sorted(t for t in ra if t not in rb and not any(t.startswith(x.rstrip("…")) for x in rb if x.endswith("…")))
    truncated = sorted(x for x in rb if x.endswith("…") and x not in ra)
    print(f"# Comparison {a.before} -> {a.after}")
    print(f"- texts before: {len(ra)}, after: {len(rb)}")
    print(f"- truncated with an ellipsis after: {len(truncated)}" + ("".join(f"\n  - {t[:80]}" for t in truncated[:15])))
    print(f"- texts no longer present after: {len(lost)}" + ("".join(f"\n  - {t[:80]}" for t in lost[:15])))
    if truncated or lost:
        print("\nREVIEW 8.2 (text at 200 %) or 11.9 (orientation): content lost or truncated; confirm on the screenshots (information must stay available, scrolling is allowed).")
    else:
        print("\nNo text lost or truncated between the two captures (compare the screenshots for overlaps and clipped layouts anyway).")


def cmd_walk(a):
    s = a.serial
    base = settings(s)
    d1 = capture(a.screen, a.out, s, label=a.screen)
    shell(["settings", "put", "system", "font_scale", "2.0"], s); time.sleep(2.5)
    d2 = capture(a.screen, a.out, s, label=a.screen + "-x2")
    shell(["settings", "put", "system", "font_scale", base.get("font_scale") or "1.0"], s)
    shell(["settings", "put", "system", "accelerometer_rotation", "0"], s); shell(["settings", "put", "system", "user_rotation", "1"], s); time.sleep(2.5)
    d3 = capture(a.screen, a.out, s, label=a.screen + "-landscape")
    shell(["settings", "put", "system", "user_rotation", base.get("user_rotation") or "0"], s)
    if base.get("accelerometer_rotation") == "1":
        shell(["settings", "put", "system", "accelerometer_rotation", "1"], s)
    print("\n== 200 % font scale"); cmd_compare(argparse.Namespace(before=d1, after=d2))
    print("\n== landscape"); cmd_compare(argparse.Namespace(before=d1, after=d3))
    print("\n== analysis of the base capture"); cmd_analyse(argparse.Namespace(capture_dir=d1, json=False))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--serial", "-s", help="adb device serial when several are connected")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("devices")
    c = sub.add_parser("capture"); c.add_argument("--screen", required=True, help="screen name as it will appear in the sample (e.g. 'Accueil')"); c.add_argument("--out", default="android-audit")
    an = sub.add_parser("analyse"); an.add_argument("capture_dir"); an.add_argument("--json", action="store_true")
    fs = sub.add_parser("font-scale"); fs.add_argument("value")
    ro = sub.add_parser("rotate"); ro.add_argument("mode", choices=["landscape", "portrait", "auto"])
    tb = sub.add_parser("talkback"); tb.add_argument("mode", choices=["on", "off"])
    cp = sub.add_parser("compare"); cp.add_argument("before"); cp.add_argument("after")
    ann = sub.add_parser("annotate"); ann.add_argument("capture_dir"); ann.add_argument("--out")
    w = sub.add_parser("walk"); w.add_argument("--screen", required=True); w.add_argument("--out", default="android-audit")
    a = ap.parse_args()
    {"devices": cmd_devices, "capture": cmd_capture, "analyse": cmd_analyse, "font-scale": cmd_font_scale, "rotate": cmd_rotate, "talkback": cmd_talkback, "compare": cmd_compare, "walk": cmd_walk, "annotate": cmd_annotate}[a.cmd](a)


if __name__ == "__main__":
    main()
