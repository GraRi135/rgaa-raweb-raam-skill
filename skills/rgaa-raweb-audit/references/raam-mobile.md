# Mobile applications: RAAM 1.1 and the Android workflow

Read this for any native or hybrid mobile app (Android, iOS, Flutter, React Native, Ionic...). Web sites viewed on a
phone are still RAWeb / RGAA, with the mobile test environment. France has no app-specific standard; the SIP's RAAM is
the only operational transcription of EN 301 549 for apps in the region, so use it for French apps too, saying so.

## The standard

* **RAAM 1.1** (référentiel d'évaluation de l'accessibilité des applications mobiles), SIP Luxembourg, published
  24 February 2025, replaces RAAM 1 (used in the 2023-2024 SIP app audits). CC-BY 3.0 LU, sources on GitHub
  (accessibility-luxembourg/ReferentielAccessibiliteMobile). Official page: accessibilite.public.lu/en/raam1.1/.
* 108 criteria in 15 topics, covering EN 301 549 v3.2.1 chapters 5 (generic), 6 (two-way voice), 7 (video), 10
  (non-web documents), 11 (software), 12 (documentation and support). Levels A and AA as for the web; both mandatory.
* **Numbering is not the RAWeb numbering.** Topics: 1 graphic elements, 2 colours, 3 multimedia, 4 tables,
  5 interactive components, 6 mandatory elements (language, layout-only elements), 7 information structure (headings,
  lists), 8 presentation (text at 200 %, focus visibility, hidden content), 9 forms, 10 navigation (sequence, keyboard
  traps, shortcuts), 11 consultation (time limits, documents, cryptic content, flashes, motion, orientation, gestures,
  biometrics, key repeat), 12 documentation and accessibility features, 13 editing tools, 14 support services,
  15 real-time communication. `references/raam-criteria-index.md` lists them all; never cite a RAWeb number in an app audit.
* Most criteria have **no numbered tests**: the criterion is the test, and each one has an evaluation methodology
  per platform ("iOS and Android", "iOS", "Android"): `python3 scripts/criteria.py show 5.1 --standard raam --methodology`.
  The methodology is explicitly non-normative; it is still what the SIP applies.
* **Web views**: screens that embed web content under the publisher's responsibility are evaluated like the other
  screens; their HTML can additionally be scanned with the web tools. Third-party web content is exempt.

## Method

Same logic as the web (`audit-method.md`), with screens instead of pages:

* Sample: home screen; legal information; authentication screen or process; contact; the screens that make up the
  app's documentation; one relevant screen per service type and main use, including search; one downloadable document
  per service type if any; every screen of each process (form, multi-step transaction); screens with distinct layouts
  or content types; plus 10 % random screens. The SIP samples typically have 6 to 10 screens: Accueil, Politique de
  confidentialité, Mentions légales (often a web view), Contact, Paramètres, Documentation / À propos, Onboarding,
  Authentification, Déclaration d'accessibilité, and the core service screens.
* Statuses C / NC / NA / NT per screen; a criterion is NC for the app if NC on one screen; process screens share
  results; rate = C / (C + NC); topics 12 and 14 are app-level (assess once). `audit_grid.py new --standard raam
  --pages "Accueil=,Contact=,..."` and `compute` apply the same rules.
* Test environment: the latest (or previous) iOS with VoiceOver and the latest (or previous) Android with TalkBack,
  latest AT versions; no need to test several Android manufacturers; a managed environment replaces the baseline.
* Report: the SIP app reports follow the full-audit outline (`sip-audit-corpus.md`) with "écrans" and "parcours"
  instead of pages, give the rate at level A and at level AA, and write findings as "Constats dans l'application".

## What the SIP finds in apps (12 full audits, 2023-2024)

Rates 26 % to 66 % (median 38 %); overall level "faible" for 9 of 12 apps. Cases present in the annex, with the
RAAM 1.1 criteria they map to:

| Apps | Case (SIP wording) | RAAM 1.1 |
|---|---|---|
| 12 / 12 | rôle inapproprié ou non défini | 5.1 |
| 12 | titres (no heading semantics for TalkBack/VoiceOver) | 7.1 |
| 11 | contrastes des textes | 2.2 |
| 10 | contraste des composants d'interface | 2.3 |
| 10 | intitulé absent ou non pertinent | 5.1 |
| 10 | agrandissement des textes (200 %) | 8.2 |
| 9 | message de statut | 5.4 |
| 9 | listes | 7.2 |
| 9 | étiquettes et champs | 9.1, 9.2, 9.3 |
| 9 | consultation des contenus indépendante de l'orientation | 11.9 |
| 9 | éléments graphiques porteurs d'information | 1.2, 1.3 |
| 9 | clavier et dispositifs de pointage | 5.2 |
| 8 | information par la couleur | 2.1 |
| 8 | contrôle de saisie et aide à la saisie | 9.7, 9.8, 9.9, 9.10 |
| 7 | ordre de tabulation | 10.1 |
| 7 | gestes complexes | 11.10 |
| 7 | état des composants interactifs | 5.1, 5.5 |
| 7 | éléments graphiques de décoration | 1.1 |
| 7 | lecteur d'écran (components unreachable with the screen reader) | 5.1 |
| 6 | contenus visibles non accessibles | 8.1 |
| 6 | ordre de restitution | 10.2 |
| 5 | changement de contexte | 5.3 |
| 5 | indication de langue | 6.1 |
| 4 | regroupements de champs et légendes | 9.6 |
| 3 | tableaux de données, documents en téléchargement, nature des saisies, forme/taille/position | 4.x, 11.3, 9.8, 8.6 |

