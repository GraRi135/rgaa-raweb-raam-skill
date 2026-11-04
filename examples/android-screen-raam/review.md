# Accessibility review — « Mäin Service » (Android), screen « Accueil » — RAAM 1.1

| | |
|---|---|
| Standard | RAAM 1.1 (Référentiel d'évaluation de l'accessibilité des applications mobiles, SIP Luxembourg, 24 February 2025) — levels A and AA, both mandatory |
| Application | « Mäin Service », package `lu.exemple.app`, activity `.MainActivity` |
| Scope of this review | One screen, « Accueil » (home). This is a screen review, not the audit of the application: no compliance rate (taux de conformité) is computed, because the rate is an application-level figure over the full sample of screens. |
| Evidence | `capture/accueil/window_dump.xml` (uiautomator view hierarchy, font scale 1.0), `capture/accueil/screen.png`, `capture/accueil/meta.json`; `capture/accueil-x2/window_dump.xml` and `meta.json` (font scale 2.0, no screenshot). Android 14 emulator, 1080 × 2340 px, density 420 dpi (1 dp = 2.625 px), portrait only. |
| Method | Desk analysis of the captured files with the `rgaa-raweb-audit` skill: `android_audit.py analyse` on both captures, `android_audit.py compare` between the two, `contrast.py`, criteria and methodology from the RAAM 1.1 data set. No device, no TalkBack, no external keyboard, no landscape capture: every criterion whose RAAM methodology starts with « Activate the screen reader » or « Connect an external keyboard » stays **not tested (NT)**. |
| Date / author | 4 November 2026 — automated static analysis, to be completed by a human pass on a device (see section 6). |

## 1. Summary

Seven RAAM 1.1 criteria are **non-compliant (non conforme)** on the home screen on the evidence of the view hierarchy alone, one more is probably non-compliant and needs a colour measurement on the device, and 63 could not be decided from the files (see section 7 for the per-criterion status and the grid `grille-raam-main-service.csv`).

| Criterion | Level | What fails on « Accueil » |
|---|---|---|
| **5.1** Compatibility with assistive technologies (name, role, state) | A | Menu button and the second card have no accessible name; the search icon, both cards and the « Petit » control expose no control role |
| **5.2** Keyboard and pointing-device operability | A | Search icon and « Envoyer » button are `focusable="false"`: unreachable with an external keyboard or switch access |
| **1.2** Alternative for informative graphics | A | Menu icon and the icon of the second card carry the whole meaning of their control and have no alternative |
| **9.1** Visible label on form fields | A | E-mail field and checkbox have no visible label |
| **9.2** Label accessible to assistive technologies | A | E-mail field and checkbox have no label at all; the switch loses its label at 200 % |
| **9.8** Expected data type / format | A | Nothing tells the user the field expects an e-mail address |
| **8.2** Text size increased by 200 % | AA | The welcome text is cut with an ellipsis and the switch label disappears at font scale 2.0; no element grows (fixed-size layout) |
| 2.2 Text contrast (probable, to confirm) | AA | « Petit »: the only colour evidence is #C8C8C8 on #FFFFFF, ratio 1.67:1 instead of 4.5:1 |

Who is affected: TalkBack users cannot identify the menu, the second card, the e-mail field or the checkbox and do not know that the cards are activatable; keyboard and switch-access users cannot reach the search or submit the form; users who enlarge text lose the welcome message and the meaning of the switch. These are the families of problems the SIP finds in almost every app it audits (roles and names: 12 of 12 apps; 200 % text: 10 of 12; labels and fields: 9 of 12), so expect the same remarks in the RAAM audit unless fixed.

## 2. What the files prove, and what they cannot

