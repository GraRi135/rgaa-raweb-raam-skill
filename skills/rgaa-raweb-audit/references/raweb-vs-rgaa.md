# RAWeb 1.1 versus RGAA 4.1.2

Read this when the audit targets Luxembourg (RAWeb) or when a client, grid or tool mixes the two standards.
`python3 scripts/criteria.py diff` prints the machine-generated list; this file explains what the differences mean for an auditor.

## Family tree

* **RGAA 4.1.2** (France, DINUM, published 18 April 2023): 13 topics, 106 criteria, 258 tests. Legal basis: article 47 of
  law 2005-102, decree 2019-768. Covers WCAG 2.1 A and AA for web pages.
* **RAWeb 1.0** (Luxembourg, SIP, 2023): an adapted copy of RGAA 4.1.2 referencing Luxembourg law.
* **RAWeb 1.1** (Luxembourg, SIP, published 6 February 2026): 17 topics, 136 criteria, 304 tests. Adds the web-relevant
  requirements of **EN 301 549 v3.2.1** that go beyond WCAG (chapters 6, 7, 11, 12), so that a RAWeb audit covers the whole
  harmonised standard. Legal basis: law of 28 May 2019 (public sector) and law of 8 March 2023 (products and services,
  monitored by OSAPS).

Criteria **1.1 to 13.12 keep the same numbers and the same intent** in both standards. A finding you would report under
RGAA 11.10 is also 11.10 in RAWeb. Levels (A/AA) are identical.

## The 30 criteria that exist only in RAWeb 1.1

| Criteria | Topic | What they cover (EN 301 549 clause) |
|---|---|---|
| 4.14 – 4.18 | Multimedia | Caption/audio-description controls at the same level as main controls (7.3), preservation of captions and audio description through conversion/transmission (7.1.2, 7.2.2), user control of caption presentation (7.1.4), spoken subtitles (7.1.5) |
| 13.13 | Consultation | Document conversion tools keep accessibility information (11.8.4) |
| 13.14 | Consultation | Biometric identification has an alternative (5.3) |
| 14.1 – 14.3 | Documentation and accessibility features | Product documentation describes accessibility features, activation mechanisms work, documentation itself is accessible (12.1) |
| 15.1 – 15.6 | Editing tools | Authoring tools (CMS, editors, generators) support accessible output, help, repair suggestions, accessible templates (11.8) |
| 16.1 – 16.3 | Support services | Help desk / support knows the accessibility features, communicates in ways suited to disabled users, its documentation is accessible (12.2) |
| 17.1 – 17.11 | Real-time communication | Two-way voice/video/RTT web apps: audio bandwidth, real-time text, simultaneous voice and text, caller id, speaker/signer indication, video quality (6.x) |

Most sites have **no** real-time communication, editing tool or biometric feature: those criteria are then not applicable,
and not applicable criteria never lower the rate. But topics 14 and 16 are applicable to almost every site: check the
accessibility page / help documentation and the support contact. Treat 12.3, topic 14 and topic 16 as site-level criteria:
evaluate them once (for instance on the accessibility page) and mark them NA on the other pages.

## Shared criteria that RAWeb 1.1 changed

Backward-incompatible changes flagged by the SIP changelog (an implementation compliant under RGAA / RAWeb 1.0 can fail
RAWeb 1.1):

* **1.2 decorative images**: `role="presentation"` or `role="none"` is accepted only when the image has no `title`,
  `aria-label` or `aria-labelledby`. Title in the criterion now says "without a caption". Technical note on `aria-hidden`
  set on a parent. RAWeb also dropped the conditions on `<svg>` naming properties.
* **13.5 cryptic content** (ASCII art, emoticons, cryptic syntax): `<abbr>` + `title` is no longer a compliant method.
  Meaning must be in the adjacent context or exposed by an accessibility-supported method; a second test (13.5.2)
  requires cryptic content that is purely decorative to be `aria-hidden="true"`.

Changes in the number of tests (cite the right test id):

