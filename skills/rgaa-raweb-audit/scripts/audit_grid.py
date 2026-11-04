#!/usr/bin/env python3
"""Create and compute an RGAA / RAWeb audit grid (pages x criteria).

The grid is a CSV with one row per criterion and one column per audited page.
Each cell holds a status: C (compliant / conforme), NC (non-compliant / non conforme),
NA (not applicable / non applicable) or NT (not tested / non testé).

  audit_grid.py new  --standard raweb --pages "Home=https://x.lu/,Contact=https://x.lu/contact" --out grille.csv
  audit_grid.py new  --standard rgaa  --pages-file pages.txt --out grille.csv     # one "Name=URL" per line
  audit_grid.py new  --standard raam  --pages "Accueil=,Contact=,Connexion=" --out grille-app.csv   # mobile app screens (RAAM 1.1)
  audit_grid.py compute grille.csv                     # markdown summary (per page + global rate + status)
  audit_grid.py compute grille.csv --json              # machine-readable
  audit_grid.py compute grille.csv --lang fr           # French vocabulary
  audit_grid.py compute grille.csv --process "Demande=Étape 1,Étape 2,Étape 3"   # pages forming one process
  audit_grid.py set grille.csv --page Accueil 1.1=NC 1.2=C 8.3=NC --default NA   # fill statuses from the CLI

Rules implemented (RGAA "Évaluation de la conformité" / RAWeb "Test methodology"):
  * a criterion is compliant for the site only if it is C on every page where it applies;
    one NC on one page makes it NC for the whole site;
  * a criterion is applicable to the site if it is applicable (C or NC) on at least one page;
    it is NA for the site only if it is NA on every page;
  * rate = compliant criteria / applicable criteria (no weighting by level A/AA);
  * compliance status: 100 % -> fully compliant; >= 50 % -> partially compliant; < 50 % -> non-compliant;
  * pages of a process: a criterion is compliant for a page of the process only if it is compliant on
    every page of that process (affects per-page rates only);
  * NT cells (not tested) make the result provisional: they are listed and excluded from "applicable"
    for the provisional rate, and the summary says the audit is incomplete.
Columns before the first page column are metadata (criterion, level, topic, title) and are preserved.
Every column after them is a page: keep comments in a separate file, not in an extra column, and pass --standard
when the grid is a subset (the standard is otherwise guessed from the criterion ids and titles).
"""
import argparse, csv, json, os, signal, sys

if hasattr(signal, "SIGPIPE"):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # no traceback when the output is piped into head

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "references", "data")
STATUSES = {"C", "NC", "NA", "NT"}
ALIASES = {"CONFORME": "C", "NON CONFORME": "NC", "NON-CONFORME": "NC", "NON APPLICABLE": "NA", "N/A": "NA",
           "NON TESTE": "NT", "NON TESTÉ": "NT", "": "NT", "PASS": "C", "FAIL": "NC", "OK": "C", "KO": "NC",
           "COMPLIANT": "C", "NON-COMPLIANT": "NC", "NOT APPLICABLE": "NA", "NOT TESTED": "NT"}

VOCAB = {
    "en": {"C": "compliant", "NC": "non-compliant", "NA": "not applicable", "NT": "not tested",
           "full": "fully compliant", "partial": "partially compliant", "none": "non-compliant",
           "title": "Audit grid results", "page": "Page", "applicable": "applicable", "rate": "rate"},
    "fr": {"C": "conforme", "NC": "non conforme", "NA": "non applicable", "NT": "non testé",
           "full": "totalement conforme", "partial": "partiellement conforme", "none": "non conforme",
           "title": "Résultats de la grille d'audit", "page": "Page", "applicable": "applicables", "rate": "taux"},
}


def load_criteria(standard, lang):
    name = {"raweb": f"raweb-1.1-{lang}.json", "rgaa": "rgaa-4.1.2-fr.json", "raam": f"raam-1.1-{lang}.json"}[standard]
    std = json.load(open(os.path.join(DATA, name), encoding="utf-8"))
    rows = []
    for t in std["topics"]:
        for c in t["criteria"]:
            import re
            title = re.sub(r"\[([^\]]+)\]\(#[^)]*\)", r"\1", c["title"])
            rows.append({"criterion": c["id"], "level": c["level"], "topic": f"{t['number']} {t['title']}", "title": title})
    return std, rows


