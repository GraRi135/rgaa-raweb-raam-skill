# Accessibility review — Modal component — RAWeb 1.1

**Files reviewed:** `Modal.jsx`, `Modal.css`, `ContactDialog.jsx` (generic modal used for the cookie notice, the session warning and the contact form; contact form instance with 8 s auto-open on the help page).
**Standard:** RAWeb 1.1 (Référentiel d'évaluation de l'accessibilité des sites web, Luxembourg, SIP, published 6 February 2026). Criteria 1.1 to 13.12 are shared with RGAA 4.1.2; test ids below are the RAWeb 1.1 ids (they differ from RGAA for some criteria), copied from the official data.
**Review date:** 4 November 2026.
**Reviewer:** Claude, static code review (no browser, no assistive technology).
**Method:** reading of the three source files; rendering of the "dialog open, both fields in error" state to a static HTML fixture and pre-check with `scan_html.py` (RAWeb mode); contrast measurement of every colour pair declared in `Modal.css` with `contrast.py`; manual pass topic by topic (1, 3, 7, 9, 10, 11, 12, 13) against the RAWeb 1.1 criteria and tests.
**Scope statement (portée):** one component in two states. **No compliance rate (taux de conformité) can be established** from a component review; the rate is a site-level figure computed over the SIP sample. Page-level criteria (8.x, 9.2, 12.x navigation, 14.x, 16.x) are out of scope here.
**Status vocabulary:** NC = non-compliant (non conforme) on the evidence in the code; "to test" = cannot be decided without a browser / keyboard / screen reader. Priority (blocking / major / minor) is the auditor's judgement of user impact, not a RAWeb notion; levels A and AA are equally mandatory.

---

## 1. Summary

**16 non-conformity tickets on 14 criteria** (1.1, 3.1, 3.3, 7.1, 7.3, 7.4, 7.5, 9.1, 10.7, 11.1, 11.10, 11.11, 11.13, 12.8), plus 6 points that need a browser or a screen reader to decide. Every non-conformity below is attributable to the component, so it is repeated on every page where the modal appears (cookie notice on all pages, session warning on authenticated pages, contact form on the help page): under RAWeb status rules each of these criteria will be NC at site level in the SIP audit until the component is fixed.

| # | Criterion [level] | Test(s) failed | Where | Priority |
|---|---|---|---|---|
| T01 | 7.1 [A] Scripts compatible with AT | 7.1.1, 7.1.3 | `Modal.jsx` L12 `<div className="modal">` — no `role="dialog"`, no accessible name | blocking |
| T02 | 9.1 [A] Headings | 9.1.3 | `Modal.jsx` L14 title in a `<span>` | minor |
| T03 | 7.3 [A] Keyboard operability; 7.1 [A] | 7.3.1, 7.1.1, 7.1.3 | `Modal.jsx` L15 close control is a `<div onClick>` | blocking |
| T04 | 1.1 [A] Image alternative | 1.1.5 | `Modal.jsx` L16 `<svg>` close icon | major |
| T05 | 12.8 [A] Focus order; 7.1 [A] | 12.8.2, 7.1.1, 7.1.2 | `Modal.jsx` whole component: no focus management, no modality | blocking |
| T06 | 10.7 [A] Visible focus | 10.7.1 | `Modal.css` L33-37 `outline: none` | blocking |
| T07 | 3.3 [AA] Non-text contrast | 3.3.1 | `Modal.css` L28 close icon `#9aa0a6` on white = 2.64:1 | major |
| T08 | 3.3 [AA] Non-text contrast | 3.3.1 | `Modal.css` L45 field border `#ccc` on white = 1.61:1 | major |
| T09 | 11.1 [A] Field label | 11.1.1 | `ContactDialog.jsx` L42-48, L51-57 placeholder only | blocking |
| T10 | 11.10 [A] Error management (instructions) | 11.10.1, 11.10.5 | `ContactDialog.jsx` L44, L52 unexplained `*` in placeholder, no format | major |
| T11 | 11.10 [A] Error management (errors) | 11.10.3, 11.10.6 | `ContactDialog.jsx` L21-31, L59-61 generic message, no `aria-invalid` | blocking |
| T12 | 3.1 [A] Colour alone | 3.1.2, 3.1.4 | `ContactDialog.jsx` L47, L56, L60 red border + "champs en rouge" | major |
| T13 | 11.11 [AA] Error suggestions | 11.11.1, 11.11.2 | `ContactDialog.jsx` L24, L60 no format / example for the e-mail | major |
| T14 | 7.5 [AA] Status messages | 7.5.2 | `ContactDialog.jsx` L59-61 error paragraph without `role="alert"` | major |
| T15 | 11.13 [AA] Input purpose | 11.13.1 | `ContactDialog.jsx` L42-48 e-mail field without `autocomplete` | major |
| T16 | 7.4 [A] Change of context | 7.4.1 (see also 13.1) | `ContactDialog.jsx` L14-19 auto-open after 8 s | major |

