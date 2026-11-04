# Project memory: rgaa-raweb-claude

Read this first when resuming development. It records what exists, why it is the way it is, and what is still open.
Everything below was built in one long Claude Code session on branch `claude/vigilant-ritchie-xmvt2a` (GitHub:
GraRi135/rgaa-raweb-claude). Merge or rebase that branch as you see fit; nothing is on `main` yet unless you merged it.

## What this repository is

A Claude Code plugin with one skill, `rgaa-raweb-audit`, that helps audit digital accessibility against:

- **RAWeb 1.1** (Luxembourg web standard, 17 topics / 136 criteria / 304 tests, published 6 February 2026),
- **RGAA 4.1.2** (France, 13 topics / 106 criteria / 258 tests),
- **RAAM 1.1** (Luxembourg mobile-app standard, 15 topics / 108 criteria, Android via adb),

plus an awareness page (`explainer/index.html`) for people who do not know the rules.

Guiding principle, repeated everywhere (README, README.fr, NOTICE.md, SKILL.md, every report): **the skill is an
aid, not an audit**. It can miss things and be wrong; it never replaces a conformity audit with assistive technologies
or tests with disabled users. Rates it computes are provisional while criteria remain "not tested".

## Layout

```
.claude-plugin/plugin.json, marketplace.json   plugin metadata (name rgaa-raweb-audit, version 0.1.0)
README.md / README.fr.md                      full English and full French README (keep them in sync, section by section)
NOTICE.md, LICENSE                            MIT for our code; third-party data licences listed in NOTICE.md
docs/                                         quick-start, web-audit-walkthrough, android-audit-walkthrough, statements,
                                              evaluation, updating-data, contributing
examples/                                     fictional inputs + outputs only (commune-homepage-raweb incl. illustrated
                                              report, rgaa-grid-and-statement, react-modal-raweb, android-screen-raam)
explainer/                                    index.html (single self-contained awareness page) + README.md
skills/rgaa-raweb-audit/
  SKILL.md                                    the instructions Claude follows (description must stay <= 1024 chars)
  references/*.md                             audit-method, report-templates, raweb-vs-rgaa, automation-map,
                                              sip-simplified-audit, sip-audit-corpus, raam-mobile, raam-criteria-index,
                                              criteria-index, browser-probes, report-builder
  references/data/*.json                      criteria/tests/methodology/glossaries for the three standards,
                                              sip-report-wording-fr.json, SOURCES.json, NOTICE.md
  scripts/                                    see "Tools" below
  evals/                                      4 eval cases (claude plugin eval layout)
*-workspace/ (git-ignored)                    eval runs and the two real-site test audits; NOT in git, only in the
                                              cloud session that built this (you have the delivered files instead)
```

## Tools (all Python 3 stdlib unless noted)

| Script | Purpose | Typical call |
|---|---|---|
| `criteria.py` | query the bundled data | `show 9.2 --standard raweb --tests`, `list`, `search`, `glossary`, `topics`, `diff` |
| `scan_html.py` | static pre-check of an HTML file, RAWeb or RGAA numbering; emits FAIL / REVIEW / INFO with a CSS `selector` per finding | `scan_html.py page.html --standard raweb [--json]` |
| `audit_grid.py` | create / fill / compute an audit grid (C, NC, NA, NT); rate = C / (C + NC); site-level rules | `new --standard raweb --pages-file pages.json`, `set`, `compute` |
| `contrast.py` | WCAG contrast ratio and 3.2 / 3.3 / 10.7 verdicts | `contrast.py "#767676" "#ffffff" --size 14` |
| `render_page.js` (Node + Playwright) | rendered DOM, `--tab-order`, `--zoom`, `--mobile`, `--screenshot`, `--annotate findings.json --out shots` (element outlined + markup badge), `--print report.html --pdf out.pdf` (tagged A4 PDF) | |
| `build_report.py` | `bootstrap` findings from a scan; `build findings.annotated.json --grid grille.csv --out rapport.html --pdf rapport.pdf --lang fr` → one self-contained accessible HTML (SIP outline, embedded screenshots) | |
| `android_audit.py` | `devices`, `capture` (uiautomator dump + screenshot via adb), `analyse` (RAAM mapping), `font-scale`, `rotate`, `talkback`, `compare`, `walk`, `annotate` | needs adb and a device/emulator |
| `refresh_data.py` | rebuild `references/data/*.json` from the upstream GitHub repos (network) | see docs/updating-data.md |

