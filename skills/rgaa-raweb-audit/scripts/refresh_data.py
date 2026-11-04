#!/usr/bin/env python3
"""Rebuild references/data/*.json from the official upstream repositories.

Sources (both publish their reference files on GitHub):
  * RAWeb 1.1  -> https://github.com/accessibility-luxembourg/ReferentielAccessibiliteWeb (CC-BY 3.0 LU)
  * RGAA 4.1.2 -> https://github.com/DISIC/accessibilite.numerique.gouv.fr (Licence Ouverte 2.0)
  * RAAM 1.1  -> https://github.com/accessibility-luxembourg/ReferentielAccessibiliteMobile (CC-BY 3.0 LU), mobile apps

Usage:
  python3 refresh_data.py                 # clones the three repos into a temp dir (needs git and network), then rebuilds
  python3 refresh_data.py --raweb-dir X --rgaa-dir Y --raam-dir Z   # use existing clones

Output (in references/data/):
  raweb-1.1-en.json, raweb-1.1-fr.json, rgaa-4.1.2-fr.json   criteria + tests + per-test methodology + level + references
  raam-1.1-en.json, raam-1.1-fr.json                          RAAM criteria + per-criterion methodology + level + references
  glossary-raweb-en.json, glossary-raweb-fr.json, glossary-rgaa-fr.json, glossary-raam-en.json, glossary-raam-fr.json
  SOURCES.json                                                 upstream commits and dates
  ../criteria-index.md, ../raam-criteria-index.md              regenerated compact indexes
"""
import argparse, json, os, re, subprocess, sys, tempfile, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "references", "data")
INDEX_MD = os.path.join(HERE, "..", "references", "criteria-index.md")

RAWEB_REPO = "https://github.com/accessibility-luxembourg/ReferentielAccessibiliteWeb.git"
RGAA_REPO = "https://github.com/DISIC/accessibilite.numerique.gouv.fr.git"
RAAM_REPO = "https://github.com/accessibility-luxembourg/ReferentielAccessibiliteMobile.git"


def git(args, cwd):
    return subprocess.check_output(["git"] + args, cwd=cwd, text=True).strip()


def clone(url, dest):
    subprocess.check_call(["git", "clone", "--depth", "1", "--quiet", url, dest])


def strip_links(s):
    """Turn [term](#anchor) into plain 'term' for the compact index."""
    return re.sub(r"\[([^\]]+)\]\(#[^)]*\)", r"\1", s)


def ref_list(v):
    """Upstream stores most references as lists but a few (RAWeb 13.3, 13.4 'norm') as a sentence: keep one shape."""
    if isinstance(v, str):
        v = re.sub(r"<[^>]+>", "", v).strip()
        return [v] if v else []
    return v


def norm_lines(lines):
    """Normalise test wording so that only substantive differences are reported
    (glossary anchors, trailing punctuation, spacing and typographic quotes are ignored)."""
    out = []
    for s in lines:
        s = strip_links(s)
        s = re.sub(r"\s*[;.]\s*$", "", s)
        s = re.sub(r"\s+", " ", s).strip().lower()
        s = s.replace("\u2019", "'").replace("\u2026", "...")
        out.append(s)
    return out


def build_standard(criteres_path, methodo_path, levels, meta, raweb_only_ids):
    src = json.load(open(criteres_path, encoding="utf-8"))
    methodo = json.load(open(methodo_path, encoding="utf-8"))
    out = dict(meta)
    out["wcag_version"] = src.get("wcag", {}).get("version")
    out["topics"] = []
    for t in src["topics"]:
        topic = {"number": t["number"], "title": t["topic"], "criteria": []}
        for c in t["criteria"]:
            cr = c["criterium"]
            cid = f"{t['number']}.{cr['number']}"
            refs = {}
            for r in cr.get("references", []):
                refs.update(r)
            refs = {k: ref_list(v) for k, v in refs.items()}
            tests = {}
            for k, lines in cr["tests"].items():
                tid = f"{cid}.{k}"
                tests[k] = {"id": tid, "text": lines, "methodology": methodo.get(tid, "")}
            topic["criteria"].append({
                "id": cid,
                "number": cr["number"],
                "level": levels.get(cid, "?"),
                "title": cr["title"],
                "raweb_only": cid in raweb_only_ids,
                "tests": tests,
                "references": refs,
            })
        out["topics"].append(topic)
    return out