Fix order suggested for the sprint: T01 + T03 + T05 + T06 (the dialog is unusable with a keyboard or a screen reader today), then T09 + T11 + T14 (the form cannot be completed or corrected without sight), then the rest.

---

## 2. Findings (one block per ticket)

### T01 — 7.1 [A] Is each script, if necessary, compatible with assistive technologies?
- **Tests:** 7.1.1 — name, role, value, properties and changes of state of the component are accessible to assistive technologies via an accessibility API; 7.1.3 — the component has a relevant name and a relevant role.
- **Where:** `Modal.jsx` L11-12.
- **Element:** `<div className="modal-backdrop" onClick={onClose}><div className="modal" onClick={(e) => e.stopPropagation()}>`
- **Problem:** the dialog container is a generic `div`. It has no `role="dialog"`, no `aria-modal="true"`, and no accessible name (`aria-labelledby` pointing at the title). When it appears, assistive technologies receive no role, no name and no state change: the screen reader keeps reading the page beneath as if nothing had happened.
- **Impact:** screen-reader users (NVDA, JAWS, VoiceOver, all required by the RAWeb test environment) do not know a dialog opened, what it is for, or that the rest of the page is blocked; voice-control users cannot target "dialog".
- **Fix (recommended):** use the native `<dialog>` element and `showModal()`, which gives the role, the modality, focus handling and Escape for free (full snippet in Appendix A):
  ```jsx
  <dialog ref={ref} className="modal" aria-labelledby={titleId}>
    <div className="modal-content">
      <div className="modal-header">
        <h2 id={titleId} className="modal-title">{title}</h2>
        ...
  ```
  **Fix (if `<dialog>` cannot be used):** `<div role="dialog" aria-modal="true" aria-labelledby={titleId} className="modal">` with an `<h2 id={titleId}>` title, plus the focus management of T05.
- **Priority:** blocking.

### T02 — 9.1 [A] Is the information structured by the appropriate use of headings?
- **Test:** 9.1.3 — each passage of text making up a heading is implemented with `<hx>` or `role="heading"` + `aria-level`.
- **Where:** `Modal.jsx` L14; `Modal.css` L22-25.
- **Element:** `<span className="modal-title">{title}</span>` rendered at 1.4 rem bold.
- **Problem:** the dialog title is visually a heading (it introduces the dialog content) but is a `span`. It does not appear in the headings list screen-reader users navigate with, and it cannot serve as the dialog's name unless it carries an `id`.
- **Impact:** screen-reader users navigating by headings (H key) cannot jump to the dialog's title; combined with T01 the dialog has no name at all.
- **Fix:** `<h2 id={titleId} className="modal-title">{title}</h2>`, referenced by `aria-labelledby` (same change as T01). Keep the visual style on the class. Use `h2` because a dialog is opened from a page that already has an `h1`; if a page opens the modal from a deeper section, the level can be made a prop.
- **Priority:** minor (fixed by T01).

