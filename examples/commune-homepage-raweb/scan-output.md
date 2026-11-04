# Static pre-check — input-index.html

Standard: RAWeb 1.1. Findings: **32 likely non-conformities** on 19 criteria (1.1, 2.1, 4.10, 6.2, 7.1, 7.3, 8.2, 8.3, 8.8, 9.2, 9.3, 10.1, 10.4, 11.1, 11.5, 11.6, 11.9, 13.1, 13.8), 37 points to review, 12 informational.

Limits: static analysis of the delivered HTML only (no rendering, no contrast, no screen reader, no keyboard, no JavaScript behaviour). A criterion without findings is not compliant by default; everything applicable still has to be tested.

## Inventory
- title: Accueil
- language_changes: 1
- stylesheets_read: []
- images: 8
- figures_with_caption: 0
- frames: 1
- links: 19
- headings: {'h1': 1, 'h2': 2, 'h3': 1}
- landmarks: {'main': 0, 'banner': 0, 'contentinfo': 0, 'navigation': 0}
- lists: 1
- tables: 2
- forms: 2
- fields: 10
- buttons: 2
- media: 1
- preconditions: {'images (excluding image links)': 5, 'frames': 1, 'tables': 2, 'form controls': 12, 'time-based or embedded media': 2}

## 1.1 [A] Does each image conveying information have a text alternative?
- **FAIL** (test 1.1.1) line 23: `<img src="/img/logo-commune.png" width="120">` Image without alt (and no aria-label/aria-labelledby/title): NC under 1.1 if it conveys information, under 1.2 if decorative (needs alt="").
- **FAIL** (test 1.1.5) line 36: `<svg width="16" height="16" viewbox="0 0 16 16">` <svg> is neither role="img" with a name (if informative, 1.1.5) nor aria-hidden="true" (if decorative, 1.2.4) (inside a link/button: the parent must then carry the name).

## 1.2 [A] Is every decorative image, without a caption, correctly ignored by assistive technologies?
- **INFO** (test 1.2.1) line 31: `<img src="/img/flag-en.svg" alt>` alt="": treated as decorative. Confirm it conveys no information (otherwise NC 1.1).
- **INFO** (test 1.2.1) line 92: `<img src="/img/send.svg" alt>` alt="": treated as decorative. Confirm it conveys no information (otherwise NC 1.1).
- **INFO** (test 1.2.1) line 100: `<img src="/img/facebook.png" alt>` alt="": treated as decorative. Confirm it conveys no information (otherwise NC 1.1).

## 1.3 [A] For each image conveying information with a text alternative, is this alternative relevant (excluding special cases)?
- **REVIEW** (test 1.3.1) line 41: `<img src="/img/hero_banner_final_v2.jpg" alt="hero_banner_final_v2.jpg" width="1200" height="400">` alt="hero_banner_final_v2.jpg" looks like a file name: not a relevant alternative.
- **REVIEW** (test 1.3.1) line 49: `<img src="/img/actu-1.jpg" alt="image">` alt="image" is generic: it should convey the information of the image (or alt="" if decorative).
- **REVIEW** (test 1.3.1) line 50: `<img src="/img/actu-2.jpg" alt="image">` alt="image" is generic: it should convey the information of the image (or alt="" if decorative).
- **REVIEW** (test 1.3.1) line 100: `<img src="/img/instagram.png" alt="Instagram">` alt="Instagram": check relevance against the image.

## 2.1 [A] Does each frame have a frame title?
- **FAIL** (test 2.1.1) line 64: `<iframe src="https://www.youtube.com/embed/abc123" width="560" height="315" allowfullscreen>` Frame without title attribute.

## 3.1 [A] On each web page, the information must not be provided by colour alone. Is this rule respected?
- **REVIEW** (test 3.1.1): Text refers to colour, shape or position (e.g. 'in red', 'on the right'): check the information is also given otherwise (3.1 / 10.9).

