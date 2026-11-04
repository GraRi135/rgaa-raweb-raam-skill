# Updating the bundled data

The criteria, tests, methodology and glossaries come from the official GitHub repositories:

| Standard | Repository | Version bundled |
|---|---|---|
| RAWeb 1.1 | accessibility-luxembourg/ReferentielAccessibiliteWeb | 1.1, 6 February 2026 |
| RGAA 4.1.2 | DISIC/accessibilite.numerique.gouv.fr (folder `RGAA/`) | 4.1.2, 18 April 2023 |
| RAAM 1.1 | accessibility-luxembourg/ReferentielAccessibiliteMobile | 1.1, 24 February 2025 |
| SIP report wording | accessibility-luxembourg/simplA11yGenReport | snapshot of November 2026 |

`skills/rgaa-raweb-audit/references/data/SOURCES.json` records the exact upstream commits.

## Rebuild

```bash
cd skills/rgaa-raweb-audit
python3 scripts/refresh_data.py
```

The script clones the three repositories into a temporary folder, merges each standard into one JSON file per
language (criteria, tests, per-test or per-criterion methodology, level, WCAG and EN 301 549 references), copies the
glossaries, and regenerates `references/criteria-index.md` and `references/raam-criteria-index.md`. Pass
`--raweb-dir`, `--rgaa-dir` and `--raam-dir` to use existing clones.

## When a standard changes

1. Run the rebuild and read the diff of the index files: new criteria, renumbered tests, changed wording.
2. Update the hand-written references that cite numbers: `raweb-vs-rgaa.md`, `audit-method.md`, `automation-map.md`,
   `sip-simplified-audit.md`, `raam-mobile.md`, and the scanner messages in `scan_html.py` and `android_audit.py`.
3. Update the versions in `NOTICE.md`, `references/data/NOTICE.md` and this page.
4. Re-run the evals (`claude plugin eval .` from the skill folder, or the skill-creator loop) because assertions cite
   test ids.
5. Bump `version` in `.claude-plugin/plugin.json`.

The SIP wording file (`sip-report-wording-fr.json`) is refreshed separately from the simplA11yGenReport repository;
the corpus statistics in `sip-audit-corpus.md` are a dated snapshot and can be recomputed from the data.public.lu
datasets with their API (`/api/1/datasets/<slug>/`, field `resources[].url`).