### T03 — 7.3 [A] Is each script operable by keyboard and any pointing device? / 7.1 [A]
- **Tests:** 7.3.1 — each element with a scripted event handler is operable by keyboard and any pointing device, or an equivalent keyboard-operable element is present on the page; 7.1.1 and 7.1.3 — role and name of the component (the close control has neither).
- **Where:** `Modal.jsx` L15-19; `Modal.css` L26-29.
- **Element:** `<div className="modal-close" onClick={onClose}><svg ...>...</svg></div>`
- **Problem:** the only close control is a `div` with a click handler: it is not in the tab order (no native control, no `tabindex`), does not react to Enter or Space, has no role (`button`) and no accessible name. No keyboard-operable equivalent exists: Escape is not handled anywhere and the backdrop close (`Modal.jsx` L11) is pointer-only. `cursor: pointer` on L27 only affects mouse users. The scanner flags 7.3.1 on all three `onClick` handlers (backdrop, `.modal`, `.modal-close`); the `.modal` one is a `stopPropagation` guard and is not a user action, the other two are covered by this ticket and T05.
- **Impact:** keyboard-only users and screen-reader users cannot close the dialog at all; voice-control users have no "Fermer" to say; switch users cannot reach it. With the cookie notice this means they are stuck on every page.
- **Fix:**
  ```jsx
  <button type="button" className="modal-close" onClick={onClose} aria-label="Fermer la fenêtre">
    <svg aria-hidden="true" focusable="false" width="20" height="20" viewBox="0 0 20 20">
      <path d="M4 4l12 12M16 4L4 16" stroke="currentColor" strokeWidth="2" />
    </svg>
  </button>
  ```
  plus Escape handling (native with `<dialog>`; otherwise an `onKeyDown` on the dialog that calls `onClose()` when `event.key === "Escape"`). Add `background: none; border: 0; padding: 8px;` to `.modal-close` so the button is unstyled but keeps a usable hit area.
- **Priority:** blocking.

### T04 — 1.1 [A] Does each image conveying information have a text alternative?
- **Test:** 1.1.5 — each informative `<svg>` has `role="img"` and a text alternative.
- **Where:** `Modal.jsx` L16-18.
- **Element:** `<svg width="20" height="20" viewBox="0 0 20 20"><path d="M4 4l12 12M16 4L4 16" .../></svg>`
- **Problem:** the cross icon is the sole content of the close control, so it conveys information ("close"), yet it has neither `role="img"` + name nor `aria-hidden="true"`. Screen readers either ignore it (the control is then nameless) or announce "graphic" / the path data. Static evidence: scanner FAIL 1.1.5.
- **Impact:** screen-reader users get no meaning from the control (compounds T03).
- **Fix:** once the control is a `<button aria-label="Fermer la fenêtre">` (T03), the icon becomes decorative: mark it `aria-hidden="true" focusable="false"`. This satisfies RAWeb 1.2.4 (decorative `<svg>` has `aria-hidden="true"`), and 1.1.5 no longer applies. Do not add `role="img"` and a name on the icon as well: the name belongs on the button.
- **Priority:** major (fixed together with T03).

### T05 — 12.8 [A] Is the navigation sequence consistent? / 7.1 [A] Compatibility with AT
- **Tests:** 12.8.2 — for each script that inserts content, the navigation sequence remains consistent (the RAWeb procedure checks "correct repositioning of the focus"); 7.1.1 — properties and state changes exposed (modality); 7.1.2 — the component is correctly rendered by assistive technologies.
- **Where:** `Modal.jsx` (whole component); `ContactDialog.jsx` L35-39.
- **Element:** `if (!open) return null; return (<div className="modal-backdrop" ...>` — the dialog is mounted and unmounted with no focus logic.
- **Problem:** four behaviours expected from a modal dialog are missing:
  1. **Opening:** focus is not moved into the dialog. A keyboard user who activated "Contactez-nous" stays on that button; a screen reader does not announce the dialog.
  2. **Modality:** nothing makes the rest of the page inert (`aria-modal`, `inert` or `aria-hidden` on the application root). Tab and screen-reader reading leave the dialog and wander through the page beneath, while the backdrop blocks pointer users: keyboard and screen-reader users and sighted users get different pages.
  3. **Closing:** when `open` becomes false the focused element is removed from the DOM; browsers then reset focus to `<body>`, so the next Tab restarts from the top of the page. Focus is not returned to the "Contactez-nous" button.
  4. **Escape:** no keyboard way to close (see T03).
