---
tags: [rgaa-raweb-audit]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Bonjour, je suis responsable du site demarches.ville-exemple.fr (une ville fictive pour l'exercice, mais le site et l'audit sont réels de mon côté). Notre pôle numérique vient de terminer l'audit RGAA 4.1.2 en interne, la grille est dans grille-audit.csv (séparateur point-virgule, une colonne par page auditée, statuts C / NC / NA). Les trois pages "Subvention - étape 1/2/3" forment un seul parcours de demande de subvention.

Est-ce que tu peux me calculer le taux de conformité et me rédiger la déclaration d'accessibilité à publier ? L'audit a été réalisé en octobre 2026 par le pôle numérique de la Ville d'Exemple, le site est fait en HTML5/CSS/JavaScript (Vue.js), testé avec NVDA + Firefox et VoiceOver + Safari, outils : inspecteur de code, Colour Contrast Analyser, HeadingsMap. Contact accessibilité : accessibilite@ville-exemple.fr, formulaire de contact https://demarches.ville-exemple.fr/contact. Merci !

Input files: grille-audit.csv