def cmd_new(a):
    pages = []
    if a.pages:
        pages += [p.strip() for p in a.pages.split(",") if p.strip()]
    if a.pages_file:
        pages += [l.strip() for l in open(a.pages_file, encoding="utf-8") if l.strip() and not l.startswith("#")]
    if not pages:
        sys.exit("give --pages or --pages-file")
    names = [p.split("=", 1)[0].strip() for p in pages]
    std, rows = load_criteria(a.standard, a.lang)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["criterion", "level", "topic", "title"] + names)
        for r in rows:
            w.writerow([r["criterion"], r["level"], r["topic"], r["title"]] + ["NT"] * len(names))
    urls = {p.split("=", 1)[0].strip(): (p.split("=", 1)[1].strip() if "=" in p else "") for p in pages}
    with open(a.out + ".pages.json", "w", encoding="utf-8") as f:
        json.dump({"standard": std["standard"], "version": std["version"], "pages": urls}, f, ensure_ascii=False, indent=1)
    print(f"wrote {a.out}: {len(rows)} criteria x {len(names)} pages (all NT). Page URLs kept in {a.out}.pages.json")


def cmd_set(a):
    """Set statuses in an existing grid: audit_grid.py set grid.csv --page Home 1.1=NC 1.2=C 4.1=NA ..."""
    with open(a.grid, newline="", encoding="utf-8-sig") as f:
        sample = f.read(4096); f.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t") if sample else csv.excel
        rows = list(csv.reader(f, dialect))
    head = [h.strip() for h in rows[0]]
    if a.page not in head:
        sys.exit(f"page '{a.page}' not found; columns are: {', '.join(head)}")
    col = head.index(a.page)
    wanted = {}
    default = None
    try:
        for item in a.assignments:
            if "=" not in item:
                sys.exit(f"expected criterion=STATUS, got '{item}'")
            cid, st = item.split("=", 1)
            wanted[cid.strip()] = norm_status(st)
        if a.default:
            default = norm_status(a.default)
    except ValueError as e:
        sys.exit(str(e))
    done = set()
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        cid = r[0].strip()
        while len(r) <= col:
            r.append("")
        if cid in wanted:
            r[col] = wanted[cid]; done.add(cid)
        elif a.default and (not r[col].strip() or r[col].strip().upper() == "NT"):
            r[col] = default
    missing = set(wanted) - done
    if missing:
        sys.exit(f"criteria not in grid: {', '.join(sorted(missing))}")
    with open(a.grid, "w", newline="", encoding="utf-8") as f:
        csv.writer(f, dialect).writerows(rows)
    print(f"{a.grid}: {len(done)} statuses set on '{a.page}'" + (f", other NT cells set to {default}" if a.default else ""))


def norm_status(v):
    v = (v or "").strip().upper()
    if v in STATUSES:
        return v
    if v in ALIASES:
        return ALIASES[v]
    raise ValueError(f"unknown status '{v}' (use C, NC, NA or NT)")