- **Impact:** keyboard, switch and screen-reader users: the dialog is announced late or never, can be left by accident, and the user is thrown back to the top of the page on close. This is the most likely root cause of the complaints you receive.
- **Fix (recommended):** `<dialog>` + `showModal()` implements all four (focus moves inside, background becomes inert, Escape fires `cancel`, focus returns to the opener on `close()`). Appendix A gives the component. If `<dialog>` cannot be used: on open store `document.activeElement`, focus the `h2` (`tabIndex={-1}`) or the first field, loop Tab/Shift+Tab inside the dialog, set `inert` on the app root (`document.getElementById("root").inert = true`), handle Escape; on close remove `inert` and call `.focus()` on the stored element **before** unmounting.
- **Also check after the fix (12.9.1, keyboard trap):** a focus loop is only acceptable because Escape and the close button let the user leave the dialog; keep both.
- **Priority:** blocking.

### T06 — 10.7 [A] For each element receiving keyboard focus, is the focus visible?
- **Test:** 10.7.1 — the browser's native focus style is not removed or degraded, or an author-defined focus style is visible.
- **Where:** `Modal.css` L33-37.
- **Element:** `.modal-close:focus, .modal input:focus, .modal button:focus { outline: none; }`
- **Problem:** the native focus indicator is removed on every focusable element of the dialog (close control, both fields, "Envoyer") and nothing replaces it in this stylesheet (no `:focus` or `:focus-visible` rule sets an outline, border, box-shadow or background). Unless a global stylesheet we have not seen restores one, this is NC on the static evidence.
- **Impact:** sighted keyboard users cannot see where they are inside the dialog; the "Envoyer" button and the fields are invisible to tabbing.
- **Fix:** delete the rule and add a visible, contrasting indicator (3:1 against white, measured 9.01:1):
  ```css
  .modal :focus-visible {
    outline: 3px solid #1a4b7a;
    outline-offset: 2px;
  }
  ```
  If the reason for `outline: none` was the mouse-click outline, `:focus-visible` already solves it.
- **Priority:** blocking (level A, affects every control of the dialog).

### T07 — 3.3 [AA] Are the colours of user interface components sufficiently contrasted?
- **Test:** 3.3.1 — the contrast ratio between a user interface component in its various states and the adjacent background is at least 3:1.
- **Where:** `Modal.css` L26-29 (`.modal-close { color: #9aa0a6 }`) on `.modal { background: #fff }` L11.
- **Element:** the close cross (`stroke="currentColor"`).
- **Problem:** `#9aa0a6` on `#fff` measures **2.64:1** (`contrast.py`), below 3:1 in the default state. The hover state (`#202124`, 16.1:1) passes but hover is not available to keyboard or touch users.
- **Impact:** low-vision users may not see that the dialog can be closed.
- **Fix:** `.modal-close { color: #5f6368; }` (6.05:1) or reuse `#202124` in all states. Keep the hover darkening if you like, it is not required.
- **Priority:** major.

### T08 — 3.3 [AA] Are the colours of user interface components sufficiently contrasted?
- **Test:** 3.3.1 (same test as T07).
- **Where:** `Modal.css` L41-46.
- **Element:** `.field input, .field textarea { border: 1px solid #ccc; }`
- **Problem:** the border is the only visual boundary of the two fields (white field on white dialog). `#ccc` on `#fff` measures **1.61:1**. The 3.3 special case for native controls whose rendering is not modified does not apply, because the author sets the border. (The error-state border `#d00` measures 5.15:1 and passes.)
- **Impact:** low-vision users cannot find the edges of the fields, i.e. where to click or whether a field exists at all.
- **Fix:** `border: 1px solid #767676;` (4.54:1) or darker; keep `#d00` for the error state.
- **Priority:** major.

### T09 — 11.1 [A] Does each form input field have a label?
- **Test:** 11.1.1 — the field has a `<label for>`, `aria-labelledby`, `aria-label`, `title`, or an adjacent button with a hidden label.
- **Where:** `ContactDialog.jsx` L42-48 and L51-57.
- **Elements:** `<input type="text" placeholder="Votre adresse e-mail *" ...>` and `<textarea placeholder="Votre message *" ...>`
- **Problem:** the only text attached to each field is a `placeholder`. A placeholder is not an accessible name under RAWeb 11.1.1 (scanner FAIL on both fields) and it disappears as soon as the user types, so sighted users also lose the field's purpose while editing.
- **Impact:** screen-reader users hear "edit text" / "edit text multi-line" without knowing what to enter (some screen readers read the placeholder, none of the RAWeb test-environment combinations can be relied on for it); voice-control users cannot say "click adresse e-mail"; users with memory or attention impairments lose the label while typing.
- **Fix:** visible labels bound by `for`/`id` (use `useId()` to keep ids unique if several instances exist):
  ```jsx
  <div className="field">
    <label htmlFor="contact-email">Adresse e-mail (obligatoire)</label>
    <input id="contact-email" type="email" autoComplete="email" required ... />
  </div>
  <div className="field">
    <label htmlFor="contact-message">Votre message (obligatoire)</label>
    <textarea id="contact-message" rows={5} required ... />
  </div>
  ```
  Remove the placeholders or keep them for an example value only (`placeholder="nom@exemple.lu"`), never as the label.
