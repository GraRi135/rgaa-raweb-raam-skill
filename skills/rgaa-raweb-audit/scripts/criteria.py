#!/usr/bin/env python3
"""Look up RAWeb 1.1 / RGAA 4.1.2 criteria, tests, test methodology and glossary terms.

Examples
  criteria.py show 1.1                       # criterion title, level, WCAG refs (RAWeb, English)
  criteria.py show 1.1 --tests               # + the wording of each test
  criteria.py show 1.1 --tests --methodology # + the step-by-step test procedure for each test
  criteria.py show 1.1.5                     # a single test (with its methodology)
  criteria.py show 11.10 --standard rgaa     # RGAA 4.1.2 (French)
  criteria.py list --topic 4                 # all criteria of a topic
  criteria.py list --level AA --raweb-only   # filters
  criteria.py search contraste --standard rgaa
  criteria.py search "keyboard trap" --in tests
  criteria.py glossary "image conveying information"
  criteria.py diff                           # what RAWeb 1.1 adds or changes versus RGAA 4.1.2
  criteria.py topics
Options
  --standard raweb|rgaa   (default raweb)     --lang en|fr   (default: en for RAWeb, fr for RGAA; RGAA is French only)
  --json                  machine-readable output
"""
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "references", "data")

FILES = {
    ("raweb", "en"): "raweb-1.1-en.json",
    ("raweb", "fr"): "raweb-1.1-fr.json",
    ("rgaa", "fr"): "rgaa-4.1.2-fr.json",
}
GLOSSARIES = {
    ("raweb", "en"): "glossary-raweb-en.json",
    ("raweb", "fr"): "glossary-raweb-fr.json",
    ("rgaa", "fr"): "glossary-rgaa-fr.json",
}


def load(standard, lang):
    if standard == "rgaa" and lang == "en":
        print("note: RGAA is published in French only; showing French.", file=sys.stderr)
        lang = "fr"
    key = (standard, lang)
    if key not in FILES:
        sys.exit(f"unknown standard/lang {key}")
    return json.load(open(os.path.join(DATA, FILES[key]), encoding="utf-8")), key


def plain(s):
    return re.sub(r"\[([^\]]+)\]\(#[^)]*\)", r"\1", s)


def all_criteria(std):
    for t in std["topics"]:
        for c in t["criteria"]:
            yield t, c


def find_criterion(std, cid):
    for t, c in all_criteria(std):
        if c["id"] == cid:
            return t, c
    return None, None


def header(std):
    return f"{std['standard']} {std['version']} ({std['lang']})"


def print_criterion(std, t, c, tests=False, methodology=False, only_test=None):
    print(f"## Criterion {c['id']} [{c['level']}] — topic {t['number']} {t['title']}" + ("  (RAWeb only)" if c.get("raweb_only") else ""))
    print(plain(c["title"]))
    refs = c.get("references", {})
    if refs.get("wcag"):
        print("WCAG: " + "; ".join(refs["wcag"]))
    if refs.get("norm"):
        print("EN 301 549: " + "; ".join(refs["norm"]))
    if refs.get("techniques"):
        print("Techniques: " + ", ".join(refs["techniques"]))
    if tests or only_test:
        for k, tst in c["tests"].items():
            if only_test and k != only_test:
                continue
            print(f"\n### Test {tst['id']}")
            lines = tst["text"]
            print(plain(lines[0]))
            for extra in lines[1:]:
                print("  - " + plain(extra))
            if methodology or only_test:
                m = tst.get("methodology", "").strip()
                if m:
                    print("\nMethodology:")
                    print(plain(m))
    print()


def cmd_show(a):
    std, key = load(a.standard, a.lang)
    print(f"# {header(std)}\n")
    for ref in a.ids:
        parts = ref.split(".")
        if len(parts) == 3:
            cid, tn = ".".join(parts[:2]), parts[2]
        else:
            cid, tn = ref, None
        t, c = find_criterion(std, cid)
        if not c:
            print(f"criterion {cid} not found in {header(std)}", file=sys.stderr)
            continue
        if a.json:
            print(json.dumps(c if not tn else c["tests"].get(tn), ensure_ascii=False, indent=1))
        else:
            print_criterion(std, t, c, tests=a.tests, methodology=a.methodology, only_test=tn)


def cmd_list(a):
    std, key = load(a.standard, a.lang)
    rows = []
    for t, c in all_criteria(std):
        if a.topic and t["number"] != a.topic:
            continue
        if a.level and c["level"] != a.level.upper():
            continue
        if a.raweb_only and not c.get("raweb_only"):
            continue
        rows.append((t, c))
    if a.json:
        print(json.dumps([{"id": c["id"], "level": c["level"], "topic": t["title"], "title": plain(c["title"]),
                           "tests": len(c["tests"]), "raweb_only": c.get("raweb_only", False)} for t, c in rows], ensure_ascii=False, indent=1))
        return
    print(f"# {header(std)} — {len(rows)} criteria\n")
    last = None
    for t, c in rows:
        if t["number"] != last:
            print(f"\n## Topic {t['number']}: {t['title']}")
            last = t["number"]
        flag = " (RAWeb only)" if c.get("raweb_only") else ""
        print(f"- {c['id']} [{c['level']}] ({len(c['tests'])} tests){flag} {plain(c['title'])}")


