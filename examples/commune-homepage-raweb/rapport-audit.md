# Rapport d'audit d'accessibilité — Site de la Commune de Fiktivbuerg — page d'accueil — RAWeb 1.1

**Accessibility audit report, RAWeb 1.1 (référentiel d'évaluation de l'accessibilité web), version 1.1**

| | |
|---|---|
| Standard | RAWeb 1.1, published by the Service information et presse (SIP) on 6 February 2026: 17 topics, 136 criteria, 304 tests. Transcription of WCAG 2.1 (levels A and AA) and of EN 301 549 v3.2.1 for web content. Criteria 1.1 to 13.12 are shared with RGAA 4.1.2; criteria 4.14-4.18, 13.13, 13.14 and topics 14 to 17 exist only in RAWeb 1.1. Official text: https://accessibilite.public.lu/en/raweb1.1/criteres.html |
| Legal basis | Law of 28 May 2019 on the accessibility of the websites and mobile applications of public sector bodies |
| Audited content | `index.html` of the home page (page d'accueil), HTML as served by the server, supplied by the commune on 4 November 2026. One page only. Site URL: [to be filled in by the commune] |
| Audit date | 4 November 2026 |
| Auditor | Static code audit produced with the assistance of an AI auditing tool (RAWeb 1.1 criteria data, static scanner `scan_html.py`, contrast calculator) for the Commune de Fiktivbuerg. No browser rendering, no keyboard test, no assistive technology was used: see section 2.3 for the consequences. |
| Status of this document | Partial audit (one page, static). It identifies non-conformities and the fixes; it does **not** establish the compliance status or the compliance rate of the site (see section 1.1). |

---

## 1. Synthèse — Summary

### 1.1 Scope of the result: no compliance rate from this document

**Portée : une page, audit statique. Aucun taux de conformité ne peut être établi sans audit de l'échantillon complet.**

The compliance rate (taux de conformité) and the compliance status (état de conformité : totalement / partiellement / non conforme) published in an accessibility statement are **site-level** figures computed over the mandatory sample of pages (home, contact, legal notice, accessibility page, site map, help, one page per service, downloadable documents, complete processes, etc., see section 7) and after tests with the assistive technologies of the RAWeb baseline. This document covers one page and only what can be proved from its source code. Any percentage derived from it (the grid script prints a provisional figure in `grille-raweb-accueil-compute.md`) is indicative only and must not be published as the compliance rate.

What this audit does establish is a list of **35 criteria non-compliant on the home page, each proven by an element of the delivered HTML**, with the RAWeb 1.1 criterion and test numbers and a fix for each. A non-conformity on one page of the sample makes the criterion non-compliant for the whole site, so every item below will remain in the final audit until it is fixed.

### 1.2 Counts for the home page (136 RAWeb 1.1 criteria)

| Status | Count | Meaning |
|---|---|---|
| Non conforme (NC) | **35** | proven in the code, listed in section 3 |
| Conforme (C) | 9 | 1.2, 5.8, 6.1, 8.1, 8.5, 8.9, 11.2, 11.4, 13.11 (what the code shows passes; 6.1 carries recommendations) |
| Non applicable (NA) | 53 | content absent from the page (CAPTCHA, complex tables, quotations, real-time communication, editing tools...) |
| Non testé (NT) | 39 | needs a browser, a keyboard, a screen reader, the other pages of the site or the media content: listed in section 5 with the test to perform |

### 1.3 The most blocking non-conformities (auditor's judgement)

1. **Forms unusable with a screen reader or voice control** — search field, name, e-mail and frequency fields have no label (11.1); the two submit buttons have no name (11.9); the radio buttons are not grouped (11.5) and the checkbox group has no legend (11.6).
2. **Keyboard users are blocked or lost** — the "Toutes les démarches" button is a `<div onclick>` that cannot receive focus (7.1, 7.3); the focus outline is removed on every link and button (10.7); the footer carries `tabindex="3"` and is reached first (12.8); there is no skip link (12.7).
3. **No page structure for assistive technologies** — no `<html lang>` (8.3), no `main` / `banner` / `navigation` / `search` / `contentinfo` regions (9.2), visual headings that are not headings (9.1), list items outside any list (9.3).
4. **Content that moves, refreshes or plays on its own** — the page reloads every 5 minutes (13.1), a `<marquee>` scrolls the closure notice (13.8), a video autoplays in a loop with sound and without controls (4.10, 4.11, 13.8).
5. **Images and frames without usable alternatives** — logo and Facebook links have no accessible name (1.1, 6.2), the hero image's alt is a file name and the news images are labelled "image" (1.3), the search icon is an unnamed `<svg>` (1.1), the YouTube frame has no title (2.1).
6. **Zoom disabled on mobile** — `user-scalable=no, maximum-scale=1` (10.4).
7. **Changing the newsletter frequency submits the form** without warning (7.4).
8. **Opening-hours table without headers or caption** (5.4, 5.6); news laid out in a table without `role="presentation"` (5.3).

Most of these are template-level defects: fixing the page template (section 6) will fix them on every page of the site at once.

---

## 2. Périmètre et méthode — Scope and method

### 2.1 Standard

RAWeb 1.1 was chosen because the commune is a Luxembourg public sector body under the law of 28 May 2019. All criterion and test numbers below are RAWeb 1.1 numbers, checked against the official data (`criteria.py show <id> --tests`). They are identical to RGAA 4.1.2 for criteria 1.1-13.12 except where RAWeb changed the tests (notably 5.3, 6.1, 8.1, 9.2, 13.5): the RAWeb wording was used in every case.

### 2.2 Sample

One page: the home page, from the file `index.html` supplied by the commune (the HTML as served; no external script, one embedded stylesheet). No URL was supplied; the finding locations are given as line numbers of that file.

### 2.3 Test environment and limits

* Static analysis of the delivered HTML and of its embedded CSS. Tools: RAWeb 1.1 static pre-check (`scan_html.py`, output kept in `scan-accueil-raweb.md` / `.json`), contrast calculator (`contrast.py`) on the colour pairs declared in the stylesheet, RAWeb 1.1 criteria and glossary data.
* **Not done**: rendering in a browser, keyboard navigation, screen-reader tests (NVDA, JAWS, VoiceOver), mobile tests (TalkBack, VoiceOver iOS), zoom and reflow tests, measurement of rendered contrast on images, inspection of the linked PDF and of the two videos' content. The RAWeb baseline requires components to work with **all** of NVDA + Firefox/Chrome/Edge, JAWS (previous version) + Firefox/Chrome/Edge and VoiceOver + Safari; these tests remain to be done by the agency or an auditor (section 5).
* Consequence: criteria that depend on those tests are marked **NT (non testé)**, never C. A criterion with no finding is not compliant by default.

### 2.4 Status rules applied (RAWeb test methodology)

* A criterion is **C** on the page only if every element concerned passes every test of the criterion; one failing element makes it **NC**.
* **NA** only when the content does not exist on the page, is exempt, or is derogated with an accessible alternative.
* Levels A and AA are both mandatory; neither the rate nor the status weighs them.
* Priorities (bloquant / majeur / mineur) are the auditor's judgement, not part of the standard.

---

## 3. Non-conformités constatées dans le code — Non-conformities proven in the code

One block per criterion. "Element" quotes the delivered HTML with its line number in `index.html`. "Fix" is code the agency can paste. The French status term for every block is **non conforme**.

### Topic 1 — Images

### 1.1 [A] Does each image conveying information have a text alternative?
- Tests: 1.1.1 — `<img>` conveying information has a text alternative; 1.1.5 — `<svg>` conveying information has `role="img"` and a text alternative
- Pages: home (header and footer: expected on every page)
- Elements:
  - line 23: `<a href="/"><img src="/img/logo-commune.png" width="120"></a>` — no `alt` at all; the image is the only content of the link to the home page.
  - line 36: `<button type="submit"><svg width="16" height="16" viewBox="0 0 16 16">…</svg></button>` — the magnifier icon is the only content of the search button; the `<svg>` has neither `role="img"` nor a `<title>`/`aria-label`, nor `aria-hidden="true"`.
  - line 92: `<button type="submit"><img src="/img/send.svg" alt=""></button>` — the send icon is the only content of the newsletter button and is declared decorative (`alt=""`), so the button's function is conveyed by nothing.
  - line 100: `<a href="https://facebook.example/fiktivbuerg"><img src="/img/facebook.png" alt=""></a>` — the Facebook logo is the only content of the link and is declared decorative.
- Problem: an image that is the sole content of a link or button conveys that link's or button's function; declaring it decorative (`alt=""`) or omitting `alt` leaves no alternative (1.1.1). The `<svg>` has no name and is not hidden (1.1.5). Same elements fail 6.2 and 11.9 below.
- Impact: screen-reader users hear "link" / "button" with no name or the file name `logo-commune.png`; voice-control users cannot say the control's name.
- Fix:
  ```html
  <a href="/"><img src="/img/logo-commune.png" width="120" alt="Commune de Fiktivbuerg – Accueil"></a>
  <button type="submit"><svg aria-hidden="true" focusable="false" width="16" height="16" viewBox="0 0 16 16">…</svg><span class="vhide">Rechercher</span></button>
  <button type="submit"><img src="/img/send.svg" alt=""> S'abonner</button>   <!-- or alt="S'abonner" if the icon stays alone -->
  <a href="https://facebook.example/fiktivbuerg"><img src="/img/facebook.png" alt="Facebook"></a>
  ```
  (`.vhide` already exists in the stylesheet; keep `position:absolute; left:-9999px` and do not use `display:none`, which would hide the text from screen readers.)
- Priority: blocking

### 1.3 [A] For each image conveying information with a text alternative, is this alternative relevant?
- Test: 1.3.1 — the value of `alt` is relevant
- Pages: home
- Elements:
  - line 41: `<img src="/img/hero_banner_final_v2.jpg" alt="hero_banner_final_v2.jpg" width="1200" height="400">` — the alternative is the file name.
  - line 49: `<img src="/img/actu-1.jpg" alt="image">` and line 50: `<img src="/img/actu-2.jpg" alt="image">` — generic word.
- Problem: a file name or the word "image" describes nothing (1.3.1). Note for the agency: if these images are decorative (pure illustration next to a title), the correct markup is `alt=""`, and the current non-empty alt fails 1.2.1 instead; either way the current code is non-compliant.
- Impact: screen-reader users hear "hero underscore banner underscore final underscore v2 dot jpg" at the top of every visit.
- Fix: decide per image. Decorative banner or thumbnail: `alt=""`. Informative (text or a scene that matters): a short description, e.g. `alt="Vue de l'hôtel de ville de Fiktivbuerg"`; `alt="Enfants jouant dans le nouveau parc de jeux"`. Also ask the editors' CMS to stop defaulting the alt to the file name (RAWeb 15.1 on editing tools, if the CMS is in scope).
- Priority: major

### Topic 2 — Frames

### 2.1 [A] Does each frame have a frame title?
- Test: 2.1.1 — each `<iframe>` has a `title` attribute
- Pages: home
- Element: line 64: `<iframe src="https://www.youtube.com/embed/abc123" width="560" height="315" allowfullscreen></iframe>`
- Problem: no `title` attribute.
- Impact: screen-reader users land in an unnamed frame containing the whole YouTube player.
- Fix: `<iframe src="https://www.youtube.com/embed/abc123" title="Vidéo de présentation de la commune de Fiktivbuerg (lecteur YouTube)" width="560" height="315" allowfullscreen></iframe>`
- Priority: major

### Topic 4 — Multimedia

### 4.7 [A] Is each time-based media clearly identifiable?
- Test: 4.7.1 — the adjacent text content clearly identifies the media
- Pages: home
- Element: line 65: `<video src="/media/jingle.mp4" autoplay loop width="320"></video>`
- Problem: no heading, paragraph or caption immediately before or after the `<video>` says what it is; the text "Vidéo de présentation" (line 63) precedes the YouTube frame, not this video.
- Impact: screen-reader and cognitively impaired users encounter an unidentified media object.
- Fix: add an identifying text, e.g. `<p id="jingle-titre">Jingle de la commune (vidéo, 20 s)</p>` before the `<video>` and `aria-labelledby="jingle-titre"` on it; or remove the video if it is purely decorative.
- Priority: minor

### 4.10 [A] Is each automatically triggered sound controllable by the user?
- Test: 4.10.1 — a sound started automatically lasts 3 s or less, or can be stopped, or has its own volume control
- Pages: home
- Element: line 65: `<video src="/media/jingle.mp4" autoplay loop width="320"></video>`
- Problem: the video starts automatically and loops indefinitely, has no `controls` attribute and no `muted` attribute, so its soundtrack (a jingle, by definition sound) cannot be stopped or turned down on the page. This is one of the non-interference criteria that apply even to exempt content.
- Impact: screen-reader users cannot hear their synthesiser over the sound; the only escape is to leave the page or mute the system.
- Fix: remove `autoplay` and add `controls`: `<video src="/media/jingle.mp4" controls width="320" aria-labelledby="jingle-titre"></video>`. If the video must start on its own, it must be silent: `autoplay muted loop playsinline controls`. If the file is in fact silent, add `muted` anyway so the fact is explicit.
- Priority: blocking

### 4.11 [A] Is the viewing of each time-based media accessible and operable by keyboard and any pointing device?
- Test: 4.11.1 — each time-based media has, if necessary, viewing control features
- Pages: home
- Element: line 65, same `<video>`
- Problem: there is no play/pause/stop/volume feature at all (no `controls`, no custom player), for a media that plays in a loop.
- Impact: nobody, keyboard or mouse, can pause it.
- Fix: same as 4.10: `controls` (the native controls are keyboard operable in all baseline browsers).
- Priority: major

### Topic 5 — Tables

### 5.3 [A] For each layout table, is the linearised content still comprehensible?
- Test: 5.3.1 — the linearised content remains understandable **and** the `<table>` has `role="presentation"`
- Pages: home
- Element: lines 47-52: `<table bgcolor="#eeeeee" cellpadding="6"><tr><td><img …> <b>Nouveau parc de jeux</b><br>…</td><td>…</td></tr></table>` (the two news items side by side)
- Problem: this table carries no data relationship: it is a layout table. RAWeb 5.3.1 requires `role="presentation"` on every layout table; it is absent, so screen readers announce a one-row, two-column table.
- Impact: screen-reader users get table navigation and "row 1, column 1" announcements around the news.
- Fix (preferred, also fixes 10.1 and the news headings): replace the table by a list of articles laid out with CSS:
  ```html
  <ul class="actus">
    <li><article><img src="/img/actu-1.jpg" alt=""><h3>Nouveau parc de jeux</h3><p>Le nouveau parc de jeux du quartier Nord est ouvert. <a href="/actualites/parc-de-jeux">En savoir plus<span class="vhide"> sur le nouveau parc de jeux</span></a></p></article></li>
    <li><article>…</article></li>
  </ul>
  ```
  Minimal fix: `<table role="presentation">` and move the colours to CSS.
- Priority: minor

### 5.4 [A] For each data table with a title, is the title correctly associated with the data table?
- Test: 5.4.1 — the title is provided by `<caption>`, `title`, `aria-label` or `aria-labelledby`
- Pages: home
- Element: line 55-56: `<p class="titre">Horaires d'ouverture</p><table id="horaires">`
- Problem: "Horaires d'ouverture" is the visible title of the data table but is not associated with it by any of the four accepted techniques.
- Impact: when a screen-reader user lists or jumps to tables, this one has no name.
- Fix: see 5.6 (the `<caption>` carries the title).
- Priority: minor

### 5.6 [A] For each data table, are each column header and each row header correctly declared?
- Tests: 5.6.1 — column headers use `<th>` (or `role="columnheader"`); 5.6.2 — row headers use `<th>` (or `role="rowheader"`)
- Pages: home
- Element: lines 56-60: `<table id="horaires"><tr><td>Jour</td><td>Matin</td><td>Après-midi</td></tr><tr><td>Lundi - Vendredi</td>…`
- Problem: "Jour / Matin / Après-midi" are column headers and "Lundi - Vendredi" / "Samedi" are row headers, all coded as `<td>`.
- Impact: in a cell, a screen-reader user hears "13h00 - 17h00" without knowing it is Monday-Friday afternoon.
- Fix (also fixes 5.4, and makes 5.7 applicable and compliant through `scope`):
  ```html
  <h2>Horaires d'ouverture</h2>
  <table id="horaires">
    <caption>Horaires d'ouverture de la mairie</caption>
    <thead><tr><th scope="col">Jour</th><th scope="col">Matin</th><th scope="col">Après-midi</th></tr></thead>
    <tbody>
      <tr><th scope="row">Lundi - Vendredi</th><td>8h00 - 12h00</td><td>13h00 - 17h00</td></tr>
      <tr><th scope="row">Samedi</th><td>9h00 - 11h30</td><td>Fermé</td></tr>
    </tbody>
  </table>
  ```
- Priority: major

### Topic 6 — Links

### 6.2 [A] On each web page, does each link have an accessible name?
- Test: 6.2.1 — each link has an accessible name
- Pages: home (header and footer: expected on every page)
- Elements: line 23: `<a href="/"><img src="/img/logo-commune.png" width="120"></a>`; line 100: `<a href="https://facebook.example/fiktivbuerg"><img src="/img/facebook.png" alt=""></a>`
- Problem: the accessible name of a link is computed from `aria-labelledby`, `aria-label`, its content, then `title`; these two links have none of them (image without alt / with empty alt, no title). The flag link on line 31 is **not** concerned: its `title="English version"` gives it a name.
- Impact: screen readers announce "link, logo-commune.png" and "link" (or read the URL); voice control cannot target them.
- Fix: the `alt` values given under 1.1.
- Priority: blocking

### Topic 7 — Scripts

### 7.1 [A] Is each script, if necessary, compatible with assistive technologies?
- Tests: 7.1.1 — name, role, value and states of a scripted component are exposed to assistive technologies (or an accessible equivalent exists); 7.1.3 — the component has a relevant name and a relevant role
- Pages: home
- Element: line 72: `<div class="btn" onclick="location.href='/demarches/'">Toutes les démarches</div>`
- Problem: a generic `<div>` is turned into a control by an `onclick` handler. It has no role (not exposed as a button or a link), hence no accessible name as a control (7.1.3 fails whatever the outcome of 7.1.1). Even if the agency invokes the "Démarches" menu link as the accessible equivalent allowed by 7.1.1, test 7.1.3 still requires the component itself to have a relevant role.
- Impact: screen-reader users hear plain text "Toutes les démarches" and do not know it is clickable; it is absent from their list of links/buttons.
- Fix: it navigates, so it is a link: `<a class="btn" href="/demarches/">Toutes les démarches</a>` (keep the `.btn` style; a native `<a>` has the right role, name and keyboard behaviour without any script).
- Priority: major

### 7.3 [A] Is each script accessible and operable by keyboard and any pointing device?
- Test: 7.3.1 — each element with a script event handler is accessible and operable by keyboard and any pointing device, or an element accessible by keyboard performing the same action is present on the page
- Pages: home
- Element: line 72, same `<div class="btn" onclick…>`
- Problem: the element has no `tabindex`, is not a native control, so it cannot receive keyboard focus nor be activated with Enter/Space. Recorded NC. Note on the second condition of 7.3.1: the agency may argue that the "Démarches" link of the main menu (line 28, same URL `/demarches/`) is the keyboard-accessible equivalent; if the auditor of the final audit accepts that reading, 7.3 can be passed for this element, but 7.1 above stays non-compliant and sighted keyboard users would still see a primary button they cannot reach. The fix is the same one-line change.
- Impact: keyboard-only users, switch users and screen-reader users cannot activate the main call to action of the section.
- Fix: `<a class="btn" href="/demarches/">Toutes les démarches</a>`. Never reproduce the `div onclick` pattern elsewhere (CMS templates, cookie banner, menus).
- Priority: major

### 7.4 [A] For each script that initiates a change of context, is the user warned or does the user have control?
- Test: 7.4.1 — a change of context is announced beforehand, or triggered by an explicit button or link
- Pages: home
- Element: line 88: `<select name="frequence" onchange="this.form.submit()" aria-labelledby="freq-label">`
- Problem: choosing a frequency submits the whole newsletter form immediately (change of context: new page), without warning and without an explicit button. With a keyboard, the first arrow-key press in the list (which changes the value in most browsers) submits the form before the user has reached the intended option.
- Impact: keyboard and screen-reader users submit an incomplete form by accident.
- Fix: remove the `onchange`; the existing submit button (made explicit under 11.9) submits the form: `<select name="frequence" id="frequence">`.
- Priority: major

### Topic 8 — Mandatory elements

### 8.2 [A] For each web page, is the generated source code valid for the specified document type?
- Test: 8.2.1 — the generated source code is valid for the declared doctype (HTML5)
- Pages: home
- Elements:
  - duplicate `id="nom"` on line 77 (`<input type="text" name="nom" id="nom" …>`) and line 79 (`<input type="date" name="naissance" id="nom" …>`); an id must be unique, and the duplicate breaks any `<label for="nom">` or ARIA reference that will be added to fix 11.1.
  - `<li>` elements whose parent is a `<div>` (lines 68-70): `<li>` is only valid inside `<ul>`, `<ol>` or `<menu>`.
  - obsolete elements `<marquee>` (line 46), `<font>` and `<center>` (line 95); obsolete attributes `bgcolor`, `cellpadding` (line 47), `color` on `<font>` (line 95).
- Problem: these are errors reported by the W3C Nu HTML checker on the generated code; the duplicate id and the orphan `<li>` are of the kind that changes what assistive technologies receive (label association, list semantics).
- Impact: see 9.3 and 11.1; the duplicate id makes a correct label association impossible for the date field.
- Fix: `id="naissance"` on the date field; the list and presentation fixes of 9.3 and 10.1; then validate the page at https://validator.w3.org/nu/ and keep the report.
- Priority: major

### 8.3 [A] On each web page, is the default language present?
- Test: 8.3.1 — the `<html>` tag has a `lang` (or `xml:lang`) attribute
- Pages: home (template: every page)
- Element: line 2: `<html>`
- Problem: no default language declared.
- Impact: screen readers may read the French page with an English or German voice (pronunciation unintelligible); browser translation and hyphenation also misbehave.
- Fix: `<html lang="fr">` (and `lang="en"` on the pages of `/en/`, `lang="de"`, `lang="lb"` on their language versions).
- Priority: blocking

### 8.6 [A] For each web page with a page title, is this title relevant?
- Test: 8.6.1 — the content of `<title>` is relevant: it lets the page be found in the browsing history or the list of tabs
- Pages: home (and probably every page, if the template only prints the page name)
- Element: line 7: `<title>Accueil</title>`
- Problem: "Accueil" does not identify the site; every commune's home page would have the same title, so the page cannot be told apart in tabs, history or bookmarks (RAWeb glossary: the title must identify the page "clearly, concisely and uniquely", e.g. "Site map www.sitename.org").
- Impact: screen-reader users (the title is the first thing read on load), users with many tabs, users of history/bookmarks.
- Fix: `<title>Accueil – Commune de Fiktivbuerg</title>`; template rule: `<title>{page name} – Commune de Fiktivbuerg</title>`.
- Priority: minor

### 8.7 [AA] On each web page, is each language change indicated in the source code?
- Test: 8.7.1 — each passage of text in another language carries a `lang` attribute (itself or a parent)
- Pages: home
- Elements:
  - line 82: `<label for="lang-de">Deutsch</label>` — German word, no `lang`.
  - line 31: `<a href="/en/" title="English version">` — English text in a `title` attribute; the RAWeb glossary says a language change in an attribute value is indicated by a `lang` attribute on the element carrying it.
  - (line 83: "Lëtzebuergesch" does carry a `lang`, but an invalid one: see 8.8.)
- Problem: no language indication on these foreign-language passages; "Deutsch" is neither a proper noun nor a word of French usage. ("Newsletter", in common French usage, is not concerned.)
- Impact: a French speech synthesiser mispronounces "Deutsch" and "English version".
- Fix:
  ```html
  <a href="/en/" lang="en" hreflang="en"><img src="/img/flag-en.svg" alt=""> English</a>
  <input type="radio" name="langue" id="lang-de" value="de"> <label for="lang-de" lang="de">Deutsch</label>
  ```
- Priority: minor

### 8.8 [AA] On each web page, is the language code for each language change valid and relevant?
- Test: 8.8.1 — the language code is valid and relevant
- Pages: home
- Element: line 83: `<span lang="letzebuergesch">Lëtzebuergesch</span>`
- Problem: `letzebuergesch` is not a valid BCP 47 language tag; the ISO 639-1 code for Luxembourgish is `lb`. An invalid code is ignored by assistive technologies.
- Impact: as 8.7.
- Fix: `<label for="lang-lb" lang="lb">Lëtzebuergesch</label>`
- Priority: minor

### Topic 9 — Information structure

### 9.1 [A] On each web page, is the information structured by the appropriate use of headings?
- Tests: 9.1.1 — the hierarchy between headings is relevant; 9.1.3 — each passage of text acting as a heading uses `<hx>` or `role="heading"` + `aria-level`
- Pages: home
- Elements:
  - line 55: `<p class="titre">Horaires d'ouverture</p>` and line 63: `<div class="titre">Vidéo de présentation</div>` — section titles styled as headings (`.titre { font-size: 1.6em; font-weight: bold }`) without heading markup (9.1.3).
  - lines 49-50: `<b>Nouveau parc de jeux</b>`, `<b>Collecte des déchets</b>` — titles of the news items, bold text only (9.1.3).
  - line 45: `<h3>Actualités</h3>` while the sections of the same level, "Démarches en ligne" and "Newsletter", are `<h2>` (lines 67, 74) (9.1.1). Note: the RAWeb glossary states that a level jump alone (h1 then h3) does not invalidate the criterion as long as the hierarchy stays consistent; here it is not consistent, because sibling sections have different levels and two of them have no heading at all.
- Problem: the heading outline exposed to assistive technologies is "Bienvenue à Fiktivbuerg / Actualités (level 3) / Démarches en ligne / Newsletter"; the opening hours and the video section are invisible in it.
- Impact: screen-reader users navigate by headings (H key / rotor): they cannot jump to the opening hours; the structure announced does not match the visual one.
- Fix: `<h2>Actualités</h2>`, `<h2>Horaires d'ouverture</h2>`, `<h2>Vidéo de présentation</h2>`, `<h2>Démarches en ligne</h2>`, `<h2>Newsletter</h2>`; `<h3>` for each news title inside the list proposed under 5.3. Keep the `.titre` style but apply it to `h2`.
- Priority: major

### 9.2 [A] On each web page, is the document structure consistent?
- Test: 9.2.1 — the header region has the computed role `banner`, the navigation regions `navigation`, the search region `search`, the main content region `main`, the footer `contentinfo`
- Pages: home (template: every page)
- Elements: line 22: `<div class="topbar">` (header: logo, menu, search); line 25: `<ul class="menu">` (main navigation, not inside `<nav>`); line 34: `<form action="/recherche">` (search, no `role="search"` / `<search>`); line 40: `<div id="contenu">` (main content, no `<main>`); line 98: `<div class="footer" tabindex="3">` (footer, no `<footer>`). The scanner inventory confirms 0 `main`, 0 `banner`, 0 `navigation`, 0 `contentinfo` landmarks.
- Problem: none of the five regions required by 9.2.1 has the expected computed role.
- Impact: screen-reader users cannot jump to the main content, the navigation or the footer with landmark navigation (D key / rotor), and must read through the header on every page.
- Fix (template):
  ```html
  <body>
    <a class="skip" href="#contenu">Aller au contenu</a>
    <header class="topbar">
      <a href="/"><img src="/img/logo-commune.png" width="120" alt="Commune de Fiktivbuerg – Accueil"></a>
      <nav aria-label="Menu principal"><ul class="menu">…</ul></nav>
      <form role="search" action="/recherche" method="get">…</form>   <!-- or <search><form …></search> -->
    </header>
    <main id="contenu" tabindex="-1">…</main>
    <footer class="footer">…</footer>
  </body>
  ```
  (`<header>` and `<footer>` get the `banner` / `contentinfo` roles only when they are direct children of `<body>`, not nested in `<main>`, `<nav>`, `<section>` or `<article>`: tests 9.2.3 and 9.2.4.)
- Priority: major

### 9.3 [A] On each web page, is each list correctly structured?
- Test: 9.3.1 — information grouped as an unordered list uses `<ul>`/`<li>` (or `role="list"`/`role="listitem"`)
- Pages: home
- Element: lines 68-70: `<li><a href="/demarches/certificat-residence">Certificat de résidence</a></li>` (three `<li>` directly inside `<div id="contenu">`, no `<ul>`)
- Problem: list items outside any list element; browsers render them as a list, but the list semantics (number of items, position) are not reliably exposed, and the markup is invalid (8.2).
- Impact: screen-reader users do not get "list of 3 items"; navigation by list (L key) does not find it.
- Fix:
  ```html
  <ul>
    <li><a href="/demarches/certificat-residence">Certificat de résidence</a></li>
    <li><a href="/demarches/declaration-arrivee">Déclaration d'arrivée</a></li>
    <li><a href="/demarches/reservation-salle">Réservation de salle</a></li>
  </ul>
  ```
- Priority: minor

### Topic 10 — Presentation of information

### 10.1 [A] In the website, are style sheets used to control the presentation of information?
- Tests: 10.1.1 — no presentational tag in the generated code; 10.1.2 — no presentational attribute in the generated code
- Pages: home
- Elements (the RAWeb glossary "Presentation of information" lists the prohibited tags and attributes):
  - line 46: `<marquee>` (10.1.1)
  - line 95: `<font color="#555">` and `<center>` (10.1.1), `color` attribute (10.1.2)
  - line 47: `<table bgcolor="#eeeeee" cellpadding="6">` (10.1.2)
  - (`width`/`height` on `<img>`, `<iframe>`, `<video>` are allowed by the glossary and are not counted.)
- Problem: presentation carried by HTML instead of CSS; users cannot override it with their own style sheets.
- Impact: low-vision users with custom style sheets or reader modes; `<marquee>` also fails 13.8.
- Fix:
  ```html
  <p class="alerte"><strong>Fermeture exceptionnelle de la mairie le 15 août.</strong></p>
  …
  <p class="maj">Mis à jour le 12 mai 2025</p>
  ```
  ```css
  .actus { background: #eee; padding: 6px; }   /* instead of bgcolor/cellpadding */
  .maj { color: #555; background-color: #fff; text-align: center; }
  ```
- Priority: minor

### 10.4 [AA] On each web page, is the text still readable when the font size is increased by at least 200 %?
- Test: 10.4.2 — it must be possible to increase the font size by at least 200 % for all the text, with the browser's text enlargement or graphical zoom (10.4.1, absence of information loss at 200 %, remains to be tested in a desktop browser)
- Pages: home (template: every page)
- Element: line 5: `<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">`
- Problem: `maximum-scale=1` and `user-scalable=no` disable pinch and double-tap zoom in mobile browsers that honour them (Chrome on Android among the baseline browsers), so the text cannot be enlarged to 200 %.
- Impact: low-vision users on phones and tablets.
- Fix: `<meta name="viewport" content="width=device-width, initial-scale=1">`
- Priority: major

### 10.5 [AA] On each web page, are the CSS declarations for element background and font colours used correctly?
- Test: 10.5.1 — each `color` declaration on an element likely to contain text is accompanied by a background colour declaration (on the element or inherited)
- Pages: home (stylesheet: every page)
- Element: line 15: `.alerte { color: #c00; }` with no background colour declared on `.alerte` or on any ancestor (`body { font-family: Arial, sans-serif; margin: 0; }` declares none).
- Problem: text colour declared without background colour: if a user's system or browser theme sets a dark page background, red text on dark becomes unreadable. (`.topbar`, `.menu a` and `.btn` are correctly paired.)
- Impact: users of high-contrast or dark system themes.
- Fix: `body { font-family: Arial, sans-serif; margin: 0; color: #222; background-color: #fff; }`
- Priority: minor

### 10.7 [A] On each web page, for each element receiving keyboard focus, is the focus visible?
- Test: 10.7.1 — the browser's native focus style is not removed, or an author-defined visible focus style replaces it
- Pages: home (stylesheet: every page)
- Element: line 10: `a:focus, button:focus { outline: none; }` — the only focus rule in the stylesheet; nothing replaces the outline.
- Problem: the native focus indicator is removed on every link and button of the site and no visible alternative is defined. (The whole stylesheet is embedded in the page, so this is established from the code; a rendered check will only confirm it.)
- Impact: sighted keyboard users cannot see where they are; combined with 7.3 and 12.8 the page is not navigable by keyboard.
- Fix: delete the rule, or replace it with a visible style contrasted at least 3:1 with its surroundings:
  ```css
  a:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible { outline: 3px solid #1d3f73; outline-offset: 2px; }
  .topbar a:focus-visible, .topbar button:focus-visible { outline-color: #fff; }   /* on the dark bar */
  ```
- Priority: blocking

### Topic 11 — Forms

### 11.1 [A] Does each form input field have a label?
- Tests: 11.1.1 — the field has a `<label for>`, `aria-label`, `aria-labelledby` (referencing an existing text) or `title` (a placeholder is none of these); 11.1.3 — a field whose label is not visible (`aria-label`) also has visible text or a `title` explaining the expected input
- Pages: home (search field: every page)
- Elements:
  - line 35: `<input type="search" name="q" placeholder="Rechercher sur le site">` — placeholder only (11.1.1).
  - line 77: `<input type="text" name="nom" id="nom" placeholder="Votre nom" required>` — placeholder only (11.1.1).
  - line 78: `<input type="email" name="email" id="email" placeholder="Votre adresse e-mail" required>` — placeholder only (11.1.1).
  - line 88: `<select name="frequence" onchange="…" aria-labelledby="freq-label">` — `aria-labelledby` points to an id `freq-label` that does not exist in the page; the field has no label (11.1.1).
  - line 79: `<input type="date" name="naissance" id="nom" aria-label="Date de naissance">` — `aria-label` only, no visible text (11.1.3).
- Problem: a placeholder is not an accessible name under 11.1.1 (and it disappears as soon as the user types); a broken `aria-labelledby` reference yields an empty name; an `aria-label` alone gives sighted users no visible label (11.1.3).
- Impact: screen-reader users hear "edit text", "combo box" with no purpose; voice-control users cannot name the fields; everyone loses the hint once they start typing.
- Fix (also adds the required marks for 11.10 and the `autocomplete` for 11.13):
  ```html
  <label for="q" class="vhide">Rechercher sur le site</label>
  <input type="search" id="q" name="q" placeholder="Rechercher sur le site">
  <button type="submit"><svg aria-hidden="true" focusable="false" …></svg><span class="vhide">Rechercher</span></button>

  <p>Les champs marqués d'un * sont obligatoires.</p>
  <label for="nom">Votre nom *</label>
  <input type="text" name="nom" id="nom" autocomplete="name" required aria-required="true">
  <label for="email">Votre adresse e-mail *</label>
  <input type="email" name="email" id="email" autocomplete="email" required aria-required="true">
  <label for="naissance">Date de naissance</label>
  <input type="date" name="naissance" id="naissance" autocomplete="bday">
  …
  <label for="frequence">Fréquence</label>
  <select name="frequence" id="frequence"><option>Hebdomadaire</option><option>Mensuelle</option></select>
  ```
  (For the search field, 11.1.1 also accepts a visually hidden label when the adjacent button carries a visible text label: give the button the visible word "Rechercher" if you prefer not to show a label.)
- Priority: blocking

### 11.5 [A] In each form, are the related form controls grouped together, if necessary?
- Test: 11.5.1 — related radio buttons are grouped in a `<fieldset>`, or in an element with `role="group"` / `role="radiogroup"`
- Pages: home
- Element: lines 80-83: `<p>Langue de la newsletter :</p> <input type="radio" name="langue" id="lang-fr"…> <label for="lang-fr">Français</label> <input type="radio" name="langue" id="lang-de"…> … <input type="radio" name="langue" id="lang-lb"…> …`
- Problem: the three "langue" radio buttons are not grouped; the question "Langue de la newsletter" is a plain paragraph, not attached to them.
- Impact: a screen-reader user who tabs to the radios hears "Français, radio button, 1 of 3" without knowing what is being chosen.
- Fix:
  ```html
  <fieldset>
    <legend>Langue de la newsletter</legend>
    <input type="radio" name="langue" id="lang-fr" value="fr"> <label for="lang-fr">Français</label>
    <input type="radio" name="langue" id="lang-de" value="de"> <label for="lang-de" lang="de">Deutsch</label>
    <input type="radio" name="langue" id="lang-lb" value="lb"> <label for="lang-lb" lang="lb">Lëtzebuergesch</label>
  </fieldset>
  ```
- Priority: major

### 11.6 [A] In each form, does each group of related form controls have a legend?
- Test: 11.6.1 — each group of related controls has a legend
- Pages: home
- Element: lines 84-87: `<fieldset><input type="checkbox" name="themes" id="t1"…> <label for="t1">Culture</label> <input type="checkbox" … id="t2"…> <label for="t2">Sport</label></fieldset>`
- Problem: the `<fieldset>` has no `<legend>`: the group has no name.
- Impact: as 11.5: "Culture, checkbox" with no indication of what the choice is about.
- Fix: `<fieldset><legend>Thèmes qui vous intéressent</legend>…</fieldset>`
- Priority: major

### 11.9 [A] In each form, is the label of each button relevant?
- Test: 11.9.1 — the button's label (content of `<button>`, `value`, `alt`, `aria-label`, `aria-labelledby` or `title`) is relevant
- Pages: home (search button: every page)
- Elements: line 36: `<button type="submit"><svg …></svg></button>` (search); line 92: `<button type="submit"><img src="/img/send.svg" alt=""></button>` (newsletter)
- Problem: both buttons have an empty accessible name: no text, an unnamed `<svg>`, an image declared decorative.
- Impact: screen readers announce "button"; voice control cannot activate them by name.
- Fix: see 1.1: `<span class="vhide">Rechercher</span>` in the search button (or a visible word) and `<button type="submit"><img src="/img/send.svg" alt=""> S'abonner</button>`.
- Priority: blocking

### 11.10 [A] In each form, is the error management used appropriately?
- Test: 11.10.2 — each field with `required` / `aria-required="true"` has a **visible** mandatory indication that identifies it (in the label, in an attached text or in the group legend) before data is entered
- Pages: home
- Elements: line 76: `<p>Les champs marqués d'un * sont obligatoires.</p>`; line 77 and 78: the `required` fields `nom` and `email` — no `*` appears anywhere (the placeholders do not carry one, and there are no labels).
- Problem: the page announces a convention ("fields marked with *") and then marks nothing; the mandatory fields cannot be identified visually before submission. (Tests 11.10.3 to 11.10.7, on the error messages after submission, could not be tested statically: see section 5.)
- Impact: all users, especially cognitively impaired users and screen-magnifier users, discover the obligation only through the browser's error after submitting.
- Fix: the labels with `*` given under 11.1 (`<label for="nom">Votre nom *</label>`) and keep the explanatory sentence before the form.
- Priority: major

### 11.13 [AA] Can the purpose of an input field be identified to facilitate the automatic filling of fields with user data?
- Test: 11.13.1 — each field collecting data about the user has an `autocomplete` attribute with a valid, relevant token
- Pages: home
- Elements: line 77 (`name="nom"`), line 78 (`name="email"`), line 79 (`name="naissance"`): no `autocomplete` attribute.
- Problem: name, e-mail address and date of birth are user data listed in the HTML autocomplete field names; the attribute is missing.
- Impact: users with motor or cognitive impairments rely on browser autofill; identification of the field purpose also lets assistive tools add icons.
- Fix: `autocomplete="name"`, `autocomplete="email"`, `autocomplete="bday"` (already included in the 11.1 fix).
- Priority: minor

### Topic 12 — Navigation

### 12.7 [A] On each web page, is there a bypass or skip link to the main content region?
- Test: 12.7.1 — a link allows the main content region to be skipped to or reached (special case: none when the page has no navigation block before the main content, which is not the case here)
- Pages: home (template: every page)
- Element: the first links of the page (lines 23-31) are the logo and the menu; no link targets `#contenu`.
- Problem: there is no skip link, and (9.2) no `main` landmark that could serve as a fallback target for assistive technologies.
- Impact: keyboard users must tab through the logo, six menu links, the search field and button on every page before reaching the content.
- Fix: as first child of `<body>`:
  ```html
  <a class="skip" href="#contenu">Aller au contenu</a>
  …
  <main id="contenu" tabindex="-1">
  ```
  ```css
  .skip { position: absolute; left: -9999px; }
  .skip:focus { position: static; left: auto; display: inline-block; padding: 8px; background: #fff; color: #1d3f73; outline: 3px solid #1d3f73; }
  ```
  (The link may be hidden until focused, but must become visible on focus: test 12.7.2, to be verified in the final audit on all pages.)
- Priority: major

### 12.8 [A] On each web page, is the navigation sequence consistent?
- Test: 12.8.1 — the navigation (tab) sequence is consistent with the content
- Pages: home (template: probably every page)
- Element: line 98: `<div class="footer" tabindex="3">`
- Problem: a positive `tabindex` places the element **before** every element with natural tab order: the first Tab press on the page focuses the footer `<div>` (a non-interactive block), then the sequence jumps back to the logo at the top. Established from the HTML tabbing algorithm; a browser check will only confirm the order.
- Impact: keyboard and screen-reader users start at the bottom of the page, on an element that does nothing, with (10.7) no visible focus.
- Fix: remove the `tabindex` attribute entirely: `<footer class="footer">`. Never use `tabindex` values above 0.
- Priority: major

### Topic 13 — Consultation

### 13.1 [A] For each web page, does the user have control over each time limit modifying the content?
- Test: 13.1.1 — a refresh process (`<meta>`) can be stopped, extended tenfold, is announced with 20 s to react, or has an interval of at least 20 hours
- Pages: home (template: check every page)
- Element: line 6: `<meta http-equiv="refresh" content="300">`
- Problem: the page reloads itself every 300 seconds (5 minutes) with no way to stop it. This is a non-interference criterion: it applies even to exempt content.
- Impact: screen-reader users lose their reading position and hear the page again from the top; users filling the newsletter form slowly lose their input; magnifier users lose their viewport.
- Fix: remove the `<meta http-equiv="refresh">`. If a live content block needs refreshing, update that block with a script that the user can pause, or let the user reload manually.
- Priority: blocking

### 13.8 [A] On each web page, is every moving or blinking content controllable by the user?
- Test: 13.8.1 — automatically started moving content lasts 5 s or less, or can be stopped/restarted, or hidden, or all its information can be displayed without the movement
- Pages: home
- Elements: line 46: `<marquee>Fermeture exceptionnelle de la mairie le 15 août.</marquee>` (scrolls indefinitely, no control); line 65: `<video src="/media/jingle.mp4" autoplay loop width="320"></video>` (plays in a loop, no control). This is a non-interference criterion.
- Problem: two moving contents start automatically, last more than 5 seconds and offer no pause.
- Impact: people with attention or reading difficulties cannot read the scrolling closure notice (an important message); moving content distracts from the rest of the page; some users with vestibular disorders are made unwell.
- Fix: static notice `<p class="alerte"><strong>Fermeture exceptionnelle de la mairie le 15 août.</strong></p>`; video without `autoplay` and with `controls` (see 4.10).
- Priority: major

---

## 4. Points à vérifier manuellement — Points that need a human decision (not counted as NC)

| Criterion / test | Element | What to check |
|---|---|---|
| 3.1.2 (colour) | line 61: "Les jours marqués **en rouge** dans le calendrier sont des jours de fermeture." | The sentence says the calendar (on another page) conveys closures by colour alone. On the calendar page, 3.1 will be NC unless closures are also marked by text, a symbol or a pattern; the sentence itself should then say "marqués en rouge et signalés par le mot Fermé". |
| 6.1.1 (explicit links) | lines 49-50 "En savoir plus" (x2), line 53 "cliquez ici" | Compliant by the letter of 6.1.1 because the surrounding table cell / sentence gives the context (RAWeb glossary "link context"), but weak for screen-reader users who list links out of context. Recommended: `En savoir plus<span class="vhide"> sur le nouveau parc de jeux</span>` and `<a href="/actualites/">Consulter toutes les actualités</a>` instead of "cliquez ici". |
| 6.1.2 | line 31 flag link (name "English version" from `title`), line 100 "Instagram" | Names describe the destination; compliant. Prefer a visible text "English" (see 8.7). |
| 1.2.1 | lines 31, 92, 100 images with `alt=""` | Correctly ignored where decorative (flag beside a named link). The send icon and the Facebook logo are not decorative: counted under 1.1. |
| 1.6 / 1.8 | line 41 hero banner | If the banner contains text (an image of text) or a complex scene, 1.8 / 1.6 apply: look at the image. |
| 4.1, 4.3, 4.5 (and RAWeb 4.14, 4.17, 4.18) | YouTube video line 64, jingle line 65 | Transcript, captions and audio description are required if the videos have speech or informative visuals; YouTube's automatic captions are not sufficient unless corrected (4.4). Media published before 23 September 2020 are exempt, but 4.10 and 13.8 still apply. |
| 4.13 | YouTube player | Player compatible with the assistive technologies of the baseline: test with NVDA, JAWS, VoiceOver. |
| 11.10.5 | line 79 date field | Native `type="date"` renders a browser date picker; check in the baseline browsers that the expected format is visible or that the picker is usable, otherwise add "(jj/mm/aaaa)" to the label. |
| 13.3 / 13.4 | line 71 `reglement-communal-2024.pdf` | The PDF must be accessible (tagged, with headings, alt texts, language; check with PAC 2024 / Acrobat) or have an accessible HTML version. Good practice: `Règlement communal (PDF, 1,2 Mo)` in the link text. Office documents published before 23 September 2018 and not needed for an active process are exempt. |
| 12.6 | newsletter block, social links | If these blocks repeat on several pages, they must be reachable/avoidable (landmark role, heading, skip link): the `<h2>Newsletter</h2>` heading added under 9.1 satisfies it for the newsletter block. |
| 8.9 | `<b>` + `<br>` structuring the news items | Resolved by the list/heading markup proposed under 5.3 and 9.1. |

---

## 5. Non testé — What could not be tested from the code, and how to test it

The final audit must cover these criteria, on every page of the sample, in the RAWeb test environment (NVDA latest + Firefox/Chrome/Edge; JAWS previous version + Firefox/Chrome/Edge; VoiceOver + Safari; and, strongly recommended for a public site, TalkBack + Chrome on Android and VoiceOver + Safari on iOS). Record the versions in the report and in the statement.

| Criteria | What to test | How |
|---|---|---|
| **3.2, 3.3** contrast | Text 4.5:1 (3:1 for large text), UI components and graphics 3:1 | The colour pairs declared in the stylesheet all pass (white on `#1d3f73` = 10.4:1; white on `#2a7f62` = 4.9:1; `#c00` on white = 5.9:1; `#555` on white = 7.5:1). Still to measure in the browser: placeholder text (browser default grey, borderline in Firefox), any text over the hero image, input borders and the future focus indicator. Use Colour Contrast Analyser or the devtools. |
| **7.1.2, 4.13, 10.2** screen-reader rendering | Every scripted or media component is rendered and operable with each baseline screen reader | NVDA + Firefox, NVDA + Chrome, JAWS + Chrome, VoiceOver + Safari; read the whole page, operate the forms and the YouTube player. |
| **12.8 (confirmation), 12.9** keyboard | Tab/Shift+Tab order over the whole page (after removing `tabindex="3"`), no keyboard trap in the YouTube frame and the video | Keyboard only, in each baseline browser; `node scripts/render_page.js URL --tab-order` can log the sequence. |
| **10.4.1, 10.11, 10.12** zoom, reflow, text spacing | No loss of content at 200 % zoom; no horizontal scrolling at 320 px wide / 256 px high; text spacing bookmarklet | Browser zoom 200 %, responsive mode 320 px, text-spacing bookmarklet. |
| **10.3, 10.6** CSS off, link visibility | Reading order without CSS; links in body text distinguishable from text | Disable styles (Web Developer toolbar); check links are underlined (they are by default here). |
| **13.7, 13.9** flashes, orientation | No more than 3 flashes/s in the videos; content usable in portrait and landscape | View the videos (PEAT tool if in doubt); rotate a phone. |
| **11.3, 11.11** forms across the site, error correction | Same labels for the same fields on every page; error messages suggest corrections | Submit the newsletter and search forms with errors. |
| **12.1 to 12.5** site-level navigation | At least two navigation systems (menu, search, site map), consistent position, relevant site map | Needs the other pages: menu + search exist on the home page. |
| **13.3, 13.4** documents | Accessibility of the PDF and of the other downloadable documents of the sample | PAC 2024, Acrobat accessibility checker. |
| **RAWeb topic 14 (14.1 to 14.3)** documentation and accessibility features | The site's documentation (the accessibility page, help page) describes the accessibility features and is itself accessible | Audit the accessibility page `/accessibilite/` and any help page; they are mandatory sample pages. |
| **RAWeb topic 16 (16.1 to 16.3)** support services | The contact / support service knows the accessibility features and can communicate with disabled users (e-mail, form, relay service), and its documentation is accessible | Audit the contact page; check the response channels and the one-month answer procedure. |
| **RAWeb topics 15 and 17** | Editing tools and real-time communication | Not applicable on this page (no editing tool offered to the public, no real-time communication). If the CMS counts as an editing tool used by the commune's editors, topic 15 applies to it. |
| 1.6, 1.8, 4.1-4.6, 4.14, 4.17, 4.18 | See section 4 | Look at the images and watch the videos. |

---

## 6. Recommandations transversales — Cross-cutting recommendations for the agency

1. **Fix the page template once** (header, footer, `<html lang>`, `<title>` pattern, landmarks, skip link, focus style, viewport, no meta refresh): this clears 8.3, 8.6, 9.2, 10.4, 10.7, 12.7, 12.8, 13.1 and the header/footer parts of 1.1, 6.2, 11.1, 11.9 on every page of the site. Corrected skeleton:
   ```html
   <!DOCTYPE html>
   <html lang="fr">
   <head>
     <meta charset="utf-8">
     <meta name="viewport" content="width=device-width, initial-scale=1">
     <title>Accueil – Commune de Fiktivbuerg</title>
     <style>
       body { font-family: Arial, sans-serif; margin: 0; color: #222; background-color: #fff; }
       a:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible { outline: 3px solid #1d3f73; outline-offset: 2px; }
       .topbar a:focus-visible, .topbar button:focus-visible { outline-color: #fff; }
       .skip { position: absolute; left: -9999px; }
       .skip:focus { position: static; display: inline-block; padding: 8px; }
       .vhide { position: absolute; left: -9999px; }
       …
     </style>
   </head>
   <body>
     <a class="skip" href="#contenu">Aller au contenu</a>
     <header class="topbar"> logo link with alt · <nav aria-label="Menu principal">…</nav> · <form role="search">…</form> </header>
     <main id="contenu" tabindex="-1"> h1, then one h2 per section </main>
     <footer class="footer"> … </footer>
   </body>
   </html>
   ```
2. **Form component rules** for the CMS and all templates: every field has a visible `<label for>`; required fields marked `*` in the label plus `required`; radio/checkbox series in `<fieldset><legend>`; buttons with text (visible or `.vhide`); no `onchange` submission; `autocomplete` on personal-data fields; unique ids.
3. **Image rules for editors**: the CMS must require an alt decision (decorative = empty alt; informative = short description) and never default to the file name; icons as `<svg aria-hidden="true">` inside a named link/button.
4. **No HTML presentation**: ban `<marquee>`, `<font>`, `<center>`, `bgcolor`, `cellpadding`, positive `tabindex`, `div onclick`. Validate the generated HTML in the build or CMS pipeline.
5. **Media policy**: no autoplay with sound; `controls` on every `<video>`/`<audio>`; captions and a transcript for every video with speech; `title` on every `<iframe>`.
6. **Data tables**: `<caption>`, `<th scope>`; never a `<table>` for layout.

---

## 7. Vers la déclaration d'accessibilité — What is needed for next month's accessibility statement

The statement (déclaration d'accessibilité) required by the law of 28 May 2019 must state a compliance status based on a RAWeb audit of the site's sample. This document is not that audit. To publish a valid statement next month:

1. **Audit the mandatory sample** (RAWeb 1.1 test methodology): home page; contact page; legal notice (mentions légales); accessibility page (the one that will carry the statement); site map; help page; authentication page if any; at least one page per type of service / first-level section (La commune, Démarches, Actualités, the search results page); at least one downloadable document per service type (e.g. `reglement-communal-2024.pdf`); every page of each process (e.g. the complete "Réservation de salle" or "Certificat de résidence" procedure, step by step); pages with distinct content types (data tables, video, forms); RAWeb adds the site and support-service documentation pages if distinct; plus at least 10 % of those pages chosen at random. List each page with its URL in the report and in the statement.
2. **Test with the baseline assistive technologies** (section 5) and resolve every NT; fill the grid `grille-raweb-accueil.csv` (one column per page, add columns with `audit_grid.py new/set`) and compute the rate with `audit_grid.py compute`: rate = compliant criteria ÷ (compliant + non-compliant) over the whole sample, no weighting by level. Status: 100 % fully compliant; 50 % to < 100 % partially compliant; below 50 % **or no valid audit** non-compliant.
3. **Fix before auditing what can be fixed now**: the template defects of section 6 are cheap and would otherwise appear in the statement as non-conformities on every page. On the home page alone, 35 criteria are non-compliant; with 44 criteria decided so far, the site will be far below 50 % unless the fixes are applied before the final audit.
4. **Write the statement** with the SIP generator (https://accessibilite.public.lu/en/tools/decla.html) or the RAWeb structure: commitment under the law of 28 May 2019; compliance status and rate with the audit date and auditor; the list of non-conformities (criterion, description, pages, planned fix or alternative); derogations for disproportionate burden (justified case by case, never for a whole site, with an accessible alternative); exempt content (e.g. office documents before 23 September 2018, media before 23 September 2020, third-party content not controlled by the commune); preparation date and method; technologies used; test environment with versions; tools; pages audited with URLs; a feedback contact (accessible e-mail address or form) with a commitment to answer within one month; the enforcement route (Service information et presse, accessibilite@sip.etat.lu, or the Ombudsman). Publish it on the accessibility page, linked from every page (the footer link "Accessibilité" already exists), and send the link to the SIP within 30 days of publication.
5. If the full audit cannot be completed in time, the statement can still be published on time with the status **non conforme** ("no valid audit"), a list of the known non-conformities (this report) and a dated action plan; update it as soon as the audit is done. The exempt and derogated contents must in any case respect 4.10, 12.9, 13.1, 13.7 and 13.8 (non-interference).

---

## 8. Annexes

* `grille-raweb-accueil.csv` — RAWeb 1.1 audit grid, 136 criteria, column "Accueil" filled with C / NC / NA / NT (statuses in English codes; conforme / non conforme / non applicable / non testé). Add the other sample pages as columns for the final audit.
* `grille-raweb-accueil-compute.md` — output of the grid script for the home page column (counts; the printed percentage is provisional and is not the site's compliance rate).
* `scan-accueil-raweb.md` and `scan-accueil-raweb.json` — static pre-check evidence, with the line numbers quoted in this report. Every FAIL in it was checked against the page before being counted; REVIEW items were resolved in sections 3 and 4.
* Status vocabulary: C conforme / compliant; NC non conforme / non-compliant; NA non applicable / not applicable; NT non testé / not tested. Site status: conformité totale / partielle / non-conformité.
* Cross-references to WCAG 2.1 and EN 301 549 clauses are those printed by the RAWeb 1.1 data for each criterion (e.g. 11.1 → WCAG 1.3.1, 3.3.2, 4.1.2; EN 301 549 9.1.3.1, 9.3.3.2, 9.4.1.2); they are given for information only, the applicable requirement is the RAWeb criterion.
