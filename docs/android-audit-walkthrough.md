# Android app audit walkthrough (RAAM 1.1)

[RAAM 1.1](https://accessibilite.public.lu/en/raam1.1/criteres.html) is the Luxembourg standard for mobile applications (108 criteria, 15 topics, its own numbering; do not
reuse RAWeb numbers). The skill ships an evidence collector for Android that works through adb on a physical device or
an emulator. iOS has no collector: use Accessibility Inspector and VoiceOver on macOS with the per-criterion iOS
procedure (`criteria.py show <id> --standard raam --methodology`).

## Setup

1. Install Android platform-tools; `adb` must be on the PATH.
2. Start an emulator (`emulator -list-avds`, `emulator -avd <name>`) or connect a device with USB debugging.
   A Google Play system image lets you install the Android Accessibility Suite, which provides TalkBack.
3. Install the app under test and sign in if needed.
4. `python3 skills/rgaa-raweb-audit/scripts/android_audit.py devices`

## Per screen of the sample

The sample follows the RAAM list: home, legal information, authentication, contact, documentation screens, one
screen per service, downloadable documents, every screen of each process, distinct layouts, plus 10 % random screens.
The SIP's samples have 6 to 10 screens.

1. Navigate to the screen by hand.
2. `android_audit.py walk --screen "Accueil" --out android-audit/` captures the view hierarchy and a screenshot three
   times: as is, at system font scale 2.0, and in landscape; restores the settings; compares the texts (truncation or
   loss at 200 % is evidence for 8.2, a display that stays in portrait is evidence for 11.9); and analyses the base capture.
   `capture` and `analyse` do the two halves separately.
3. Read the analysis:
   * FAIL 5.1: interactive element without a name; FAIL 5.2: clickable but not focusable (unreachable by keyboard or
     switch access); FAIL 9.2: form field with no label at all.
   * REVIEW: containers used as buttons without a role, images without or with an alternative, toggle states, hint
     used as label, reading order, estimated text contrast from the screenshot.
   * INFO: web views (audit their HTML with the web tools), small touch targets (a recommendation, not a criterion),
     and the list of criteria only TalkBack or a keyboard can decide.
4. TalkBack pass: `android_audit.py talkback on`, then swipe right through the screen, use headings navigation,
   activate every control, submit forms with errors. Record what is announced: that is the evidence for names and
   roles as rendered (5.1), context changes (5.3), status messages (5.4), language (6.1), headings and lists (7.1,
   7.2), hidden content (8.1), reading order (10.2).
5. Keyboard pass with a hardware keyboard or the emulator's host keyboard: focus order (10.1), traps (10.3), focus
   visibility (8.5).
6. Fill the grid: `audit_grid.py new --standard raam --pages "Accueil=,Contact=,..."` then `set` per screen, then
   `compute`. Topics 12 (documentation) and 14 (support) are app-level: assess them once.

## Reading the SIP's app audits

[Twelve published RAAM audits (2023-2024)](https://data.public.lu/en/datasets/audits-complets-de-laccessibilite-numerique-2024-1/) had rates between 26 % and 66 %; nine were rated "faible". The cases found
in every app: roles missing on interactive components (5.1) and no heading semantics (7.1); then text and component
contrast (2.2, 2.3), missing names (5.1), text that does not scale (8.2), status messages (5.4), lists (7.2), field
labels (9.1 to 9.3), orientation (11.9), keyboard operability (5.2). The skill's `references/raam-mobile.md` has the
full table and real finding wording.

## Limits

The view hierarchy from `uiautomator dump` omits heading flags, `labelFor` relations, role descriptions and state
descriptions, and exposes little of web views. Contrast from a screenshot is an estimate. Nothing replaces the TalkBack
pass; the report must say which criteria it covered and which it did not.