def cmd_search(a):
    std, key = load(a.standard, a.lang)
    q = a.query.lower()
    hits = []
    for t, c in all_criteria(std):
        hay = []
        if a.scope in ("all", "titles"):
            hay.append(("title", plain(c["title"])))
        if a.scope in ("all", "tests"):
            for k, tst in c["tests"].items():
                hay.append((f"test {tst['id']}", " ".join(plain(x) for x in tst["text"])))
        if a.scope == "methodology":
            for k, tst in c["tests"].items():
                hay.append((f"methodology {tst['id']}", plain(tst.get("methodology", ""))))
        for where, text in hay:
            if q in text.lower():
                hits.append((c["id"], c["level"], where, text))
    print(f"# {header(std)} — {len(hits)} hits for '{a.query}'\n")
    for cid, lvl, where, text in hits:
        snippet = text if len(text) < 300 else text[:300] + "…"
        print(f"- {cid} [{lvl}] ({where}): {snippet}")


def cmd_glossary(a):
    key = (a.standard, a.lang if not (a.standard == "rgaa") else "fr")
    g = json.load(open(os.path.join(DATA, GLOSSARIES[key]), encoding="utf-8"))
    q = a.term.lower()
    found = [e for e in g["entries"] if q in e["title"].lower()] if q else g["entries"]
    if not found:
        found = [e for e in g["entries"] if q in e["body"].lower()]
    for e in found:
        print(f"## {e['title']}")
        body = re.sub(r"<[^>]+>", " ", e["body"])
        body = re.sub(r"\s+", " ", body).strip()
        print(body if a.full or len(body) < 1200 else body[:1200] + "…")
        print()
    if not found:
        print("no glossary entry matches", a.term)


def cmd_topics(a):
    std, key = load(a.standard, a.lang)
    print(f"# {header(std)}")
    for t in std["topics"]:
        n = len(t["criteria"]); nt = sum(len(c["tests"]) for c in t["criteria"])
        ro = sum(1 for c in t["criteria"] if c.get("raweb_only"))
        print(f"- Topic {t['number']}: {t['title']} — {n} criteria, {nt} tests" + (f" ({ro} RAWeb only)" if ro else ""))


def norm_lines(lines):
    out = []
    for s in lines:
        s = plain(s)
        s = re.sub(r"\s*[;.]\s*$", "", s)
        s = re.sub(r"\s+", " ", s).strip().lower().replace("’", "'").replace("…", "...")
        out.append(s)
    return out


def cmd_diff(a):
    rw = json.load(open(os.path.join(DATA, FILES[("raweb", "fr")]), encoding="utf-8"))
    rg = json.load(open(os.path.join(DATA, FILES[("rgaa", "fr")]), encoding="utf-8"))
    rw_en = json.load(open(os.path.join(DATA, FILES[("raweb", "en")]), encoding="utf-8"))
    en_titles = {c["id"]: plain(c["title"]) for _, c in all_criteria(rw_en)}
    rg_tests = {c["id"]: c["tests"] for _, c in all_criteria(rg)}
    print("# RAWeb 1.1 versus RGAA 4.1.2\n")
    print("## Criteria only in RAWeb 1.1")
    for t, c in all_criteria(rw):
        if c.get("raweb_only"):
            print(f"- {c['id']} [{c['level']}] {en_titles[c['id']]}")
    print("\n## Shared criteria whose tests differ (number of tests)")
    for t, c in all_criteria(rw):
        if c["id"] in rg_tests and len(rg_tests[c["id"]]) != len(c["tests"]):
            print(f"- {c['id']}: RGAA {len(rg_tests[c['id']])} tests / RAWeb {len(c['tests'])} tests — {en_titles[c['id']]}")
    print("\n## Shared criteria whose test wording differs (same number of tests)")
    for t, c in all_criteria(rw):
        if c["id"] in rg_tests and len(rg_tests[c["id"]]) == len(c["tests"]):
            a_ = {k: norm_lines(v["text"]) for k, v in rg_tests[c["id"]].items()}
            b_ = {k: norm_lines(v["text"]) for k, v in c["tests"].items()}
            if a_ != b_:
                changed = [k for k in a_ if a_[k] != b_.get(k)]
                print(f"- {c['id']}: tests {', '.join(changed)} — {en_titles[c['id']]}")


def main():
    # The common options are accepted both before and after the sub-command.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--standard", choices=["raweb", "rgaa"], default=argparse.SUPPRESS)
    common.add_argument("--lang", choices=["en", "fr"], default=argparse.SUPPRESS)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, parents=[common])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("show", parents=[common]); s.add_argument("ids", nargs="+"); s.add_argument("--tests", action="store_true"); s.add_argument("--methodology", action="store_true")
    l = sub.add_parser("list", parents=[common]); l.add_argument("--topic", type=int); l.add_argument("--level"); l.add_argument("--raweb-only", action="store_true")
    se = sub.add_parser("search", parents=[common]); se.add_argument("query"); se.add_argument("--in", dest="scope", choices=["all", "titles", "tests", "methodology"], default="all")
    g = sub.add_parser("glossary", parents=[common]); g.add_argument("term", nargs="?", default=""); g.add_argument("--full", action="store_true")
    sub.add_parser("topics", parents=[common])
    sub.add_parser("diff", parents=[common])
    a = ap.parse_args()
    a.standard = getattr(a, "standard", "raweb")
    a.json = getattr(a, "json", False)
    a.lang = getattr(a, "lang", None) or ("fr" if a.standard == "rgaa" else "en")
    {"show": cmd_show, "list": cmd_list, "search": cmd_search, "glossary": cmd_glossary, "topics": cmd_topics, "diff": cmd_diff}[a.cmd](a)


if __name__ == "__main__":
    main()
