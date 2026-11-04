#!/usr/bin/env python3
"""Build an accessible, self-contained HTML audit report (and optionally a PDF) from a findings file.

  build_report.py bootstrap scan.json --url https://x.lu/ --page "P01" --title "Accueil" [--append findings.json] > findings.json
      Turn scan_html.py --json output into findings entries (FAIL and REVIEW), ready to annotate and complete.
  node render_page.js --annotate findings.json --out shots/        # screenshots (web); android_audit.py annotate (apps)
  build_report.py build findings.annotated.json --out rapport.html [--grid grille.csv] [--pdf rapport.pdf] [--lang fr]

The findings file schema is documented in references/report-builder.md. Images are embedded as data URIs so the
HTML is one file; --pdf prints it to A4 through render_page.js (needs Node and Playwright).
"""
import argparse, base64, csv, datetime, html, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "references", "data")
sys.path.insert(0, HERE)

L = {
    "fr": {"report": "Rapport d'audit d'accessibilité", "notice_h": "Avertissement", "summary": "Synthèse", "scope": "Périmètre et méthode", "sample": "Échantillon", "env": "Environnement de test",
           "results": "Accessibilité des pages auditées", "opinion": "Avis", "annex": "Annexe technique", "nt": "Critères non testés", "page": "Page", "title": "Titre", "url": "URL", "standard": "Référentiel",
           "date": "Date", "auditor": "Auditeur", "method": "Méthode", "rate": "Taux de conformité", "provisional": "provisoire", "status": "État de conformité", "level": "Niveau général d'accessibilité",
           "counts": "Critères", "C": "conformes", "NC": "non conformes", "NA": "non applicables", "NT": "non testés", "statuses": {"full": "totalement conforme", "partial": "partiellement conforme", "none": "non conforme"},
           "blocking": "Les non-conformités les plus bloquantes pour les utilisateurs concernent :", "finding": "Constat", "criterion": "Critère", "test": "Test", "pages": "Pages", "element": "Élément",
           "problem": "Problème", "impact": "Impact", "fix": "Correction", "priority": "Priorité (appréciation de l'auditeur)", "per_page": "Résultats par page", "applicable": "Applicables", "rate_col": "Taux",
           "figure": "Capture d'écran annotée : l'élément concerné est entouré en rouge", "shot_alt": "Capture d'écran du constat", "no_shot": "Aucune capture pour ce constat", "toc": "Sommaire", "skip": "Aller au contenu", "generated": "Rapport généré le",
           "notice": "Ce rapport a été produit avec une aide automatisée (analyse du code et du DOM rendu). Il peut comporter des erreurs ou des omissions. Il ne remplace ni un audit de conformité réalisé par un auditeur sur l'échantillon complet avec les technologies d'assistance de l'environnement de test, ni des tests avec des utilisateurs en situation de handicap. Les taux indiqués sont provisoires tant que chaque critère applicable n'a pas été testé par une personne ; l'absence de constat sur un critère signifie « non testé », pas « conforme ».",
           "stmt": "Déclaration d'accessibilité", "topic": "Thématique", "how": "Comment tester", "no_findings": "Aucun constat dans cette thématique."},
    "en": {"report": "Accessibility audit report", "notice_h": "Notice", "summary": "Summary", "scope": "Scope and method", "sample": "Sample", "env": "Test environment",
           "results": "Accessibility of the audited pages", "opinion": "Opinion", "annex": "Technical annex", "nt": "Criteria not tested", "page": "Page", "title": "Title", "url": "URL", "standard": "Standard",
           "date": "Date", "auditor": "Auditor", "method": "Method", "rate": "Compliance rate", "provisional": "provisional", "status": "Compliance status", "level": "Overall accessibility level",
           "counts": "Criteria", "C": "compliant", "NC": "non-compliant", "NA": "not applicable", "NT": "not tested", "statuses": {"full": "fully compliant", "partial": "partially compliant", "none": "non-compliant"},
           "blocking": "The most blocking non-conformities for users concern:", "finding": "Finding", "criterion": "Criterion", "test": "Test", "pages": "Pages", "element": "Element",
           "problem": "Problem", "impact": "Impact", "fix": "Fix", "priority": "Priority (auditor's judgement)", "per_page": "Results per page", "applicable": "Applicable", "rate_col": "Rate",
           "figure": "Annotated screenshot: the element concerned is outlined in red", "shot_alt": "Screenshot of finding", "no_shot": "No screenshot for this finding", "toc": "Contents", "skip": "Skip to content", "generated": "Report generated on",
           "notice": "This report was produced with an automated aid (analysis of the code and of the rendered DOM). It may contain errors or omissions. It does not replace a conformity audit carried out by an auditor on the full sample with the assistive technologies of the test environment, nor testing with disabled users. Rates are provisional until every applicable criterion has been tested by a person; the absence of a finding on a criterion means not tested, not compliant.",
           "stmt": "Accessibility statement", "topic": "Topic", "how": "How to test", "no_findings": "No finding in this topic."},
}
STD_NAMES = {"raweb": "RAWeb 1.1", "rgaa": "RGAA 4.1.2", "raam": "RAAM 1.1"}


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def load_std(standard, lang):
    name = {"raweb": f"raweb-1.1-{lang if lang in ('en', 'fr') else 'en'}.json", "rgaa": "rgaa-4.1.2-fr.json", "raam": f"raam-1.1-{lang if lang in ('en', 'fr') else 'en'}.json"}[standard]
    std = json.load(open(os.path.join(DATA, name), encoding="utf-8"))
    crit = {}; topics = {}
    for t in std["topics"]:
        topics[t["number"]] = t["title"]
        for c in t["criteria"]:
            crit[c["id"]] = {"level": c["level"], "title": re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", c["title"]), "topic": t["number"]}
    return crit, topics


def key(cid):
    try:
        return tuple(int(x) for x in str(cid).split("."))
    except ValueError:
        return (999,)


def data_uri(path):
    ext = os.path.splitext(path)[1].lower().lstrip(".") or "png"
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif", "webp": "image/webp", "svg": "image/svg+xml"}.get(ext, "image/png")
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()


def md_inline(s):
    """Minimal inline formatting: backticks to <code>, line breaks kept; a line starting with {lang=xx} is wrapped
    in <span lang="xx"> so a language change (an English summary in a French report) is marked (criterion 8.7)."""
    out = []
    for line in str(s).split("\n"):
        m = re.match(r"^\{lang=([A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})?)\}\s*(.*)$", line)
        body = esc(m.group(2) if m else line)
        body = re.sub(r"`([^`]+)`", r"<code>\1</code>", body)
        out.append(f'<span lang="{esc(m.group(1))}">{body}</span>' if m else body)
    return "<br>".join(out)


def fmt_rate(x, lang):
    """Rates are printed with a decimal comma in French reports."""
    s = str(x)
    return s.replace(".", ",") if str(lang).lower().startswith("fr") else s


# ---------------------------------------------------------------- bootstrap
def cmd_bootstrap(a):
    scan = json.load(open(a.scan, encoding="utf-8"))
    base = json.load(open(a.append, encoding="utf-8")) if a.append and os.path.exists(a.append) else {"findings": []}
    base.setdefault("findings", []); base.setdefault("sample", []); base.setdefault("standard", "raweb" if "RAWeb" in scan.get("standard", "") else "rgaa")
    if not any(p.get("id") == a.page for p in base["sample"]):
        base["sample"].append({"id": a.page, "title": a.title or a.page, "url": a.url})
    n = len(base["findings"])
    for f in scan["findings"]:
        if f["status"] not in ("fail", "review") or f["criterion"] in ("0.0", "0"):
            continue
        n += 1
        base["findings"].append({"id": f"F{n:03d}", "criterion": f["criterion"], "test": f.get("test"), "status": "NC" if f["status"] == "fail" else "to-verify",
                                 "pages": [a.page], "url": a.url, "selector": f.get("selector"), "element": f.get("element"), "line": f.get("line"),
                                 "problem": f["message"], "impact": "", "fix": "", "priority": ""})
    json.dump(base, sys.stdout, ensure_ascii=False, indent=1); print()


# ---------------------------------------------------------------- build
def per_page_table(grid_path, standard, lang, T):
    try:
        import audit_grid
        pages, grid = audit_grid.read_grid(grid_path)
        res = audit_grid.compute(pages, grid, {})
    except Exception as e:
        return f"<p>{esc(T['per_page'])}: {esc(str(e))}</p>", None
    rows = "".join(f"<tr><th scope=\"row\">{esc(p)}</th><td>{r['applicable']}</td><td>{r['compliant']}</td><td>{r['not_tested']}</td><td>{esc(fmt_rate(r['rate'], lang)) if r['rate'] is not None else '-'} %</td></tr>" for p, r in res["pages"].items())
    table = f"<table><caption>{esc(T['per_page'])}</caption><thead><tr><th scope=\"col\">{esc(T['page'])}</th><th scope=\"col\">{esc(T['applicable'])}</th><th scope=\"col\">{esc(T['C'])}</th><th scope=\"col\">{esc(T['NT'])}</th><th scope=\"col\">{esc(T['rate_col'])}</th></tr></thead><tbody>{rows}</tbody></table>"
    return table, res["site"]


def cmd_build(a):
    doc = json.load(open(a.findings, encoding="utf-8"))
    lang = a.lang or doc.get("lang") or "fr"
    T = L["fr"] if lang.startswith("fr") else L["en"]
    standard = doc.get("standard", "raweb")
    crit, topics = load_std(standard, "fr" if lang.startswith("fr") else "en")
    base_dir = os.path.dirname(os.path.abspath(a.findings))
    findings = doc.get("findings", [])
    for f in findings:
        if f.get("criterion") in crit:
            f.setdefault("level", crit[f["criterion"]]["level"]); f.setdefault("title", crit[f["criterion"]]["title"])
    site = doc.get("site", ""); title = doc.get("title") or f"{T['report']} — {site} — {STD_NAMES.get(standard, standard)}"
    summary = doc.get("summary", {}); opinion = doc.get("opinion", {})
    grid_html, site_res = (per_page_table(a.grid, standard, lang, T) if a.grid else ("", None))
    if site_res and not summary.get("rate") and site_res.get("rate") is not None:
        summary.setdefault("rate", site_res["rate"]); summary.setdefault("status", site_res["status"]); summary.setdefault("provisional", bool(site_res["not_tested"]))
        summary.setdefault("counts", {"C": len(site_res["compliant"]), "NC": len(site_res["non_compliant"]), "NA": len(site_res["not_applicable"]), "NT": len(site_res["not_tested"])})
    # group findings by topic then criterion
    by_topic = {}
    for f in findings:
        tn = crit.get(f.get("criterion"), {}).get("topic") or int(str(f.get("criterion", "0")).split(".")[0] or 0)
        by_topic.setdefault(tn, {}).setdefault(f.get("criterion"), []).append(f)
    parts = []
    parts.append(f"<!DOCTYPE html><html lang=\"{esc(lang)}\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>{esc(title)}</title><style>{CSS}</style></head><body>")
    parts.append(f"<a class=\"skip\" href=\"#main\">{esc(T['skip'])}</a><header><h1>{esc(title)}</h1><p class=\"meta\">{esc(T['standard'])} : {esc(STD_NAMES.get(standard, standard))}"
                 + (f" · {esc(T['date'])} : {esc(doc['date'])}" if doc.get("date") else "") + (f" · {esc(T['auditor'])} : {esc(doc['auditor'])}" if doc.get("auditor") else "") + "</p></header>")
    parts.append(f"<main id=\"main\"><section class=\"notice\" aria-labelledby=\"notice\"><h2 id=\"notice\">{esc(T['notice_h'])}</h2><p>{esc(doc.get('notice') or T['notice'])}</p></section>")
    # toc
    secs = [("summary", T["summary"]), ("scope", T["scope"]), ("results", T["results"]), ("opinion", T["opinion"]), ("annex", T["annex"]), ("nt", T["nt"])]
    parts.append("<nav aria-labelledby=\"toc\"><h2 id=\"toc\">" + esc(T["toc"]) + "</h2><ol>" + "".join(f"<li><a href=\"#{i}\">{esc(n)}</a></li>" for i, n in secs) + "</ol></nav>")
    # 1 summary
    parts.append(f"<section aria-labelledby=\"summary\"><h2 id=\"summary\">1. {esc(T['summary'])}</h2>")
    if summary.get("level"):
        parts.append(f"<p>{esc(T['level'])} : <strong>{esc(summary['level'])}</strong>.</p>")
    if summary.get("rate") is not None:
        st = T["statuses"].get(summary.get("status"), summary.get("status", ""))
        parts.append(f"<p>{esc(T['rate'])}{' (' + esc(T['provisional']) + ')' if summary.get('provisional') else ''} : <strong>{esc(fmt_rate(summary['rate'], lang))} %</strong>. {esc(T['status'])} : <strong>{esc(st)}</strong>.</p>")
    c = summary.get("counts")
    if c:
        parts.append("<table><caption>" + esc(T["counts"]) + "</caption><thead><tr>" + "".join(f"<th scope=\"col\">{esc(T[k])}</th>" for k in ("C", "NC", "NA", "NT")) + "</tr></thead><tbody><tr>" + "".join(f"<td>{esc(c.get(k, 0))}</td>" for k in ("C", "NC", "NA", "NT")) + "</tr></tbody></table>")
    if summary.get("text"):
        parts.append(f"<p>{md_inline(summary['text'])}</p>")
    parts.append("</section>")
    # 2 scope
    parts.append(f"<section aria-labelledby=\"scope\"><h2 id=\"scope\">2. {esc(T['scope'])}</h2>")
    if doc.get("method"):
        parts.append(f"<p>{md_inline(doc['method'])}</p>")
    if doc.get("sample"):
        parts.append(f"<h3>{esc(T['sample'])}</h3><table><caption>{esc(T['sample'])}</caption><thead><tr><th scope=\"col\">N°</th><th scope=\"col\">{esc(T['title'])}</th><th scope=\"col\">{esc(T['url'])}</th></tr></thead><tbody>"
                     + "".join(f"<tr><th scope=\"row\">{esc(p.get('id', ''))}</th><td>{esc(p.get('title', ''))}</td><td>{('<a href=\"' + esc(p['url']) + '\">' + esc(p['url']) + '</a>') if str(p.get('url', '')).startswith('http') else esc(p.get('url', ''))}</td></tr>" for p in doc["sample"]) + "</tbody></table>")
    if doc.get("statement"):
        parts.append(f"<h3>{esc(T['stmt'])}</h3><p>{md_inline(doc['statement'])}</p>")
    if doc.get("environment"):
        parts.append(f"<h3>{esc(T['env'])}</h3><ul>" + "".join(f"<li>{md_inline(e)}</li>" for e in doc["environment"]) + "</ul>")
    parts.append("</section>")
    # 3 results
    parts.append(f"<section aria-labelledby=\"results\"><h2 id=\"results\">3. {esc(T['results'])}</h2>{grid_html}")
    if doc.get("results_text"):
        parts.append(f"<p>{md_inline(doc['results_text'])}</p>")
    parts.append("</section>")
    # 4 opinion
    parts.append(f"<section aria-labelledby=\"opinion\"><h2 id=\"opinion\">4. {esc(T['opinion'])}</h2>")
    if opinion.get("text"):
        parts.append(f"<p>{md_inline(opinion['text'])}</p>")
    if opinion.get("blocking"):
        parts.append(f"<p>{esc(T['blocking'])}</p><ul>" + "".join(f"<li>{md_inline(b)}</li>" for b in opinion["blocking"]) + "</ul>")
    parts.append("</section>")
    # 5 annex
    parts.append(f"<section aria-labelledby=\"annex\"><h2 id=\"annex\">5. {esc(T['annex'])}</h2>")
    for tn in sorted(by_topic):
        parts.append(f"<h3 id=\"topic-{tn}\">{esc(T['topic'])} {tn} — {esc(topics.get(tn, ''))}</h3>")
        for cid in sorted(by_topic[tn], key=key):
            fs = by_topic[tn][cid]; info = crit.get(cid, {})
            parts.append(f"<h4 id=\"crit-{esc(cid).replace('.', '-')}\">{esc(T['criterion'])} {esc(cid)} [{esc(info.get('level', '?'))}] {esc(info.get('title', ''))}</h4>")
            for f in fs:
                parts.append("<article class=\"finding\" aria-labelledby=\"f-" + esc(f.get("id", "")) + "\">")
                parts.append(f"<h5 id=\"f-{esc(f.get('id', ''))}\">{esc(T['finding'])} {esc(f.get('id', ''))}" + (f" — {esc(T['test'])} {esc(f['test'])}" if f.get("test") else "") + (" <span class=\"tag\">" + esc(f["status"]) + "</span>" if f.get("status") else "") + "</h5>")
                parts.append("<dl>")
                if f.get("pages"):
                    parts.append(f"<dt>{esc(T['pages'])}</dt><dd>{esc(', '.join(f['pages']))}</dd>")
                if f.get("element"):
                    parts.append(f"<dt>{esc(T['element'])}</dt><dd><code>{esc(f['element'])}</code></dd>")
                for k in ("problem", "impact", "fix"):
                    if f.get(k):
                        parts.append(f"<dt>{esc(T[k])}</dt><dd>{md_inline(f[k])}</dd>")
                if f.get("priority"):
                    parts.append(f"<dt>{esc(T['priority'])}</dt><dd>{esc(f['priority'])}</dd>")
                parts.append("</dl>")
                shot = f.get("screenshot")
                if shot:
                    sp = shot if os.path.isabs(shot) else os.path.join(base_dir, shot)
                    if os.path.exists(sp):
                        cap = f.get("caption") or T["figure"]
                        alt = f.get("screenshot_alt") or f"{T['shot_alt']} {f.get('id', '')}".strip()
                        parts.append(f"<figure role=\"figure\" aria-label=\"{esc(cap)}\"><img src=\"{data_uri(sp)}\" alt=\"{esc(alt)}\"><figcaption>{esc(cap)}</figcaption></figure>")
                elif f.get("screenshot_note"):
                    parts.append(f"<p class=\"note\">{esc(T['no_shot'])} ({esc(f['screenshot_note'])}).</p>")
                parts.append("</article>")
    if not by_topic:
        parts.append(f"<p>{esc(T['no_findings'])}</p>")
    parts.append("</section>")
    # 6 not tested
    parts.append(f"<section aria-labelledby=\"nt\"><h2 id=\"nt\">6. {esc(T['nt'])}</h2>")
    if doc.get("not_tested"):
        parts.append(f"<table><caption>{esc(T['nt'])}</caption><thead><tr><th scope=\"col\">{esc(T['criterion'])}</th><th scope=\"col\">{esc(T['how'])}</th></tr></thead><tbody>" + "".join(f"<tr><td>{md_inline(n.get('criteria', ''))}</td><td>{md_inline(n.get('how', ''))}</td></tr>" for n in doc["not_tested"]) + "</tbody></table>")
    parts.append("</section>")
    parts.append(f"</main><footer><p>{esc(T['generated'])} {datetime.date.today().isoformat()} · rgaa-raweb-audit</p></footer></body></html>")
    out = a.out or os.path.splitext(a.findings)[0] + ".html"
    open(out, "w", encoding="utf-8").write("".join(parts))
    print(f"wrote {out} ({os.path.getsize(out) // 1024} KB, {len(findings)} findings)")
    if a.pdf:
        r = subprocess.run(["node", os.path.join(HERE, "render_page.js"), "--print", out, "--pdf", a.pdf], capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip())


CSS = """
:root{--ink:#1a1a1a;--muted:#555;--accent:#8b1d1d;--line:#d9d9d9;--bg:#fff}
html{font:16px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:var(--ink);background:var(--bg)}
body{margin:0;padding:0 16px}main,header,footer{max-width:900px;margin:0 auto}
.skip{position:absolute;left:-9999px}.skip:focus{position:static;display:inline-block;padding:8px;background:#ffd;border:2px solid var(--accent)}
h1{font-size:1.7rem;line-height:1.25}h2{font-size:1.35rem;margin-top:2.2em;border-bottom:2px solid var(--accent);padding-bottom:.2em}h3{font-size:1.15rem;margin-top:1.8em}h4{font-size:1.02rem;margin-top:1.4em;color:var(--accent)}h5{font-size:.98rem;margin:.9em 0 .3em}
.meta{color:var(--muted)}.notice{background:#fff8e1;border:2px solid #e0a800;border-radius:4px;padding:8px 16px;margin:16px 0}.notice h2{margin-top:.4em;border:0;font-size:1.1rem}
nav ol{columns:2;gap:24px}table{border-collapse:collapse;width:100%;margin:1em 0;font-size:.95rem}caption{text-align:left;font-weight:600;margin-bottom:.3em}th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}th{background:#f3f3f3}
.finding{border:1px solid var(--line);border-left:4px solid var(--accent);padding:4px 14px 10px;margin:1em 0}dl{display:grid;grid-template-columns:max-content 1fr;gap:.3em 1em}dt{font-weight:600}dd{margin:0}
code{font:.9em Menlo,Consolas,monospace;background:#f4f4f4;padding:0 .2em;word-break:break-all}.tag{font-size:.75rem;font-weight:400;color:#fff;background:var(--accent);padding:1px 6px;border-radius:3px;margin-left:.5em;vertical-align:middle}
figure{margin:.8em 0}figure img{max-width:100%;height:auto;border:1px solid var(--line)}figcaption{font-size:.85rem;color:var(--muted)}.note{font-size:.9rem;color:var(--muted)}
footer{margin:3em auto 2em;color:var(--muted);font-size:.85rem}a{color:#0b4f9c}a:focus,button:focus{outline:3px solid #0b4f9c;outline-offset:2px}
@media print{html{font-size:11pt}body{padding:0}.skip,nav{display:none}h2,h3,h4,h5{page-break-after:avoid;break-after:avoid}figure{break-inside:avoid;page-break-inside:avoid}figure img{max-height:95mm;width:auto}.finding h5{break-after:avoid;page-break-after:avoid}dt,dd{break-inside:avoid}a{color:inherit;text-decoration:none}}
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bootstrap"); b.add_argument("scan"); b.add_argument("--url", required=True); b.add_argument("--page", default="P01"); b.add_argument("--title"); b.add_argument("--append")
    c = sub.add_parser("build"); c.add_argument("findings"); c.add_argument("--out"); c.add_argument("--grid"); c.add_argument("--pdf"); c.add_argument("--lang")
    a = ap.parse_args()
    {"bootstrap": cmd_bootstrap, "build": cmd_build}[a.cmd](a)


if __name__ == "__main__":
    main()