| Criterion | RGAA 4.1.2 | RAWeb 1.1 | Note |
|---|---|---|---|
| 4.3 captions | 2 tests | 3 tests | adds a test for synchronised media delivered as audio + video alternative |
| 4.4 caption relevance | 1 | 2 | |
| 5.7 cell/header association | 5 | 6 | |
| 6.1 explicit links | 5 | 6 | RAWeb adds 6.1.5 "accessible name contains the visible label" and 6.1.6 "identical links have the same destination"; RGAA treats label-in-name under 6.1 generically |
| 8.1 doctype | 3 (present, valid, before `<html>`) | 1 | RAWeb merges the three conditions |
| 9.2 document structure | 1 | 4 | RAWeb reasons in **computed roles** (banner, navigation, search, main, contentinfo), adds the search landmark, uniqueness of main/banner/contentinfo, and a test on `<nav>` reserved to navigation |
| 13.5 cryptic content | 1 | 2 | see above |

Wording changes with the same number of tests (RAWeb 1.1 clarifies or tightens): 1.3, 1.4, 1.6, 1.7, 1.9, 6.2 (link
"accessible name" rather than "intitulé"), 8.2 (what counts as an invalidating error), 10.2, 10.7, 10.12, 10.13, 11.1, 11.2,
11.10 (mandatory/optional indications, error message placement), 12.5, 12.6, 12.10, 13.6, 13.7, 13.8, 13.9.
Read the RAWeb wording with `criteria.py show <id> --tests` before citing a test in a Luxembourg audit.

## Method and legal differences that change the report

| Point | RGAA 4.1.2 (France) | RAWeb 1.1 (Luxembourg) |
|---|---|---|
| Test environment | a component is "accessibility compatible" if it works on **at least one** listed combination (NVDA+Firefox, JAWS+Firefox/IE, VoiceOver+Safari) | it must work on **all** listed desktop combinations (NVDA + Firefox/Chrome/Edge, JAWS previous version + Firefox/Chrome/Edge, VoiceOver + Safari); mobile: TalkBack+Chrome or VoiceOver+Safari, both recommended for public sites |
| Sample | home, contact, legal notice, accessibility, site map, help, authentication, + one page per service, downloadable document, full processes, distinct page types, +10 % random | same list plus documentation pages, support-service documentation; entities under the law of 8 March 2023 add service-specific pages (e.g. banking: account list, transfer, 3D Secure, secure messaging, purchase funnel) |
| Compliance status thresholds | fully = 100 %, partially ≥ 50 %, non-compliant < 50 % or no valid audit | identical |
| Statement validity | update on substantial change, after 3 years, or 18 months after a new RGAA version | update regularly, on substantial change; link sent to the SIP (accessibilite@sip.etat.lu) within 30 days of publication |
| Complaint handling | answer within one week (code des relations entre le public et l'administration) | answer within one month |
| Escalation route named in the statement | Défenseur des droits | Service information et presse (SIP) or the Ombudsman (Médiateur) |
| Average page rate | optional figure in the statement | not mentioned |
| Audit tool | Ara (ara.numerique.gouv.fr) | SIP audit kit; statement generator at accessibilite.public.lu/en/tools/decla.html |
| Language of the deliverable | French | French, German or Luxembourgish; English common for international audiences |

## Choosing the standard

* Site or app of a French public body, or a French supplier contract that names the RGAA: **RGAA 4.1.2**, report in French.
* Luxembourg public body, or a Luxembourg entity under the law of 8 March 2023: **RAWeb 1.1**, in the language of the
  request. Say explicitly that criteria 1.1 to 13.12 are shared with RGAA 4.1.2 when the reader knows RGAA.
* Private company elsewhere in the EU wanting EN 301 549 / European Accessibility Act evidence: RAWeb 1.1 is the most
  complete operational transcription of the standard for web content; present it as such.
* A grid or tool that only has 106 criteria is RGAA (or RAWeb 1.0): do not add the 30 RAWeb 1.1 criteria to it silently;
  say which version the grid follows.