- **Priority:** blocking.

### T10 — 11.10 [A] Is the error management used appropriately? (instructions before input)
- **Tests:** 11.10.1 — the mandatory-field indication is visible and allows the field to be identified by name before input, or the field has `required` / `aria-required="true"`; 11.10.5 — an instruction on the mandatory data type or format is visible and identifies the field before input.
- **Where:** `ContactDialog.jsx` L44 and L52 (`placeholder="... *"`), L24 (e-mail format enforced by regex).
- **Problem:** the mandatory status is conveyed only by an asterisk inside the placeholder: the asterisk is never explained, there is no label to identify the field by name (T09), the indication vanishes on input, and the fields carry neither `required` nor `aria-required`. The e-mail field enforces a format (`x@y.z`) that is not stated anywhere before submission.
- **Impact:** screen-reader users are not told the fields are mandatory; all users discover the e-mail format only through the error.
- **Fix:** either write it in the label (`Adresse e-mail (obligatoire)`) or keep the asterisk and explain it once above the form; add `required` (and `aria-required="true"` for older AT); state the format in the label or in a hint attached with `aria-describedby`:
  ```jsx
  <p id="contact-required-hint">Les champs marqués d'un astérisque (*) sont obligatoires.</p>
  <label htmlFor="contact-email">Adresse e-mail *</label>
  <p id="contact-email-hint">Format attendu : nom@exemple.lu</p>
  <input id="contact-email" type="email" required aria-required="true"
         aria-describedby="contact-email-hint" ... />
  ```
- **Priority:** major.

### T11 — 11.10 [A] Is the error management used appropriately? (errors after submission)
- **Tests:** 11.10.3 — the message for an empty mandatory field is visible and identifies the field by name, or the field has `aria-invalid="true"`; 11.10.6 — the message for a wrong data type/format is visible and identifies the field, or the field has `aria-invalid="true"`. Once `aria-invalid` is used, 11.10.4 and 11.10.7 additionally require the message (and the format instruction) to be in the label or in a passage of text associated with the field.
- **Where:** `ContactDialog.jsx` L21-31 (validation sets `errors.email` / `errors.message` to `true`), L59-61 (single message).
- **Element:** `<p className="error">Veuillez corriger les champs en rouge.</p>`
- **Problem:** one generic sentence for every error; it does not name the field(s) in error nor the kind of error (empty vs. invalid format); no `aria-invalid="true"` on the fields; no message associated with a field. The fields have no name to be identified by anyway (T09).
- **Impact:** screen-reader users cannot find which field is wrong or why; sighted users must guess that "red" refers to the border; the form cannot be corrected without sight.
- **Fix:** per-field messages bound with `aria-describedby`, `aria-invalid` on the field, and a summary that names the fields:
  ```jsx
  <label htmlFor="contact-email">Adresse e-mail *</label>
  <input id="contact-email" type="email" required
         aria-invalid={errors.email ? "true" : undefined}
         aria-describedby={errors.email ? "contact-email-hint contact-email-error" : "contact-email-hint"} ... />
  {errors.email && (
    <p id="contact-email-error" className="error">
      Erreur : l'adresse e-mail est manquante ou invalide. Format attendu : nom@exemple.lu
    </p>
  )}
  ```
  Distinguish the two cases in `submit()` (`errs.email = email ? "format" : "empty"`) so the message can say "est obligatoire" or "n'est pas au format attendu".
- **Priority:** blocking.

