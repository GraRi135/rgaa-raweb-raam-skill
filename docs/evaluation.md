# How the skill was evaluated

The skill was built with Anthropic's skill-creator loop: write a draft, run realistic tasks with and without the
skill, grade the outputs on written assertions, improve, repeat. Everything below is reproducible with the cases in
`skills/rgaa-raweb-audit/evals/` (Claude Code can run them with `claude plugin eval`).

## Test cases

| Case | Input | What a good answer does |
|---|---|---|
| audit-homepage-raweb | a fictional Luxembourg commune homepage with 30+ planted defects | lists them with RAWeb criterion and test ids and a fix each, separates verified from untested, gives no rate |
| compute-rate-declaration-rgaa | a 9-page RGAA grid with traps (criteria NA on some pages, a 3-page process) | finds 67.1 % and "partiellement conforme", not the 93 % page average or 50 %; drafts the statement in the mandatory format without inventing facts |
| review-react-modal-raweb | a React modal with a dozen accessibility bugs | ticket-ready findings with correct RAWeb criterion and test ids (7.1, 7.3, 12.8, 10.7, 1.2, 11.1, 11.10, 3.1, 11.13) |
| audit-android-screen-raam | a synthetic uiautomator capture at font scale 1.0 and 2.0 | RAAM numbering (5.1, 5.2, 9.2, 2.2, 8.2), Android fixes, list of what needs TalkBack |

## Results

| Round | With the skill | Without the skill |
|---|---|---|
| Web cases, round 1 (3 cases, 36 assertions) | 36 / 36 | 33 / 36 |
| Web cases, round 2 after improvements (38 assertions) | 38 / 38 | 33 / 38 |
| Android case (12 assertions) | 12 / 12 | 5 / 12 |

The model already knows the criteria well; the skill's measurable value is where memory fails: the exact scope of
RAWeb 1.1 (136 criteria, not 106), test numbers matching the official wording, RAAM's 15-topic numbering (the baseline
cited a remembered 12-topic structure), refusing a rate from one page, and not inventing facts in a statement. Round 2
also cut the skill's token cost by 15 to 35 % by telling Claude which reference to read for which request.

## Calibration against real audits

The Luxembourg SIP publishes its monitoring reports on data.public.lu (CC0). 228 of them (42 full audits, 186
simplified) were mined for the structure and wording of reports and for the most frequent findings; the results are in
`skills/rgaa-raweb-audit/references/sip-audit-corpus.md` and `skills/rgaa-raweb-audit/references/raam-mobile.md` and drive the "test first what fails most" guidance.

Two real Luxembourg public sites were then audited with the skill as a test, on the SIP's own samples, and the
findings compared with the SIP's published cases. Those test reports are not published here because they concern
third-party sites and were produced without assistive technologies.

## Known weaknesses

* No screen reader anywhere in the loop: the largest class of criteria stays "not tested".
* Contrast is computed from declared or dominant colours; text over images and gradients needs a manual measure.
* The scanner's REVIEW heuristics (generic link text, visual headings, suspicious alt) over-report on large pages.
* A full site audit with the skill costs 200k tokens or more per run.
