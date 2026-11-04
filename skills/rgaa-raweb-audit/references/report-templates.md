# Report and statement templates

Use the language of the request (French for RGAA deliverables unless asked otherwise; French, German, Luxembourgish or
English for RAWeb). Keep official terms in French in parentheses the first time when writing in English for a
French/Luxembourg reader.

## 1. Finding format (one block per non-conformity)

```
### <criterion id> [<level>] <criterion title>
- Test: <test id> — <short test wording>
- Pages: <page names or "all pages">
- Element: `<snippet>` (line / selector / screenshot reference)
- Problem: what is wrong and why it fails the test (facts, not opinions)
- Impact: who is blocked and how (screen reader users, keyboard users, low vision, cognitive...)
- Fix: concrete code or content change, with a short example
- Priority (auditor's judgement): blocking / major / minor
```

Example:

```
### 11.1 [A] Does each form input field have a label?
- Test: 11.1.1 — the field has a <label for>, aria-label, aria-labelledby or title
- Pages: Home (newsletter block), Contact
- Element: `<input type="email" name="email" placeholder="Votre adresse e-mail">`
- Problem: the only text is a placeholder, which is not an accessible name and disappears on input.
- Impact: screen-reader users hear "edit text" with no purpose; voice-control users cannot target the field.
- Fix: `<label for="email">Adresse e-mail (obligatoire)</label><input id="email" type="email" autocomplete="email" required>`
- Priority: major
```

## 2. Audit report structure

Every report starts with the notice below (translate it when the report is not in French), placed before the
summary so that no reader takes a provisional result for an audit:

> Avertissement : ce rapport a été produit avec une aide automatisée (analyse du code et du DOM rendu). Il peut
> comporter des erreurs ou des omissions. Il ne remplace ni un audit de conformité réalisé par un auditeur sur
> l'échantillon complet avec les technologies d'assistance de l'environnement de test, ni des tests avec des
> utilisateurs en situation de handicap. Les taux indiqués sont provisoires tant que chaque critère applicable n'a
> pas été testé par une personne ; l'absence de constat sur un critère signifie « non testé », pas « conforme ».

```
# Rapport d'audit d'accessibilité — <site> — <RGAA 4.1.2 | RAWeb 1.1>
## 0. Avertissement (see above)
## 1. Synthèse
   - état de conformité et taux (or "audit partiel: taux provisoire" / "pas de taux: audit statique d'une page")
   - nombre de critères conformes / non conformes / non applicables (/ non testés)
   - les 5 à 10 non-conformités les plus bloquantes, en une ligne chacune
## 2. Périmètre et méthode
   - référentiel et version, date, auditeur
   - échantillon: liste des pages avec URL (et processus)
   - environnement de test: OS, navigateurs, technologies d'assistance et versions; outils
   - limites (ce qui n'a pas pu être testé)
## 3. Résultats par thématique (ou par critère)
   - for each topic: table of criteria with site-level status, then the finding blocks
## 4. Résultats par page
   - per page: applicable / compliant / rate (from audit_grid.py)
## 5. Recommandations transversales
   - patterns (design system, CMS templates, components) that fix many findings at once
## 6. Annexes
   - full grid (CSV), glossary of statuses, mapping to WCAG / EN 301 549 if requested
```

For a Luxembourg deliverable that should read like an SIP report, use the SIP full-audit outline instead
(`sip-audit-corpus.md`, section "Structure of a SIP full-audit report"): Introduction, Échantillon (with the
statement check), Environnement de test (tables with versions), Accessibilité des pages auditées (overall level on
the five-step scale, rate, status, note on the calculation, per-page and per-topic tables, impacts utilisateurs,
contenus exemptés), Avis (what users cannot do, the 4 to 6 most blocking families), Annexe technique by topic with
"Recommandation", cases and "Constats sur le site". RGAA-era SIP reports also give the rate at level A and at level
AA; the legal figure is the all-criteria (AA) rate.

For a single page or a code review (no sample), replace sections 1 and 4 with: "Portée: une page / un composant;
aucun taux de conformité ne peut être établi sans audit de l'échantillon complet" and give counts of findings instead.

## 3. Accessibility statement, RGAA (France) — mandatory format

The headings and the order are prescribed. Fill the brackets; delete nothing. A statement is a legal document
of the publishing body: hand over a draft, clearly marked as such, and say that it must only be published once a
conformity audit has been completed with assistive technologies and its figures confirmed by the body.

