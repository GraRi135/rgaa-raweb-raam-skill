# rgaa-raweb-audit — a Claude skill for RGAA, RAWeb and RAAM accessibility audits

*Version française : [README.fr.md](README.fr.md)*

A skill (installable as a Claude Code plugin) that lets Claude audit websites, pages, front-end code and mobile
applications against:

* **RGAA 4.1.2** — Référentiel général d'amélioration de l'accessibilité (France, DINUM), 106 criteria
* **RAWeb 1.1** — Référentiel d'évaluation de l'accessibilité web (Luxembourg, SIP), 136 criteria (RGAA 4.1.2 + the
  remaining web requirements of EN 301 549 v3.2.1)
* **RAAM 1.1** — Référentiel d'évaluation de l'accessibilité des applications mobiles (Luxembourg, SIP), 108
  criteria for Android and iOS apps, with an adb-based Android evidence collector

It bundles the official criteria, tests and methodology of the three standards (English and French for RAWeb and
RAAM, French for RGAA), the audit method (sample, applicability, compliance rate, statement), the SIP simplified-audit
method, what 228 published SIP audits show (most frequent findings, report structure and wording), and these scripts:

| Script | Purpose |
|---|---|
| `scripts/criteria.py` | look up criteria, tests, test procedures, glossary; diff RAWeb vs RGAA |
| `scripts/scan_html.py` | static pre-check of an HTML page or URL, findings mapped to criteria and tests |
| `scripts/audit_grid.py` | create a pages × criteria grid, fill statuses, compute the compliance rate and status with the official rules |
| `scripts/contrast.py` | contrast ratios with the RGAA/RAWeb thresholds (text, components, focus), from colour pairs or a stylesheet |
| `scripts/android_audit.py` | Android app screens through adb (device or emulator): view hierarchy, screenshot, 200 % text, orientation, TalkBack toggle; findings mapped to RAAM 1.1 |
| `scripts/build_report.py` | findings file → one accessible HTML report with annotated screenshots embedded, and an A4 PDF, in the SIP's report order |
| `scripts/render_page.js` | optional: render a URL with Playwright (SPA support, tab order, zoom and mobile screenshots); `--annotate` outlines each finding's element and clips a screenshot; `--print` makes the PDF |
| `scripts/refresh_data.py` | regenerate the bundled data from the upstream GitHub repositories |

## Important: an aid, not an audit

This skill is a working aid for auditors and developers. It can miss problems and it can be wrong: the static
checks only see what is in the delivered HTML or in an Android view hierarchy, the "review" items are
heuristics, and Claude's own judgement on a criterion can be mistaken even with the official test wording in
front of it. Nothing it produces replaces a conformity audit carried out by a trained auditor on the full
sample, with the assistive technologies of the test environment (NVDA, JAWS, VoiceOver, TalkBack), a
keyboard, and real users where possible. In particular:

* a compliance rate or status computed from its output is provisional until every applicable criterion has
  been tested by a person;
* an accessibility statement must rest on such an audit, and the body publishing it remains responsible for it;
* a page or app with no reported finding is untested, not compliant.

Treat its reports as evidence to verify and as a to-do list, never as the audit itself.

## Install

From your shell (Claude Code v2.1.292 or later), in one command:

```bash
claude plugin install rgaa-raweb-audit --marketplace GraRi135/rgaa-raweb-claude
```

Or in two steps (this repository is its own one-plugin marketplace):

```bash
claude plugin marketplace add GraRi135/rgaa-raweb-claude
```

```bash
claude plugin install rgaa-raweb-audit@rgaa-raweb-claude
```

Inside a session the same works with `/plugin marketplace add GraRi135/rgaa-raweb-claude` then `/plugin install rgaa-raweb-audit@rgaa-raweb-claude`.
Add `--scope project` to enable it for everyone working in a repository.

To try it without installing, start Claude Code with the clone as a plugin directory:

```bash
claude --plugin-dir /path/to/rgaa-raweb-claude
```

