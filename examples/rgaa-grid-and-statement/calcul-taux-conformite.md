# Calcul du taux de conformité RGAA 4.1.2 — demarches.ville-exemple.fr

| | |
|---|---|
| **Site** | https://demarches.ville-exemple.fr |
| **Référentiel** | RGAA version 4.1.2 (106 critères, niveaux A et AA, sans pondération) |
| **Audit** | octobre 2026, réalisé en interne par le pôle numérique de la Ville d'Exemple |
| **Grille analysée** | `grille-audit.csv` (séparateur « ; »), 106 critères × 9 pages, statuts C / NC / NA |
| **Contrôle de la grille** | 106 critères reconnus, aucun critère inconnu ni manquant, **aucun statut NT** : le taux est définitif, pas provisoire |
| **Processus déclaré** | « Demande de subvention » = Subvention - étape 1, étape 2, étape 3 |
| **Calcul** | `python3 scripts/audit_grid.py compute grille-audit.csv --standard rgaa --lang fr --process "Demande de subvention=Subvention - étape 1,Subvention - étape 2,Subvention - étape 3"` |

## 1. Règles appliquées (méthode RGAA 4.1.2, « évaluation de la conformité »)

Statut d'un critère au niveau du site :

- **conforme** s'il est conforme sur toutes les pages où il s'applique (et applicable sur au moins une page) ;
- **non conforme** s'il est non conforme sur au moins une page de l'échantillon ;
- **non applicable** uniquement s'il est non applicable sur toutes les pages, sans exception.

Taux de conformité = critères conformes ÷ critères applicables (conformes + non conformes), sans pondération par niveau (A et AA comptent pareil), par thématique ni par gravité.

État de conformité : 100 % → conformité totale ; de 50 % à moins de 100 % → conformité partielle ; moins de 50 % → non-conformité.

Processus : un critère n'est conforme sur une page d'un processus que s'il est conforme sur **toutes** les pages de ce processus. Cette règle modifie les taux par page (et donc le taux moyen facultatif) ; elle ne change pas le taux de conformité du site, qui est déjà calculé sur l'ensemble de l'échantillon.

## 2. Résultat global

| Indicateur | Valeur |
|---|---|
| Critères conformes (C) | **53** |
| Critères non conformes (NC) | **26** (19 de niveau A, 7 de niveau AA) |
| Critères non applicables (NA) | 27 |
| Critères non testés (NT) | 0 |
| Critères applicables (C + NC) | **79** |
| **Taux de conformité** | **67,1 %** (53 ÷ 79) |
| **État de conformité** | **Partiellement conforme** |
| Taux moyen de conformité des pages (facultatif) | 89,5 % |

Contrôle : 53 + 26 + 27 = 106 critères.

## 3. Taux par page (processus « Demande de subvention » appliqué)

| Page | Critères applicables | Conformes | Non conformes | Taux de la page |
|---|---|---|---|---|
| Accueil | 60 | 49 | 11 | 81,7 % |
| Contact | 65 | 61 | 4 | 93,8 % |
| Mentions légales | 47 | 46 | 1 | 97,9 % |
| Accessibilité | 52 | 50 | 2 | 96,2 % |
| Plan du site | 48 | 47 | 1 | 97,9 % |
| Recherche | 63 | 60 | 3 | 95,2 % |
| Subvention - étape 1 | 63 | 51 | 12 | 81,0 % |
| Subvention - étape 2 | 67 | 54 | 13 | 80,6 % |
| Subvention - étape 3 | 63 | 51 | 12 | 81,0 % |

Effet de la règle des processus : prises isolément (sans déclarer le parcours), les trois étapes afficheraient 90,5 %, 92,5 % et 92,1 % et le taux moyen serait de 93,1 %. Comme elles forment un seul parcours, chaque non-conformité relevée sur une étape s'applique aux autres étapes (lorsque le critère y est applicable). Le taux de conformité du site reste 67,1 % dans les deux cas.