```
# Déclaration d'accessibilité

[Nom de l'organisme] s'engage à rendre son site internet accessible conformément à l'article 47 de la loi n° 2005-102 du 11 février 2005.
À cette fin, il met en œuvre la stratégie et les actions suivantes : [lien vers le schéma pluriannuel] ; [lien vers le plan d'action de l'année en cours].
Cette déclaration d'accessibilité s'applique à [URL du site].

## État de conformité
[Nom du site] est [totalement / partiellement / non] conforme avec le référentiel général d'amélioration de l'accessibilité (RGAA), version 4.1.2, en raison des non-conformités et des dérogations énumérées ci-dessous.

### Résultats des tests
L'audit de conformité réalisé [en interne / par la société X] révèle que :
- [xx,x] % des critères du RGAA version 4.1.2 sont respectés.
- (Facultatif) Le taux moyen de conformité du site s'élève à [xx] %.

## Contenus non accessibles
Les contenus listés ci-dessous ne sont pas accessibles pour les raisons suivantes.
### Non-conformités
- [critère n° — description courte — pages concernées — alternative ou date de correction prévue, le cas échéant]
### Dérogations pour charge disproportionnée
- [contenu — justification — alternative]
### Contenus non soumis à l'obligation d'accessibilité
- [contenu exempté — raison]

## Établissement de cette déclaration d'accessibilité
Cette déclaration a été établie le [JJ mois AAAA]. Elle a été mise à jour le [JJ mois AAAA].
### Technologies utilisées pour la réalisation du site
- [HTML5, CSS, JavaScript, framework...]
### Environnement de test
Les vérifications de restitution de contenus ont été réalisées sur la base de la combinaison fournie par la base de référence du RGAA, avec les versions suivantes :
- [NVDA x + Firefox y], [VoiceOver + Safari], ...
### Outils utilisés lors de l'évaluation
- [inspecteur de code, Colour Contrast Analyser, HeadingsMap, ...]
### Pages du site ayant fait l'objet de la vérification de conformité
- [page d'accueil — URL], [contact — URL], ...

## Retour d'information et contact
Si vous n'arrivez pas à accéder à un contenu ou à un service, vous pouvez contacter le responsable du site pour être orienté vers une alternative accessible ou obtenir le contenu sous une autre forme.
- Envoyer un message : [URL du formulaire]
- Contacter [entité] : [adresse e-mail / page de contact]

## Voies de recours
Si vous constatez un défaut d'accessibilité vous empêchant d'accéder à un contenu ou une fonctionnalité du site, que vous nous le signalez et que vous ne parvenez pas à obtenir une réponse de notre part, vous êtes en droit de faire parvenir vos doléances ou une demande de saisine au Défenseur des droits.
- Écrire un message au Défenseur des droits : https://www.defenseurdesdroits.fr/nous-contacter-355
- Contacter le délégué du Défenseur des droits dans votre région : https://www.defenseurdesdroits.fr/carte-des-delegues
- Envoyer un courrier par la poste (gratuit, ne pas mettre de timbre) : Défenseur des droits, Libre réponse 71120, 75342 Paris CEDEX 07
```

## 4. Accessibility statement, RAWeb (Luxembourg)

The law of 28 May 2019 prescribes the content, not the exact wording; the SIP provides a multilingual generator
(accessibilite.public.lu/en/tools/decla.html) and public bodies are expected to use its structure. Produce this content:

```
# Accessibility statement / Déclaration d'accessibilité
[Organisation] undertakes to make its website [URL] accessible in accordance with the law of 28 May 2019 on the
accessibility of the websites and mobile applications of public sector bodies.
This statement applies to [URL].

## Compliance status / État de conformité
[Site] is [fully / partially / not] compliant with the RAWeb 1.1 (référentiel d'évaluation de l'accessibilité web),
version 1.1, because of the non-conformities and derogations listed below.
Audit carried out [internally / by X] on [date]: [xx.x] % of the RAWeb 1.1 criteria are met.
[Optional: link to the audit report.]

## Non-accessible content / Contenus non accessibles
### Non-conformities with the RAWeb / Non-conformités
- [criterion — description — pages — alternative or planned fix]
### Derogation for disproportionate burden / Dérogations pour charge disproportionnée
- [content — justification — alternative]
### Content not within the scope of the legislation / Contenus non soumis à l'obligation d'accessibilité
- [exempt content — reason]

## Preparation of this statement / Établissement de cette déclaration
Prepared on [date], last reviewed on [date]. Method: RAWeb 1.1 audit of the sample listed below.
### Technologies used
### Test environment (assistive technologies, browsers, versions)
### Tools
### Pages audited (with URLs)

## Feedback and contact / Retour d'information et contact
If you cannot access content or a service, contact [e-mail address or accessible form] to be directed to an accessible
alternative or to obtain the content in another form. The organisation acknowledges receipt and answers within one month.

## Enforcement procedure / Procédure d'application
If you have reported an accessibility problem and have not received a satisfactory answer, you can contact the
Service information et presse (accessibilite@sip.etat.lu) or the Ombudsman (Médiateur).
```

## 5. Status vocabulary for grids

| Code | FR | EN |
|---|---|---|
| C | conforme | compliant |
| NC | non conforme | non-compliant |
| NA | non applicable | not applicable |
| NT | non testé | not tested |

Status of the site: conformité totale / partielle / non-conformité — full / partial / non-compliance.
