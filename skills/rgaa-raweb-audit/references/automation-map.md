# What can be checked automatically, and what cannot

`scripts/scan_html.py` is a static pre-check. It reads the delivered HTML (or the DOM rendered by `render_page.js`) and
maps each finding to a criterion and test. This table says how far to trust it, criterion by criterion, so that the
report never presents an automated observation as a completed test.

Status vocabulary used by the scanner:

* **FAIL**: the markup itself violates the test (an auditor would record NC). Still quote the element in the report and
  make sure it is visible / in scope (exempt or derogated content does not count).
* **REVIEW**: candidate issue or applicability signal that needs a human decision.
* **INFO**: inventory. It tells you which criteria are applicable on the page.

| Topic | Fully static (FAIL possible) | Needs judgement (REVIEW) | Needs a browser, a keyboard or a screen reader |
|---|---|---|---|
| 1 Images | missing alt / role=img name / svg neither named nor hidden / input image alt / area alt / decorative image carrying title or aria-label (1.1, 1.2) | alt relevance, file-name or generic alt (1.3), captions (1.9), canvas/object/embed (1.1) | whether an image conveys information at all, detailed descriptions (1.6, 1.7), images of text (1.8), CAPTCHA (1.4, 1.5) |
| 2 Frames | missing title (2.1) | generic title (2.2) | title relevance against actual frame content |
| 3 Colours | nothing | text that refers to colour/shape (3.1) | contrast measurement 3.2 (4.5:1 text, 3:1 large text) and 3.3 (3:1 UI components and graphics): compute from rendered colours; use a contrast tool or the browser devtools |
| 4 Multimedia | autoplay with sound and no controls (4.10) | presence of caption / description tracks (4.3, 4.5), media identification (4.7), custom players (4.11, 4.13) | relevance of transcripts, captions, audio description (4.2, 4.4, 4.6); RAWeb 4.14 to 4.18 |
| 5 Tables | layout table using th/caption/scope (5.8) | table without th (5.6 or layout?), scope/headers association (5.7), complex table summary (5.1), caption (5.4) | data vs layout decision, linearised reading order (5.3), relevance of summary and caption (5.2, 5.5) |
| 6 Links | link without accessible name (6.2), aria-label not containing visible text (6.1.5 RAWeb) | generic link text (6.1.1), image links (6.1.2), identical names with different targets (6.1.6 RAWeb) | whether the link context makes a generic link explicit |
| 7 Scripts | ARIA reference to a missing id, unknown role, widget role without name, focusable element with aria-hidden, blur() on focus (7.1, 7.3) | dialogs, live regions, onchange navigation (7.4), mouseover without focus | rendering by assistive technologies (7.1.2), keyboard operation of every component (7.3), status messages (7.5): test with NVDA/VoiceOver and the keyboard, in the baseline environment |
| 8 Mandatory elements | doctype (8.1), duplicate ids/attributes (8.2), missing or invalid lang (8.3, 8.4), missing title (8.5), invalid lang on changes (8.8) | title relevance (8.6), presence of lang on foreign passages (8.7), tags used for layout (8.9) | relevance of the declared language against content |
| 9 Structure | role=heading without level, empty heading (9.1), missing/multiple main, menu outside nav (9.2), li outside list, dt/dd outside dl (9.3) | missing h1 and level jumps (tolerated by the glossary if the hierarchy stays consistent), visual headings not marked up (9.1.3), banner/contentinfo/search landmarks (9.2), textual pseudo-lists (9.3), quotations (9.4) | whether heading content and hierarchy are relevant (9.1.1, 9.1.2) |
| 10 Presentation | presentational tags and attributes (10.1), viewport blocking zoom (10.4) | focus outline removed (10.7), spaced-out letters (10.1.3) | CSS disabled (10.2, 10.3), 200 % zoom (10.4), reflow at 320 px / 256 px (10.11), text spacing (10.12), hover/focus content (10.13, 10.14), shape/position information (10.9, 10.10), hidden content (10.8), link visibility (10.6) |
| 11 Forms | field without label, label for a missing id (11.1), empty label (11.2), ungrouped radio/checkbox series (11.5), fieldset without legend (11.6), empty legend (11.7), button without name (11.9), invalid autocomplete token (11.13) | aria-label-only fields (11.1.3), hidden labels, required fields without visible mark, format hints (11.10), autocomplete on user-data fields (11.13) | label relevance and adjacency (11.2, 11.4), error messages after submission (11.10, 11.11), modification/confirmation of data (11.12), consistency across pages (11.3) |
| 12 Navigation | skip link to a missing target (12.7.2) | no skip link detected (12.7.1), positive tabindex (12.8) | two navigation systems and site map (12.1 to 12.5: site-level), consistent tab order (12.8), keyboard traps (12.9), single-key shortcuts (12.10), hover/focus content reachable by keyboard (12.11) |
| 13 Consultation | meta refresh / delayed meta redirect (13.1), marquee/blink (13.8) | window.open in scripts (13.2), office documents (13.3), CAPTCHA (1.4/1.5) | session time limits and script redirects (13.1), accessible versions of documents (13.3, 13.4), cryptic content (13.5, 13.6), flashes (13.7), CSS/JS animations (13.8), orientation (13.9), gestures and motion (13.10 to 13.12), RAWeb 13.13, 13.14 |
| 14 to 17 (RAWeb) | nothing | nothing | documentation, support service, editing tools, real-time communication: read the documentation, call/test the support, test the tools |

