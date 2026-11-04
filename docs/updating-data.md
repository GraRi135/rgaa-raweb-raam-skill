# Updating the bundled data

The criteria, tests, methodology and glossaries come from the official GitHub repositories:

| Standard | Repository | Version bundled |
|---|---|---|
| [RAWeb 1.1](https://accessibilite.public.lu/en/raweb1.1/criteres.html) | [accessibility-luxembourg/ReferentielAccessibiliteWeb](https://github.com/accessibility-luxembourg/ReferentielAccessibiliteWeb) | 1.1, 6 February 2026 |
| [RGAA 4.1.2](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/) | [DISIC/accessibilite.numerique.gouv.fr](https://github.com/DISIC/accessibilite.numerique.gouv.fr) (folder `RGAA/`) | 4.1.2, 18 April 2023 |
| [RAAM 1.1](https://accessibilite.public.lu/en/raam1.1/criteres.html) | [accessibility-luxembourg/ReferentielAccessibiliteMobile](https://github.com/accessibility-luxembourg/ReferentielAccessibiliteMobile) | 1.1, 24 February 2025 |
| SIP report wording | [accessibility-luxembourg/simplA11yGenReport](https://github.com/accessibility-luxembourg/simplA11yGenReport) | snapshot of November 2026 |

`skills/rgaa-raweb-audit/references/data/SOURCES.json` records the exact upstream commits (and, for the SIP
wording, the snapshot date: that file is copied by hand, see below).

## Rebuild

```bash
cd skills/rgaa-raweb-audit
python3 scripts/refresh_data.py
```

The script clones the three repositories into a temporary folder, merges each standard into one JSON file per
language (criteria, tests, per-test or per-criterion methodology, level, WCAG and [EN 301 549](https://www.etsi.org/deliver/etsi_en/301500_301599/301549/03.02.01_60/en_301549v030201p.pdf) references), copies the
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

The SIP wording file (`sip-report-wording-fr.json`) is not rebuilt by `refresh_data.py`: copy `topics.json` and
`solutions.json` from the simplA11yGenReport repository by hand, keep the MIT notice, and update `SOURCES.json`;
the corpus statistics in `sip-audit-corpus.md` are a dated snapshot and can be recomputed from the [data.public.lu](https://data.public.lu/en/)
datasets with their API (`/api/1/datasets/<slug>/`, field `resources[].url`).