* **The view hierarchy is reliable evidence** for names, roles (class names), focusability, states and text content as exposed to accessibility services. `window_dump.xml` is what TalkBack, switch access and voice access read. A node with empty `text` and empty `content-desc` has no accessible name; `focusable="false"` on a clickable view means keyboard focus cannot land on it; the `class` attribute is the role TalkBack announces unless the app overrides it in code (a `roleDescription` or an accessibility delegate is invisible in the dump, which is why role findings are marked « to confirm »).
* **The 200 % capture is reliable** for text truncation and loss: the two dumps were compared node by node.
* **`screen.png` is not a rendering of the interface.** It is 98 % pure white; the toolbar, hero, cards, field, switch, checkbox, button and web view areas are 100 % white, and the only non-white pixels are two hatched rectangles exactly at the bounds of the texts « Bienvenue » (#141414 pattern) and « Petit » (#C8C8C8 pattern). It is a placeholder render, so nothing visual can be decided from it: contrast of the other texts, contrast of components, focus indicator, visual state of the switch and checkbox, colour-only information, actual visibility of labels. The 1.67:1 figure for « Petit » comes from the hatch colour, which is why it is reported as probable rather than certain.
* **No capture at font scale 2.0 screenshot, no landscape capture, no TalkBack or keyboard session**: see section 6.
* **The web view** (`lu.exemple.app:id/web`, bottom 490 px of the screen) exposes no children in the dump. Its content is under your responsibility and is evaluated like the rest of the screen; it is entirely untested here.

## 3. Non-conformities (non-conformités)

One block per criterion; element references are the nodes of `capture/accueil/window_dump.xml` with their pixel bounds.

### 5.1 [A] Is each user interface component, if necessary, compatible with assistive technologies?
- Tests: 5.1.1 (name, role, value, state exposed through the accessibility API) and 5.1.2 (relevant name, accessible name contains the visible text, relevant role, relevant state)
- Screen: Accueil
- Elements:
  - `ImageButton` `lu.exemple.app:id/menu` [20,100][150,230] — `text=""`, `content-desc=""`, flagged `NAF="true"` by uiautomator (« not accessibility friendly »).
  - `LinearLayout` `lu.exemple.app:id/card2` [560,940][1040,1240], `clickable="true"` — no text, no content-desc, its only child is `ImageView` `id/icon2` without content-desc.
  - `ImageView` `lu.exemple.app:id/search` [930,100][1060,230], `clickable="true"`, name « Rechercher » — class `android.widget.ImageView`.
  - `LinearLayout` `lu.exemple.app:id/card1` [40,940][520,1240], `clickable="true"`, name « Démarches » — class `android.widget.LinearLayout`.
  - `TextView` « Petit » [900,1720][940,1760], `clickable="true"` — class `android.widget.TextView`.
- Problem: the menu button and the second card have **no accessible name**: TalkBack announces « bouton » / « non libellé » and voice-control users have no word to say. The search icon, the two cards and « Petit » are activatable but expose **no control role** (ImageView, LinearLayout, TextView): TalkBack reads « Rechercher », « Démarches », « Petit » as plain images or text, so users do not know these elements can be activated. The role part is certain for the dump but can be overridden by a role description set in code; confirm with TalkBack (expected announcement: « Rechercher, bouton »). « Petit » is also a name that does not describe a function (5.1.2, relevance).
- Impact: blind and low-vision TalkBack users cannot identify the main menu or the second service card and do not discover the cards as navigation; voice-control users cannot target unnamed controls.
- Fix:
  ```xml
  <!-- menu -->
  <ImageButton android:id="@+id/menu" ... android:contentDescription="@string/a11y_open_menu" />   <!-- "Ouvrir le menu" -->
  <!-- search: a button, not an image -->
  <ImageButton android:id="@+id/search" ... android:contentDescription="@string/search" />           <!-- "Rechercher" -->
  <!-- card 2: name on the container, icon ignored -->
  <LinearLayout android:id="@+id/card2" android:clickable="true" android:focusable="true"
      android:contentDescription="@string/card2_title">                                            <!-- e.g. "Mes documents" -->
      <ImageView android:id="@+id/icon2" android:importantForAccessibility="no" ... />
  </LinearLayout>
  ```
  Give the clickable containers (card1, card2) and the « Petit » control a button role; the simplest is to make them real `Button` / `MaterialButton` / `MaterialCardView`, otherwise set the class name through a delegate:
  ```kotlin
  ViewCompat.setAccessibilityDelegate(card, object : AccessibilityDelegateCompat() {
      override fun onInitializeAccessibilityNodeInfo(host: View, info: AccessibilityNodeInfoCompat) {
          super.onInitializeAccessibilityNodeInfo(host, info)
          info.className = Button::class.java.name
      }
  })
  ```
  Jetpack Compose: `Modifier.clickable(role = Role.Button, onClickLabel = …)` or `Modifier.semantics { role = Role.Button; contentDescription = "…" }`. Rename « Petit » with its function (what does it do? the name must say it, e.g. « Réduire la taille du texte »).
- Priority: blocking

### 5.2 [A] Is every user interface component accessible and operable by keyboard and any pointing device?
- Test: criterion-level (reachable and activatable with the screen reader; reachable and activatable with an external keyboard)
- Screen: Accueil
- Elements:
  - `ImageView` `lu.exemple.app:id/search` [930,100][1060,230] — `clickable="true"`, **`focusable="false"`**.
  - `Button` `lu.exemple.app:id/send` « Envoyer » [40,1720][400,1800] — `clickable="true"`, **`focusable="false"`** (a `Button` is focusable by default: the app disables it explicitly).
- Problem: a view that is not focusable never receives keyboard focus, so it cannot be reached with an external keyboard (Tab) or with switch access, and it is skipped by TalkBack's linear navigation on some versions. The search cannot be opened and the form cannot be submitted without touch.
- Impact: keyboard users, switch-access users, people with motor impairments using an external device; the form on the home screen is unusable for them.
- Fix: remove `android:focusable="false"` (and any `isFocusable = false` in code) on `send`; turn `search` into an `ImageButton` (focusable by default) or add `android:focusable="true"`. In Compose, remove any `Modifier.focusProperties { canFocus = false }`. Then verify with a hardware keyboard on the emulator: Tab must reach menu → search → cards → field → switch → checkbox → « Envoyer » → « Petit » → web view.
- Priority: blocking

### 1.2 [A] Does each graphic element conveying information have an alternative accessible to assistive technologies?
- Test: criterion-level
- Screen: Accueil
- Elements: the icon of `ImageButton` `id/menu` (no `content-desc`); `ImageView` `lu.exemple.app:id/icon2` [700,980][900,1180] inside `card2` (no `content-desc`, and the card itself has no name).
- Problem: each icon is the only content of its control, so it conveys the information « menu » / « what this card leads to »; neither has an alternative, and no other element on the screen carries that information.
- Impact: TalkBack users get « bouton » and an unnamed card.
- Fix: same as 5.1 — `contentDescription` on the control (preferred) or on the icon; once the container is named, mark the icon `importantForAccessibility="no"` so it is not announced twice.
- Priority: blocking (same elements as 5.1; fixing 5.1 fixes this)

### 9.1 [A] Does each form field have a visible label?
- Test: criterion-level (adjacent visible label that remains visible while the field is being filled)
- Screen: Accueil
- Elements: `EditText` `lu.exemple.app:id/email` [40,1300][1040,1420]; `CheckBox` `lu.exemple.app:id/cb` [40,1600][120,1680] (`checked="true"`).
- Problem: the hierarchy contains no text element next to either field (nothing between the cards, which end at y = 1240, and the field at y = 1300; nothing to the right of the 30 × 30 dp checkbox), the `EditText` has no hint, and the `CheckBox` has no text. A sighted user sees an empty box and a ticked box without knowing what they are for. (The placeholder screenshot cannot confirm this visually, but a visible label would be a view and would be in the dump.)
- Impact: everyone, in particular users with cognitive impairments and low vision; the pre-ticked checkbox commits the user to something they cannot read.
- Fix:
  ```xml
  <com.google.android.material.textfield.TextInputLayout
      android:hint="@string/email_label">                        <!-- "Adresse e-mail (ex. : nom@exemple.lu)" : floating label stays visible -->
      <com.google.android.material.textfield.TextInputEditText android:id="@+id/email"
          android:inputType="textEmailAddress" android:autofillHints="emailAddress" />
  </com.google.android.material.textfield.TextInputLayout>

  <CheckBox android:id="@+id/cb" android:text="@string/consent_label"       <!-- the text IS the visible and accessible label -->
      android:layout_width="wrap_content" android:checked="false" />
  ```
  A bare `android:hint` on an `EditText` is not enough: it disappears when the user types, which fails the « label remains visible » step. If you keep a separate `TextView`, link it with `android:labelFor="@id/email"`.
- Priority: blocking

### 9.2 [A] Does each form field have a label that is accessible to assistive technologies?
- Test: criterion-level (a label is announced when the screen-reader focus lands on the field)
- Screen: Accueil
- Elements: `EditText` `id/email` (no text, no content-desc, no hint, no `labelFor` relation visible); `CheckBox` `id/cb` (no text, no content-desc); and at font scale 2.0 `Switch` `lu.exemple.app:id/sw` [40,1460][1040,1560], whose `text` is « Recevoir les alertes » at scale 1.0 and **empty** at scale 2.0.
- Problem: TalkBack announces « zone de texte modifiable » and « case à cocher, cochée » with no purpose. The switch is correctly labelled by its own text at 1.0 but has no name once the font scale is 2.0 (see 8.2).
- Impact: TalkBack and voice-control users cannot fill the form or know what they are consenting to.
- Fix: as in 9.1 (TextInputLayout hint or `labelFor`, text on the `CheckBox`), and keep the switch text present at every font scale (8.2 fix).
- Priority: blocking

### 9.8 [A] For each form field expecting a specific data type and/or format, is the related information available?
- Test: 9.8.1 — the expected type/format is visible and accessible to assistive technologies
- Screen: Accueil
- Element: `EditText` `lu.exemple.app:id/email` (the resource id shows it expects an e-mail address).
- Problem: no label, hint or helper text states that an e-mail address is expected, neither visibly nor through the accessibility API. (Deduced from the field's id; if the field expects free text, reclassify as NA.)
- Impact: all users; error-prone input for screen-reader users.
- Fix: put the type in the label (« Adresse e-mail ») and an example in a helper text (`app:helperText="Format : nom@exemple.lu"` on the TextInputLayout). While there, set `android:inputType="textEmailAddress"` and `android:autofillHints="emailAddress"` (criterion 9.12, personal data, not verifiable from the dump).
- Priority: major

### 8.2 [AA] On each screen, can the user increase the font size by at least 200 %?
- Test: 8.2.1 — all texts are enlarged by 200 % through the platform setting, remain legible and the components usable
- Screen: Accueil (comparison of `capture/accueil` and `capture/accueil-x2`)
- Elements:
  - Welcome `TextView` [40,800][1040,900]: text « Bienvenue » at scale 1.0, « Bienvenue dans votre espa… » at scale 2.0, **identical bounds** (100 px high) — the text is cut with an ellipsis (`maxLines="1"` / `ellipsize="end"` or a fixed height). Note that the full sentence is exposed in neither capture: check what the complete string is.
  - `Switch` `id/sw`: text « Recevoir les alertes » at 1.0, **no text at 2.0**, identical bounds — the label is dropped when it no longer fits.
  - Every node of the screen has exactly the same bounds at 1.0 and 2.0: no view grows with the font. With fixed sizes, the 15 × 15 dp « Petit » text and the 30 dp « Envoyer » button cannot display text twice as large without clipping.
- Problem: enlarged text is truncated (welcome message) or disappears (switch label), and no on-screen mechanism displays it on demand. The screen does not reflow: it is laid out in fixed `dp` heights.
- Impact: low-vision users who rely on the system font size (Android 14 allows 200 %) lose the welcome information and the meaning of the alerts switch, and probably see clipped text elsewhere.
- Fix: use `android:layout_height="wrap_content"` (with `minHeight` if a minimum is wanted) on every text container, remove `maxLines="1"` / `ellipsize="end"` on the welcome text and on the switch, never hide a label on overflow (let it wrap), keep text sizes in `sp`, and put the screen in a `ScrollView` so it can grow vertically. Do not use `autoSizeTextType` to shrink text back. In Compose avoid fixed `.height()` on text rows. Verify with `adb shell settings put system font_scale 2.0` and a new dump: every text of the 1.0 dump must still be present and un-ellipsised.
- Priority: major

## 4. Probable non-conformities (to confirm on the device)

### 2.2 [AA] Text contrast — « Petit »
- Test: 2.2.1 — ratio ≥ 4.5:1 for normal text, ≥ 3:1 for large text (≥ 24 px, or ≥ 18.5 px bold)
- Element: `TextView` « Petit » [900,1720][940,1760].
- Evidence: the only colour information in `screen.png` for this text is #C8C8C8 on a #FFFFFF background: ratio **1.67:1** (`contrast.py`), far below 4.5:1; at 15 dp the text is normal size. The welcome text, rendered #141414 on white (18.4:1), is fine. Because the screenshot is a placeholder, measure the real colours on the device with Colour Contrast Analyser or Accessibility Scanner (RAAM 2.2 Android methodology) before reporting it.
- Fix if confirmed: a text colour of at least #767676 on white (4.54:1), or your design token for secondary text, and the same check for every grey text in the app.

### 5.1 — roles of the clickable containers and 1.1 / 1.2 — hero image
- The missing roles of `search`, `card1`, `card2` and « Petit » (section 3) are certain in the dump but a `roleDescription` set in code would not show there: confirm with TalkBack.
- `ImageView` `lu.exemple.app:id/hero` [0,260][1080,760], no `content-desc`, not clickable: the files cannot tell whether it is decorative or carries a message. If decorative (1.1): it must not be reachable with TalkBack — set `android:importantForAccessibility="no"`. If it carries information or text (1.2 / 1.3): give it a `contentDescription` with that information; text embedded in a hero image also does not follow the 200 % setting (8.2). Swipe through the screen with TalkBack: if it stops on the image, decide and fix.

## 5. Recommendations outside the RAAM 1.1 criteria

* Touch target of « Petit »: 40 × 40 px = **15 × 15 dp**; the checkbox is 30 × 30 dp and « Envoyer » 30 dp high. RAAM 1.1 has no target-size criterion (WCAG 2.5.8 / 2.5.5 are not in EN 301 549 v3.2.1), but the SIP notes it and Android's guideline is 48 × 48 dp: use `minWidth`/`minHeight` 48 dp or a `TouchDelegate`.
* The checkbox is pre-ticked (`checked="true"`) without a readable label: if it is a consent, it should be unticked by default (not an accessibility criterion, but it will be noticed).
* Mark the screen's title and the welcome text as headings (`android:accessibilityHeading="true"`, `ViewCompat.setAccessibilityHeading(view, true)`, Compose `Modifier.semantics { heading() }`) so that TalkBack heading navigation works: this is criterion 7.1, untested here (the dump does not expose the heading flag) and failed by 12 of the 12 apps the SIP audited.
* If « Démarches » and the second card form a set of services, expose them as a list (7.2) with `RecyclerView` / `CollectionInfo`, or Compose `LazyColumn` with `collectionInfo` semantics.

## 6. What could not be checked from these files, and how to check it

| Criteria | Why not decidable from the captures | How to test (RAAM 1.1 methodology) |
|---|---|---|
| 5.1 (roles as announced, state announcements), 5.3 context changes, 5.4 status messages, 5.5 toggle states (switch, checkbox), 6.1 language, 7.1 headings, 7.2 lists, 8.1 hidden information, 10.2 reading order | Need the screen reader's rendering; the dump does not expose heading flags, role descriptions, live regions or language | TalkBack on the Android 14 emulator (Android Accessibility Suite from the Play image): swipe through every element and note each announcement; use the reading-controls menu « Headings »; activate each control; submit the form empty and note whether the error is announced (also 9.9, 9.10); set text-to-speech language detection to « Aggressive » for 6.1. The dump order (toolbar → hero → welcome → cards → field → switch → checkbox → Envoyer → Petit → web view) matches the visual order, which is a good sign for 10.2 but not a proof. |
| 5.2 (confirmation), 8.5 focus visibility, 10.1 navigation sequence, 10.3 keyboard traps, 10.4 single-key shortcuts | Need keyboard interaction and a real rendering | Hardware keyboard on the emulator: Tab through the screen, check the focus indicator is visible on each element, that nothing traps focus (the web view in particular) and that order is consistent |
| 2.1 colour-only information, 2.2 (all texts except the two rendered), 2.3 component contrast, 8.3, 8.4, 8.6 shape/size/position | `screen.png` is a placeholder: no real pixels | Real screenshot or screen mirroring, then Colour Contrast Analyser / Accessibility Scanner; check the switch and checkbox states are perceptible without colour |
| 8.2 visual confirmation | No screenshot in `accueil-x2/` | Capture a screenshot at font scale 2.0 and confirm that the clipped texts are not readable; `android_audit.py walk` does the 1.0 / 2.0 / landscape captures in one go |
| 11.9 orientation | No landscape capture | `android_audit.py rotate landscape` then capture; the content must stay available and the layout must adapt (a screen locked in portrait is NC unless essential) |
| 9.3, 9.4 label relevance and adjacency, 9.6 field grouping, 9.7 mandatory fields, 9.9 / 9.10 errors, 9.11 data modification, 9.12 personal-data input (inputType, autofill) | Only the switch has a label; the dump does not expose `inputType` or autofill hints; errors appear only after submission | TalkBack pass on the form after the labels are added; submit with an empty or invalid e-mail; check `inputType="textEmailAddress"` and `autofillHints` in the layout |
| 11.1, 11.2 time limits, 11.7 flashes, 11.8 moving content, 11.10 / 11.11 gestures, 11.12 pointer cancellation, 11.13 motion, 11.15 biometrics, 11.16 key repeat | Dynamic behaviour, not in a static dump | Use the screen: any carousel, auto-refresh, swipe-only action, shake gesture, biometric login elsewhere in the app |
| 6.2 layout-only elements | Needs the source or the rendering | Review the layout: no semantic element used only for spacing |
| Web view `id/web` | Its DOM is not in the dump | Give the URL or HTML it loads: `scan_html.py` and a TalkBack pass; the web content is in scope of the audit unless it is third-party content |
| Topics 12 (documentation, accessibility features, non-interference with platform features) and 14 (support services) | Application-level, not on this screen | Check that the app documentation / « À propos » describes the accessibility features, that the support channels are accessible, and that the app has an accessibility statement (déclaration d'accessibilité), which the SIP checks in every audit (law of 28 May 2019; generator on accessibilite.public.lu) |
| Topics 3, 4, 13, 15; 1.4, 1.5; 11.3 to 11.6; 11.14 | No media, table, captcha, document, cryptic content, editing tool or real-time communication on this screen | Marked NA for « Accueil », subject to the web view content and to the other screens of the sample |

## 7. Status of the 108 criteria for « Accueil » (provisional)

`grille-raam-main-service.csv` holds the column (statuses C / NC / NA / NT); it is the starting point of the application grid: add the other screens with `audit_grid.py new … --pages "Accueil=,Connexion=,Contact=,…"` and fill them after the device pass. Counts for this screen: **7 NC** (1.2, 5.1, 5.2, 8.2, 9.1, 9.2, 9.8), **2 C** (1.3 — the search icon's alternative « Rechercher » is relevant; 9.5 — the submit button's visible text « Envoyer » is its accessible name and relevant for the only form on the screen), **36 NA**, **63 NT** (including 2.2, probable NC). Because of the NT cells, no rate is computed; a rate from this screen alone would be meaningless anyway.

Next steps for the RAAM audit: build the sample the SIP expects (home, legal notices, privacy policy, authentication, contact, settings, documentation / about, accessibility statement, one screen per service type, every step of each process, plus 10 % random screens; 6 to 10 screens in practice), capture each with `android_audit.py walk`, do the TalkBack and keyboard passes, fill the grid, compute the rate with `audit_grid.py compute`, and write the report in the SIP outline (« écrans » and « parcours », rate at level A and at level AA, « Constats dans l'application »).

## Annex — element inventory from `window_dump.xml` (font scale 1.0 → 2.0)

| Node (resource-id) | Class | Accessible name 1.0 → 2.0 | clickable / focusable | Bounds (px) | Findings |
|---|---|---|---|---|---|
| `id/toolbar` | ViewGroup | — | no / no | [0,80][1080,250] | container |
| `id/menu` | ImageButton | **none** (NAF) → none | yes / yes | [20,100][150,230] (49 dp) | 5.1, 1.2 |
| (title) | TextView | « Mäin Service » | no / no | [180,120][700,210] | heading? 7.1 NT |
| `id/search` | ImageView | « Rechercher » (content-desc) | yes / **no** | [930,100][1060,230] (49 dp) | 5.2; 5.1 role |
| `id/hero` | ImageView | none | no / no | [0,260][1080,760] | 1.1 / 1.2 to decide |
| (welcome) | TextView | « Bienvenue » → « Bienvenue dans votre espa… » | no / no | [40,800][1040,900], unchanged | 8.2 |
| `id/card1` | LinearLayout | « Démarches » | yes / yes | [40,940][520,1240] | 5.1 role |
| `id/card2` | LinearLayout | **none** | yes / yes | [560,940][1040,1240] | 5.1 name + role, 1.2 |
| `id/icon2` (in card2) | ImageView | none | no / no | [700,980][900,1180] | 1.2 |
| `id/email` | EditText | **none** (no hint) | yes / yes | [40,1300][1040,1420] | 9.1, 9.2, 9.8 |
| `id/sw` | Switch, unchecked | « Recevoir les alertes » → **none** | yes / yes | [40,1460][1040,1560], unchanged | 8.2; 9.2 at 200 % |
| `id/cb` | CheckBox, checked | **none** | yes / yes | [40,1600][120,1680] (30 dp) | 9.1, 9.2 |
| `id/send` | Button | « Envoyer » | yes / **no** | [40,1720][400,1800] (137 × 30 dp) | 5.2 |
| (Petit) | TextView | « Petit » | yes / yes | [900,1720][940,1760] (15 dp) | 5.1 role and name; 2.2; target size |
| `id/web` | WebView | — (no children exposed) | no / yes | [0,1850][1080,2340] | content not captured |

Tooling used: `android_audit.py analyse` (both captures), `android_audit.py compare`, `contrast.py`, `criteria.py show … --standard raam --methodology`, `audit_grid.py new/set` from the `rgaa-raweb-audit` skill; `screen.png` decoded and sampled region by region to establish that it is a placeholder.
