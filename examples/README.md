# Examples

Fictional inputs from the evaluation cases and the outputs Claude produced from them with the skill, unedited apart
from removing session paths and renaming the grids to `grille.csv` (the `compute` outputs are not included). They show what to expect; they are not models of correctness, and each report carries
the aid-not-audit notice for that reason.

| Folder | Input | Output |
|---|---|---|
| `commune-homepage-raweb/` | `input-index.html`, a fictional Luxembourg commune homepage with planted defects | `rapport-audit.md` (RAWeb 1.1 report for a web agency), `grille.csv`, `scan-output.md` (scanner evidence), and the illustrated version: `findings.json` (14 findings with CSS selectors), `rapport-illustre.html` (single self-contained file with annotated screenshots) and `rapport-illustre.pdf` built by `build_report.py` |
| `rgaa-grid-and-statement/` | `input-grille-audit.csv`, an RGAA 4.1.2 grid of 9 pages for a fictional town | `calcul-taux-conformite.md` (67.1 %, partially compliant), `declaration-accessibilite.md` (statement draft in the mandatory format, facts to fill in brackets) |
| `react-modal-raweb/` | `Modal.jsx`, `Modal.css`, `ContactDialog.jsx` | `review.md` (ticket-ready findings with RAWeb test ids and fixes) |
| `android-screen-raam/` | `input-capture/`, a synthetic uiautomator capture of a home screen at font scale 1.0 and 2.0 | `review.md` (RAAM 1.1 findings), `grille.csv` |

To reproduce one: install the skill, give Claude the input files and the prompt from the matching folder in
`skills/rgaa-raweb-audit/evals/`.

To rebuild the illustrated report: set each finding's `url` in `findings.json` to the `file://` URL of
`input-index.html` on your machine, then run `render_page.js --annotate findings.json --out shots` and
`build_report.py build findings.annotated.json --grid grille.csv --out rapport-illustre.html --pdf rapport-illustre.pdf --lang fr`
(see `docs/web-audit-walkthrough.md`). The images referenced by the fixture do not exist, so the screenshots show
missing-image icons; the YouTube frame is blank because the report was built offline.
