# rgaa-raweb-audit — une compétence Claude pour les audits d'accessibilité RGAA, RAWeb et RAAM

*English version: [README.md](README.md)*

Une compétence (« skill », installable comme plugin Claude Code) qui permet à Claude d'auditer des sites, des pages, du
code front-end et des applications mobiles au regard de :

* **RGAA 4.1.2** — Référentiel général d'amélioration de l'accessibilité (France, DINUM), 106 critères ;
* **RAWeb 1.1** — Référentiel d'évaluation de l'accessibilité web (Luxembourg, SIP), 136 critères (RGAA 4.1.2 plus les
  exigences web restantes de la norme EN 301 549 v3.2.1) ;
* **RAAM 1.1** — Référentiel d'évaluation de l'accessibilité des applications mobiles (Luxembourg, SIP), 108 critères
  pour les applications Android et iOS, avec un collecteur de preuves Android fondé sur adb.

Elle embarque les critères, tests et méthodologies officiels des trois référentiels (anglais et français pour RAWeb et
RAAM, français pour le RGAA), la méthode d'audit (échantillon, applicabilité, taux de conformité, déclaration), la
méthode d'audit simplifié du SIP, ce que montrent 228 audits publiés par le SIP (constats les plus fréquents, structure
et formulation des rapports), et les outils suivants :

| Script | Rôle |
|---|---|
| `scripts/criteria.py` | consulter critères, tests, méthodologie de test, glossaire ; comparer RAWeb et RGAA |
| `scripts/scan_html.py` | pré-vérification statique d'une page HTML ou d'une URL, constats rattachés aux critères et tests |
| `scripts/audit_grid.py` | créer une grille pages × critères, remplir les statuts, calculer le taux et l'état de conformité selon les règles officielles |
| `scripts/contrast.py` | rapports de contraste avec les seuils RGAA/RAWeb (textes, composants, focus), à partir de couleurs ou d'une feuille de style |
| `scripts/android_audit.py` | écrans d'applications Android via adb (appareil ou émulateur) : hiérarchie de vues, capture d'écran, texte à 200 %, orientation, TalkBack ; constats rattachés au RAAM 1.1 |
| `scripts/build_report.py` | fichier de constats → un rapport HTML accessible en un seul fichier avec captures annotées intégrées, et un PDF A4, dans l'ordre des rapports du SIP |
| `scripts/render_page.js` | optionnel : rendu d'une URL avec Playwright (applications monopage, ordre de tabulation, zoom, captures mobiles) ; `--annotate` entoure l'élément de chaque constat et découpe une capture ; `--print` produit le PDF |
| `scripts/refresh_data.py` | régénérer les données embarquées depuis les dépôts GitHub officiels |

## Important : une aide, pas un audit

Cette compétence est une aide de travail pour les auditeurs et les développeurs. Elle peut manquer des problèmes et se
tromper : les vérifications statiques ne voient que le HTML livré ou la hiérarchie de vues Android, les points « à
vérifier » sont des heuristiques, et le jugement de Claude sur un critère peut être erroné même avec le libellé officiel
du test sous les yeux. Rien de ce qu'elle produit ne remplace un audit de conformité réalisé par un auditeur formé sur
l'échantillon complet, avec les technologies d'assistance de l'environnement de test (NVDA, JAWS, VoiceOver, TalkBack),
au clavier, et avec de vrais utilisateurs lorsque c'est possible. En particulier :

* un taux ou un état de conformité calculé à partir de ses résultats est provisoire tant que chaque critère applicable
  n'a pas été testé par une personne ;
* une déclaration d'accessibilité doit reposer sur un tel audit, et l'organisme qui la publie en reste responsable ;
* une page ou une application sans constat est non testée, pas conforme.

Considérez ses rapports comme des éléments à vérifier et une liste de tâches, jamais comme l'audit lui-même.

## Installation

Depuis votre terminal (Claude Code 2.1.292 ou plus récent), en une commande :

```bash
claude plugin install rgaa-raweb-audit --marketplace GraRi135/rgaa-raweb-claude
```

Ou en deux étapes (ce dépôt est sa propre place de marché à un plugin) :

```bash
claude plugin marketplace add GraRi135/rgaa-raweb-claude
```

```bash
claude plugin install rgaa-raweb-audit@rgaa-raweb-claude
```

Dans une session, les commandes `/plugin marketplace add GraRi135/rgaa-raweb-claude` puis
`/plugin install rgaa-raweb-audit@rgaa-raweb-claude` font la même chose. Ajoutez `--scope project` pour l'activer pour
toute l'équipe d'un dépôt.

Pour l'essayer sans l'installer, lancez Claude Code avec le clone comme répertoire de plugin :

```bash
claude --plugin-dir /chemin/vers/rgaa-raweb-claude
```