## How to use the scanner inside an audit

1. Run it on every page of the sample (`--render` for client-side apps). Keep the JSON output as evidence.
2. Every FAIL becomes a non-conformity line in the grid, after you have confirmed the element is visible and in scope.
3. Every REVIEW is a to-do for the manual pass. Resolve it to C, NC or NA; never leave it as "to review" in the final grid.
4. INFO items tell you which criteria are applicable (media present, tables present, forms present...). Criteria with no
   inventory signal on any page are the candidates for NA, but check: 12.x, topic 8, 9, 10 and 13 apply to every page
   that has content.
5. The keyboard and screen-reader pass is not optional. If it cannot be performed (no browser, no AT), mark the criteria
   in the last column as **NT** and say so in the report. Do not compute a definitive rate from static evidence alone.

## Rendering helpers (`render_page.js`, needs Node and Playwright)

* `node scripts/render_page.js URL > page.html` then scan it: client-rendered content, cookie banners, injected ARIA.
* `--tab-order` prints the sequence of focused elements and their outline style: evidence for 12.8 (order), 12.9 (loops)
  and 10.7 (outline removed), and a list of what is reachable by keyboard for 7.3.
* `--zoom 200 --screenshot zoom.png` and `--mobile --screenshot m.png`: evidence for 10.4, 10.11 and 13.9.
* Contrast: `python3 scripts/contrast.py FG BG [--size px --bold]` gives the ratio and the 3.2 / 3.3 / 10.7 verdicts;
  `--css file.css` lists the pairs a stylesheet declares (a pair with only one colour declared depends on inheritance:
  read the computed colours in the browser or through Playwright before deciding). The scanner itself does not measure contrast.

## Mobile apps (`android_audit.py`, RAAM 1.1)

| Fully static from the view hierarchy (FAIL) | Needs judgement (REVIEW) | Needs TalkBack / VoiceOver / keyboard |
|---|---|---|
| interactive element without name (5.1), clickable but not focusable (5.2), form field with no label at all (9.2) | role of clickable containers (5.1), image alternatives (1.1 to 1.3), toggle states (5.5), hint used as label (9.1), reading order heuristic (10.2), estimated text contrast from the screenshot (2.2), text truncated or lost at 200 % and orientation lock from `walk` (8.2, 11.9) | how components are announced (5.1), context changes (5.3), status messages (5.4), language (6.1), headings and lists (7.1, 7.2), hidden content (8.1), focus visibility (8.5), keyboard traps (10.3), gestures, motion, time limits (11.x) |

iOS has no collector in this skill: use Accessibility Inspector on macOS and VoiceOver (see `raam-mobile.md`).
