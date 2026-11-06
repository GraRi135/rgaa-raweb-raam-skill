# Building an illustrated HTML / PDF report

`scripts/build_report.py` turns a structured findings file into one self-contained, accessible HTML report
(images embedded) in the order the SIP uses, and prints it to A4 PDF through Playwright. Screenshots come from
`render_page.js --annotate` (web: element outlined in red with a devtools-style badge showing its markup, clipped
with some context) or `android_audit.py annotate` (apps: crop of the screen around the element's bounds, numbered).

## Workflow

```bash
S=skills/rgaa-raweb-audit/scripts
node $S/render_page.js https://x.lu/ > p01.html                              # rendered DOM (or fetch the HTML otherwise)
python3 $S/scan_html.py p01.html --json > p01.scan.json
python3 $S/build_report.py bootstrap p01.scan.json --url https://x.lu/ --page P01 --title Accueil > findings.json
python3 $S/build_report.py bootstrap p02.scan.json --url https://x.lu/contact --page P02 --title Contact --append findings.json > f2.json && mv f2.json findings.json
# edit findings.json: keep real non-conformities, set status, write problem / impact / fix / priority, add findings the scanner cannot see
node $S/render_page.js --annotate findings.json --out shots/                 # writes findings.annotated.json with screenshot paths
python3 $S/build_report.py build findings.annotated.json --grid grille.csv --out rapport.html --pdf rapport.pdf --lang fr
```

For an app: `android_audit.py annotate android-audit/accueil/ --out shots/` writes `shots/findings.json` (RAAM
findings with cropped screenshots) that `build_report.py build` consumes after you complete the texts.

`bootstrap` is a starting point: it copies every FAIL and REVIEW line with its selector. The auditor (you) decides
which stay as non-conformities, deletes the rest, and writes the problem, impact and fix in the language of the
report. Findings that no scanner produces (keyboard behaviour, screen-reader rendering, relevance of an alt) are
added by hand with a selector so they can be illustrated too.

## findings.json

```json
{
  "site": "https://x.lu/",
  "standard": "raweb",                      // raweb | rgaa | raam
  "lang": "fr",                             // language of the report labels and notice
  "title": "Rapport d'audit d'accessibilité — x.lu — RAWeb 1.1",
  "date": "2026-11-04",
  "auditor": "Service numérique, avec l'aide rgaa-raweb-audit",
  "method": "Analyse statique du DOM rendu de 10 pages, sondes clavier Playwright, mesures de contraste. Aucune technologie d'assistance.",
  "sample": [{"id": "P01", "title": "Accueil", "url": "https://x.lu/"}],
  "statement": "La déclaration d'accessibilité est présente et complète (…).",
  "environment": ["Chromium 130 (Playwright), fenêtre 1280 × 900", "Aucun lecteur d'écran"],
  "summary": {"level": "moyen", "rate": 71.4, "provisional": true, "status": "partial", "counts": {"C": 50, "NC": 20, "NA": 60, "NT": 6}, "text": "…"},
  "results_text": "optional paragraph under the per-page table",
  "opinion": {"text": "Le site peut être consulté mais…", "blocking": ["Des champs de formulaire sans étiquette…", "…"]},
  "findings": [
    {"id": "F001", "criterion": "11.1", "test": "11.1.1", "status": "NC",
     "pages": ["P01", "P02"], "url": "https://x.lu/", "selector": "#newsletter > input:nth-of-type(1)",
     "element": "<input type=\"email\" placeholder=\"Votre adresse e-mail\">",
     "problem": "Le champ n'a qu'un placeholder…", "impact": "Les utilisateurs de lecteur d'écran…", "fix": "<label for=…>…",
     "priority": "majeur",
     "badge": "optional text for the markup badge (defaults to element)",
     "caption": "optional figure caption (also the figure's aria-label)", "screenshot_alt": "optional short alt (default: 'Capture d'écran du constat F001')",
     "expect": "optional regex the NVDA pass must hear on this element (nvda_capture.js)",
     "nvda": [{"browser": "firefox 1xx", "screenReader": "NVDA 2025.x", "onFocus": "…", "lineRead": "…", "verdict": "…"}],
     "click": "optional selector (or list) clicked before the screenshot, to open a menu, tab or accordion panel",
     "hover": "optional selector (or list) hovered first, for hover-driven menus",
     "focus": "optional selector focused, then \"press\" keys (default Enter) for keyboard-only triggers",
     "wait": 400, "margin": 120}
  ],
  "not_tested": [{"criteria": "7.1.2, 4.13, 10.2", "how": "Lecteur d'écran NVDA + Firefox, VoiceOver + Safari sur chaque page"}]
}
```

`summary.rate`, `status` and `counts` are filled from `--grid` when omitted. `status` is `full`, `partial` or `none`.
Findings are grouped by topic and criterion in the annex; criterion titles and levels come from the bundled data of
`standard`, so only the id is needed. Screenshot paths are relative to the findings file. In any text field, backticks
become `<code>` and a line that starts with `{lang=en}` is wrapped in `<span lang="en">`: use it for the English
executive summary of a French report so the language change is marked (criterion 8.7). `margin` (pixels of context
around the element, default 60 or `--margin`) can be set per finding.

## What the report contains

Notice (aid, not an audit) · 1 Summary (level, rate marked provisional when NT remain, status, counts) · 2 Scope and
method (sample table with links, statement check, test environment) · 3 Results (per-page table from the grid)
· 4 Opinion (text and the most blocking families) · 5 Technical annex by topic and criterion, one block per finding
(pages, element, problem, impact, fix, priority, annotated screenshot with alt text and caption) · 6 Criteria not
tested and how to test them. Headings, landmarks, a skip link, table captions and scopes, image alternatives and a
print stylesheet are built in: the report itself passes the structural criteria it audits.

## Limits

Screenshots show the rendered page at the time of the run in a 1280 px window; hidden elements (collapsed menus,
dialogs not open) are reported as not visible and get no image unless you add a `click` on the trigger, or a
`badge`/`selector` for the trigger instead. The badge is placed outside the outlined element but can cover a
neighbour; that is cosmetic. The PDF is tagged (Playwright `tagged: true`) and carries an outline, but its tags are
the browser's: check it in Acrobat or PAC before publishing it as an accessible PDF. The badge shows the start tag as captured by the scanner, not the live DOM. PDF printing needs Node with
Playwright; without it, open the HTML and print to PDF from the browser.
