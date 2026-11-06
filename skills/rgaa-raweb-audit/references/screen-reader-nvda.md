# Screen-reader pass with the real NVDA (`nvda_capture.js`, `nvda_review.py`)

The RAWeb 1.1 and RGAA 4.1.2 reference environments pair NVDA with Firefox, Chrome and Edge (and JAWS with the same
browsers, VoiceOver with Safari, TalkBack and VoiceOver on mobile). Static analysis and rendered-DOM probes never
replace that: criteria about announcements and scripted components stay "not tested" until a screen reader has run.
This pass drives the real NVDA on a Windows PC, records what it says, and turns that into evidence the audit can quote.

Read this file when the user is on Windows with NVDA, or asks how to get screen-reader evidence.

## What it does and does not do

* `nvda_capture.js` starts NVDA (through Guidepup, an MIT screen-reader automation library), opens each page of the
  sample in Chrome (Firefox and Edge on request with `--browser`), and records:
  1. the linear reading from the top of the document ("next" item by item, like a user discovering the page);
  2. the element lists NVDA exposes: headings, links, landmarks, form fields, graphics, tables, lists;
  3. for every finding of the page that has a `selector`, what NVDA announces when the element receives the focus
     (`reportCurrentFocus`) and when its line is read (`readLine`); a finding may carry an `expect` regular
     expression, and the capture says whether the expected announcement was heard.
* `nvda_review.py` reads the captures, flags announcement patterns that usually mean a non-conformity (with the
  criterion to check), lists the per-finding results, writes the evidence into `findings.json` (`--apply`) so the
  illustrated report shows it, and prints the grid statuses to consider.
* It does not click through scenarios (menus, dialogs, form submission). Those remain a manual pass with NVDA, or a
  future scenario file. It does not run JAWS, VoiceOver or TalkBack.
* It runs on Windows only. `--mock` runs anywhere and feeds the pipeline with phrases derived from the accessibility
  tree; the output is labelled "mock, not evidence" everywhere and must never be presented as screen-reader testing.

## Setup on the Windows PC (once)

1. Install NVDA (free, nvaccess.org) and make it the default screen reader; set its language (the transcripts are in
   NVDA's interface language; both French and English are understood by the review script).
2. Install Node.js and Google Chrome, then in `skills/rgaa-raweb-audit/scripts/`:
   `npm install @guidepup/guidepup playwright`. Chrome is used through its installed channel (no browser download);
   `--browser firefox` needs `npx playwright install firefox`, `--browser edge` needs Edge installed.
3. `npx @guidepup/setup setup` configures NVDA for automation (adds the Guidepup add-on and settings). Run it once,
   and again after an NVDA upgrade.
4. `node nvda_capture.js check` must print `ready`.

During a capture: keep the session unlocked, do not touch keyboard or mouse, let the browser window stay in front.
NVDA started by the script replaces a running NVDA and restores it afterwards.

## Running the pass

```bash
cd skills/rgaa-raweb-audit/scripts
node nvda_capture.js check
node nvda_capture.js --findings ../../audit/findings.json --out ../../audit/nvda            # every page of the sample, Chrome
node nvda_capture.js https://x.lu/contact --page P03 --findings findings.json --out nvda      # one page
python3 nvda_review.py ../../audit/nvda --findings ../../audit/findings.json --apply --lang fr > ../../audit/nvda-review.md
python3 build_report.py build ../../audit/findings.annotated.json --grid ../../audit/grille.csv --out rapport.html --pdf rapport.pdf --lang fr
```

Order: scan → bootstrap findings → annotate screenshots → NVDA capture → review `--apply` → build. If the screenshots
were annotated before the NVDA pass, run the review on `findings.annotated.json` (the builder reads that file).

Options: `--browser chrome|firefox|edge|chromium|all` (default: Chrome; `all` = Chrome, Firefox, Edge), `--max-items 400`,
`--wait 1500` after load, `--settle 250` after each command, `--lang fr|en` for the transcript labels.

## Reading the transcripts

The capture writes `<page>-<browser>.json` and `.md`. In the `.md`: the linear reading, each list, then one block per
finding with "on focus" and "line read" phrases. Typical signs, and the criterion to check:

| NVDA says (fr / en) | Check |
|---|---|
| « graphique logo-commune.png » / "graphic logo-commune.png" | 1.1 / 1.3: no alternative, the file name is read |
| « graphique » alone / "graphic" alone, or « lien » alone / "link" alone | 1.1 / 6.2: element without a name |
| « cliquable » / "clickable" before a text | 7.1 / 7.3: scripted control without a role; test the keyboard |
| « édition » / "edit" with no label before it | 11.1: field without an accessible label |
| « bouton » / "button" with nothing else | 11.9 / 7.1: button without a name |
| heading list with levels 1 → 3, or no heading | 9.1 |
| landmark list empty | 9.2 / 12.6: regions not exposed |
| « non sélectionné », « réduit » etc. missing on a custom widget | 7.1: state not exposed |
| nothing announced when a field errors, a dialog opens, content changes | 7.1 / 7.5 / 11.10: status messages and focus management |

A finding carrying `"expect": "regex"` is marked "expected announcement heard" or "NOT heard": write the expectation
in the language of NVDA on that PC (for example `"expect": "Rechercher"` on a search button that should carry that name).

## Counting rule (decided for this project)

* A failure under NVDA makes the criterion **NC** on that page; quote the announcement in the
  finding and keep the transcript as evidence.
* A success is recorded as **C under NVDA, JAWS and VoiceOver to confirm**; the rate stays marked provisional until a
  person runs those, because the standard requires the component to work with every assistive technology of the
  reference environment (and, for NVDA, also with Firefox; a Chrome-only pass is the project's chosen scope). The review script prints statuses to consider; the auditor sets them with `audit_grid.py set`.
* Mock captures change nothing in the grid.

## In the report

With `--apply`, each checked finding gets `finding["nvda"] = [{browser, screenReader, onFocus, lineRead, verdict}]`,
rendered by `build_report.py` as a "Lecteur d'écran (NVDA 2025.x, firefox 1xx)" line in the finding block, and the
test environment list gains "NVDA … + firefox …" entries. Say in the method paragraph which pages and browsers were
captured, and that JAWS, VoiceOver and TalkBack were not run (unless they were, by a person).

## Limits and troubleshooting

* Guidepup reads NVDA's speech; a locked session, a browser window behind another, or a modal dialog stops the capture
  (the script then records fewer lines and a note). Run again.
* Chrome needs `--force-renderer-accessibility` (the script passes it); Firefox exposes accessibility by default.
* Non-focusable elements are given a temporary `tabindex="-1"` to receive the focus for the "on focus" line, then the
  attribute is removed; the "line read" phrase is the browse-mode reading and is the one to quote for 1.x, 9.x, 10.x.
* Elements hidden, inside a closed menu or a dialog, are reported as not visible; open them in a manual pass.
* NVDA verbosity settings change the phrases (punctuation, "visité", levels); keep NVDA's defaults, which
  `@guidepup/setup` installs, for comparable transcripts.
* The linear reading stops when the same phrase repeats or at `--max-items`; very long pages need a higher cap.