def read_grid(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(4096); f.seek(0)
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t") if sample else csv.excel
        rows = list(csv.reader(f, dialect))
    head = [h.strip() for h in rows[0]]
    meta_cols = []
    for h in head:
        if h.lower() in ("criterion", "critere", "critère", "id", "level", "niveau", "topic", "thematique", "thématique", "theme", "thème", "title", "titre", "intitule", "intitulé"):
            meta_cols.append(h)
        else:
            break
    if not meta_cols:
        sys.exit("first column must be the criterion id (header 'criterion' or 'critère')")
    pages = head[len(meta_cols):]
    grid = {}
    errors = []
    for r in rows[1:]:
        if not r or not r[0].strip():
            continue
        cid = r[0].strip()
        cells = {}
        for i, p in enumerate(pages):
            raw = r[len(meta_cols) + i] if len(meta_cols) + i < len(r) else ""
            try:
                cells[p] = norm_status(raw)
            except ValueError as e:
                errors.append(f"{cid} / {p}: {e}")
        grid[cid] = cells
    if errors:
        sys.exit("invalid statuses:\n  " + "\n  ".join(errors))
    return pages, grid


def detect_standard(grid):
    ids = set(grid)
    if any(i.startswith(("3.15", "3.16", "3.17", "3.18", "11.14", "11.15", "11.16", "15.")) for i in ids) and not any(i.startswith("17.") for i in ids) and "13.14" not in ids:
        return "raam"
    return "raweb" if any(i.startswith(("14.", "15.", "16.", "17.")) or i in ("4.14", "13.13") for i in ids) else "rgaa"


def compute(pages, grid, processes):
    # per-page view, applying the process rule
    page_group = {}
    for name, members in processes.items():
        for m in members:
            page_group[m] = members
    per_page = {}
    for p in pages:
        applicable = compliant = nt = 0
        for cid, cells in grid.items():
            s = cells[p]
            if s == "NA":
                continue
            if s == "NT":
                nt += 1
                continue
            applicable += 1
            ok = s == "C"
            if ok and p in page_group:
                ok = all(grid[cid][q] in ("C", "NA") for q in page_group[p] if q in grid[cid])
            if ok:
                compliant += 1
        per_page[p] = {"applicable": applicable, "compliant": compliant, "not_tested": nt,
                       "rate": round(100 * compliant / applicable, 1) if applicable else None}
    # site-level
    site = {}
    for cid, cells in grid.items():
        vals = set(cells.values())
        if "NC" in vals:
            site[cid] = "NC"
        elif "C" in vals and "NT" not in vals:
            site[cid] = "C"
        elif vals <= {"NA"}:
            site[cid] = "NA"
        elif "NT" in vals and "C" in vals:
            site[cid] = "C?"   # compliant where tested, still NT somewhere
        else:
            site[cid] = "NT"
    nc = sorted([c for c, s in site.items() if s == "NC"], key=key)
    c_ = sorted([c for c, s in site.items() if s == "C"], key=key)
    na = sorted([c for c, s in site.items() if s == "NA"], key=key)
    nt = sorted([c for c, s in site.items() if s in ("NT", "C?")], key=key)
    applicable = len(nc) + len(c_)
    rate = round(100 * len(c_) / applicable, 1) if applicable else None
    status = None
    if rate is not None:
        status = "full" if rate == 100 else "partial" if rate >= 50 else "none"
    nc_pages = {cid: [p for p in pages if grid[cid][p] == "NC"] for cid in nc}
    avg = [v["rate"] for v in per_page.values() if v["rate"] is not None]
    return {"pages": per_page, "site": {"compliant": c_, "non_compliant": nc, "not_applicable": na, "not_tested": nt,
                                        "applicable": applicable, "rate": rate, "status": status,
                                        "average_page_rate": round(sum(avg) / len(avg), 1) if avg else None,
                                        "non_compliant_pages": nc_pages}}


def key(cid):
    """Sort key for criterion ids; a non-numeric id (a 'Total' row, a note) sorts last instead of crashing."""
    try:
        return tuple(int(x) for x in cid.split("."))
    except ValueError:
        return (999, cid)


def cmd_compute(a):
    pages, grid = read_grid(a.grid)
    standard = a.standard or detect_standard(grid)
    lang = a.lang or ("fr" if standard == "rgaa" else "en")
    std, rows = load_criteria(standard, lang)
    titles = {r["criterion"]: r for r in rows}
    unknown = [c for c in grid if c not in titles]
    missing = [r["criterion"] for r in rows if r["criterion"] not in grid]
    processes = {}
    for spec in a.process or []:
        if "=" not in spec:
            sys.exit(f'--process expects "Name=Page A,Page B", got \'{spec}\'')
        name, members = spec.split("=", 1)
        members = [m.strip() for m in members.split(",") if m.strip()]
        unknown_pages = [m for m in members if m not in pages]
        if unknown_pages:
            print(f"WARNING: process '{name.strip()}': page(s) not in the grid are ignored: {', '.join(unknown_pages)} (grid columns: {', '.join(pages)})", file=sys.stderr)
        processes[name.strip()] = members
    res = compute(pages, grid, processes)
    res["standard"] = f"{std['standard']} {std['version']}"
    res["unknown_criteria"] = unknown
    res["missing_criteria"] = missing
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1)); return
    v = VOCAB[lang]
    s = res["site"]
    print(f"# {v['title']} — {res['standard']}\n")
    if unknown:
        print(f"WARNING: criteria not in {res['standard']}: {', '.join(unknown)}")
    if missing:
        print(f"WARNING: {len(missing)} criteria of {res['standard']} are absent from the grid: {', '.join(missing[:15])}{'…' if len(missing) > 15 else ''}")
    provisional = bool(s["not_tested"])
    print(f"| {v['page']} | {v['applicable']} | {v['C']} | {v['NT']} | {v['rate']} |")
    print("|---|---|---|---|---|")
    for p, r in res["pages"].items():
        print(f"| {p} | {r['applicable']} | {r['compliant']} | {r['not_tested']} | {r['rate'] if r['rate'] is not None else '-'} % |")
    print()
    print(f"- {v['C']}: {len(s['compliant'])}")
    print(f"- {v['NC']}: {len(s['non_compliant'])}")
    print(f"- {v['NA']}: {len(s['not_applicable'])}")
    if provisional:
        print(f"- {v['NT']} ({'incomplete audit' if lang == 'en' else 'audit incomplet'}): {len(s['not_tested'])} — {', '.join(s['not_tested'])}")
    if s["rate"] is not None:
        label = ("Provisional rate" if lang == "en" else "Taux provisoire") if provisional else ("Compliance rate" if lang == "en" else "Taux de conformité")
        print(f"- **{label}: {s['rate']} %** ({len(s['compliant'])} / {s['applicable']}) → **{v[s['status']]}**")
        if lang == "fr":
            print(f"- Taux moyen de conformité des pages (facultatif) : {s['average_page_rate']} %")
        else:
            print(f"- Average page rate (optional figure): {s['average_page_rate']} %")
    print()
    if s["non_compliant"]:
        print(f"## {v['NC'].capitalize()} ({len(s['non_compliant'])})")
        for cid in s["non_compliant"]:
            t = titles.get(cid, {})
            print(f"- {cid} [{t.get('level', '?')}] {t.get('title', '')} — {', '.join(s['non_compliant_pages'][cid])}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new"); n.add_argument("--standard", choices=["raweb", "rgaa", "raam"], default="raweb"); n.add_argument("--lang", choices=["en", "fr"], default=None)
    n.add_argument("--pages"); n.add_argument("--pages-file"); n.add_argument("--out", default="audit-grid.csv")
    c = sub.add_parser("compute"); c.add_argument("grid"); c.add_argument("--standard", choices=["raweb", "rgaa", "raam"]); c.add_argument("--lang", choices=["en", "fr"])
    c.add_argument("--process", action="append", help='"Name=Page A,Page B" (repeatable)'); c.add_argument("--json", action="store_true")
    st = sub.add_parser("set", help="set statuses for one page: set grid.csv --page Home 1.1=NC 1.2=C [--default NA]")
    st.add_argument("grid"); st.add_argument("--page", required=True); st.add_argument("assignments", nargs="*")
    st.add_argument("--default", help="status for every remaining empty/NT cell of that page (e.g. NA after you have listed all C and NC)")
    a = ap.parse_args()
    if a.cmd == "set":
        cmd_set(a)
    elif a.cmd == "new":
        a.lang = a.lang or ("fr" if a.standard == "rgaa" else "en")
        if a.standard == "rgaa":
            a.lang = "fr"
        cmd_new(a)
    else:
        cmd_compute(a)


if __name__ == "__main__":
    main()
