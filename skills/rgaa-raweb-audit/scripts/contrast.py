#!/usr/bin/env python3
"""WCAG / RGAA / RAWeb contrast ratios (criteria 3.2 text, 3.3 UI components and graphics, 10.7 focus indicator).

  contrast.py "#1d3f73" "#ffffff"                  # one pair: ratio and verdicts
  contrast.py "#c00" white --size 14               # text size in px (bold with --bold) decides the threshold
  contrast.py --css styles.css                     # list every color / background-color pair declared per selector
  contrast.py --pairs pairs.txt                    # one "fg bg [size] [bold]" per line
  contrast.py "#9aa0a6" "#fff" --json

Thresholds (RGAA 3.2.x / RAWeb 3.2.x): text < 24 px normal or < 18.5 px bold needs 4.5:1; larger text needs 3:1.
UI components, graphical elements and focus indicators (3.3, 10.7): 3:1 against adjacent colours.
Colours accepted: #rgb, #rrggbb, #rrggbbaa (alpha ignored), rgb()/rgba() (alpha composited on the background if given), CSS named colours.
"""
import argparse, json, re, sys

NAMED = {"white": "#ffffff", "black": "#000000", "red": "#ff0000", "green": "#008000", "blue": "#0000ff", "gray": "#808080", "grey": "#808080",
         "silver": "#c0c0c0", "yellow": "#ffff00", "orange": "#ffa500", "navy": "#000080", "teal": "#008080", "maroon": "#800000", "purple": "#800080",
         "olive": "#808000", "lime": "#00ff00", "aqua": "#00ffff", "cyan": "#00ffff", "fuchsia": "#ff00ff", "magenta": "#ff00ff", "darkgray": "#a9a9a9",
         "darkgrey": "#a9a9a9", "lightgray": "#d3d3d3", "lightgrey": "#d3d3d3", "dimgray": "#696969", "dimgrey": "#696969", "whitesmoke": "#f5f5f5",
         "gainsboro": "#dcdcdc", "darkblue": "#00008b", "darkgreen": "#006400", "darkred": "#8b0000", "crimson": "#dc143c", "royalblue": "#4169e1",
         "steelblue": "#4682b4", "dodgerblue": "#1e90ff", "tomato": "#ff6347", "gold": "#ffd700", "transparent": None}


def parse(c):
    """Return (r, g, b, a) floats 0-1, or None for transparent."""
    c = c.strip().lower()
    if c in NAMED:
        return parse(NAMED[c]) if NAMED[c] else None
    m = re.match(r"^#([0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})$", c)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(ch * 2 for ch in h)
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return r, g, b, a
    m = re.match(r"^rgba?\(([^)]+)\)$", c)
    if m:
        parts = [p.strip() for p in re.split(r"[,/\s]+", m.group(1)) if p.strip()]
        vals = []
        for p in parts[:3]:
            vals.append(float(p[:-1]) / 100 if p.endswith("%") else float(p) / 255)
        a = 1.0
        if len(parts) > 3:
            a = float(parts[3][:-1]) / 100 if parts[3].endswith("%") else float(parts[3])
        return vals[0], vals[1], vals[2], a
    raise ValueError(f"unrecognised colour: {c}")


def composite(fg, bg):
    """Alpha-composite fg over bg (both rgba); bg assumed opaque."""
    if fg is None:
        return bg
    r, g, b, a = fg
    br, bg_, bb, _ = bg
    return (r * a + br * (1 - a), g * a + bg_ * (1 - a), b * a + bb * (1 - a), 1.0)


def luminance(rgb):
    def ch(v):
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b, _ = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def ratio(fg, bg):
    l1, l2 = luminance(fg), luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def verdicts(r, size=None, bold=False):
    large = size is not None and (size >= 24 or (bold and size >= 18.5))
    text_threshold = 3.0 if large else 4.5
    return {
        "ratio": round(r, 2),
        "text_threshold": text_threshold,
        "text_3_2": r >= text_threshold,
        "large_text_3_2": r >= 3.0,
        "ui_component_3_3": r >= 3.0,
        "focus_indicator_10_7": r >= 3.0,
        "note": ("large text" if large else "normal text") if size is not None else "size unknown: 4.5:1 applied for text",
    }


