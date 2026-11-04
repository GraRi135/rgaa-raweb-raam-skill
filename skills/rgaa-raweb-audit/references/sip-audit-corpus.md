# What the SIP's published audits teach (corpus of 228 reports, 2023-2025)

The [Service information et presse](https://accessibilite.public.lu/en/) publishes every monitoring report on [data.public.lu](https://data.public.lu/en/) (licence CC0). This file
distils 228 of them: 42 full audits ("audits complets", 2023 and 2024: 30 websites under RGAA 4.1 / 4.1.2 / RAWeb 1,
12 mobile apps under RAAM 1) and 186 simplified audits ("audits simplifiés", 2024 and 2025, RAWeb). Use it to
prioritise an audit, to write a Luxembourg report that reads like the SIP's, and to predict what the SIP will find.
Datasets: data.public.lu/fr/datasets/[audits-complets-de-laccessibilite-numerique-2023](https://data.public.lu/en/datasets/audits-complets-de-laccessibilite-numerique-2023/) (and -2024-1),
[audits-simplifies-de-laccessibilite-numerique-2024](https://data.public.lu/en/datasets/audits-simplifies-de-laccessibilite-numerique-2024/) (and -2025); each report also exists as an accessible HTML page
under accessibilite.public.lu/fr/rapports/.

## Headline numbers

| Full audits (websites, n = 30; 26 state a rate) | |
|---|---|
| Compliance rate | min 27 %, median 61 %, max 89 % |
| Status | partially compliant 15, non-compliant 14, not stated 1 (none fully compliant) |
| Overall level ("niveau général d'accessibilité") | faible 11, moyen 10, bon 6, not stated 3 |
| Sample size | median 14 pages |
| Accessibility statement | missing on 14 of the 30 websites at audit time (17 of the 42 reports, apps included) |

| Simplified audits (n = 186) | |
|---|---|
| Overall level | très bon 31, bon 56, moyen 91, faible 8 |
| Accessibility statement | complete 64, incomplete 36, missing 86 (only a third of monitored sites comply) |
| Cases reported per site | median 12 "examples of problems" blocks over 3 pages |

Two consequences for an auditor: a median public site is around 50 % and "non conforme" is as common as
"partiellement conforme", so a report that finds 30 to 40 non-compliant criteria on a sample is normal, not harsh; and
the statement is the first thing the SIP checks, so always say whether it exists, is complete, and names the SIP route.

## What fails most often

Full audits: share of the 42 reports whose technical annex contains the case (case names are the SIP's own section
titles; criteria in brackets are the mapping to RAWeb / RGAA numbers).

| Reports | Case (SIP wording) | Criteria |
|---|---|---|
| 40 | titres (heading structure) | 9.1 |
| 37 | listes | 9.3 |
| 33 | contrastes des textes | 3.2 |
| 31 | contrôle de saisie et aide à la saisie | 11.10, 11.11 |
| 30 | balises utilisées à des fins de présentation | 10.1, 8.9 |
| 29 | étiquettes et champs | 11.1, 11.2, 11.4 |
| 28 | indication de langue | 8.3, 8.4, 8.7, 8.8 |
| 27 | structure du document (header/nav/main/footer) | 9.2 |
| 27 | documents en téléchargement | 13.3, 13.4 |
| 27 | visibilité de la prise de focus | 10.7 |
| 23 | images de décoration | 1.2 |
| 23 | utilisation des boutons et des liens (links used as buttons and vice versa) | 7.1, 7.3, 6.1 |
| 23 | ordre de tabulation | 12.8 |
| 22 | contraste des composants d'interface | 3.3 |
| 21 | landmarks ARIA | 12.6 |
| 20 | utilisation de CSS exclusivement | 10.1 |
| 20 | information par la couleur | 3.1 |
| 19 | message de statut | 7.5 |
| 19 | ordre visible vs ordre réel (content understandable without styles) | 10.3 |
| 18 | images porteuses d'information | 1.1, 1.3 |
| 18 | identification des données attendues (autocomplete) | 11.13 |
| 17 | gestion de la visibilité de zones (show/hide, accordions) | 7.1, 10.8 |
| 17 | largeur réduite (reflow 320 px) | 10.11 |
| 16 | présence d'intitulés (links without name) | 6.2 |
| 15 | tableaux de données | 5.6, 5.7 |
| 15 | fenêtres modales | 7.1, 7.3, 12.8 |
| 15 | regroupements de champs et légendes | 11.5, 11.6, 11.7 |
| 14 | pertinence des intitulés (link text) | 6.1 |
| 14 | contenus additionnels au survol et au focus | 10.13, 12.11 |
| 13 | titre de la page | 8.5, 8.6 |
| 13 | transcription textuelle | 4.1, 4.2 |
| 13 | information donnée par la forme, la taille ou la position | 10.9, 10.10 |
| 13 | paramètres typographiques (text spacing) | 10.12 |
| 13 | intitulés de bouton pertinents | 11.9 |
| 13 | contenus en mouvement ou clignotants | 13.8 |
| 12 | liens d'accès rapide | 12.7 |
| 12 | rôle inapproprié ou non défini | 7.1 |
| 11 | images légendées | 1.9 |
| 11 | agrandissement des tailles de texte | 10.4 |

Simplified audits: share of the 186 reports containing the case (mapping from the SIP generator's `solutions.json`).

| Reports | Case (SIP wording) | Criteria |
|---|---|---|
| 160 (86 %) | éléments interactifs inaccessibles au clavier | 7.3 |
| 140 | indication de langue | 8.3, 8.4, 8.7, 8.8 |
| 136 | contrastes des textes | 3.2 |
| 135 | landmarks ARIA | 12.6 |
| 113 | contrôle et aide à la saisie | 11.10 |
| 108 | présence d'intitulés (links) | 6.2 |
| 105 | liens d'accès rapide | 12.7 |
| 104 | visibilité du focus | 10.7 |
| 89 | structure du document HTML5 | 9.2 |
| 87 | images porteuses d'information | 1.1, 1.3 |
| 85 | titres | 9.1 |
| 75 | contenus additionnels au survol et au focus | 10.14 |
| 71 | identification des champs, des contrôles et des regroupements | 11.1, 11.2, 11.5, 11.6, 11.7 |
| 65 | images de décoration | 1.2 |
| 64 | informations données uniquement par la couleur | 3.1 |
| 62 | pertinence des intitulés | 6.1 |
| 58 | contenus en mouvement ou clignotants | 13.8 |
| 47 | titres de cadres | 2.1 |
| 45 | ordre de tabulation | 12.8 |
| 44 | information donnée par la forme, la taille ou la position | 10.9, 10.10 |
| 42 | contenus cachés | 10.8 |
| 39 | contenus additionnels (keyboard access to hover content) | 12.11 |
| 30 | images porteuses d'informations complexes | 1.6, 1.7 |
| 29 | transcription textuelle et audiodescription | 4.1, 4.2 |
| 27 | en-têtes de tableaux et liaison des cellules | 5.6, 5.7 |
| 22 | sous-titres | 4.3, 4.4 |
| 14 | titre de page | 8.5, 8.6 |

Reading across both lists, the criteria an auditor should test first on any Luxembourg (or French) public site are
7.3, 8.3/8.7, 3.2, 12.6/9.2, 11.10, 6.2, 12.7, 10.7, 9.1, 9.3, 1.1/1.2/1.3, 11.1, 10.1 and 13.3. The static scanner covers
most of their code-visible part; 7.3, 3.2, 10.7 and 12.6 still need a keyboard, a contrast tool and a screen reader.

## Typical full-audit sample

Page titles that appear in the SIP samples (count over 25 website audits): Accueil 29, Contact 25, Accessibilité 22,
Résultats de recherche 18, Plan du site 17, Mentions légales 22 (two spellings), Actualités / une actualité 11,
Publications 9, Formulaires 3, Authentification 2, Annuaire, FAQ, Agenda, Glossaire, Inscription à la newsletter.
The SIP therefore audits the search results page and at least one news article almost systematically; put them in
every sample.

## Structure of a SIP full-audit report (reproduce it for Luxembourg deliverables)

1. **Introduction**: "Ce rapport accompagne le relevé d'audit effectué sur le site « X »"; referential and its URL;
   method: browsers, specialised tools, rendering tests in the referential's test environment.
2. **Échantillon**: table "Nº page | Titre de la page | URL" with P01, P02... then the statement check (missing /
   incomplete / present, with the legal reminder: article 5 of the [law of 28 May 2019](https://legilux.public.lu/eli/etat/leg/loi/2019/05/28/a373/jo), generator on
   accessibilite.public.lu, 30 days to notify accessibilite@sip.etat.lu).
3. **Environnement de test**: the paragraph on rendering tests, then two tables, desktop (assistive technology +
   browser, with versions: "NVDA 2022.4 | Firefox 116", "JAWS 2022 | Firefox 116", "VoiceOver (macOS 13.4) | Safari 16.5")
   and mobile (OS, AT, browser).
4. **Accessibilité des pages auditées**: three sentences, in this order: "Le site présente un niveau général
   d'accessibilité [très faible / faible / moyen / bon / très bon]." "Le niveau de conformité relevé atteint
   NN,NN % de conformité [au RAWeb] sur l'ensemble des pages auditées" (RGAA-era reports add the rate at level A and at
   level AA). "Le site est [non / partiellement / totalement] conforme." Then:
   * table "Conformité" (Conforme / Non conforme per level, AA marked "(légal)");
   * "Note sur le calcul de conformité": the formula C / (C + NC), "C'est ce nombre qui constitue la référence
     légale", why the site rate is lower than page rates (one NC on one page makes the criterion NC for the sample),
     and that full compliance needs 100 % on every page;
   * "Moyenne par pages" (table Nº, title, % C) and "Moyenne par thématiques" (C / NC per topic);
   * "Impacts utilisateurs": one paragraph naming the most affected users (blind users, keyboard users...) and why;
   * "Contenus exemptés": which exemptions apply (office files before 23 September 2018, media before 23 September 2020...);
   * "Note sur le relevé des non-conformités": only examples are cited, not every occurrence.
5. **Avis**: what users can and cannot do ("Le site peut être en partie consulté mais les utilisateurs utilisant un
   lecteur d'écran ne pourront pas déposer une plainte...") followed by "Les non-conformités les plus bloquantes pour
   les utilisateurs concernent :" and 4 to 6 bullets, each a family of problems with its user consequence, ending with
   "Ce sont donc ces points qui devront nécessiter une attention toute particulière".
6. **Annexe technique**, one section per topic in referential order, each with:
   * "Recommandation": one sentence, the topic's general rule (the same texts as the simplified reports);
   * one sub-section per case met (e.g. "Images de décoration", "Fenêtres modales", "Ordre de tabulation"): a
     paragraph explaining the rule and who it affects, the technique to apply, then **"Constats sur le site"**: the
     actual findings.

## How findings are written ("Constats sur le site")

Each constat is one or two sentences, locates the element on a named page, names the element by its visible text
or role, and states the problem (and sometimes the measurement or the fix). Real examples:

* "Sur la page « Une actu », les images img du carrousel sont les seuls contenus affichés et doivent donc avoir une
  alternative même si l'image est décorative (utiliser par exemple "Photo 1", "photo 2", etc.)."
* "Sur l'ensemble des pages, la couleur #4DA5E4 sur le fond #FFF (ratio : 2,69) (concerne de nombreux textes et
  composants interactifs, y compris au survol ou lors de la prise de focus)."
* "Sur la page « Formulaire », l'indication de lien actif dans le menu de navigation secondaire latéral (lien "Tous les
  formulaires")." (information given by colour alone)
* "Dans la modale « Mobilité », les tableaux dans les blocs sous les boutons "Plus d'informations" n'ont pas la
  propriété role="presentation"."
* "Sur la version mobile de la page « Généralités », on trouve « Sommaire » qui est implémenté dans une fenêtre
  modale. Cependant, cette fenêtre modale n'implémente pas les principes du motif de conception ARIA Dialog."
* "Sur la page « Résultats de recherche », on trouve des paragraphes <p> vides servant à créer des espacements."
* "Sur l'ensemble de pages, la suite de liens d'accès rapide n'est pas structurée dans une liste."
* "On trouve des images qui ne sont pas ignorées par les technologies d'assistance comme l'image d'illustration de
  l'article « Un rapport qui reflète... » sur la page d'Accueil."

Conventions to copy: start with the location ("Sur la page « X »", "Sur l'ensemble des pages", "Dans la modale « Y »");
quote visible labels in « »; give colour pairs and ratios for contrast; name the ARIA pattern that should have been
used; when something is decorative-but-only-content, say what alternative to give. Criteria numbers are not repeated
in every constat in SIP reports (the case title carries them); in your reports add the criterion and test id anyway,
since clients ask for them.

In simplified reports the same findings appear under "Exemples de problèmes détectés sur la page N", for example:
"Lors de l'ouverture de la fenêtre modale « Compte lecteur », le focus clavier n'est pas correctement piégé : la
tabulation peut sortir du dialogue. Par ailleurs, la touche Echap est inopérante. Il faut respecter le design pattern
WAI-ARIA « Dialog (Modal) »" or "Dans la section « Actualités », les dates en gris clair présenteront un contraste
insuffisant (3.11:1 au lieu de 4.5:1)."

## Using the corpus yourself

`python3 - <<'EOF'` style scripts are not bundled; the datasets are CC0 and each report has an HTML version, so a
fresh corpus can be rebuilt with the dataset API (`https://data.public.lu/api/1/datasets/<slug>/`, field
`resources[].url`), which is how the numbers above were produced (November 2026 snapshot).

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