Real wording: "De nombreux éléments interactifs n'ont pas de rôle défini ou pertinent. Par exemple dans les
formulaires, les listes déroulantes n'ont pas de rôle défini. Les personnes utilisant un lecteur d'écran ne peuvent
savoir que ces éléments sont interactifs." — "Les puces indiquant les éléments actifs et inactifs dans les carrousels
ne sont pas assez contrastées. Elles sont de couleur jaune #F9BD00 et grise #D7D7D7 sur fond blanc #FFFFFF avec
respectivement un ratio de contraste de 1,7 et 1,4." — "Dans les paramètres de l'application, le composant de
sélection de langue n'est pas atteignable avec un lecteur d'écran."

## Android workflow with adb (device or emulator)

Prerequisites: Android platform-tools (`adb`) on the PATH; either a device with USB debugging or an emulator
(`emulator -list-avds`, `emulator -avd <name>`; a Google Play system image lets you install the "Android
Accessibility Suite", which provides TalkBack). The app under test installed and logged in as needed.

1. `python3 scripts/android_audit.py devices` to confirm the connection (use `--serial` if several).
2. Navigate to each screen of the sample by hand, then `python3 scripts/android_audit.py capture --screen "Accueil"
   --out android-audit/`: saves the uiautomator view hierarchy (what TalkBack sees), a screenshot, the activity name
   and the display settings.
3. `python3 scripts/android_audit.py analyse android-audit/accueil/` maps the hierarchy to RAAM criteria:
   * FAIL 5.1: interactive element without name (uiautomator marks them `NAF="true"`); FAIL 5.2: clickable but not
     focusable (unreachable with a keyboard or switch); FAIL 9.2: form field with no label at all;
   * REVIEW 5.1: clickable containers or TextViews without a control role; REVIEW 1.1 / 1.3: images without or with
     alternative; REVIEW 5.5 toggle states; REVIEW 9.1 hint used as label; REVIEW 10.2 hierarchy order differs from
     the visual order; REVIEW 2.2 estimated text contrast below 4.5:1 from the screenshot (dominant colours, to confirm
     with a contrast analyser);
   * INFO: web views (scan their HTML with the web tools), small targets (recommendation only), and the list of
     criteria that only TalkBack or a keyboard can decide.
4. `python3 scripts/android_audit.py walk --screen "Accueil" --out android-audit/` does step 2 three times, at font
   scale 1.0, 2.0 and in landscape, and compares the texts: truncation or loss at 200 % is evidence for 8.2,
   a display that stays in portrait after requesting landscape is evidence for 11.9 (NC unless essential).
   `font-scale`, `rotate` and `talkback on|off` do the individual settings changes.
5. Manual pass with TalkBack (enable it, then swipe right through the screen, use headings navigation, activate every
   control, submit the forms with errors, check status messages) and with a hardware keyboard (Tab order, traps,
   focus visibility). On an emulator the host keyboard acts as a hardware keyboard; TalkBack also has keyboard
   shortcuts (Settings > TalkBack > Advanced > Keyboard shortcuts). Record what is announced; it is the evidence for
   5.1, 5.3, 5.4, 6.1, 7.1, 7.2, 8.5, 10.x and 11.x.
6. Fill the grid (`audit_grid.py set ... --page "Accueil"`), compute, write the report with the app outline.

Google's **Accessibility Scanner** (Play Store) runs on the device and flags unlabelled controls, small targets and
low contrast; its results are screenshots, not data, but they corroborate step 3. Developers can automate the same
checks in Espresso with the Accessibility Test Framework.

## iOS

Scripted inspection needs macOS and Xcode: Accessibility Inspector (Xcode > Open Developer Tool) attached to a
simulator or device walks the accessibility tree with role, label, value, traits, exactly what RAAM's iOS
methodology asks; `xcrun simctl` boots simulators; VoiceOver on a device is the baseline. There is no adb
equivalent that works from Linux or Windows, so this skill gives no iOS collector: audit iOS apps by hand with
VoiceOver and Accessibility Inspector, using the per-criterion iOS methodology from `criteria.py`, and reuse the
Android findings as hypotheses (the same design usually fails the same way on both platforms, which the SIP reports
confirm).
