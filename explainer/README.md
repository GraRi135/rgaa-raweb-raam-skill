# Explainer: twelve accessibility rules, for people who do not know the rules

`index.html` is a single, self-contained page (no dependencies, no external fonts, no tracking) that explains
twelve web accessibility rules with invented examples from the fictional commune of Fiktivbuerg: interactive
simulations (colour-blindness filters, "what a screen reader hears", a keyboard-only form, an accessible and an
inaccessible drop-down menu, a zoom slider, a phone frame that scrolls sideways), a "your turn" challenge under
each rule where every answer shows a visual example before the reader confirms the best one, a section on users'
rights in Luxembourg, and an eight-question quiz built the same way. It is in French with an English toggle; the
page remembers the choice in the visitor's browser. It says plainly that twelve rules are a very small part of the
standard.

Audience: content editors and communication staff of public-sector websites, and the general public.

## Host it

Copy `index.html` anywhere a web server (or a USB stick, or an intranet share) can serve it. It works from a
`file://` URL too. For GitHub Pages: Settings → Pages → deploy from the branch, folder `/` (the page is then at
`https://<user>.github.io/<repo>/explainer/`), or copy the file to a `docs/` folder if you prefer that layout.

## Edit or translate it

The French text lives in the HTML (every translatable element carries a `data-t` key); the English text is the
`EN` dictionary at the top of the script, keyed the same way. To add a language, copy the `EN` dictionary and
add a button in the language switcher. Colours are CSS tokens on `:root` (light and dark themes).

## What the page deliberately contains

The demos show failing patterns on purpose: a low-contrast poster, a calendar that relies on colour, a fake
button that the keyboard cannot reach, placeholder-only form fields. They are inert (not real controls), hidden
from assistive technologies where they are purely visual, and always paired with the fixed version. The page
itself follows the rules it teaches: landmarks, one heading hierarchy, a skip link, visible focus, keyboard
operation of every demo, text alternatives, reduced-motion support, and 4.5:1 contrast on its own text. Like
everything in this repository, it is an aid: it simplifies the standard and is not a substitute for it.
