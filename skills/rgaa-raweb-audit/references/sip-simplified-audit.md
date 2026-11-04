# The SIP simplified audit (Luxembourg) and how its auditors write findings

The [Service information et presse (SIP)](https://accessibilite.public.lu/en/) monitors Luxembourg public-sector sites with two methods (EU implementing
decision 2018/1524): **in-depth audits** (full RAWeb conformity audits on a sample, published as "audits complets" on
[data.public.lu](https://data.public.lu/en/)) and **simplified audits** ("audits simplifiés", several hundred per year). The simplified method and
its tooling are public (simplA11yMonit, [simplA11yGenReport](https://github.com/accessibility-luxembourg/simplA11yGenReport), MIT) and this file distils them so that a report you
produce reads like one an SIP auditor would recognise. Use it for Luxembourg work; the RGAA has no equivalent
shortlist (France uses full audits with Ara).

## Simplified method in short

* **Sample**: 3 pages per site (home page and two other representative pages), each gets its own sheet (P01, P02, P03).
* **Shortlist of 53 RAWeb criteria** (not the full 136), the ones that can be assessed quickly and that block users most:

  | Topic | Criteria in the shortlist |
  |---|---|
  | 1 Images | 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7 |
  | 2 Frames | 2.1 |
  | 3 Colours | 3.1, 3.2 |
  | 4 Multimedia | 4.1, 4.2, 4.3, 4.4, 4.8, 4.9, 4.10, 4.11 |
  | 5 Tables | 5.6, 5.7 |
  | 6 Links | 6.1, 6.2 |
  | 7 Scripts | 7.3 |
  | 8 Mandatory elements | 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8 |
  | 9 Structure | 9.1, 9.2 |
  | 10 Presentation | 10.7, 10.8, 10.9, 10.10, 10.14 |
  | 11 Forms | 11.1, 11.2, 11.5, 11.6, 11.7, 11.9, 11.10 |
  | 12 Navigation | 12.6, 12.7, 12.8, 12.9, 12.11 |
  | 13 Consultation | 13.1, 13.7, 13.8 |

* **Automation**: axe-core runs first and pre-fills 19 criteria (1.1, 1.2, 2.1, 3.2, 4.3, 5.7, 6.2, 8.3, 8.4, 8.5, 8.8, 9.1,
  9.2, 10.8, 11.1, 11.9, 12.7, 13.1, 13.8) with "NC" for violations and "needs review" for incomplete results (contrast
  "needs review" results are dropped as too noisy). Only 2.1, 8.3 and 8.5 are considered **fully automated**: no axe
  finding means C. Everything else is confirmed by hand.
* **8.1 and 8.2 are always recorded as C** (the SIP treats source validity as deprecated, following the withdrawal of
  WCAG 4.1.1 Parsing in WCAG 2.2). When duplicate ids or broken markup have a functional consequence, report it under
  the criterion that suffers (11.1 label association, 7.1 ARIA references, 9.x structure), not under 8.2.
* **Preconditions make criteria NA automatically**: no visible image (img, role=img, area, input image, svg, object/embed
  image, canvas; image links excluded) → 1.1, 1.2, 1.3, 1.6, 1.7 NA; no iframe → 2.1 NA; no table / role=table → 5.6,
  5.7 NA; no form control (inputs, select, textarea, ARIA form roles) → 11.1, 11.2, 11.5, 11.6, 11.7, 11.9, 11.10 NA.
* **Every NC needs a comment** describing the occurrence (the generator refuses an NC without a comment, and refuses
  any NT). Derogated content (column "dérogation" = O) is not reported as a problem.
* **Score**: an overall assessment on a five-step scale, "très faible, faible, moyen, bon, très bon", for the criteria
  tested; no percentage, because a simplified audit is not a conformity audit.

## Structure of the published simplified report (French)

1. **Titre**: "Audit d'accessibilité simplifié - <site>", date.
2. **Appréciation générale**: the five-step score.
3. **Avertissement**: it is a simplified audit, not a conformity audit; no finding on a criterion does not mean
   compliance; one reported occurrence may have others; a full RAWeb audit is required. Reuse this disclaimer, adapted,
   whenever you audit less than the full sample.
4. **Échantillon de pages et référentiel**: the three pages with URLs; method "Méthode de contrôle simplifiée de
   l'accessibilité pour le Luxembourg"; referential [RAWeb 1.1](https://accessibilite.public.lu/en/raweb1.1/criteres.html).
5. **Déclaration sur l'accessibilité**: missing / incomplete (which mandatory items are missing) / present and complete,
   with the legal reminder (article 5 of the [law of 28 May 2019](https://legilux.public.lu/eli/etat/leg/loi/2019/05/28/a373/jo), generator on accessibilite.public.lu, 30 days to notify
   accessibilite@sip.etat.lu).
6. **Documents bureautiques en téléchargement** (when relevant): count of files, share of PDF, share of exempt PDFs
   (published before 23 September 2018), share with blocking problems (untagged, protected, scanned), pointer to RAPDF.
7. **Annexe technique**, one block per topic with problems:
   * "Recommandations générales" for the topic (the `topics` texts in `data/sip-report-wording-fr.json`);
   * for each case met: "Cas rencontré : <title>", an explanation of the rule, **who is affected and why**, and the
     technique to apply (the `solutions` texts), then "Exemples de problèmes détectés sur la page N" with the auditor's
     occurrences (element, what is wrong), keyboard keys marked up as such.

## What this tells you about auditor style

* Findings are grouped by **topic**, then by **case** (a case can group several criteria: "1.1, 1.3 images porteuses
  d'information", "11.1, 11.2, 11.5, 11.6, 11.7 identification des champs"), then **examples per page**.
* Each explanation names the **users affected** (aveugles et grands malvoyants, handicapés moteurs naviguant au clavier,
  personnes avec des troubles de l'attention...) before the technique. Copy that habit: impact first, then fix.
* Fixes are concrete and technology-specific (`alt`, `role="img"` + `aria-label` for SVG, `scope="col"/"row"`,
  `<fieldset>`/`<legend>`, `aria-hidden="true"` on decorative SVG, `<header>/<nav>/<main>/<footer>/<search>` for computed
  roles, focus indicator with 3:1 contrast, skip link to `<main>` that may appear on focus).
* Examples quote the element and its location; one example per case per page is enough in the report, the grid holds
  the rest.
* The report never claims completeness and always points back to the full RAWeb audit and to the statement obligations.

## Corpus numbers

Over the 186 simplified reports of 2024-2025: overall level très bon 31, bon 56, moyen 91, faible 8; statement complete
64, incomplete 36, missing 86; the case "éléments interactifs inaccessibles au clavier" (7.3) appears in 86 % of reports.
Full frequency tables and real wording are in `sip-audit-corpus.md`.

## Using the shortlist outside the SIP method

For a quick pre-audit, a design review or a triage of a large site, the 53-criterion shortlist is a reasonable
prioritisation: it covers what blocks screen-reader and keyboard users first. Say explicitly that it is the SIP
simplified shortlist and that the full standard has 136 criteria; never derive a compliance rate or a status from it.

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
