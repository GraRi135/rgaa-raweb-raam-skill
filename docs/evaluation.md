# How the skill was evaluated

The skill was built with Anthropic's skill-creator loop: write a draft, run realistic tasks with and without the
skill, grade the outputs on written assertions, improve, repeat. Everything below is reproducible with the cases in
`skills/rgaa-raweb-audit/evals/` (Claude Code can run them with `claude plugin eval`).

## Test cases

| Case | Input | What a good answer does |
|---|---|---|
| audit-homepage-raweb | a fictional Luxembourg commune homepage with 30+ planted defects | lists them with RAWeb criterion and test ids and a fix each, separates verified from untested, gives no rate |
| compute-rate-declaration-rgaa | a 9-page RGAA grid with traps (criteria NA on some pages, a 3-page process) | finds 67.1 % and "partiellement conforme", not the 93 % page average or 50 %; drafts the statement in the mandatory format without inventing facts |
| review-react-modal-raweb | a React modal with a dozen accessibility bugs | ticket-ready findings with correct RAWeb criterion and test ids (7.1, 7.3, 12.8, 10.7, 1.2, 11.1, 11.10, 3.1, 11.13) |
| audit-android-screen-raam | a synthetic uiautomator capture at font scale 1.0 and 2.0 | RAAM numbering (5.1, 5.2, 9.2, 2.2, 8.2), Android fixes, list of what needs TalkBack |

## Results

| Round | With the skill | Without the skill |
|---|---|---|
| Web cases, round 1 (3 cases, 36 assertions) | 36 / 36 | 33 / 36 |
| Web cases, round 2 after improvements (38 assertions) | 38 / 38 | 33 / 38 |
| Android case (12 assertions) | 12 / 12 | 5 / 12 |

The model already knows the criteria well; the skill's measurable value is where memory fails: the exact scope of
[RAWeb 1.1](https://accessibilite.public.lu/en/raweb1.1/criteres.html) (136 criteria, not 106), test numbers matching the official wording, RAAM's 15-topic numbering (the baseline
cited a remembered 12-topic structure), refusing a rate from one page, and not inventing facts in a statement. Round 2
also cut the skill's token cost by 15 to 35 % by telling Claude which reference to read for which request.

## Calibration against real audits

The Luxembourg SIP publishes its monitoring reports on [data.public.lu](https://data.public.lu/en/) (CC0). 228 of them (42 full audits, 186
simplified) were mined for the structure and wording of reports and for the most frequent findings; the results are in
`skills/rgaa-raweb-audit/references/sip-audit-corpus.md` and `skills/rgaa-raweb-audit/references/raam-mobile.md` and drive the "test first what fails most" guidance.

Two real Luxembourg public sites were then audited with the skill as a test, on the SIP's own samples, and the
findings compared with the SIP's published cases. Those test reports are not published here because they concern
third-party sites and were produced without assistive technologies.

## Known weaknesses

* No screen reader anywhere in the loop: the largest class of criteria stays "not tested".
* Contrast is computed from declared or dominant colours; text over images and gradients needs a manual measure.
* The scanner's REVIEW heuristics (generic link text, visual headings, suspicious alt) over-report on large pages.
* A full site audit with the skill costs 200k tokens or more per run.

## Sources

* RAWeb 1.1, Luxembourg web accessibility standard: https://accessibilite.public.lu/en/raweb1.1/criteres.html (source files: https://github.com/accessibility-luxembourg/ReferentielAccessibiliteWeb, CC-BY 3.0 LU)
* RAAM 1.1, Luxembourg mobile-app accessibility standard: https://accessibilite.public.lu/en/raam1.1/criteres.html (source files: https://github.com/accessibility-luxembourg/ReferentielAccessibiliteMobile, CC-BY 3.0 LU)
* RGAA 4.1.2, French standard: https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/ (source files: https://github.com/DISIC/accessibilite.numerique.gouv.fr, Licence Ouverte 2.0, DINUM)
* WCAG 2.1: https://www.w3.org/TR/WCAG21/ ; EN 301 549 v3.2.1: https://www.etsi.org/deliver/etsi_en/301500_301599/301549/03.02.01_60/en_301549v030201p.pdf
* Law of 28 May 2019 on the accessibility of the websites and mobile applications of public sector bodies (Luxembourg): https://legilux.public.lu/eli/etat/leg/loi/2019/05/28/a373/jo
* Service information et presse (SIP), monitoring body, guides, statement generator and complaint form: https://accessibilite.public.lu/en/ ; published monitoring reports: https://accessibilite.public.lu/fr/rapports/
* SIP monitoring datasets on data.public.lu (CC0): full audits 2023 https://data.public.lu/en/datasets/audits-complets-de-laccessibilite-numerique-2023/ ; full audits 2024 https://data.public.lu/en/datasets/audits-complets-de-laccessibilite-numerique-2024-1/ ; simplified audits 2024 https://data.public.lu/en/datasets/audits-simplifies-de-laccessibilite-numerique-2024/ ; simplified audits 2025 https://data.public.lu/en/datasets/audits-simplifies-de-laccessibilite-numerique-2025/
* SIP report wording (simplA11yGenReport, MIT): https://github.com/accessibility-luxembourg/simplA11yGenReport
* Ombudsman (Luxembourg): https://www.ombudsman.lu/ ; Défenseur des droits (France): https://www.defenseurdesdroits.fr/
* France, legal basis of the RGAA: article 47 of law 2005-102 https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000809647 and decree 2019-768 https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000038811937