Ou copiez le dossier de la compétence dans un répertoire de compétences lu par Claude Code (`~/.claude/skills/` pour
tous les projets, `.claude/skills/` dans un projet) :

```bash
cp -r skills/rgaa-raweb-audit ~/.claude/skills/
```

Demandez ensuite, par exemple : « audite cette page selon le RAWeb 1.1 », « calcule le taux de conformité RGAA de cette
grille et rédige la déclaration d'accessibilité », « relis ce composant React au regard du RGAA » ou « audite notre
application Android selon le RAAM ». Les scripts n'ont besoin que de Python 3 ; `render_page.js` demande en plus
Node.js et Playwright, et `android_audit.py` demande adb (Android platform-tools).

## Où cela fonctionne

| Environnement | Scripts | Pages | Remarques |
|---|---|---|---|
| Claude Code (terminal, application de bureau, cloud, VS Code) | oui | pages publiques récupérées et rendues avec Playwright ; fichiers locaux | le flux complet, y compris le collecteur Android si adb est installé |
| Application de bureau ou Cowork avec le navigateur intégré | oui | toute page que le navigateur peut ouvrir, y compris derrière une authentification | les outils de lecture et les captures ajoutent les preuves clavier et focus ; le shell exécute les scripts sur le DOM exporté |
| Claude Code ou claude.ai avec Claude dans Chrome | si un shell existe | toute page de votre Chrome, avec vos sessions | son outil JavaScript exécute les sondes de `references/browser-probes.md` et exporte le DOM rendu pour le scanner |
| claude.ai seul avec la compétence | bac à sable, sans réseau | HTML collé ou téléversé | consultation, grille et scanner sur les fichiers fournis ; pas de navigation |

Aucun environnement ne donne un lecteur d'écran à Claude : les critères qui exigent NVDA, JAWS, VoiceOver ou TalkBack
restent « non testés » tant qu'une personne ne les a pas passés.

## Documentation

* [Démarrage rapide](docs/quick-start.md) pour les développeurs et utilisateurs de Claude Code (en anglais).
* [Déroulé d'un audit web](docs/web-audit-walkthrough.md) pour les auditeurs : la méthode, ce que fait Claude, ce que vous devez faire, comment lire et vérifier un constat.
* [Déroulé d'un audit d'application Android](docs/android-audit-walkthrough.md) : RAAM 1.1 avec le collecteur adb, passes TalkBack et clavier.
* [Déclarations d'accessibilité](docs/statements.md) : obligations en France et au Luxembourg, calcul du taux à partir d'une grille.
* [Comment la compétence a été évaluée](docs/evaluation.md) : cas de test, résultats avec et sans la compétence, calibrage sur 228 audits réels du SIP, faiblesses connues.
* [Mettre à jour les données embarquées](docs/updating-data.md) quand un référentiel change.
* [Contribuer](docs/contributing.md).
* [Exemples](examples/README.md) : entrées fictives et rapports produits par Claude à partir d'elles.
* [Page de sensibilisation](explainer/README.md) : une page unique, hébergeable partout, en français et en anglais, qui explique dix règles d'accessibilité avec des simulations, des exercices et un quiz, pour les personnes qui ne connaissent pas les règles.

Les guides sont en anglais ; les livrables produits par la compétence (rapports, déclarations) sont rédigés dans la
langue de la demande, en français pour les documents officiels.

## Organisation du dépôt

```
docs/                         guides
examples/                     entrées fictives et exemples de sorties
explainer/                    la page de sensibilisation hébergeable (index.html) et ses notes
skills/rgaa-raweb-audit/
├── SKILL.md                  instructions suivies par Claude
├── references/               méthode d'audit, modèles de rapport, RAWeb vs RGAA, RAAM et flux Android, méthodes
│   │                         et corpus du SIP, sondes navigateur, carte de l'automatisation, index des critères
│   └── data/                 critères + tests + méthodologie + glossaires en JSON (voir NOTICE.md)
├── scripts/                  les outils ci-dessus (Python 3 standard ; render_page.js demande Node + Playwright)
└── evals/                    cas de test (compatibles `claude plugin eval`)
```

## Licence

Les scripts, les instructions de la compétence et la documentation sont sous licence MIT (`LICENSE`). Les données de
référence embarquées sont des contenus tiers conservés sous leurs propres conditions : RAWeb 1.1 et RAAM 1.1 sous
CC-BY 3.0 LU (Service information et presse, Luxembourg), RGAA 4.1.2 sous Licence Ouverte 2.0 (DINUM, France), les
formulations de rapport du SIP sous MIT, et les statistiques d'audit proviennent de jeux de données CC0. `NOTICE.md`
liste chaque composant avec son titulaire, sa version, sa licence et ce qui a été modifié ; la même information est
livrée dans la compétence (`references/data/NOTICE.md`). Si vous redistribuez les données, conservez ces attributions.
