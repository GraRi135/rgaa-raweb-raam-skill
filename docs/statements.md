# Accessibility statements (déclaration d'accessibilité)

A statement is a legal document of the body that publishes it. The skill drafts it in the mandatory structure and
fills in only the facts you give it; everything missing stays in brackets. Publish only after a conformity audit has
been completed with assistive technologies and the figures confirmed.

## France (RGAA)

* Legal basis: article 47 of [law 2005-102](https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000809647), [decree 2019-768](https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000038811937). The headings and their order are prescribed:
  commitment and scope, "État de conformité", "Résultats des tests", "Contenus non accessibles" (non-conformités,
  dérogations pour charge disproportionnée, contenus non soumis), "Établissement de cette déclaration", "Retour
  d'information et contact", "Voies de recours" ([Défenseur des droits](https://www.defenseurdesdroits.fr/)).
* Status from the rate: 100 % totally compliant, 50 % or more partially compliant, below 50 % or no valid audit non-compliant.
* Also required: the multi-year plan ("schéma pluriannuel") and the year's action plan, linked from the statement.
* Validity: update on substantial change, after three years, or 18 months after a new RGAA version. Complaints are
  answered within one week.
* Give Claude: audit date and author, technologies, test environment with versions, tools, the list of audited pages
  with URLs, contact e-mail or form, derogations and exempt content. The template is in
  `skills/rgaa-raweb-audit/references/report-templates.md`.

## Luxembourg (RAWeb, RAAM)

* Legal basis: [law of 28 May 2019](https://legilux.public.lu/eli/etat/leg/loi/2019/05/28/a373/jo) (public sector), law of 8 March 2023 (products and services). The content is
  prescribed, not the exact wording; the SIP provides a multilingual generator at accessibilite.public.lu.
* Content: compliance status with the same thresholds, non-accessible content (non-conformities, derogations, exempt
  content), preparation of the statement, feedback and contact, enforcement procedure naming the SIP and the
  [Ombudsman](https://www.ombudsman.lu/). The link to the published statement is sent to accessibilite@sip.etat.lu within 30 days. Complaints are
  answered within one month.
* Two thirds of the sites the SIP monitors have a missing or incomplete statement: the simplified audit reports start
  with that check.

## Computing the rate from your grid

```bash
python3 skills/rgaa-raweb-audit/scripts/audit_grid.py compute grille.csv --process "Demande=Étape 1,Étape 2,Étape 3"
```

The rules the script applies: a criterion is compliant for the site only if compliant on every page where it applies;
non-compliant if non-compliant on one page; not applicable only if not applicable everywhere; process pages share
their results; rate = compliant ÷ applicable. The optional "taux moyen" (mean of page rates, France) is never the
compliance rate. Any NT cell makes the result provisional.

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
