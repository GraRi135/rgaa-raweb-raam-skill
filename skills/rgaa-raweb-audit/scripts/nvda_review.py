#!/usr/bin/env python3
"""nvda_review.py — read NVDA capture files (from nvda_capture.js) and turn them into audit evidence.

  python3 nvda_review.py nvda/                         # summary of every capture in the folder (Markdown on stdout)
  python3 nvda_review.py nvda/ --findings findings.json --apply    # add an "nvda" evidence block to each finding
  python3 nvda_review.py nvda/ --json                  # machine-readable summary

What it does, for each page and browser:
  * lists what NVDA announced (linear reading, headings, links, landmarks, form fields, graphics);
  * flags announcement patterns that usually mean a non-conformity (image read as a file name, graphic or link with
    no name, "clickable" element, edit field with no label, button with no name, heading level jumps, no landmark),
    each with the RAWeb / RGAA criterion to check;
  * for each finding checked during the capture, shows what NVDA said on focus and when reading the line, and the
    verdict when the finding carried an "expect" regular expression;
  * with --apply, writes the evidence into findings.json: finding["nvda"] = [{browser, onFocus, lineRead, verdict}]
    and (unless --no-grid-hints) prints the grid statuses to consider.

Counting rule (RAWeb / RGAA reference environment): a failure under NVDA makes the criterion NC on that page; a success
is "C under NVDA, JAWS and VoiceOver to confirm". This script suggests, the auditor decides; it never edits the grid.
Mock captures (nvda_capture.js --mock) are reported but labelled: they are not screen-reader evidence.
"""
import argparse, glob, json, os, re, sys

VOCAB = {
    "graphic": r"\b(graphique|graphic|image)\b",
    "link": r"\b(lien|link)\b",
    "button": r"\b(bouton|button)\b",
    "edit": r"\b(édition|edit|zone de texte|text field|champ)\b",
    "clickable": r"\b(cliquable|clickable)\b",
    "heading": r"\b(titre|heading)\b\s*(niveau|level)?\s*(\d)",
    "landmark": r"\b(repère|landmark|région|region|principal|main|navigation|bannière|banner)\b",
    "visited": r"\b(visité|visited)\b",
    "required": r"\b(obligatoire|required)\b",
    "filename": r"\b[\w-]+\.(jpe?g|png|gif|svg|webp|pdf)\b",
    "nolabel_edit": r"^(édition|edit|zone de texte|text field)(\s+(obligatoire|required|vide|blank|protégé|protected))*$",
}
R = {k: re.compile(v, re.I) for k, v in VOCAB.items()}


def flags_for(spoken):
    """Heuristic patterns in one announcement → list of (criterion, why)."""
    s = spoken.strip(); out = []
    if R["graphic"].search(s) and R["filename"].search(s):
        out.append(("1.1 / 1.3", "image announced with a file name: missing or irrelevant alternative"))
    elif re.fullmatch(r"(graphique|graphic)(\s+(lien|link))?", s, re.I):
        out.append(("1.1", "graphic announced without any name"))
    if re.fullmatch(r"(lien|link)(\s+(visité|visited))?", s, re.I):
        out.append(("6.2", "link announced without a name"))
    if R["clickable"].search(s):
        out.append(("7.1 / 7.3", "'clickable' element: a scripted control without a role; check keyboard operation and role"))
    if R["nolabel_edit"].match(s):
        out.append(("11.1", "edit field announced without a label"))
    if re.fullmatch(r"(bouton|button)", s, re.I):
        out.append(("11.9 / 7.1", "button announced without a name"))
    return out


def heading_levels(items):
    levels = []
    for it in items:
        m = R["heading"].search(it.get("spoken", ""))
        if m:
            levels.append(int(m.group(3)))
    return levels