### T12 — 3.1 [A] Information must not be provided by colour alone
- **Tests:** 3.1.2 — for each indication of colour given by a text, the information is not given solely by the colour; 3.1.4 — for each CSS property defining a colour and conveying information, the information is not given solely by the colour.
- **Where:** `ContactDialog.jsx` L47 and L56 (`style={{ borderColor: "#d00" }}`), L60 (text).
- **Elements:** red border on the field in error; `Veuillez corriger les champs en rouge.`
- **Problem:** the per-field error state exists only as a red border (CSS colour, 3.1.4), and the text tells the user to look for "the red fields" (3.1.2). Nothing else (icon, text next to the field, `aria-invalid`) identifies the field in error.
- **Impact:** colour-blind users (about 8 % of men), low-vision users with forced colours or high-contrast mode (where author borders are often replaced), and screen-reader users cannot tell which field is in error.
- **Fix:** keep the red border if you like, but add a visible text message next to each field (T11) and, optionally, an error icon with a text alternative; rewrite the summary without colour: `Le formulaire contient 2 erreurs : adresse e-mail, message.`
- **Priority:** major.

### T13 — 11.11 [AA] Is error management accompanied by suggestions to help correct input errors?
- **Tests:** 11.11.1 — for each input error, data types and formats are suggested if necessary; 11.11.2 — examples of expected values are suggested if necessary.
- **Where:** `ContactDialog.jsx` L24 (regex `^[^@\s]+@[^@\s]+\.[^@\s]+$`), L60 (message).
- **Problem:** an e-mail that fails the regex triggers the same "corriger les champs en rouge" sentence: neither the expected format nor an example is suggested. The message field only needs "mandatory", so 11.11 concerns the e-mail field.
- **Impact:** users with cognitive impairments, and anyone unsure what was wrong (a space, a missing dot), cannot correct the entry.
- **Fix:** covered by the per-field message of T11: `Format attendu : nom@exemple.lu`.
- **Priority:** major.