## 3.2 [AA] On each web page, is the contrast between the colour of the text and the colour of its background sufficiently high (excluding special cases)?
- **INFO**: Contrast (3.2, 3.3), focus visibility (10.7), 200 % zoom (10.4), reflow at 320 px (10.11), text spacing (10.12), hover/focus content (10.13), orientation (13.9), gestures (13.10, 13.11) and flashes (13.7) need a rendered page: test them in a browser.

## 4.1 [A] Does each pre-recorded time-based media have, if necessary, a transcript or an audio description (excluding special cases)?
- **INFO**: Time-based media found: criteria 4.1 to 4.13 (and 4.14 to 4.18 in RAWeb 1.1) apply.
- **INFO** line 64: `<iframe src="https://www.youtube.com/embed/abc123" width="560" height="315" allowfullscreen>` Embedded media player: criteria 4.1 to 4.13 apply (transcript, captions, audio description, identification, keyboard control, AT compatibility).

## 4.3 [A] Does each synchronised time-based media have, if necessary, synchronised captions (excluding special cases)?
- **REVIEW** (test 4.3.1) line 65: `<video src="/media/jingle.mp4" autoplay loop width="320">` No captions track: if the video has speech, synchronised captions are required (4.3) and a transcript or audio description (4.1).

## 4.5 [AA] Does each pre-recorded time-based media have, if necessary, a synchronised audio description (excluding special cases)?
- **REVIEW** (test 4.5.1) line 65: `<video src="/media/jingle.mp4" autoplay loop width="320">` No audio-description track: needed if visual information is not available in the soundtrack (4.5, AA).

## 4.7 [A] Is each time-based media clearly identifiable (excluding special cases)?
- **REVIEW** (test 4.7.1) line 65: `<video src="/media/jingle.mp4" autoplay loop width="320">` <video>: the media must be clearly identifiable (title/adjacent text).

## 4.10 [A] Is each automatically triggered sound controllable by the user?
- **FAIL** (test 4.10.1) line 65: `<video src="/media/jingle.mp4" autoplay loop width="320">` <video> autoplays with sound and has no controls.

## 4.11 [A] Is the viewing of each time-based media, if required, accessible and operable by keyboard and any pointing device?
- **REVIEW** (test 4.11.1) line 65: `<video src="/media/jingle.mp4" autoplay loop width="320">` <video> without native controls: check custom controls are keyboard operable and AT compatible (4.11, 4.13).

## 5.6 [A] For each data table, are each column header and each row header correctly declared?
- **REVIEW** (test 5.6.1) line 47: `<table bgcolor="#eeeeee" cellpadding="6">` Table (1 rows) without any <th>/columnheader/rowheader: NC 5.6 if it is a data table; if it is a layout table it should have role="presentation" (and keep linearised reading order, 5.3).
- **REVIEW** (test 5.6.1) line 56: `<table id="horaires">` Table (3 rows) without any <th>/columnheader/rowheader: NC 5.6 if it is a data table; if it is a layout table it should have role="presentation" (and keep linearised reading order, 5.3).

## 6.1 [A] Is every link explicit (except in special cases)?
- **REVIEW** (test 6.1.2) line 31: `<a href="/en/" title="English version">` Image link named "English version" (from title): the name must describe the destination/function, not the image.
- **REVIEW** (test 6.1.1) line 49: `<a href="/actualites/parc-de-jeux">` Link "En savoir plus" is not explicit on its own: NC unless the link context (same sentence, paragraph, list item, table cell or preceding heading) makes the destination clear.
- **REVIEW** (test 6.1.1) line 50: `<a href="/actualites/dechets">` Link "En savoir plus" is not explicit on its own: NC unless the link context (same sentence, paragraph, list item, table cell or preceding heading) makes the destination clear.
- **REVIEW** (test 6.1.1) line 53: `<a href="/actualites/">` Link "cliquez ici" is not explicit on its own: NC unless the link context (same sentence, paragraph, list item, table cell or preceding heading) makes the destination clear.
- **REVIEW** (test 6.1.2) line 100: `<a href="https://instagram.example/fiktivbuerg">` Image link named "Instagram" (from content): the name must describe the destination/function, not the image.

