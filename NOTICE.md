# Third-party content and licences

The scripts, skill instructions and documentation of this repository are released under the MIT licence
(see `LICENSE`). The reference material bundled under `skills/rgaa-raweb-audit/references/data/` is third-party
content redistributed under its own terms, listed below, which apply to any copy of this repository and to the
packaged skill. The full statement with per-file details is in
`skills/rgaa-raweb-audit/references/data/NOTICE.md`.

| Component | Copyright holder | Licence | Our use |
|---|---|---|---|
| RAWeb 1.1 (criteria, tests, test methodology, glossary), version 1.1 of 6 February 2026, from https://github.com/accessibility-luxembourg/ReferentielAccessibiliteWeb | Service information et presse du gouvernement luxembourgeois (SIP) | [CC-BY 3.0 LU](https://creativecommons.org/licenses/by/3.0/lu/) | Adapted: the Markdown/JSON sources were merged into one JSON file per language with the A/AA level and the per-test methodology; wording unchanged |
| RAAM 1.1 (criteria, methodology, glossary), version 1.1 of 24 February 2025, from https://github.com/accessibility-luxembourg/ReferentielAccessibiliteMobile | SIP; itself derived from DINUM works (DISIC/RGAA, DISIC/rgaa-apps, DISIC/rgaa_methodologie) | CC-BY 3.0 LU | Adapted: merged into one JSON file per language with the level parsed from the technical reference; wording unchanged |
| RGAA 4.1.2 (criteria, tests, test methodology, glossary), version 4.1.2 of 18 April 2023, from https://github.com/DISIC/accessibilite.numerique.gouv.fr | Direction interministérielle du numérique (DINUM), République française | [Licence Ouverte / Open Licence 2.0](https://www.etalab.gouv.fr/licence-ouverte-open-licence/) | Adapted: merged into one JSON file with the per-test methodology; wording unchanged |
| Report wording of the SIP simplified audits (`topics.json`, `solutions.json`) from https://github.com/accessibility-luxembourg/simplA11yGenReport | Information and Press Service (SIP), 2020-2021 | MIT (notice reproduced below) | Copied into `sip-report-wording-fr.json` |
| Statistics and short quotations from the SIP audit reports published on data.public.lu (datasets "audits complets" 2023 and 2024, "audits simplifiés" 2024 and 2025) | SIP | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) | Aggregated figures and quoted sentences in the references; the reports themselves are not redistributed |

The RGAA technical method, and through it RAWeb and RAAM, derives from the RGAA 3 (2017) technical framework,
itself an adapted copy of the AccessiWeb HTML5/ARIA framework, copyright 2013 BrailleNet Association, as stated by
DINUM and the SIP in their own notices. WCAG success-criterion titles are quoted from the W3C Web Content
Accessibility Guidelines 2.1 (W3C document licence), EN 301 549 clause titles from ETSI EN 301 549 v3.2.1.

## MIT notice for the SIP simplified-audit wording

```
MIT License

Copyright (c) 2020-2021 Information and Press Service

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## What the licences require from you

* **CC-BY 3.0 LU** (RAWeb, RAAM): keep the attribution to the SIP, the licence name and link, and say that the
  data was adapted if you change it. No share-alike obligation.
* **Licence Ouverte 2.0** (RGAA): keep the attribution to DINUM with the source and the date of the version used.
* **MIT** (this repository's code, the SIP wording): keep the copyright and permission notices in copies.
* **CC0** (the audit datasets): no obligation; the figures in the references cite their source as a courtesy.

The official, authoritative texts remain the published sites: https://accessibilite.public.lu (RAWeb, RAAM) and
https://accessibilite.numerique.gouv.fr (RGAA). When they change, `scripts/refresh_data.py` regenerates the data
files and `SOURCES.json` records the upstream commits.