def review_capture(rec):
    res = {"page": rec.get("page"), "browser": rec.get("browser"), "browserVersion": rec.get("browserVersion", ""), "screenReader": rec.get("screenReader", ""),
           "screenReaderVersion": rec.get("screenReaderVersion", ""), "mock": bool(rec.get("mock")), "url": rec.get("url"), "flags": [], "structure": {}, "findings": []}
    seen = set()
    for x in rec.get("linear", []):
        for crit, why in flags_for(x.get("spoken", "")):
            key = (crit, x.get("spoken"))
            if key in seen:
                continue
            seen.add(key); res["flags"].append({"criterion": crit, "why": why, "spoken": x.get("spoken"), "line": x.get("i")})
    lists = rec.get("lists", {})
    hl = heading_levels(lists.get("headings", []))
    res["structure"] = {k: len(v) for k, v in lists.items()}
    res["structure"]["headingLevels"] = hl
    if hl:
        if hl[0] != 1:
            res["flags"].append({"criterion": "9.1", "why": f"first heading announced is level {hl[0]} (no level 1 before it)", "spoken": lists["headings"][0]["spoken"]})
        for a, b in zip(hl, hl[1:]):
            if b > a + 1:
                res["flags"].append({"criterion": "9.1", "why": f"heading level jump {a} → {b}: check the hierarchy is consistent", "spoken": ""})
                break
    else:
        res["flags"].append({"criterion": "9.1", "why": "NVDA finds no heading on the page", "spoken": ""})
    if not lists.get("landmarks"):
        res["flags"].append({"criterion": "9.2 / 12.6", "why": "NVDA finds no landmark (main, navigation, banner, contentinfo): regions not exposed", "spoken": ""})
    for f in rec.get("findings", []):
        heard = " | ".join(filter(None, [f.get("onFocus"), f.get("lineRead")]))
        extra = []
        for crit, why in flags_for(f.get("onFocus", "") or "") + flags_for(f.get("lineRead", "") or ""):
            extra.append(f"{crit}: {why}")
        res["findings"].append({"id": f.get("id"), "criterion": f.get("criterion"), "test": f.get("test"), "selector": f.get("selector"), "onFocus": f.get("onFocus"),
                                "lineRead": f.get("lineRead"), "verdict": f.get("verdict") or f.get("note") or "", "patterns": sorted(set(extra)), "heard": heard})
    return res


def to_markdown(reviews, lang):
    L = lang == "fr"; out = []
    out.append("# " + ("Relecture des captures NVDA" if L else "Review of the NVDA captures"))
    for r in reviews:
        out.append("")
        out.append(f"## {r['page']} — {r['browser']} {r['browserVersion']} — {r['screenReader']} {r['screenReaderVersion']}")
        if r["mock"]:
            out.append("**" + ("Capture simulée (arbre d'accessibilité) : pas une preuve de restitution." if L else "Mock capture (accessibility tree): not screen-reader evidence.") + "**")
        st = r["structure"]
        out.append(("Structure annoncée" if L else "Announced structure") + f" : headings {st.get('headings', 0)} (levels {st.get('headingLevels')}), links {st.get('links', 0)}, landmarks {st.get('landmarks', 0)}, form fields {st.get('formFields', 0)}, graphics {st.get('graphics', 0)}, tables {st.get('tables', 0)}, lists {st.get('lists', 0)}")
        if r["flags"]:
            out.append("")
            out.append(("### Annonces à vérifier" if L else "### Announcements to check"))
            for fl in r["flags"]:
                out.append(f"- **{fl['criterion']}** — {fl['why']}" + (f" — « {fl['spoken']} »" if fl.get("spoken") else "") + (f" (line {fl['line']})" if fl.get("line") else ""))
        if r["findings"]:
            out.append("")
            out.append(("### Constats vérifiés au lecteur d'écran" if L else "### Findings checked with the screen reader"))
            for f in r["findings"]:
                out.append(f"- **{f['id']}** ({f.get('criterion') or ''} {f.get('test') or ''}) `{f.get('selector') or ''}` — " + ("au focus" if L else "on focus") + f" : « {f.get('onFocus') or '—'} » ; " + ("ligne" if L else "line") + f" : « {f.get('lineRead') or '—'} » — {f.get('verdict')}" + (("; " + "; ".join(f["patterns"])) if f["patterns"] else ""))
    out.append("")
    out.append(("Règle de comptage : un échec sous NVDA rend le critère non conforme ; une réussite reste « C sous NVDA, JAWS et VoiceOver à confirmer ». Ce script suggère, l'auditeur décide." if L else
                "Counting rule: a failure under NVDA makes the criterion non-compliant; a success stays 'C under NVDA, JAWS and VoiceOver to confirm'. This script suggests, the auditor decides."))
    return "\n".join(out) + "\n"