## 6.2 [A] On each web page, does each link have an accessible name?
- **FAIL** (test 6.2.1) line 23: `<a href="/">` Link without accessible name (image link with empty alt / svg without title).
- **FAIL** (test 6.2.1) line 100: `<a href="https://facebook.example/fiktivbuerg">` Link without accessible name (image link with empty alt / svg without title).

## 7.1 [A] Is each script, if necessary, compatible with assistive technologies?
- **FAIL** (test 7.1.1) line 88: `<select name="frequence" onchange="this.form.submit()" aria-labelledby="freq-label">` aria-labelledby references missing id(s): freq-label.

## 7.3 [A] Is each script accessible and operable by keyboard and any pointing device (excluding special cases)?
- **FAIL** (test 7.3.1) line 72: `<div class="btn" onclick="location.href='/demarches/'">` Element with a mouse handler is not keyboard focusable (no tabindex="0", not a native control): NC unless an equivalent keyboard-accessible control exists.

## 7.4 [A] For each script that initiates a change of context, is the user warned or does the user have control?
- **REVIEW** (test 7.4.1) line 88: `<select name="frequence" onchange="this.form.submit()" aria-labelledby="freq-label">` onchange on a <select> triggers navigation or submission: context change without warning or control?

## 8.2 [A] For each web page, is the generated source code valid for the specified document type?
- **FAIL** (test 8.2.1): Duplicate id="nom" (lines 77, 79). Note: the SIP records 8.1/8.2 as compliant in simplified audits; report the consequence under the criterion that breaks (11.1 label/for, 7.1 ARIA references) as well.

## 8.3 [A] On each web page, is the default language present?
- **FAIL** (test 8.3.1) line 2: `<html>` No lang attribute on <html>: the default language is not declared.

## 8.6 [A] For each web page with a page title, is this title relevant?
- **REVIEW** (test 8.6.1) line 7: `<title>` Page title "Accueil" looks generic: it should identify the page content and ideally the site.

## 8.7 [AA] On each web page, is each language change indicated in the source code (excluding special cases)?
- **REVIEW** (test 8.7.1): 1 element(s) carry a lang attribute. Foreign-language words or passages without a lang attribute cannot be detected statically: read the page.

## 8.8 [AA] On each web page, is the language code for each language change valid and relevant?
- **FAIL** (test 8.8.1) line 83: `<span lang="letzebuergesch">` Invalid language code lang="letzebuergesch" on a language change.

## 9.1 [A] On each web page, is the information structured by the appropriate use of headings?
- **REVIEW** (test 9.1.1) line 45: `<h3>` Heading level jump (h1 → h3): tolerated by the glossary if the hierarchy stays consistent; NC only if sibling sections get different levels or the outline misleads.
- **REVIEW** (test 9.1.3) line 55: `<p class="titre">` <p class="titre"> "Horaires d'ouverture" looks like a visual heading implemented without <hx>/role=heading.
- **REVIEW** (test 9.1.3) line 63: `<div class="titre">` <div class="titre"> "Vidéo de présentation" looks like a visual heading implemented without <hx>/role=heading.

## 9.2 [A] On each web page, is the document structure consistent (excluding special cases)?
- **FAIL** (test 9.2.1): No <main> / role=main: the main content region is not identified.
- **FAIL** (test 9.2.1) line 25: `<ul class="menu">` Navigation menu(s) not structured with <nav> / role=navigation (1 list(s) of links outside a nav).
- **REVIEW** (test 9.2.1): No <header> / role=banner at page level: NC if the page has a header zone (logo, site title, main navigation).
- **REVIEW** (test 9.2.1): No <footer> / role=contentinfo at page level: NC if the page has a footer zone.
- **REVIEW** (test 9.2.1) line 35: `<input type="search" name="q" placeholder="Rechercher sur le site">` Search field not inside a search landmark (<search> or role="search"): RAWeb 1.1 expects the search zone to have the computed role search.

