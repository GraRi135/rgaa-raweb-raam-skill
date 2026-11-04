# Contributing

## Ways to help

* **Report a wrong finding.** Open an issue with the page or markup, the criterion the skill cited, and what the
  standard actually says. Wrong test numbers and false FAIL lines are the most valuable reports.
* **Add a check to the scanner** (`scripts/scan_html.py`, `scripts/android_audit.py`). Each check adds findings with
  a status (`fail` only when the markup itself violates the test, otherwise `review`), the criterion and test id from
  the bundled data, a message that says what to fix, and the element. Update `references/automation-map.md` so the
  table stays true.
* **Add an eval case.** A folder under `skills/rgaa-raweb-audit/evals/<case-name>/` with `prompt.md`, `case.yaml`,
  one grader file per assertion in `graders/`, and input files in `files/` (see the existing cases for the format).
  Fictional inputs only.
* **Improve the references.** They are read by Claude at run time; keep them factual, cite the standard, and explain
  why a rule exists rather than adding capitalised commands.

## Checks before a pull request

```bash
claude plugin validate .
cd skills/rgaa-raweb-audit
python3 scripts/scan_html.py evals/audit-homepage-raweb/files/index.html --json > /dev/null
python3 scripts/audit_grid.py compute evals/compute-rate-declaration-rgaa/files/grille-audit.csv | head
python3 scripts/android_audit.py analyse evals/audit-android-screen-raam/files/capture/accueil > /dev/null
python3 scripts/criteria.py show 9.2 --standard raweb --tests > /dev/null
```

Running the evals costs real model calls: `claude plugin eval . --allow-tools Write,Edit,Bash --scaffold` from the
skill folder runs every case with and without the skill.

## Licensing of contributions

Code and documentation are MIT. Do not add content from the standards or from SIP/DINUM publications outside the
mechanisms in `scripts/refresh_data.py`, so that `NOTICE.md` stays accurate. No real audit reports of identified
third-party sites in the repository.