def check(fg_s, bg_s, size=None, bold=False):
    bg = parse(bg_s)
    if bg is None:
        raise ValueError("background cannot be transparent; give the effective colour behind it")
    bg = composite(bg, (1, 1, 1, 1)) if bg[3] < 1 else bg
    fg = parse(fg_s)
    fg = composite(fg, bg) if fg is None or fg[3] < 1 else fg
    v = verdicts(ratio(fg, bg), size, bold)
    v.update({"foreground": fg_s, "background": bg_s})
    return v


def fmt(v):
    t = "PASS" if v["text_3_2"] else "FAIL"
    u = "PASS" if v["ui_component_3_3"] else "FAIL"
    return (f"{v['foreground']} on {v['background']}: {v['ratio']}:1 — text (3.2, needs {v['text_threshold']}:1, {v['note']}): {t}; "
            f"UI component / graphic / focus (3.3, 10.7, needs 3:1): {u}")


def css_pairs(path):
    css = open(path, encoding="utf-8", errors="replace").read()
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out = []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        sel, body = m.group(1).strip(), m.group(2)
        decl = {}
        for d in body.split(";"):
            if ":" in d:
                k, v = d.split(":", 1)
                decl[k.strip().lower()] = v.strip().split("!")[0].strip()
        color = decl.get("color")
        bgc = decl.get("background-color") or decl.get("background")
        if bgc:
            m2 = re.match(r"^\s*(rgba?\([^)]*\)|#[0-9a-fA-F]{3,8}|[a-zA-Z]+)", bgc)
            bgc = m2.group(1) if m2 and (m2.group(1).startswith(("#", "rgb")) or m2.group(1).lower() in NAMED) else None
        if color or bgc:
            out.append({"selector": sel, "color": color, "background": bgc})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("foreground", nargs="?")
    ap.add_argument("background", nargs="?")
    ap.add_argument("--size", type=float, help="font size in px")
    ap.add_argument("--bold", action="store_true")
    ap.add_argument("--css", help="list colour pairs declared in a stylesheet")
    ap.add_argument("--pairs", help="file with one 'fg bg [size] [bold]' per line")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    results = []
    if a.css:
        for p in css_pairs(a.css):
            if p["color"] and p["background"]:
                try:
                    v = check(p["color"], p["background"]); v["selector"] = p["selector"]; results.append(v)
                except ValueError as e:
                    results.append({"selector": p["selector"], "error": str(e)})
            else:
                results.append({"selector": p["selector"], "color": p["color"], "background": p["background"], "note": "only one colour declared: the effective pair depends on inherited/ancestor colours; check in the browser"})
    elif a.pairs:
        for line in open(a.pairs, encoding="utf-8"):
            parts = line.split()
            if len(parts) < 2 or line.strip().startswith("#!"):
                continue
            size = float(parts[2]) if len(parts) > 2 and re.match(r"^[\d.]+$", parts[2]) else None
            results.append(check(parts[0], parts[1], size, "bold" in parts[2:]))
    elif a.foreground and a.background:
        results.append(check(a.foreground, a.background, a.size, a.bold))
    else:
        ap.error("give two colours, --css FILE or --pairs FILE")
    if a.json:
        print(json.dumps(results, ensure_ascii=False, indent=1)); return
    for v in results:
        if "ratio" in v:
            print((f"[{v['selector']}] " if "selector" in v else "") + fmt(v))
        else:
            print(f"[{v.get('selector', '?')}] " + (v.get("error") or f"color={v.get('color')} background={v.get('background')}: {v.get('note')}"))


if __name__ == "__main__":
    main()