Or copy the skill folder into a skills directory Claude Code reads (`~/.claude/skills/` for every project, `.claude/skills/` inside one project):

```bash
cp -r skills/rgaa-raweb-audit ~/.claude/skills/
```

Then ask things like "audit this page against RAWeb 1.1", "calcule le taux de conformité RGAA de cette grille et rédige
la déclaration d'accessibilité", or "review this React component for RGAA conformity", or "audit our Android app against RAAM". The skill's scripts need
Python 3 only; `render_page.js` additionally needs Node.js and Playwright, and `android_audit.py` needs adb (Android platform-tools).

## Where it works

| Environment | Scripts | Pages | Notes |
|---|---|---|---|
| Claude Code (terminal, desktop app, cloud, VS Code) | yes | public pages fetched and rendered with Playwright; local files | the full workflow, including the Android collector when adb is installed |
| Desktop app or Cowork with the built-in browser | yes | any page the browser can open, including behind a login | browser reading tools and screenshots add keyboard and focus evidence; the shell runs the scripts on exported DOM |
| Claude Code or claude.ai with Claude in Chrome | if a shell exists | any page in your Chrome, with your sign-ins | its JavaScript tool runs the probes in `references/browser-probes.md` and exports the rendered DOM for the scanner |
| claude.ai chat with the skill only | sandbox, no network | HTML you paste or upload | lookup, grid and scanner on supplied files; no browsing |

No environment gives Claude a screen reader: criteria that need NVDA, JAWS, VoiceOver or TalkBack stay "not tested"
until a person runs them.

## Documentation

* [Quick start](docs/quick-start.md) for developers and Claude Code users: install, first commands, what you get.
* [Web audit walkthrough](docs/web-audit-walkthrough.md) for auditors: the method, what Claude does, what you must do, how to read and check a finding.
* [Android app audit walkthrough](docs/android-audit-walkthrough.md): RAAM 1.1 with the adb collector, TalkBack and keyboard passes.
* [Accessibility statements](docs/statements.md): France and Luxembourg obligations, computing the rate from a grid.
* [How the skill was evaluated](docs/evaluation.md): test cases, results with and without the skill, calibration on 228 real SIP audits, known weaknesses.
* [Updating the bundled data](docs/updating-data.md) when a standard changes.
* [Contributing](docs/contributing.md).
* [Examples](examples/README.md): fictional inputs and the reports Claude produced from them.
* [Explainer](explainer/README.md): a single hostable page, in French and English, that teaches twelve accessibility rules with simulations, visual challenges and a quiz, for people who do not know the rules.

## Layout

```
docs/                         guides (quick start, walkthroughs, statements, evaluation, updating, contributing)
examples/                     fictional inputs and example outputs
explainer/                    the hostable awareness page (index.html) and its notes
skills/rgaa-raweb-audit/
├── SKILL.md                  instructions Claude follows
├── references/               audit method, report templates, RAWeb vs RGAA, RAAM and Android workflow, SIP methods
│                             and corpus findings, browser probes, automation map, criteria indexes
│   └── data/                 criteria + tests + methodology + glossary JSON (see NOTICE.md)
├── scripts/                  the tools above (Python 3 stdlib; render_page.js needs Node + Playwright)
└── evals/                    test cases (claude plugin eval compatible)
```

## Licence

The scripts, skill instructions and documentation are under the MIT licence (`LICENSE`). The bundled reference data
is third-party content kept under its own terms: RAWeb 1.1 and RAAM 1.1 under CC-BY 3.0 LU (Service information et
presse, Luxembourg), RGAA 4.1.2 under Licence Ouverte 2.0 (DINUM, France), the SIP report wording under MIT, and the
audit statistics come from CC0 datasets. `NOTICE.md` lists each component with its copyright holder, version, licence
and what was changed; the same information ships inside the skill (`references/data/NOTICE.md`). If you redistribute
the data, keep those attributions.
