# Web audit walkthrough (for accessibility auditors)

How an RGAA 4.1.2 or RAWeb 1.1 audit runs with this skill, step by step, and what you as the auditor must do yourself.
The skill applies the method published by DINUM and the SIP; it does not change it. Vocabulary is given in English
with the French term auditors use.

## Before you start

* **Standard**: RGAA 4.1.2 for France, RAWeb 1.1 for Luxembourg. They share criteria 1.1 to 13.12; RAWeb adds 30
  criteria (topics 14 to 17 and a few multimedia/consultation criteria) and rewrote about 30 tests. Claude cites test
  numbers from the bundled data of the standard you name; check which one appears in the report header.
* **Sample** ("échantillon"): home, contact, legal notice, accessibility page, site map, help, authentication, one page
  per service, one downloadable document, every page of each process, pages with distinct layouts, plus 10 % random
  pages. The SIP also always audits the search results page and a news article. Give Claude the URLs; it will ask
  for the mandatory ones it cannot find rather than guess.
* **Test environment** ("base de référence"): NVDA, JAWS and VoiceOver on desktop, TalkBack and VoiceOver on mobile,
  with versions. Claude has none of them. Decide now who will run that pass and when.

## What Claude does

1. Fetches or renders each page (Playwright for client-rendered sites) and runs the static scanner. Output per page:
   FAIL lines (markup that violates a test), REVIEW lines (needs a human decision), INFO lines (what is applicable).
2. Looks up the wording and procedure of every criterion it is about to cite.
3. Runs keyboard probes in a headless browser (tab order, focus outline) and contrast measurements on declared
   colours.
4. Fills the grid page by page with C / NC / NA / NT, computes the rate, and writes the report with findings quoted
   element by element, the way the SIP writes its "Constats sur le site".

## What you must do

* **Decide the REVIEW items.** They are the auditor's judgement calls: is this image decorative, does the link context
  make "En savoir plus" explicit, is this heading hierarchy consistent, is this table a layout table. Claude proposes;
  you decide and the grid changes with your decision.
* **Run the assistive-technology pass.** Topic 7 (scripts), 4.13, 10.2, and anything about announcements or
  rendering stay NT until someone has used a screen reader. The report lists them with the procedure to run. Fill the
  grid after that pass and recompute with `audit_grid.py compute`.
* **Check the FAIL lines against the live page.** The scanner reads markup; an element hidden by CSS, injected after
  load, or inside exempt content changes the verdict. Spot-check at least the findings you will put first.
* **Check the contrast figures.** Computed-style measurements miss text over images and gradients; the report flags
  those as unresolved. Measure them with a contrast analyser on a screenshot.
* **Own the rate.** A rate with NT criteria is provisional, and the report says so. Only after the AT pass, and your
  review of the REVIEW items, is it the audit's rate.

## Reading a finding

```
### 11.1 [A] Does each form input field have a label?
- Test: 11.1.1 — the field has a <label for>, aria-label, aria-labelledby or title
- Pages: Home (newsletter block), Contact
- Element: <input type="email" name="email" placeholder="Votre adresse e-mail">
- Problem: the only text is a placeholder, which is not an accessible name and disappears on input.
- Impact: screen-reader users hear "edit text" with no purpose; voice-control users cannot target the field.
- Fix: <label for="email">Adresse e-mail (obligatoire)</label><input id="email" type="email" autocomplete="email" required>
- Priority: major
```

Criterion and test ids follow the standard's numbering; "Priority" is the auditor's judgement, not part of the standard.

## Typical errors to look for in Claude's output

Even with the official wording in front of it, Claude can be wrong. In our tests the mistakes were of these kinds:
marking a criterion NC for a heading-level jump that the glossary tolerates (fixed in the scanner, but the pattern
can recur elsewhere); citing a test number for a condition that belongs to a neighbouring test (11.10.3 instead of
11.10.5); treating a page with no finding as compliant; computing a rate from a single page. The notice at the top
of every report exists because of this. Read the report as a colleague's draft, not as a result.

## Deliverables

* `rapport-audit-<site>.md`: SIP full-audit outline (introduction, sample with statement check, test environment,
  results with per-page and per-topic tables, opinion, technical annex by topic).
* `grille-audit-<site>.csv` and the `compute` output.
* On request, the illustrated version: `rapport.html` (single file, screenshots of each finding with the element
  outlined and its markup) and `rapport.pdf`, built from a findings file you can review and edit before building.
  A fictional example is in `examples/commune-homepage-raweb/` (`findings.json`, `rapport-illustre.html`, `rapport-illustre.pdf`).
* On request, the accessibility statement draft: see [statements.md](statements.md).
