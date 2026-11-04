# Audit method: RGAA 4.1.2 and RAWeb 1.1

This is the operational method both standards prescribe (RGAA "Évaluation de la conformité", RAWeb "Test
methodology"). Follow it whenever the deliverable is an audit, a grid, a compliance rate or an accessibility statement.
Vocabulary is given as English / French because grids and statements are usually written in French.

## 1. Scope the audit

1. **Standard and version.** France: [RGAA 4.1.2](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/) ("référentiel général d'amélioration de l'accessibilité"). Luxembourg:
   [RAWeb 1.1](https://accessibilite.public.lu/en/raweb1.1/criteres.html) ("référentiel d'évaluation de l'accessibilité web"). Always write the version in the report; a client
   grid with 106 criteria is RGAA, one with 136 is RAWeb 1.1 (see raweb-vs-rgaa.md).
2. **Perimeter.** One website (a coherent set of pages under one responsibility). Native mobile apps use [RAAM 1.1](https://accessibilite.public.lu/en/raam1.1/criteres.html)
   (Luxembourg) or the RGAA mobile guidance, not these criteria. PDF documents use RAPDF (Luxembourg) / are evaluated
   under 13.3 and 13.4.
3. **Exempt content** (outside the legal obligation, so its criteria are NA, but the non-interference rules still
   apply): office files published before 23 September 2018 (unless needed for an active administrative process),
   pre-recorded media published before 23 September 2020, live media, online maps (if essential information is given
   accessibly), third-party content not funded, developed or controlled by the body, heritage reproductions that cannot
   be made accessible, intranet/extranet content published before 23 September 2019 until a substantial revision,
   archives (content not needed for active processes and not updated after 23 September 2019).
4. **Derogation for disproportionate burden** ("dérogation pour charge disproportionnée"): invoked case by case for a
   feature or content, justified (size and resources of the body, costs versus benefits, frequency and duration of use),
   accompanied by an accessible alternative when possible, listed in the statement. Lack of priority, time or knowledge
   is not a legitimate reason. It never covers a whole site.

## 2. Build the sample ("échantillon")

Mandatory pages, when they exist:

1. home page ("page d'accueil")
2. contact page
3. legal notice ("mentions légales")
4. accessibility page (the one with the statement)
5. site map ("plan du site")
6. help page ("aide")
7. authentication page ("authentification")
8. at least one relevant page per type of service and per main intended use (first-level sections, including the search
   functionality)
9. at least one relevant downloadable document per service type, if any
10. all the pages of each process ("processus": multi-step form, transaction, appointment booking)
11. pages with a significantly distinct appearance or content type (data tables, multimedia, illustrations, forms, real-time communication)
12. RAWeb adds: the documentation pages of the site and of the support service, if distinct from the accessibility and help pages
13. plus randomly selected pages, at least 10 % of the pages listed above

Luxembourg entities under the law of 8 March 2023 add the service-specific pages (for online banking: electronic
signature, account list and details, transactions, account opening/closing, transfers and standing orders, beneficiaries,
card orders, investments, 3D Secure payment validation, secure messaging, purchase funnel to payment).

Web analytics can guide the choice. Write the list of audited pages with their URLs: it is a mandatory part of the
statement and of the report.

## 3. Test environment ("environnement de test", "base de référence")

Criteria that require rendering by assistive technologies (notably topic 7 Scripts, 4.13, 10.2, 7.5) are checked on the
baseline. Record the exact versions used.

* **RGAA desktop**: NVDA (latest) + Firefox; JAWS (previous version) + Firefox or Internet Explorer; VoiceOver (latest) +
  Safari. A component is "compatible with accessibility" if it works on at least one combination.
* **RAWeb desktop**: NVDA (latest) + Firefox, Chrome or Edge; JAWS (previous version) + Firefox, Chrome or Edge;
  VoiceOver (latest) + Safari. The component must be fully functional on all of them.
* **Mobile (both)**: TalkBack (latest) + Chrome on Android; VoiceOver (latest) + Safari on iOS. RAWeb strongly recommends
  testing both for public sites.
* **Controlled environment** (intranet, equipment imposed by the employer): the baseline is the configuration actually
  used.
* Optional additions: ZoomText, Dragon NaturallySpeaking.

When no assistive technology is available to you (for example when auditing from code only), say it and record the
corresponding criteria as **NT** (not tested), never as C.

## 4. Test each page

For each page of the sample, go through every criterion:

* **C** / "conforme" (compliant): every element of the page concerned by the criterion passes all the tests of the
  criterion. One failing element makes the whole criterion **NC** for that page.
* **NC** / "non conforme".
* **NA** / "non applicable": only for one of three reasons: (1) the content or feature does not exist on the page (no video
  means 4.x is NA); (2) the content is exempt; (3) the content is derogated for disproportionate burden **and** has an
  accessible alternative. Derogated content without an alternative keeps its criteria applicable.
* **NT** / "non testé": not yet tested. A final grid has no NT.

Rules that change results and that newcomers get wrong:

* **Processes**: a criterion is compliant for a page of a process only if it is compliant on every page of that process.
* **Site-level criteria** (12.1 to 12.5 "ensemble de pages", 12.3 site map, RAWeb topics 14 and 16) can be assessed once
  and marked NA on the other pages; this does not change the site rate.
* **Non-interference principle**: exempt, derogated or non-accessible content with an accessible alternative must still
  comply with 4.10 (automatic sound), 12.9 (keyboard trap), 13.1.1 (refresh), 13.7 (flashes), 13.8 (moving/blinking
  content). Failing one of these makes the corresponding criterion NC.
* Levels A and AA are both mandatory and count the same. AAA criteria (published separately by DINUM) are out of scope.
* The tests of a criterion are alternatives or conditions as written: read the test wording (`criteria.py show <id>
  --tests`) rather than assuming the WCAG success criterion.
* Hidden content (`display:none`, `hidden`, `aria-hidden`) is evaluated under 10.8; it does not make other criteria NA.
* A finding must point to an element and a page: "image without alternative" is not a finding; "logo in the header,
  `<img src="/img/logo.png">` without `alt`, home page and all pages" is.

## 5. Compute the compliance rate ("taux de conformité")

Site-level status of a criterion:

* **compliant** if compliant on every page where it is applicable, and applicable on at least one page;
* **non-compliant** if non-compliant on at least one page;
* **not applicable** only if not applicable on every page of the sample, without exception.

Rate = compliant criteria ÷ applicable criteria (compliant + non-compliant), as a percentage, one decimal. No weighting
by level, topic or severity. The optional "taux moyen de conformité" (RGAA) is the mean of the page rates; it is never the
compliance rate. `scripts/audit_grid.py compute grid.csv` applies these rules; use it rather than hand counting.

Compliance status ("état de conformité") for the statement:

| Rate | RGAA | RAWeb |
|---|---|---|
| 100 % | conformité totale | full compliance |
| 50 % to < 100 % | conformité partielle | partial compliance |
| < 50 %, or no valid audit | non-conformité | non-compliance |

## 6. Deliverables

1. **Audit grid** ("grille d'audit"): criteria × pages with statuses, plus one line per non-conformity (page, criterion,
   test, element, description, recommendation). Ara (France) or the SIP audit kit (Luxembourg) produce the same thing.
2. **Audit report** ("rapport d'audit"): see report-templates.md. Findings by criterion (or by topic), each with the
   affected pages, the element, why it fails (which test), impact for users, how to fix, and an auditor's priority.
   Priority is not part of the standard; label it as the auditor's judgement.
3. **Accessibility statement** ("déclaration d'accessibilité"): mandatory structure, see report-templates.md.
   France: also the multi-year plan ("schéma pluriannuel") and yearly action plan links; the statement is updated on
   substantial change, after 3 years, or 18 months after a new RGAA version; complaints answered within one week;
   escalation to the [Défenseur des droits](https://www.defenseurdesdroits.fr/). Luxembourg: the statement link is sent to the SIP (accessibilite@sip.etat.lu)
   within 30 days of publication; complaints answered within one month; escalation to the SIP or the [Ombudsman](https://www.ombudsman.lu/); the
   SIP's online generator can produce it in several languages.

## 7. Tools the standards cite

Browser code inspector and accessibility tree; the assistive technologies of the baseline; Web Developer toolbar; WAVE;
W3C Nu validator (paste the generated DOM); WCAG Contrast Checker, Colour Contrast Analyser; HeadingsMap; PAC 2024 for
PDF, Microsoft Office accessibility checker, Ace by DAISY for EPUB; PEAT for flashes. Automated tools find a minority of
non-conformities and can never validate a criterion on their own.

## 8. Frequent auditor errors to avoid

* Giving a rate from a partial or static audit. Say "provisional" and list the NT criteria.
* Marking NA to avoid a decision. NA needs one of the three reasons.
* Counting a criterion as compliant because a page has no failing element when other pages of the sample fail it.
* Citing RGAA test numbers in a RAWeb audit (8.1.3, 9.2.1 with the RGAA conditions) or RAWeb-only criteria (4.14+,
  14.x to 17.x) in an RGAA audit.
* Reporting WCAG success criteria instead of RGAA/RAWeb criteria. Map to the criterion; mention WCAG only as a cross-reference.
* Accepting `placeholder` as a label (11.1), `title` alone as a visible label (11.1.3), `role="presentation"` with a
  `title` on a decorative image (RAWeb 1.2), `<abbr title>` for cryptic content (RAWeb 13.5).
* Forgetting that `<svg>` icons must be either `role="img"` with a name or `aria-hidden="true"`.
* Treating AA as optional, or weighting the rate by level.

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