def apply_to_findings(reviews, findings_path, lang):
    doc = json.load(open(findings_path, encoding="utf-8"))
    findings = doc if isinstance(doc, list) else doc.get("findings", [])
    by_id = {f.get("id"): f for f in findings}
    n = 0
    for r in reviews:
        for f in r["findings"]:
            tgt = by_id.get(f["id"])
            if not tgt:
                continue
            ev = {"browser": f"{r['browser']} {r['browserVersion']}".strip(), "screenReader": f"{r['screenReader']} {r['screenReaderVersion']}".strip(), "onFocus": f.get("onFocus"), "lineRead": f.get("lineRead"), "verdict": f.get("verdict"), "mock": r["mock"]}
            tgt.setdefault("nvda", [])
            tgt["nvda"] = [e for e in tgt["nvda"] if e.get("browser") != ev["browser"]] + [ev]
            n += 1
    if not isinstance(doc, list):
        env = doc.setdefault("environment", [])
        for r in reviews:
            line = (f"{r['screenReader']} {r['screenReaderVersion']} + {r['browser']} {r['browserVersion']}" + (" (simulation, pas une preuve)" if r["mock"] and lang == "fr" else " (mock, not evidence)" if r["mock"] else "")).strip()
            if line not in env:
                env.append(line)
    json.dump(doc, open(findings_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return n


def grid_hints(reviews, lang):
    L = lang == "fr"; lines = []
    for r in reviews:
        if r["mock"]:
            continue
        nc = {}
        for fl in r["flags"]:
            for c in fl["criterion"].split("/"):
                nc.setdefault(c.strip(), fl["why"])
        for f in r["findings"]:
            if f.get("verdict", "").startswith("expected announcement NOT") and f.get("criterion"):
                nc.setdefault(f["criterion"], f"finding {f['id']}: expected announcement not heard")
        if nc:
            lines.append(f"{r['page']} ({r['browser']}): " + ("à considérer NC après lecture : " if L else "consider NC after reading: ") + ", ".join(f"{k} ({v})" for k, v in sorted(nc.items())))
    return lines


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", help="folder with <page>-<browser>.json captures (or one .json file)")
    ap.add_argument("--findings", help="findings.json to enrich with --apply")
    ap.add_argument("--apply", action="store_true", help="write the evidence into --findings")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--lang", default="fr")
    ap.add_argument("--no-grid-hints", action="store_true")
    a = ap.parse_args()
    files = [a.folder] if a.folder.endswith(".json") else sorted(glob.glob(os.path.join(a.folder, "*.json")))
    files = [f for f in files if not f.endswith(".annotated.json")]
    if not files:
        sys.exit(f"no capture .json in {a.folder}")
    reviews = []
    for f in files:
        try:
            rec = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            print(f"skip {f}: {e}", file=sys.stderr); continue
        if "linear" not in rec:
            continue
        reviews.append(review_capture(rec))
    if a.json:
        print(json.dumps(reviews, ensure_ascii=False, indent=1))
    else:
        print(to_markdown(reviews, a.lang), end="")
        if not a.no_grid_hints:
            hints = grid_hints(reviews, a.lang)
            if hints:
                print("\n" + ("## Statuts de grille à envisager" if a.lang == "fr" else "## Grid statuses to consider"))
                for h in hints:
                    print("- " + h)
                print(("\n(un critère réussi sous NVDA reste « C sous NVDA, JAWS et VoiceOver à confirmer » : laissez la mention dans le rapport)" if a.lang == "fr" else
                       "\n(a criterion that passes under NVDA stays 'C under NVDA, JAWS and VoiceOver to confirm': keep that wording in the report)"))
    if a.apply:
        if not a.findings:
            sys.exit("--apply needs --findings findings.json")
        n = apply_to_findings(reviews, a.findings, a.lang)
        print(f"\napplied NVDA evidence to {n} finding check(s) in {a.findings}", file=sys.stderr)


if __name__ == "__main__":
    main()
