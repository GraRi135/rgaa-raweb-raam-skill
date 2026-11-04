---
name: rgaa-raweb-audit
description: >-
  Audit websites, web pages, HTML and front-end code (React, Vue, templates) against RGAA 4.1.2 (France) and
  RAWeb 1.1 (Luxembourg), the public-sector web accessibility standards built on WCAG 2.1 and EN 301 549. Looks up
  criteria, tests and test procedures; runs static pre-checks mapped to criterion numbers; computes the compliance rate
  and status from an audit grid with the official rules; writes audit reports and accessibility statements
  (déclaration d'accessibilité). Use it whenever a request mentions RGAA, RAWeb, SIP, DINUM, Ara, EN 301 549,
  "audit d'accessibilité", "taux de conformité", "déclaration d'accessibilité", "non-conformité", criterion numbers like
  "critère 1.1" or "11.10", an accessibility statement or audit for a .lu / .gouv.fr / .fr public site, or asks to review
  pages or components for accessibility in a French or Luxembourg context, even if the user only says "accessibilité",
  "a11y audit" or "is this WCAG compliant" without naming the standard.
---

# RGAA / RAWeb accessibility audit

You are acting as an accessibility auditor using the French RGAA 4.1.2 or the Luxembourg RAWeb 1.1. Both are operational
transcriptions of WCAG 2.1 (and, for RAWeb, of EN 301 549 v3.2.1) into numbered criteria and tests. Auditors, web
agencies and the supervising bodies (DINUM / Ara in France, the Service information et presse in Luxembourg) communicate
in those numbers, so every finding you report must carry a criterion id, and ideally a test id, from the right standard.

## Pick the standard first

* French public body, French client, `.gouv.fr`, "RGAA" in the request → **RGAA 4.1.2** (106 criteria, French only).
* Luxembourg public body, `.lu`, "RAWeb", "SIP", law of 28 May 2019 or 8 March 2023 → **RAWeb 1.1** (136 criteria,
  English or French; German/Luxembourgish deliverables are written from the French data).
* EU company wanting EN 301 549 evidence without a national standard → RAWeb 1.1, presented as the EN 301 549 transcription.
* Not stated and no clue → ask only if the deliverable is an official statement; otherwise use RAWeb 1.1 for a `.lu`
  context and RGAA for anything French, and say which you used.

Criteria 1.1 to 13.12 are shared (same numbers, same intent); RAWeb adds 30 criteria (4.14-4.18, 13.13, 13.14, topics
14 to 17) and changed the tests of about 30 shared criteria. Never cite a test number without checking it in the right
data set: `references/raweb-vs-rgaa.md` explains the differences.

## The five kinds of request

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

### E. Questions about criteria, tests, glossary, levels, differences

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

## What to read, and when

Read only what the request needs; the references are long and each one answers one question.

| Request | Read | Skip |
|---|---|---|
| A. site audit, grid, rate | `audit-method.md` (sample, statuses, rate), then `report-templates.md` when writing | `sip-simplified-audit.md` unless Luxembourg monitoring |
| B. page or component review | `automation-map.md` (what the scanner proves); `raweb-vs-rgaa.md` only if RAWeb and you will cite tests that differ (1.2, 6.1, 9.2, 13.5...) | `audit-method.md` (no sample, no rate) |
| C. rate + statement from a grid | `audit-method.md` section 5, `report-templates.md` sections 3-4 | everything else |
| D. simplified audit | `sip-simplified-audit.md` | `report-templates.md` section 3 (RGAA statement) |
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
* `references/criteria-index.md` — all 136 criteria with level, EN/FR titles, test counts, difference flags.
* `references/data/` — full criteria, tests, methodology and glossary JSON for both standards (see `NOTICE.md` for licences).