def raam_levels(md_path):
    """RAAM publishes the A/AA level only in the technical reference markdown: '#### [Criterion 1.1](#crit-1-1) [A] ...'."""
    md = open(md_path, encoding="utf-8").read()
    levels = {}
    for m in re.finditer(r"#### \[(?:Criterion|Criteria|Crit\u00e8re) (\d+\.\d+)\]\(#crit-[\d-]+\)\s*\[(A{1,2})\]", md):
        levels[m.group(1)] = m.group(2)
    return levels


def build_raam(criteres_path, methodo_path, levels, meta):
    """RAAM criteria mostly have no numbered tests: the criterion is the test and the methodology is keyed by criterion id."""
    src = json.load(open(criteres_path, encoding="utf-8"))
    methodo = json.load(open(methodo_path, encoding="utf-8"))
    out = dict(meta)
    out["wcag_version"] = src.get("wcag", {}).get("version")
    out["en301549_version"] = src.get("en301549")
    out["topics"] = []
    for t in src["topics"]:
        topic = {"number": t["number"], "title": t["topic"], "criteria": []}
        for c in t["criteria"]:
            cr = c["criterium"]
            cid = f"{t['number']}.{cr['number']}"
            refs = cr.get("references") or {}
            if isinstance(refs, list):
                merged = {}
                for r in refs:
                    merged.update(r)
                refs = merged
            refs = {k: ref_list(v) for k, v in refs.items()}
            tests = {}
            for k, lines in (cr.get("tests") or {}).items():
                tests[k] = {"id": f"{cid}.{k}", "text": lines, "methodology": ""}
            topic["criteria"].append({
                "id": cid, "number": cr["number"], "level": levels.get(cid, "?"), "title": strip_links(cr["title"]),
                "tests": tests, "methodology": methodo.get(cid, ""), "references": refs,
            })
        out["topics"].append(topic)
    return out


def build_glossary(path, meta):
    g = json.load(open(path, encoding="utf-8"))
    items = g.get("glossary") or g.get("glossaire")
    return dict(meta, entries=items)


