# Quick start (for developers and Claude Code users)

Ten minutes from install to a first finding list. For the method behind the tools, read
[web-audit-walkthrough.md](web-audit-walkthrough.md); for what the tools can and cannot prove, read the
[aid, not an audit](../README.md#important-an-aid-not-an-audit) notice first.

## 1. Install

```bash
claude plugin install rgaa-raweb-audit --marketplace GraRi135/rgaa-raweb-claude
```

Other routes (local clone, `--plugin-dir`, copying the skill folder) are in the [README](../README.md#install).
Requirements: Python 3 (no packages). Optional: Node.js with Playwright for rendered pages, adb for Android apps.

## 2. Ask Claude

In a Claude Code session, requests like these load the skill:

* `Audit https://example.lu/ against RAWeb 1.1 and write the report for our agency.`
* `Review Modal.jsx for RGAA conformity, ticket by ticket.`
* `Voici notre grille d'audit RGAA (grille.csv). Calcule le taux de conformité et rédige la déclaration d'accessibilité.`
* `Audit our Android app against RAAM 1.1; the emulator is running.`
* `Which RAWeb tests differ from RGAA for criterion 9.2?`

Claude picks the standard from the context (France → RGAA 4.1.2, Luxembourg → RAWeb 1.1, mobile app → RAAM 1.1) and
says which one it used.

## 3. Or run the tools yourself

All scripts live in `skills/rgaa-raweb-audit/scripts/` and print `--help`.

```bash
cd skills/rgaa-raweb-audit
python3 scripts/criteria.py show 11.10 --tests --methodology          # a criterion, its tests, how to test
python3 scripts/scan_html.py https://example.lu/ --standard raweb     # static pre-check of a page
node scripts/render_page.js https://example.lu/ > home.html            # rendered DOM for single-page apps
python3 scripts/scan_html.py home.html --json > home.scan.json
python3 scripts/contrast.py "#767676" "#ffffff" --size 14             # 4.54:1, passes 4.5:1
python3 scripts/audit_grid.py new --standard raweb --pages "Home=https://example.lu/,Contact=https://example.lu/contact" --out grid.csv
python3 scripts/audit_grid.py set grid.csv --page Home 1.1=NC 8.3=NC 9.2=C --default NA
python3 scripts/audit_grid.py compute grid.csv                         # rate and status with the official rules
```

## 4. What you get

* Findings with a criterion and test id, the element, the problem, who it affects and a fix, grouped by criterion.
* A grid (CSV) of criteria × pages with C / NC / NA / NT, and the compliance rate computed as the standards require.
* A report in the structure the Luxembourg SIP uses for its own audits, and, on request, an accessibility statement
  draft in the mandatory French format.
* A list of what still needs a person with a screen reader and a keyboard. That list is never empty.

## 5. Keep the data current

`python3 scripts/refresh_data.py` rebuilds the bundled criteria from the official GitHub repositories of the SIP and
DINUM; see [updating-data.md](updating-data.md).