## 4. Critères non conformes au niveau du site (26), par thématique

| Critère | Niveau | Intitulé (abrégé) | Pages concernées |
|---|---|---|---|
| 1.1 | A | Image porteuse d'information sans alternative textuelle | Accueil |
| 1.3 | A | Alternative textuelle d'image non pertinente | Recherche |
| 2.1 | A | Cadre sans titre de cadre | Contact |
| 3.2 | AA | Contraste texte / arrière-plan insuffisant | Accueil ; parcours subvention (étape 2) |
| 4.3 | A | Média temporel synchronisé sans sous-titres synchronisés | Accueil |
| 4.5 | AA | Média temporel sans audiodescription synchronisée | Accueil |
| 5.6 | A | En-têtes de colonnes / de lignes de tableau de données non déclarés | parcours subvention (étape 2) |
| 6.1 | A | Liens non explicites | Accueil, Contact |
| 7.1 | A | Script non compatible avec les technologies d'assistance | parcours subvention (étape 1) |
| 7.4 | A | Changement de contexte initié par script sans avertissement ni contrôle | parcours subvention (étape 3) |
| 7.5 | AA | Messages de statut non restitués par les technologies d'assistance | parcours subvention (étape 2) |
| 8.2 | A | Code source non valide selon le type de document | Accueil |
| 8.7 | AA | Changement de langue non indiqué dans le code source | Accueil |
| 9.1 | A | Information non structurée par des titres appropriés | Contact |
| 10.6 | A | Lien non visible par rapport au texte environnant | Accueil |
| 10.7 | A | Prise de focus non visible | **toutes les pages** (9/9) |
| 10.11 | AA | Perte d'information ou de fonctionnalité à 320 px de large / 256 px de haut | parcours subvention (étape 2) |
| 11.1 | A | Champ de formulaire sans étiquette | Recherche ; parcours subvention (étape 1) |
| 11.5 | A | Champs de même nature non regroupés | parcours subvention (étape 1) |
| 11.10 | A | Contrôle de saisie non pertinent | parcours subvention (étapes 1 et 3) |
| 11.11 | AA | Pas de suggestion facilitant la correction des erreurs de saisie | parcours subvention (étape 3) |
| 11.13 | AA | Finalité des champs non déductible (remplissage automatique) | parcours subvention (étape 1) |
| 12.7 | A | Absence de lien d'évitement ou d'accès rapide au contenu principal | Accueil |
| 13.1 | A | Limite de temps modifiant le contenu non contrôlable | parcours subvention (étape 3) |
| 13.3 | A | Document bureautique en téléchargement sans version accessible | Accessibilité |
| 13.8 | A | Contenu en mouvement ou clignotant non contrôlable | Accueil |

Les 27 critères non applicables sur tout l'échantillon : 1.4, 1.5, 1.6, 1.7, 1.8, 4.4, 4.6, 4.8, 4.9, 4.10, 4.12, 5.1, 5.2, 5.3, 5.8, 7.2, 8.8, 8.10, 9.4, 10.13, 11.8, 12.10, 13.4, 13.5, 13.6, 13.10, 13.12.

## 5. Détail par page