## 9.3 [A] On each web page, is each list correctly structured?
- **FAIL** (test 9.3.1) line 68: `<li>` <li> whose parent is <div> instead of <ul>/<ol>.
- **FAIL** (test 9.3.1) line 69: `<li>` <li> whose parent is <div> instead of <ul>/<ol>.
- **FAIL** (test 9.3.1) line 70: `<li>` <li> whose parent is <div> instead of <ul>/<ol>.

## 10.1 [A] In the website, are style sheets used to control the presentation of information?
- **FAIL** (test 10.1.1) line 46: `<marquee>` Presentational tag <marquee> in the source.
- **FAIL** (test 10.1.2) line 47: `<table bgcolor="#eeeeee" cellpadding="6">` Presentational attribute(s) bgcolor, cellpadding.
- **FAIL** (test 10.1.1) line 95: `<font color="#555">` Presentational tag <font> in the source.
- **FAIL** (test 10.1.2) line 95: `<font color="#555">` Presentational attribute(s) color.
- **FAIL** (test 10.1.1) line 95: `<center>` Presentational tag <center> in the source.

## 10.4 [AA] On each web page, is the text still readable when the font size is increased by at least 200% (excluding special cases)?
- **FAIL** (test 10.4.1) line 5: `<meta name="viewport" content="width=device-width, initial-scale=1, max">` Viewport blocks pinch zoom (user-scalable=no / maximum-scale=1): text cannot be enlarged to 200 % on mobile.

## 10.7 [A] On each web page, for each element receiving keyboard focus, is the focus visible?
- **REVIEW** (test 10.7.1) line 8: `<style>` inline <style>: 'a:focus, button:focus' removes the focus outline without an obvious replacement in the same rule: check that a visible focus style exists (3:1 against the background).

## 11.1 [A] Does each form input field have a label?
- **FAIL** (test 11.1.1) line 35: `<input type="search" name="q" placeholder="Rechercher sur le site">` Form field without label (no <label for>, aria-label, aria-labelledby or title); placeholder "Rechercher sur le site" alone is not a label.
- **FAIL** (test 11.1.1) line 77: `<input type="text" name="nom" id="nom" placeholder="Votre nom" required>` Form field without label (no <label for>, aria-label, aria-labelledby or title); placeholder "Votre nom" alone is not a label.
- **FAIL** (test 11.1.1) line 78: `<input type="email" name="email" id="email" placeholder="Votre adresse e-mail" required>` Form field without label (no <label for>, aria-label, aria-labelledby or title); placeholder "Votre adresse e-mail" alone is not a label.
- **FAIL** (test 11.1.1) line 88: `<select name="frequence" onchange="this.form.submit()" aria-labelledby="freq-label">` Form field without label (no <label for>, aria-label, aria-labelledby or title).
- **REVIEW** (test 11.1.3) line 79: `<input type="date" name="naissance" id="nom" aria-label="Date de naissance">` Field labelled only via aria-label ("Date de naissance"): a visible label or a title/visible text is needed so the expected input is understandable (11.1.3); check the visible label is contained in the name (11.2.5).

## 11.2 [A] Is each label associated with a form input field relevant (excluding special cases)?
- **REVIEW** (test 11.2.1) line 81: `<input type="radio" name="langue" id="lang-fr" value="fr">` Label "Français": check relevance and that it is adjacent to the field (11.4).
- **REVIEW** (test 11.2.1) line 82: `<input type="radio" name="langue" id="lang-de" value="de">` Label "Deutsch": check relevance and that it is adjacent to the field (11.4).
- **REVIEW** (test 11.2.1) line 83: `<input type="radio" name="langue" id="lang-lb" value="lb">` Label "Lëtzebuergesch": check relevance and that it is adjacent to the field (11.4).
- **REVIEW** (test 11.2.1) line 85: `<input type="checkbox" name="themes" id="t1" value="culture">` Label "Culture": check relevance and that it is adjacent to the field (11.4).
- **REVIEW** (test 11.2.1) line 86: `<input type="checkbox" name="themes" id="t2" value="sport">` Label "Sport": check relevance and that it is adjacent to the field (11.4).