### T14 — 7.5 [AA] Are status messages correctly rendered by assistive technologies?
- **Test:** 7.5.2 — each status message that warns of an error uses `role="alert"`.
- **Where:** `ContactDialog.jsx` L59-61.
- **Element:** `{Object.keys(errors).length > 0 && (<p className="error">Veuillez corriger les champs en rouge.</p>)}`
- **Problem:** the error paragraph is inserted dynamically after submission, focus stays on "Envoyer" (no change of context), so it is a status message in the RAWeb sense; it has no `role="alert"` (or `aria-live`). Screen readers say nothing when it appears.
- **Impact:** a screen-reader user presses Enter on "Envoyer", nothing happens audibly, and the dialog stays open: they do not know the submission failed.
- **Fix:** either `<p role="alert" className="error">Le formulaire contient 2 erreurs : adresse e-mail, message.</p>` (role present in the DOM before the text is injected works best: render the container permanently and fill it), or move focus to the summary / first invalid field on submit (then it is no longer a status message, and the field's `aria-describedby` message is read).
- **Priority:** major.

### T15 — 11.13 [AA] Can the purpose of an input field be identified to facilitate autofill?
- **Test:** 11.13.1 — each field collecting information about the user has an `autocomplete` attribute with a valid, relevant token.
- **Where:** `ContactDialog.jsx` L42-48.
- **Element:** `<input type="text" placeholder="Votre adresse e-mail *" ...>`
- **Problem:** the field collects the user's own e-mail address and has no `autocomplete="email"`. (`type="text"` is also wrong for the data: `type="email"` gives the right virtual keyboard and lets AT announce the expected type.)
- **Impact:** users with motor or cognitive impairments who rely on browser autofill must type the address; the browser cannot propose it.
- **Fix:** `<input id="contact-email" type="email" autoComplete="email" ...>`. The message field is free text, not user data: no `autocomplete` required.
- **Priority:** major.

### T16 — 7.4 [A] For each script that initiates a change of context, is the user warned or in control?
- **Test:** 7.4.1 — the change of context is initiated by an explicit button or link, or the user is warned by text before it is triggered.
- **Where:** `ContactDialog.jsx` L14-19.
- **Element:** `useEffect(() => { if (autoOpen) { const t = setTimeout(() => setOpen(true), 8000); ... } }, [autoOpen]);`
- **Problem:** eight seconds after the help page loads, a modal overlay covers the page and intercepts every pointer interaction (and, once T05 is fixed, takes the focus). This is a change of context in the RAWeb glossary sense (significant re-arrangement of the content, focus moved), triggered by a timer, not by a button or link, with no prior warning. The same pattern will be judged under criterion 13.1 ("does the user have control over each time limit modifying the content"): the user can neither disable nor postpone it, and it fires again on every visit. Note that the modal component is also used for the cookie notice, which is presumably auto-opened on load as well: the same finding applies there.
- **Impact:** screen-reader users lose their place mid-reading; users with cognitive impairments or slow readers are interrupted; keyboard users who were typing in another field are hijacked.
- **Fix:** remove the timer and let "Contactez-nous" open the dialog. If the product owner wants proactive support, use a non-modal, non-focus-stealing invitation that does not block the page, e.g. an `<aside aria-labelledby="help-offer-title">` inserted at the end of the main content with a heading "Besoin d'aide ?" and the "Contactez-nous" button, with `role="status"` on a short sentence if it must be announced. For the cookie notice, prefer a non-modal banner, first in the tab order, that never takes focus automatically.
- **Priority:** major.

---

## 3. Could not be assessed from the code — to test in the SIP environment

RAWeb requires components to work on every listed desktop combination (NVDA + Firefox/Chrome/Edge, JAWS + Firefox/Chrome/Edge, VoiceOver + Safari), not just one. Test these after the fixes:

| Criterion / test | What to check | How |
|---|---|---|
| 7.1.2 | The dialog is announced as "dialogue, Contactez le support" on open, the background is not read, the close button is announced "Fermer la fenêtre, bouton" | NVDA/JAWS/VoiceOver in browse and focus mode |
| 12.9.1 | With the focus loop in place, Escape and the close button both leave the dialog and return focus to "Contactez-nous" | keyboard only |
| 10.4.1, 10.11.1, 10.11.2 | `.modal-backdrop` is `position: fixed; inset: 0; align-items: center` and `.modal` has no `max-height` or `overflow`: at 200 % zoom, or in a 320 px wide / 256 px high window, the form (title + 2 fields + 5-row textarea + button + 24 px padding) may be clipped with no way to scroll to "Envoyer" | browser zoom 200 %, responsive mode 320 × 256; preventive CSS in Appendix A (`max-height: calc(100vh - 2rem); overflow: auto`) |
| 3.2.1 | Placeholder text colour is the browser default (Chrome `#757575` = 4.61:1, Firefox uses opacity on the text colour): measure in the deployed browsers | devtools / contrast tool; moot once placeholders are no longer the labels |
| 13.1.4 | The "session warning" instance of this modal must let the user extend the session (or remove the limit); not visible in these files | open the session-warning instance |
| 12.8.1 | Where the component is mounted in the page determines its position in the tab order when it is not modal (cookie notice) | `render_page.js --tab-order` or manual tabbing |

A finding-free state after these tests is what makes the criteria above compliant; the absence of a finding in this review is not a pass.

---

## 4. Recommendations outside RAWeb non-conformities

- **Feedback after submission:** `submit()` fires the `fetch` and closes the dialog with no success or failure message, and ignores a failed request. Add `<p role="status">Votre message a été envoyé.</p>` near the trigger after a 2xx response (7.5.1 applies to that message once it exists) and keep the dialog open with an error message on failure.
- **Trigger button:** give `<button className="btn-primary" onClick={() => setOpen(true)}>` an explicit `type="button"` so it never submits an enclosing form.
- **Hit area:** the close control is 20 × 20 px. Target size is not a RAWeb 1.1 criterion (WCAG 2.2 only), but 24 × 24 px minimum (padding on the button) reduces mis-taps on mobile.
- **Reuse:** the cookie notice and the session warning inherit every fix above through `Modal.jsx`; the session warning should use `role="alertdialog"` (or `<dialog>` with `aria-labelledby` and `aria-describedby`) because it interrupts the user.

---

## Appendix A — Reference implementation closing T01 to T08

`Modal.jsx` (native `<dialog>`; React 18+; supported by all browsers in the RAWeb test environment):

```jsx
import React, { useEffect, useId, useRef } from "react";
import "./Modal.css";

export default function Modal({ open, onClose, title, children }) {
  const ref = useRef(null);
  const titleId = useId();

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal(); // focus moves inside, page behind becomes inert (T05)
    if (!open && dialog.open) dialog.close();     // focus returns to the opener (T05)
  }, [open]);

  return (
    <dialog
      ref={ref}
      className="modal"
      aria-labelledby={titleId}                       /* T01 */
      onCancel={(e) => { e.preventDefault(); onClose(); }}            /* Escape (T03, T05) */
      onClick={(e) => { if (e.target === e.currentTarget) onClose(); }} /* backdrop click only */
    >
      <div className="modal-content">
        <div className="modal-header">
          <h2 id={titleId} className="modal-title">{title}</h2>   {/* T01, T02 */}
          <button type="button" className="modal-close" onClick={onClose} aria-label="Fermer la fenêtre"> {/* T03 */}
            <svg aria-hidden="true" focusable="false" width="20" height="20" viewBox="0 0 20 20">      {/* T04 */}
              <path d="M4 4l12 12M16 4L4 16" stroke="currentColor" strokeWidth="2" />
            </svg>
          </button>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </dialog>
  );
}
```

`Modal.css` (replaces `.modal-backdrop`, `.modal`, `.modal-close`, the `outline: none` rule and the field border):

```css
.modal {                       /* the <dialog> element */
  border: 0;
  padding: 0;                  /* padding lives on .modal-content so backdrop clicks are unambiguous */
  border-radius: 6px;
  width: min(560px, calc(100vw - 2rem));
  max-height: calc(100vh - 2rem);   /* 10.4 / 10.11: scroll inside instead of clipping */
  overflow: auto;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
.modal::backdrop { background: rgba(0, 0, 0, 0.45); }
.modal-content { padding: 24px; }
.modal-header { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.modal-title { font-size: 1.4rem; font-weight: 700; margin: 0; }
.modal-close {
  background: none; border: 0; padding: 8px; cursor: pointer;
  color: #5f6368;              /* T07: 6.05:1 on white */
}
.modal-close:hover { color: #202124; }
.modal :focus-visible {        /* T06: replaces outline: none */
  outline: 3px solid #1a4b7a;  /* 9.01:1 on white */
  outline-offset: 2px;
}
.field input, .field textarea {
  width: 100%; padding: 8px;
  border: 1px solid #767676;   /* T08: 4.54:1 on white */
}
.field input[aria-invalid="true"], .field textarea[aria-invalid="true"] { border-color: #d00; } /* 5.15:1, with a text message next to it (T11, T12) */
.error { color: #d00; font-size: 0.85rem; }  /* 5.15:1 at 13.6 px: passes 3.2.1 */
```

Notes: `onCancel` keeps React state in sync when the browser closes the dialog on Escape. If the app must support a browser without `<dialog>` (none in the RAWeb baseline), use the ARIA fallback described in T01 and T05 with the same markup inside a `div role="dialog" aria-modal="true"`.

## Appendix B — Evidence

- Rendered fixture scanned (state: dialog open, both fields in error): `help-page-dialog-open-with-errors.html`, built by hand from the JSX; the React `onClick` handlers were written as `onclick` attributes so the scanner sees them. Scanner result (RAWeb 1.1): FAIL 1.1.5 (svg), FAIL 7.3.1 (3 elements with mouse handler not focusable), FAIL 11.1.1 (2 fields), REVIEW 3.1.1 (text refers to colour), REVIEW 9.1.3 (`.modal-title` looks like a heading). Page-level REVIEW lines (8.4, 8.6, 8.7, 12.7) come from the fixture skeleton, not from the component.
- Contrast measurements (`contrast.py`): `#9aa0a6`/`#fff` 2.64:1 FAIL 3:1; `#ccc`/`#fff` 1.61:1 FAIL 3:1; `#d00`/`#fff` 5.15:1 PASS (text 13.6 px and border); `#fff`/`#2b6cb0` 5.42:1 PASS; `#202124`/`#fff` 16.1:1 PASS. Replacement colours: `#5f6368` 6.05:1, `#767676` 4.54:1, `#1a4b7a` 9.01:1.
- Test wording and procedures: RAWeb 1.1 data (accessibilite.public.lu/en/raweb1.1/criteres.html), looked up for 1.1, 1.2, 3.1, 3.2, 3.3, 7.1, 7.3, 7.4, 7.5, 9.1, 10.4, 10.7, 10.11, 11.1, 11.10, 11.11, 11.13, 12.8, 12.9, 13.1.
