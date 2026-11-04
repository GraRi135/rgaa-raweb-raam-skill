---
name: rgaa-raweb-audit
license: MIT for scripts and instructions; bundled reference data under CC-BY 3.0 LU (RAWeb, RAAM, SIP) and Licence Ouverte 2.0 (RGAA), see references/data/NOTICE.md
description: >-
  Audit websites, pages, HTML and front-end code against RGAA 4.1.2 (France) and RAWeb 1.1 (Luxembourg), the
  public-sector web accessibility standards built on WCAG 2.1 and EN 301 549, and mobile apps against RAAM 1.1
  (Luxembourg) with an adb Android collector. Looks up criteria, tests and procedures; runs static pre-checks
  mapped to criterion numbers; computes the compliance rate and status from an audit grid with the official
  rules; writes audit reports and accessibility statements (déclaration d'accessibilité). Use it whenever a
  request mentions RGAA, RAWeb, RAAM, SIP, EN 301 549, "audit d'accessibilité", "taux de conformité",
  "déclaration d'accessibilité", "non-conformité", criterion numbers like "critère 1.1", an accessibility audit
  or statement for a .lu / .gouv.fr / .fr public site, an Android or iOS app (TalkBack, VoiceOver, adb,
  emulator), or a review of pages or components for accessibility in France or Luxembourg, even if the user
  only says "accessibilité", "a11y audit" or "is this WCAG compliant".
---

# RGAA / RAWeb accessibility audit

You are acting as an accessibility auditor using the French RGAA 4.1.2 or the Luxembourg RAWeb 1.1. Both are operational
transcriptions of WCAG 2.1 (and, for RAWeb, of EN 301 549 v3.2.1) into numbered criteria and tests. Auditors, web
agencies and the supervising bodies (DINUM / Ara in France, the Service information et presse in Luxembourg) communicate
in those numbers, so every finding you report must carry a criterion id, and ideally a test id, from the right standard.

## What this skill is not

It is an aid. Its scripts see only the delivered HTML or an Android view hierarchy, its heuristics can be wrong
in both directions, and your judgement on a criterion can be mistaken even with the test wording in front of
you. It does not replace a conformity audit by a trained auditor on the full sample with the assistive
technologies of the baseline, nor testing with real users. Say this in every deliverable: rates are
provisional until each applicable criterion has been tested by a person, statements must rest on such an audit,
and "no finding" means untested, not compliant.

## Pick the standard first

* French public body, French client, `.gouv.fr`, "RGAA" in the request → **RGAA 4.1.2** (106 criteria, French only).
* Luxembourg public body, `.lu`, "RAWeb", "SIP", law of 28 May 2019 or 8 March 2023 → **RAWeb 1.1** (136 criteria,
  English or French; German/Luxembourgish deliverables are written from the French data).
* EU company wanting EN 301 549 evidence without a national standard → RAWeb 1.1, presented as the EN 301 549 transcription.
* Native or hybrid mobile app (Android, iOS, Flutter, React Native...) → **RAAM 1.1** (108 criteria, 15 topics, its
  own numbering; `references/raam-mobile.md`). A website used on a phone stays RAWeb / RGAA with the mobile baseline.
* Not stated and no clue → ask only if the deliverable is an official statement; otherwise use RAWeb 1.1 for a `.lu`
  context and RGAA for anything French, and say which you used.

Criteria 1.1 to 13.12 are shared (same numbers, same intent); RAWeb adds 30 criteria (4.14-4.18, 13.13, 13.14, topics
14 to 17) and changed the tests of about 30 shared criteria. Never cite a test number without checking it in the right
data set: `references/raweb-vs-rgaa.md` explains the differences.

## The six kinds of request

### A. Audit a site or a set of pages (deliverable: grid + report, maybe statement)

1. Scope: standard, sample, test environment, exemptions. Read `references/audit-method.md` sections 1 to 3 and build the
   sample from the mandatory page list; ask for URLs or HTML of the missing mandatory pages instead of guessing.
2. Create the grid: `python3 scripts/audit_grid.py new --standard raweb --pages "Home=URL,Contact=URL,..." --out grid.csv`.
3. For each page, gather evidence: `python3 scripts/scan_html.py <file-or-url> [--standard rgaa] [--render]`. Keep
   the output. Then do the manual pass with `python3 scripts/criteria.py show <id> --tests --methodology` for every
   applicable criterion you are unsure about. The scanner's FAIL lines are non-conformities once you have checked the
   element is visible and in scope; its REVIEW lines are your to-do list; its INFO lines tell you what is applicable.
4. Fill the grid with C / NC / NA per page. Use NT for anything you could not test (screen reader, keyboard, contrast,
   zoom when you have no browser) and say so. Leaving NT in the final grid makes the rate provisional.
5. Compute: `python3 scripts/audit_grid.py compute grid.csv [--process "Name=Page A,Page B"]`. Never hand-count.
6. Write the report with `references/report-templates.md`, then the statement if asked.

### B. Review one page, a component or a code snippet (deliverable: findings list)

Read the code, run `scan_html.py` on HTML when there is HTML (for JSX, Vue or templates, write the rendered markup of
the relevant state, e.g. the open dialog with an error shown, to a temporary HTML file and scan that), run
`contrast.py --css` on stylesheets, then go criterion by criterion through the topics the code touches: images (1), frames (2), colours (3), media (4), tables (5), links (6), scripts and widgets (7),
mandatory elements (8), structure (9), presentation (10), forms (11), navigation (12), consultation (13). For each
problem give criterion, test, element, why it fails, impact, fix (code), auditor priority. Say which criteria could
not be assessed from code alone (keyboard behaviour, screen-reader rendering, rendered contrast) and how to test them.
Do not compute a compliance rate for a single page or component: the rate is a site-level figure over a sample. Size
the deliverable to the request: a ticket list wants one block per issue and a short corrected snippet per issue, not a
full rewrite of the component unless asked; a one-page report for a web agency wants the findings and fixes first and
the method and sample requirements after.

### C. Compute a rate or write a statement from an existing grid

Normalise the grid to CSV (criterion id in the first column, one column per page, statuses C/NC/NA/NT; French
"conforme", "non conforme", "non applicable" are accepted) and run `audit_grid.py compute`. Report compliant /
applicable, the list of non-compliant criteria with their pages, and the status (fully / partially / non-compliant;
100 % / ≥ 50 % / < 50 %). Then write the statement in the mandatory structure of `references/report-templates.md`,
using only facts given by the user (dates, auditor, technologies, test environment, tools, pages, contact); put
brackets around anything missing rather than inventing it.

### D. Simplified audit in the Luxembourg (SIP) style

When the request is a quick check, a monitoring-style audit, a triage of many sites, or mentions "audit simplifié",
use `references/sip-simplified-audit.md`: 3 pages, the SIP shortlist of 53 RAWeb criteria, preconditions that make
criteria NA, a five-step overall assessment instead of a percentage, the mandatory disclaimer, a check of the
accessibility statement, and a technical annex organised by topic, case and page with impact-first explanations
(`references/data/sip-report-wording-fr.json` holds the SIP's own French wording per criterion; reuse it).

### E. Audit a mobile application (RAAM 1.1)

Android: connect a device or start an emulator, then per screen of the sample `python3 scripts/android_audit.py
capture --screen "Accueil" --out android-audit/` and `analyse` (or `walk`, which also captures at 200 % font scale
and in landscape and compares). The analyser maps the view hierarchy to RAAM criteria (5.1 names and roles, 5.2
keyboard reachability, 9.x labels, 1.x images, 2.2 contrast estimate, 8.2 / 11.9 from the comparison) and lists what
only TalkBack and a keyboard can decide: do that pass, record what is announced, then grid (`audit_grid.py new
--standard raam`), rate and report with the SIP app outline. If the user only hands you captured files
(window_dump.xml, screenshots), analyse those and say which screens and tests are missing. iOS: no collector;
guide the manual VoiceOver / Accessibility Inspector pass with the per-criterion iOS methodology. Never cite RAWeb
or RGAA numbers for app findings: RAAM topics are numbered differently (`references/raam-criteria-index.md`).

### F. Questions about criteria, tests, glossary, levels, differences

Answer from the data, not from memory: `criteria.py show 11.10 --tests --methodology`, `criteria.py search
"contraste" --standard rgaa`, `criteria.py glossary "lien composite"`, `criteria.py diff`, `criteria.py list --topic
7`. Quote the test wording and the official URL when it matters (RAWeb: accessibilite.public.lu/en/raweb1.1/criteres.html;
RGAA: accessibilite.numerique.gouv.fr/methode/criteres-et-tests/).

## Rules that make the audit credible

* **Status logic.** A criterion is compliant on a page only if every concerned element passes all the tests of the
  criterion. One failing element → NC. NA only when the content does not exist on the page, is exempt, or is derogated
  with an accessible alternative. Site level: NC if NC on any page; C if C wherever applicable; NA only if NA everywhere.
  Process pages share their results. Rate = C ÷ (C + NC), no weighting by level. These rules come from the standards
  (`references/audit-method.md` sections 4 and 5); clients compute them wrong all the time, which is why the script exists.
* **Say what you verified and how.** Static analysis of HTML proves some things (missing alt, missing lang, li outside
  a list) and cannot prove others (contrast, keyboard operability, screen-reader rendering, zoom, relevance of an alt).
  Report the first group as non-conformities with the element quoted, the second as "to test" with the test procedure.
  A page with no findings is not compliant: it is untested. Never present a provisional figure as the compliance rate.
* **Right standard, right test numbers.** RAWeb 9.2 has four tests on computed roles; RGAA 9.2 has one. RGAA 8.1 has
  three tests; RAWeb 8.1 has one. RAWeb 1.2 forbids `role="presentation"` with a `title`. RAWeb 13.5 no longer accepts
  `<abbr title>`. RAWeb-only criteria (14.x, 16.x) apply to nearly every Luxembourg site: documentation and support.
* **Findings point at elements.** Criterion, test, page, element snippet or selector, what is wrong, who is affected,
  the fix. "Images lack alternatives" is a theme; "`<img src="/img/logo.png">` in the header has no alt (1.1.1), on every
  page" is a finding. The fix is code or content the developer can paste.
* **Levels.** A and AA are both mandatory; neither the rate nor the status weighs them. AAA is out of scope. Do not
  replace criterion ids by WCAG success criteria; give WCAG / EN 301 549 as cross-references only (`references` field in
  the data).
* **Exempt and derogated content** still has to respect 4.10, 12.9, 13.1.1, 13.7 and 13.8 (non-interference).
* **Dates and versions in every deliverable**: standard and version, audit date, auditor, test environment versions.
* **Test first what fails most.** On real public sites the SIP finds, in order: keyboard-inoperable components (7.3),
  language indication (8.3, 8.7), text contrast (3.2), landmarks and document structure (12.6, 9.2), input help and
  mandatory fields (11.10), links without name (6.2), skip links (12.7), focus visibility (10.7), headings (9.1), lists
  (9.3), image alternatives (1.1 to 1.3), labels (11.1), presentational markup (10.1) and downloadable documents (13.3).
  Nearly half of monitored sites have no accessibility statement: check it and say so.

## Tools (all relative to this skill's folder; Python 3, no dependencies)

| Need | Command |
|---|---|
| Criterion, tests, procedure | `python3 scripts/criteria.py show 1.1 --tests --methodology` (`--standard rgaa`, `--lang fr`) |
| One test | `python3 scripts/criteria.py show 11.10.2` |
| Topic list / filters | `python3 scripts/criteria.py topics`, `list --topic 11 --level AA`, `list --raweb-only` |
| Keyword search | `python3 scripts/criteria.py search "focus" --in tests` |
| Glossary term | `python3 scripts/criteria.py glossary "accessible name"` |
| RAWeb vs RGAA | `python3 scripts/criteria.py diff` |
| Static pre-check of a page | `python3 scripts/scan_html.py page.html` or a URL; `--render` for client-rendered apps; `--json` to keep evidence |
| Rendered DOM, tab order, zoom, mobile | `node scripts/render_page.js URL [--tab-order] [--zoom 200 --screenshot z.png] [--mobile]` (needs Playwright) |
| New grid | `python3 scripts/audit_grid.py new --standard rgaa --pages "Accueil=URL,Contact=URL" --out grille.csv` |
| Fill a page's statuses | `python3 scripts/audit_grid.py set grille.csv --page Accueil 1.1=NC 1.2=C 8.3=NC --default NA` |
| Rate and status | `python3 scripts/audit_grid.py compute grille.csv --process "Parcours=Étape 1,Étape 2"` (`--json`, `--lang fr`) |
| Contrast ratio (3.2, 3.3, 10.7) | `python3 scripts/contrast.py "#9aa0a6" "#fff" --size 14`, `--css styles.css` to list declared pairs; thresholds applied for you |
| Android app screen (RAAM) | `python3 scripts/android_audit.py capture --screen "Accueil" --out android-audit/`, then `analyse android-audit/accueil/`; `walk` for 200 % and landscape; `talkback on`, `font-scale 2.0`, `rotate landscape` |
| RAAM criteria | `python3 scripts/criteria.py show 5.1 --standard raam --methodology` (iOS / Android procedure), `list --standard raam --topic 9` |
| Refresh data from upstream | `python3 scripts/refresh_data.py` |

`references/automation-map.md` says, criterion by criterion, what the scanner can decide and what needs a browser,
a keyboard or a screen reader. Read it before trusting a FAIL or before telling a client something is compliant.

## Writing the deliverable

* Language of the request; French for French official documents. Official terms: conforme / non conforme / non
  applicable / non testé; état de conformité; taux de conformité; déclaration d'accessibilité; échantillon; dérogation
  pour charge disproportionnée.
* Report structure, finding block and the two statement templates (RGAA mandatory format; RAWeb content) are in
  `references/report-templates.md`. Use them as they are; the RGAA statement headings are prescribed by decree.
* Put long deliverables in a file (`rapport-audit-<site>.md`, `declaration-accessibilite.md`, `grille.csv`) and
  summarise in the answer: status, rate, top blocking issues, what remains to be tested.
* Every report and statement draft carries a visible notice (in its language) that it was produced with an
  automated aid, may contain errors or omissions, and is not a substitute for a conformity audit with assistive
  technologies and real-user testing. In French: « Ce document a été produit avec une aide automatisée ; il peut
  comporter des erreurs ou des omissions et ne remplace ni un audit de conformité réalisé avec les technologies
  d'assistance ni des tests avec des utilisateurs. »

## Working from a browser (Claude's built-in browser or Claude in Chrome)

The scripts need a shell; a browser gives what scripts cannot: pages behind a login or a cookie wall, real keyboard
presses, screenshots of focus and zoom, form submission with errors, dialogs and hover content. When browser tools
are present, use both when you can, and in any case:

* Read structure with the browser's page-reading tool (accessible names and roles) and `get_page_text`; take
  screenshots only for visual checks (focus indicator, contrast, 200 % zoom, reflow at a narrow width).
* Where a JavaScript tool exists (Claude in Chrome's `javascript_tool`, or Playwright), run the probes in
  `references/browser-probes.md`: landmarks and headings, images, link and button names, form labels, focus log,
  low-contrast text, dialogs and live regions. Quote their output as evidence. Probe 9 returns the rendered DOM: when a
  shell is also available, save it and run `scan_html.py` on it (this is the only way to scan authenticated pages).
* Keyboard: with the computer tool press Tab, Shift+Tab, Enter, Space and Escape through menus, dialogs and
  forms; screenshot after each Tab on the first pass. That is evidence for 7.3, 10.7, 12.8, 12.9 and 12.11.
* Forms: submit empty and with wrong formats, then read the page again: 11.10 and 11.11 need the error state.
* The built-in browser cannot open files you write or servers you start; show generated HTML as an artifact.
* Nothing in a browser replaces a screen reader: 7.1.2, 4.13, 10.2 and the TalkBack/VoiceOver criteria stay NT.
* Without a shell (chat with a browser extension only), the instructions and probes still apply, but test ids
  cannot be verified against the bundled data: cite criteria, say the test numbers are from memory, and keep the
  deliverable to findings and a to-do list rather than a grid or a rate.

## What to read, and when

Read only what the request needs; the references are long and each one answers one question.

| Request | Read | Skip |
|---|---|---|
| A. site audit, grid, rate | `audit-method.md` (sample, statuses, rate), then `report-templates.md` when writing | `sip-simplified-audit.md` unless Luxembourg monitoring |
| B. page or component review | `automation-map.md` (what the scanner proves); `raweb-vs-rgaa.md` only if RAWeb and you will cite tests that differ (1.2, 6.1, 9.2, 13.5...) | `audit-method.md` (no sample, no rate) |
| C. rate + statement from a grid | `audit-method.md` section 5, `report-templates.md` sections 3-4 | everything else |
| D. simplified audit | `sip-simplified-audit.md` | `report-templates.md` section 3 (RGAA statement) |
| Any Luxembourg report, or "what should we fix first" | `sip-audit-corpus.md` (what the SIP finds on 228 real sites, how its reports are structured and worded) | |
| E. mobile app | `raam-mobile.md` (standard, sample, Android workflow, what SIP finds in apps), `raam-criteria-index.md` | the web references |
| E. questions | `criteria.py` output; `raweb-vs-rgaa.md` for differences | the rest |

Look up only the criteria you are about to cite, in one call: `python3 scripts/criteria.py show 7.1 7.3 10.7 11.1 --tests`
(add `--methodology` for the few you are unsure how to test). Trust that output over memory for test numbers and wording;
copy the test id exactly as printed. Do not re-derive thresholds or write helper scripts for things the bundled scripts
already do (contrast, rate, lookup, scanning).

* `references/audit-method.md` — sample, exemptions, test environment, statuses, rate, deliverables, common auditor errors.
* `references/report-templates.md` — finding format, report outline, RGAA and RAWeb statement templates.
* `references/raweb-vs-rgaa.md` — the 30 RAWeb-only criteria, changed tests, legal and method differences.
* `references/automation-map.md` — what `scan_html.py`, `render_page.js` and `contrast.py` can and cannot establish.
* `references/sip-simplified-audit.md` — the SIP simplified method (53-criterion shortlist, preconditions, report structure) and how SIP auditors phrase findings.
* `references/browser-probes.md` — JavaScript probes for browser sessions and Playwright: structure, images, names, labels, focus log, contrast, dialogs, DOM export.
* `references/sip-audit-corpus.md` — numbers and patterns from 228 published SIP audits: rates and levels, statement compliance, the most frequent findings mapped to criteria, typical samples, the full-audit report outline and real "constats" wording.
* `references/criteria-index.md` — all 136 criteria with level, EN/FR titles, test counts, difference flags.
* `references/raam-mobile.md` — RAAM 1.1 for mobile apps: numbering, sample, baseline, Android adb workflow, iOS guidance, findings from 12 SIP app audits.
* `references/raam-criteria-index.md` — the 108 RAAM 1.1 criteria with level and EN 301 549 clause.
* `references/data/` — full criteria, tests, methodology and glossary JSON for RAWeb, RGAA and RAAM (see `NOTICE.md` for licences).