## 11.5 [A] In each form, are the related form controls grouped together, if necessary?
- **FAIL** (test 11.5.1) line 81: `<input type="radio" name="langue" id="lang-fr" value="fr">` 3 radio buttons "langue" are not grouped (fieldset/legend or role=group|radiogroup with a name).

## 11.6 [A] In each form, does each group of related form controls have a legend?
- **FAIL** (test 11.6.1) line 84: `<fieldset>` <fieldset> without <legend>.

## 11.9 [A] In each form, is the label of each button relevant (excluding special cases)?
- **FAIL** (test 11.9.1) line 36: `<button type="submit">` Button without accessible name (icon-only button needs aria-label, visually hidden text or svg title).
- **FAIL** (test 11.9.1) line 92: `<button type="submit">` Button without accessible name (icon-only button needs aria-label, visually hidden text or svg title).

## 11.10 [A] In each form, is the error management used appropriately (excluding special cases)?
- **REVIEW** (test 11.10.5) line 79: `<input type="date" name="naissance" id="nom" aria-label="Date de naissance">` Field "Date de naissance" expects a specific type/format (date): the expected format must be indicated visibly before input.
- **INFO** (test 11.10.1) line 79: `<input type="date" name="naissance" id="nom" aria-label="Date de naissance">` Field "Date de naissance" is not marked required: if it is mandatory, add a visible indication and required/aria-required.
- **INFO** (test 11.10.1) line 81: `<input type="radio" name="langue" id="lang-fr" value="fr">` Field "Français" is not marked required: if it is mandatory, add a visible indication and required/aria-required.
- **INFO** (test 11.10.1) line 82: `<input type="radio" name="langue" id="lang-de" value="de">` Field "Deutsch" is not marked required: if it is mandatory, add a visible indication and required/aria-required.
- **INFO** (test 11.10.1) line 83: `<input type="radio" name="langue" id="lang-lb" value="lb">` Field "Lëtzebuergesch" is not marked required: if it is mandatory, add a visible indication and required/aria-required.
- **INFO** (test 11.10.1) line 85: `<input type="checkbox" name="themes" id="t1" value="culture">` Field "Culture" is not marked required: if it is mandatory, add a visible indication and required/aria-required.
- **INFO** (test 11.10.1) line 86: `<input type="checkbox" name="themes" id="t2" value="sport">` Field "Sport" is not marked required: if it is mandatory, add a visible indication and required/aria-required.

## 11.13 [AA] Can the purpose of an input field be identified to facilitate the automatic filling of fields with user data?
- **REVIEW** (test 11.13.1) line 79: `<input type="date" name="naissance" id="nom" aria-label="Date de naissance">` Field "Date de naissance" seems to collect user data but has no autocomplete attribute (NC if the data is about the user).

## 12.7 [A] On each web page, is there a bypass or skip link to the main content region (excluding special cases)?
- **REVIEW** (test 12.7.1): No skip link to the main content detected among the first links of the page (NC unless the page has no repeated blocks before the main content).

## 12.8 [A] On each web page, is the navigation sequence consistent?
- **REVIEW** (test 12.8.1) line 98: `<div class="footer" tabindex="3">` Positive tabindex=3 changes the natural tab order.

## 13.1 [A] For each web page, does the user have control over each time limit modifying the content (excluding special cases)?
- **FAIL** (test 13.1.1) line 6: `<meta http-equiv="refresh" content="300">` Automatic page refresh every 300 s without user control.

## 13.3 [A] On each web page, does each downloadable office document have an accessible version (excluding special cases)?
- **REVIEW** (test 13.3.1) line 71: `<a href="/docs/reglement-communal-2024.pdf">` Downloadable office document (/docs/reglement-communal-2024.pdf): it must be accessible or have an accessible version (13.3/13.4); good practice: announce format and size in the link.

## 13.8 [A] On each web page, is every moving or blinking content controllable by the user (excluding special cases)?
- **FAIL** (test 13.8.1) line 46: `<marquee>` <marquee> moves or blinks without user control.

