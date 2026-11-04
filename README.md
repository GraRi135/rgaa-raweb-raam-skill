# rgaa-raweb-audit — a Claude skill for RGAA and RAWeb accessibility audits

A skill (installable as a Claude Code plugin) that lets Claude audit websites, pages and front-end code against:

* **RGAA 4.1.2** — Référentiel général d'amélioration de l'accessibilité (France, DINUM), 106 criteria
* **RAWeb 1.1** — Référentiel d'évaluation de l'accessibilité web (Luxembourg, SIP), 136 criteria (RGAA 4.1.2 + the
  remaining web requirements of EN 301 549 v3.2.1)

It bundles the official criteria, tests and per-test methodology of both standards (in English and French for RAWeb,
French for RGAA), the audit method (sample, applicability, compliance rate, statement), the SIP simplified-audit
method, what 228 published SIP audits show (most frequent findings, report structure and wording), and these scripts:

| Script | Purpose |
|---|---|
| `scripts/criteria.py` | look up criteria, tests, test procedures, glossary; diff RAWeb vs RGAA |
| `scripts/scan_html.py` | static pre-check of an HTML page or URL, findings mapped to criteria and tests |
| `scripts/audit_grid.py` | create a pages × criteria grid, fill statuses, compute the compliance rate and status with the official rules |
| `scripts/contrast.py` | contrast ratios with the RGAA/RAWeb thresholds (text, components, focus), from colour pairs or a stylesheet |
| `scripts/render_page.js` | optional: render a URL with Playwright (SPA support, tab order, zoom and mobile screenshots) |
| `scripts/refresh_data.py` | regenerate the bundled data from the upstream GitHub repositories |

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
la déclaration d'accessibilité", or "review this React component for RGAA conformity". The skill's scripts need
Python 3 only; `render_page.js` additionally needs Node.js and Playwright.

## Layout

```
skills/rgaa-raweb-audit/
├── SKILL.md                  instructions Claude follows
├── references/               audit method, report templates, RAWeb vs RGAA, automation map, criteria index
│   └── data/                 criteria + tests + methodology + glossary JSON (see NOTICE.md)
├── scripts/                  the tools above (Python 3 stdlib; render_page.js needs Node + Playwright)
└── evals/                    test cases (claude plugin eval compatible)
```

## Licence

Code and documentation: MIT (see `LICENSE`). The bundled RAWeb and RGAA reference data stays under its original
licences, CC-BY 3.0 LU (SIP, Luxembourg) and Licence Ouverte 2.0 (DINUM, France); see
`skills/rgaa-raweb-audit/references/data/NOTICE.md`.