def write(obj, name):
    p = os.path.join(DATA, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    print("wrote", os.path.relpath(p, HERE), f"({os.path.getsize(p)//1024} KB)")


def criterion_ids(std):
    return [c["id"] for t in std["topics"] for c in t["criteria"]]


def write_index(raweb_en, raweb_fr, rgaa_fr):
    fr_titles = {c["id"]: c["title"] for t in raweb_fr["topics"] for c in t["criteria"]}
    rgaa_tests = {c["id"]: c["tests"] for t in rgaa_fr["topics"] for c in t["criteria"]}
    raweb_fr_tests = {c["id"]: c["tests"] for t in raweb_fr["topics"] for c in t["criteria"]}
    lines = [
        "# Criteria index: RAWeb 1.1 and RGAA 4.1.2",
        "",
        "Generated by `scripts/refresh_data.py`; do not edit by hand.",
        "",
        "Both standards share the same numbering for criteria 1.1 to 13.12. RAWeb 1.1 adds the criteria marked **RAWeb only**",
        "(30 criteria: 4.14-4.18, 13.13, 13.14 and topics 14 to 17). A **tests differ** flag means the French wording or number of",
        "tests is not identical between RGAA 4.1.2 and RAWeb 1.1 for that criterion, so cite the right standard's test numbers.",
        "",
        f"Totals: RAWeb 1.1 = {len(criterion_ids(raweb_en))} criteria; RGAA 4.1.2 = {len(criterion_ids(rgaa_fr))} criteria.",
        "",
        "Level is the WCAG level the criterion is mapped to (A or AA). The compliance rate does not weight by level.",
        "",
        "Use `python3 scripts/criteria.py show <id> --tests --methodology` for full test wording and procedure.",
        "",
    ]
    for t in raweb_en["topics"]:
        lines.append(f"## Topic {t['number']}: {t['title']}")
        lines.append("")
        lines.append("| Id | Level | Tests | Title (EN) | Titre (FR) | Notes |")
        lines.append("|---|---|---|---|---|---|")
        for c in t["criteria"]:
            cid = c["id"]
            notes = []
            if c["raweb_only"]:
                notes.append("RAWeb only")
            elif cid in rgaa_tests:
                a = {k: norm_lines(v["text"]) for k, v in rgaa_tests[cid].items()}
                b = {k: norm_lines(v["text"]) for k, v in raweb_fr_tests[cid].items()}
                if len(a) != len(b):
                    notes.append(f"test count differs (RGAA {len(a)} / RAWeb {len(b)})")
                elif a != b:
                    notes.append("wording differs")
            en = strip_links(c["title"]).replace("|", "\\|")
            fr = strip_links(fr_titles.get(cid, "")).replace("|", "\\|")
            lines.append(f"| {cid} | {c['level']} | {len(c['tests'])} | {en} | {fr} | {'; '.join(notes)} |")
        lines.append("")
    with open(INDEX_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("wrote", os.path.relpath(INDEX_MD, HERE))


RAAM_INDEX_MD = os.path.join(HERE, "..", "references", "raam-criteria-index.md")


def write_raam_index(raam_en, raam_fr):
    fr_titles = {c["id"]: c["title"] for t in raam_fr["topics"] for c in t["criteria"]}
    lines = ["# Criteria index: RAAM 1.1 (mobile applications, Luxembourg)", "",
             "Generated by `scripts/refresh_data.py`; do not edit by hand.", "",
             f"RAAM 1.1 (published 24 February 2025) has {len(criterion_ids(raam_en))} criteria in {len(raam_en['topics'])} topics, covering EN 301 549 v3.2.1",
             "chapters 5, 6, 7, 10, 11 and 12 for mobile applications. Most criteria carry no numbered tests: the criterion itself is the",
             "test, and `criteria.py show <id> --standard raam --methodology` prints the iOS / Android evaluation procedure.", ""]
    for t in raam_en["topics"]:
        lines += [f"## Topic {t['number']}: {t['title']}", "", "| Id | Level | Tests | Title (EN) | Titre (FR) | EN 301 549 |", "|---|---|---|---|---|---|"]
        for c in t["criteria"]:
            en = strip_links(c["title"]).replace("|", "\\|"); fr = strip_links(fr_titles.get(c["id"], "")).replace("|", "\\|")
            norm = "; ".join(c["references"].get("norm", []))[:60]
            lines.append(f"| {c['id']} | {c['level']} | {len(c['tests']) or '-'} | {en} | {fr} | {norm} |")
        lines.append("")
    with open(RAAM_INDEX_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("wrote", os.path.relpath(RAAM_INDEX_MD, HERE))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raweb-dir")
    ap.add_argument("--rgaa-dir")
    ap.add_argument("--raam-dir")
    a = ap.parse_args()
    tmp = None
    if not (a.raweb_dir and a.rgaa_dir and a.raam_dir):
        tmp = tempfile.mkdtemp(prefix="a11y-sources-")
        a.raweb_dir = a.raweb_dir or os.path.join(tmp, "raweb")
        a.rgaa_dir = a.rgaa_dir or os.path.join(tmp, "rgaa")
        a.raam_dir = a.raam_dir or os.path.join(tmp, "raam")
        if not os.path.exists(os.path.join(a.raweb_dir, ".git")):
            print("cloning", RAWEB_REPO); clone(RAWEB_REPO, a.raweb_dir)
        if not os.path.exists(os.path.join(a.rgaa_dir, ".git")):
            print("cloning", RGAA_REPO); clone(RGAA_REPO, a.rgaa_dir)
        if not os.path.exists(os.path.join(a.raam_dir, ".git")):
            print("cloning", RAAM_REPO); clone(RAAM_REPO, a.raam_dir)
    os.makedirs(DATA, exist_ok=True)

    levels = json.load(open(os.path.join(a.raweb_dir, "en", "niveaux.json"), encoding="utf-8"))
    rgaa_src = json.load(open(os.path.join(a.rgaa_dir, "RGAA", "criteres.json"), encoding="utf-8"))
    rgaa_ids = {f"{t['number']}.{c['criterium']['number']}" for t in rgaa_src["topics"] for c in t["criteria"]}
    raweb_src = json.load(open(os.path.join(a.raweb_dir, "en", "json", "criteres.json"), encoding="utf-8"))
    raweb_ids = {f"{t['number']}.{c['criterium']['number']}" for t in raweb_src["topics"] for c in t["criteria"]}
    raweb_only = raweb_ids - rgaa_ids

    sources = {
        "generated": datetime.date.today().isoformat(),
        "raweb": {"repo": RAWEB_REPO, "commit": git(["rev-parse", "HEAD"], a.raweb_dir),
                  "commit_date": git(["log", "-1", "--format=%cs"], a.raweb_dir),
                  "licence": "CC-BY 3.0 LU (Service information et presse, Luxembourg)"},
        "rgaa": {"repo": RGAA_REPO, "commit": git(["rev-parse", "HEAD"], a.rgaa_dir),
                 "commit_date": git(["log", "-1", "--format=%cs"], a.rgaa_dir),
                 "licence": "Licence Ouverte 2.0 (DINUM, France)"},
        "raam": {"repo": RAAM_REPO, "commit": git(["rev-parse", "HEAD"], a.raam_dir),
                 "commit_date": git(["log", "-1", "--format=%cs"], a.raam_dir),
                 "licence": "CC-BY 3.0 LU (Service information et presse, Luxembourg)"},
    }

    meta_raweb = {"standard": "RAWeb", "version": "1.1", "published": "2026-02-06",
                  "official_url": "https://accessibilite.public.lu/en/raweb1.1/criteres.html"}
    meta_rgaa = {"standard": "RGAA", "version": "4.1.2", "published": "2023-04-18",
                 "official_url": "https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/"}

    raweb_en = build_standard(os.path.join(a.raweb_dir, "en", "json", "criteres.json"),
                              os.path.join(a.raweb_dir, "en", "json", "methodologies.json"),
                              levels, dict(meta_raweb, lang="en"), raweb_only)
    raweb_fr = build_standard(os.path.join(a.raweb_dir, "fr", "json", "criteres.json"),
                              os.path.join(a.raweb_dir, "fr", "json", "methodologies.json"),
                              levels, dict(meta_raweb, lang="fr", official_url="https://accessibilite.public.lu/fr/raweb1.1/criteres.html"), raweb_only)
    rgaa_fr = build_standard(os.path.join(a.rgaa_dir, "RGAA", "criteres.json"),
                             os.path.join(a.rgaa_dir, "RGAA", "methodologies.json"),
                             levels, dict(meta_rgaa, lang="fr"), set())

    write(raweb_en, "raweb-1.1-en.json")
    write(raweb_fr, "raweb-1.1-fr.json")
    write(rgaa_fr, "rgaa-4.1.2-fr.json")
    write(build_glossary(os.path.join(a.raweb_dir, "en", "json", "glossaire.json"), dict(meta_raweb, lang="en")), "glossary-raweb-en.json")
    write(build_glossary(os.path.join(a.raweb_dir, "fr", "json", "glossaire.json"), dict(meta_raweb, lang="fr")), "glossary-raweb-fr.json")
    write(build_glossary(os.path.join(a.rgaa_dir, "RGAA", "glossaire.json"), dict(meta_rgaa, lang="fr")), "glossary-rgaa-fr.json")
    meta_raam = {"standard": "RAAM", "version": "1.1", "published": "2025-02-24",
                 "official_url": "https://accessibilite.public.lu/en/raam1.1/referentiel-technique.html"}
    lv_raam = raam_levels(os.path.join(a.raam_dir, "en", "referentiel-technique.md"))
    missing = []
    raam_en = build_raam(os.path.join(a.raam_dir, "en", "json", "criteres.json"), os.path.join(a.raam_dir, "en", "json", "methodologies.json"), lv_raam, dict(meta_raam, lang="en"))
    raam_fr = build_raam(os.path.join(a.raam_dir, "fr", "json", "criteres.json"), os.path.join(a.raam_dir, "fr", "json", "methodologies.json"), lv_raam, dict(meta_raam, lang="fr", official_url="https://accessibilite.public.lu/fr/raam1.1/referentiel-technique.html"))
    missing = [c["id"] for t in raam_en["topics"] for c in t["criteria"] if c["level"] == "?"]
    if missing:
        print("warning: RAAM level not found for", ", ".join(missing))
    write(raam_en, "raam-1.1-en.json")
    write(raam_fr, "raam-1.1-fr.json")
    write(build_glossary(os.path.join(a.raam_dir, "en", "json", "glossaire.json"), dict(meta_raam, lang="en")), "glossary-raam-en.json")
    write(build_glossary(os.path.join(a.raam_dir, "fr", "json", "glossaire.json"), dict(meta_raam, lang="fr")), "glossary-raam-fr.json")
    write(sources, "SOURCES.json")
    write_index(raweb_en, raweb_fr, rgaa_fr)
    write_raam_index(raam_en, raam_fr)


if __name__ == "__main__":
    main()
