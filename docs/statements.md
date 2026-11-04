# Accessibility statements (déclaration d'accessibilité)

A statement is a legal document of the body that publishes it. The skill drafts it in the mandatory structure and
fills in only the facts you give it; everything missing stays in brackets. Publish only after a conformity audit has
been completed with assistive technologies and the figures confirmed.

## France (RGAA)

* Legal basis: article 47 of law 2005-102, decree 2019-768. The headings and their order are prescribed:
  commitment and scope, "État de conformité", "Résultats des tests", "Contenus non accessibles" (non-conformités,
  dérogations pour charge disproportionnée, contenus non soumis), "Établissement de cette déclaration", "Retour
  d'information et contact", "Voies de recours" (Défenseur des droits).
* Status from the rate: 100 % totally compliant, 50 % or more partially compliant, below 50 % or no valid audit non-compliant.
* Also required: the multi-year plan ("schéma pluriannuel") and the year's action plan, linked from the statement.
* Validity: update on substantial change, after three years, or 18 months after a new RGAA version. Complaints are
  answered within one week.
* Give Claude: audit date and author, technologies, test environment with versions, tools, the list of audited pages
  with URLs, contact e-mail or form, derogations and exempt content. The template is in
  `skills/rgaa-raweb-audit/references/report-templates.md`.

## Luxembourg (RAWeb, RAAM)

* Legal basis: law of 28 May 2019 (public sector), law of 8 March 2023 (products and services). The content is
  prescribed, not the exact wording; the SIP provides a multilingual generator at accessibilite.public.lu.
* Content: compliance status with the same thresholds, non-accessible content (non-conformities, derogations, exempt
  content), preparation of the statement, feedback and contact, enforcement procedure naming the SIP and the
  Ombudsman. The link to the published statement is sent to accessibilite@sip.etat.lu within 30 days. Complaints are
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