- **Accueil** (11 NC) : 1.1, 3.2, 4.3, 4.5, 6.1, 8.2, 8.7, 10.6, 10.7, 12.7, 13.8.
- **Contact** (4 NC) : 2.1, 6.1, 9.1, 10.7.
- **Mentions légales** (1 NC) : 10.7.
- **Accessibilité** (2 NC) : 10.7, 13.3.
- **Plan du site** (1 NC) : 10.7.
- **Recherche** (3 NC) : 1.3, 10.7, 11.1.
- **Parcours « Demande de subvention »** (13 critères NC sur le parcours) :
  - relevés à l'étape 1 : 7.1, 10.7, 11.1, 11.5, 11.10, 11.13 ;
  - relevés à l'étape 2 : 3.2, 5.6, 7.5, 10.7, 10.11 ;
  - relevés à l'étape 3 : 7.4, 10.7, 11.10, 11.11, 13.1 ;
  - par la règle des processus, chaque étape porte en plus les non-conformités des deux autres étapes quand le critère y est applicable (d'où 12, 13 et 12 critères NC par étape dans le tableau du § 3 ; 5.6 n'est pas reporté sur les étapes 1 et 3 où il n'y a pas de tableau de données).

## 6. Lecture des résultats et points d'attention

- **Un critère corrigé partout = + 1,27 point.** Pour atteindre la conformité totale (100 %), les 26 critères doivent être corrigés sur toutes les pages concernées.
- **10.7 (focus visible)** est le seul critère non conforme sur les 9 pages. C'est en général une correction CSS transversale (ne pas supprimer `outline` sans le remplacer par un indicateur visible) : + 1 critère → 68,4 %.
- **Parcours de subvention** : 13 critères NC, dont 10 ne sont en défaut que sur ce parcours (5.6, 7.1, 7.4, 7.5, 10.11, 11.5, 11.10, 11.11, 11.13, 13.1). C'est le service en ligne lui-même : les corriger ferait passer le taux à 79,7 % et, surtout, rendrait la démarche utilisable (étiquettes, regroupements, contrôle de saisie et messages d'erreur, messages de statut, limite de temps, changement de contexte).
- **Accueil** : 11 critères NC, dont 8 propres à cette page (1.1, 4.3, 4.5, 8.2, 8.7, 10.6, 12.7, 13.8) ; les corriger ferait passer le taux à 77,2 %. La vidéo de la page d'accueil (4.3 sous-titres, 4.5 audiodescription) et le lien d'évitement (12.7) sont des points très visibles pour les usagers.
- **Page Accessibilité** : 13.3 (document bureautique sans version accessible) est en défaut sur la page même qui accueillera la déclaration ; à corriger de préférence avant publication.
- **Cohérence de la grille** (à confirmer par les auditeurs, pas des erreurs en soi) : 2.1 NC et 2.2 C sur Contact n'est cohérent que si au moins un cadre a un titre pertinent et un autre n'en a pas ; de même 5.6 NC et 5.7 C sur l'étape 2 supposent plusieurs tableaux de données dont certains sont correctement associés.
- **Échantillon** : l'échantillon couvre accueil, contact, mentions légales, accessibilité, plan du site, recherche et les trois pages du processus. Le RGAA impose aussi, lorsqu'elles existent, la page d'aide, la page d'authentification (connexion / compte usager, fréquent sur un site de démarches), au moins un document téléchargeable par type de service et un tirage aléatoire d'au moins 10 % des pages de l'échantillon. Si ces pages existent et sont ajoutées, le taux doit être recalculé avec la même commande. Les URL des pages auditées doivent figurer dans la déclaration.

## Annexe — sortie brute du script

```
# Résultats de la grille d'audit — RGAA 4.1.2

| Page | applicables | conforme | non testé | taux |
|---|---|---|---|---|
| Accueil | 60 | 49 | 0 | 81.7 % |
| Contact | 65 | 61 | 0 | 93.8 % |
| Mentions légales | 47 | 46 | 0 | 97.9 % |
| Accessibilité | 52 | 50 | 0 | 96.2 % |
| Plan du site | 48 | 47 | 0 | 97.9 % |
| Recherche | 63 | 60 | 0 | 95.2 % |
| Subvention - étape 1 | 63 | 51 | 0 | 81.0 % |
| Subvention - étape 2 | 67 | 54 | 0 | 80.6 % |
| Subvention - étape 3 | 63 | 51 | 0 | 81.0 % |

- conforme: 53
- non conforme: 26
- non applicable: 27
- Taux de conformité: 67.1 % (53 / 79) → partiellement conforme
- Taux moyen de conformité des pages (facultatif) : 89.5 %
```