Findings file schema and per-finding options (`selector`, `badge`, `caption`, `screenshot_alt`, `click`, `hover`,
`focus`/`press`, `wait`, `margin`; `{lang=en}` line prefix for language changes in texts) are in
`references/report-builder.md`.

## Conventions and decisions taken with the owner

- Audience of the docs: developers **and** auditors. English docs plus a **full** French README. `docs/` folder.
- **Fictional examples only** in the repo (commune of Fiktivbuerg, Ville d'Exemple, personas Lena/Marc/Anne/Tom/Sara/Jo).
  No real third-party audit reports or figures in git. Two real sites (adem.public.lu, info-handicap.lu) were audited
  as tests in the cloud session; those reports were delivered to the owner as files and are deliberately not committed.
- Licences: our code MIT (copyright GraRi135); RAWeb and RAAM data CC-BY 3.0 LU (Service information et presse);
  RGAA data Licence Ouverte 2.0 (DINUM); SIP report wording MIT; SIP audit datasets CC0. Keep NOTICE.md,
  references/data/NOTICE.md, SOURCES.json and the README licence sections in agreement.
- Reports: French for Luxembourg/France official documents, SIP full-audit outline ("Constats sur le site"),
  statuses C/NC/NA/NT, non-interference criteria, provisional rate while NT remain, aid-not-audit notice on top.
  Illustrated reports: single self-contained HTML + PDF, cropped element screenshot with a devtools-style markup badge,
  neutral, no cover page.
- Sources: the first mention of a standard, law, body or dataset in each documentation file is a link, and the main
  files end with a "Sources" section (English URLs in English files, French in README.fr.md). Keep both in sync.
- Commit messages: plain, descriptive; the branch is pushed with `git push -u origin <branch>`.
- Validate before committing: `claude plugin validate .` (one harmless warning: no icon file).

## The explainer page (explainer/index.html)

- Single file, no dependencies, **system fonts only** (no Google Fonts: public-sector/GDPR choice), light and dark
  themes via CSS tokens on `:root`, phone layout, reduced-motion support.
- French is the source text in the HTML (`data-t` keys); English is the `EN` dictionary in the script; the `FR`
  dictionary holds the strings the script generates. Language toggle remembered in localStorage; default FR unless the
  browser language starts with "en".
- Structure: hero "put on someone else's glasses" simulator (Marc colour-blind filter, Anne blur, Lena screen-reader
  transcript, fix switch); why section with six fictional personas and the note that twelve rules are a small part of
  the standard; **twelve rules**, each = demo card ("Essayez") stacked above a challenge card ("À vous");
  users' rights (statement, contact, SIP or Ombudsman; France: RGAA, Défenseur des droits); eight-question quiz;
  further reading; footer disclaimer.
- Rules: 1 colour (waste calendar + colour-vision filters), 2 contrast (slider), 3 images, 4 headings (outline),
  5 links (link list), 6 keyboard (Tab counter; invitation to continue the page by keyboard), 7 menus (hover-only vs
  accessible dropdown: button, Enter/Space, Escape, real links; dropdown look kept, wrapper reserves the panel height
  while open), 8 forms, 9 zoom, 10 on a phone (phone frame: tiny / fixed width scrolling sideways / fluid),
  11 video and motion (ticker pause, captions), 12 documents (scanned PDF; a PDF with text is better than a scan but
  still has its own rules).
- Challenges and quiz: **preview, then confirm**: clicking an answer renders a visual example of it in a stage
  (`PV` renderers in the script, one per challenge, FR/EN aware); "C'est la meilleure" confirms; rule challenges can be
  re-tried, the quiz locks each question. Hints are visible callouts (`.hint`, blue; `.good` green when the fixed
  version is on; `.bad` red for a failure message). Line icons are an inline SVG sprite (`#i-*`).
- Checks that must stay green: `python3 skills/rgaa-raweb-audit/scripts/scan_html.py explainer/index.html --standard raweb`
  reports 0 FAIL; a Playwright run drives every control in both languages with no console error and no horizontal
  overflow at 1280 px and 390 px; every `data-t` key has an `EN` entry; token pairs pass 4.5:1 in both themes.
- Published preview (private artifact of the owner's Claude account, shared by link):
  https://claude.ai/artifact/JxhGApQZKQfRJZDHBwz1D6 . Republish from a copy of index.html without the
  `<!DOCTYPE>/<html>/<head>/<body>` wrappers (the artifact host adds its own skeleton).

## Evaluation (summary; details in docs/evaluation.md)

Four eval cases under `skills/rgaa-raweb-audit/evals/` (RAWeb homepage audit, RGAA grid + statement, React modal
review, Android screen RAAM). Last recorded results: with the skill 38/38 web assertions and 12/12 Android, baseline
without the skill 33/38 and 5/12. The SIP corpus (228 published audits: 42 full, 186 simplified) was used to calibrate
report structure and the "test first what fails most" guidance; headline figures recounted on 2026-11-04.

## How to resume locally

1. Clone, check out `claude/vigilant-ritchie-xmvt2a`, open Claude Code in the repo (this file loads automatically).
2. Install the plugin for testing: `claude plugin marketplace add .` then `claude plugin install rgaa-raweb-audit`
   (or copy `skills/rgaa-raweb-audit` into `.claude/skills/`). Node + Playwright are needed for render_page.js;
   adb + an emulator or device for Android.
3. Quick smoke test: `python3 skills/rgaa-raweb-audit/scripts/scan_html.py examples/commune-homepage-raweb/input-index.html --standard raweb`
   and `python3 skills/rgaa-raweb-audit/scripts/audit_grid.py compute examples/rgaa-grid-and-statement/input-grille-audit.csv --standard rgaa`.
4. Re-run the evals when SKILL.md or the scanner changes: `claude plugin eval .` from the skill folder, or the
   skill-creator loop (results go to the git-ignored `*-workspace/`).

## Open items at the time of writing

- Independent reviews of the explainer content, the documentation and the scripts were applied (commits 6e0f9c8,
  8b9a4b6 and later). Known scanner limits that remain by design: an audit grid must not carry extra columns after
  the page columns; pass `--standard` for partial grids; inline `<svg>` without `aria-hidden` is reported under 1.1.5
  even inside a named control; the 9.2.1 "menu not in nav" check fires on any list of three links outside `<main>`;
  `contrast.py --css` does not parse `hsl()`, `var()` or `url(...) #fff`; the Android 5.2 focusable check relies on
  uiautomator's `focusable` flag and the 2.2 contrast estimate is approximate.
- Android test on a real APK: the cloud session cannot run adb or an emulator. Plan: run the audit from the owner's
  PC (Claude Code locally, or Remote Control from the Claude desktop app), with the emulator running and adb on PATH;
  `android_audit.py capture` per screen, then `analyse`, `font-scale`, `rotate`, `talkback`, `annotate`,
  `build_report.py build` for the illustrated report.
- GitHub Pages for the explainer is not enabled; `explainer/README.md` explains the options.
- The plugin has no icon (validation warning only).
- Possible future work discussed but not done: iOS (considered too complicated), Luxembourgish/German versions of the
  explainer, an `--lang en` SIP-style report (labels exist in build_report.py, wording file is French only).
