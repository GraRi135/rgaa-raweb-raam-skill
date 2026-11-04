---
tags: [rgaa-raweb-audit]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We maintain the Android app of a Luxembourg public body ("Mäin Service", package lu.exemple.app) and the SIP has announced a RAAM audit. A colleague captured the home screen with adb on an emulator: capture/accueil/ holds the uiautomator view hierarchy (window_dump.xml), a screenshot (screen.png) and meta.json; capture/accueil-x2/ is the same screen with the system font scale at 2.0. Can you audit this screen against RAAM 1.1 and give us the non-conformities with the criterion numbers and what to fix in the app? Please also tell us what you could not check from these files.

Input files: capture/accueil/window_dump.xml, capture/accueil/screen.png, capture/accueil/meta.json, capture/accueil-x2/window_dump.xml, capture/accueil-x2/meta.json
