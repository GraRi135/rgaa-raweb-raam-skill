# In-page probes for browser sessions

Short JavaScript snippets that return JSON evidence for RGAA / RAWeb criteria. They run anywhere a page can
execute script: Claude in Chrome's `javascript_tool`, Playwright `page.evaluate` (`render_page.js` style),
the browser devtools console, or a bookmarklet. Each returns a plain object; keep the result as evidence and quote
elements from it in the report. They complement `scan_html.py`: the scanner reads markup, these read the
**rendered** page (computed styles, real focus order, computed names).

Always wrap in `JSON.stringify(...)` when the tool returns strings.

## 1. Page summary (8.x, 9.2, 12.7): lang, title, landmarks, headings, skip link

```js
(() => { const q = s => [...document.querySelectorAll(s)];
const role = e => e.getAttribute('role') || ({HEADER:'banner',NAV:'navigation',MAIN:'main',FOOTER:'contentinfo',ASIDE:'complementary',SEARCH:'search'})[e.tagName] || e.tagName.toLowerCase();
return { lang: document.documentElement.lang, title: document.title,
  landmarks: q('header,nav,main,footer,aside,search,[role=banner],[role=navigation],[role=main],[role=contentinfo],[role=search],[role=complementary]').map(e => ({role: role(e), name: e.getAttribute('aria-label') || e.getAttribute('aria-labelledby') || '', visible: e.offsetWidth > 0})),
  headings: q('h1,h2,h3,h4,h5,h6,[role=heading]').map(h => ({level: h.getAttribute('aria-level') || h.tagName[1], text: h.innerText.trim().slice(0, 80), visible: h.offsetWidth > 0})),
  firstLinks: q('a[href]').slice(0, 5).map(a => ({text: a.innerText.trim().slice(0, 60), href: a.getAttribute('href')})),
  langChanges: q('[lang]').filter(e => e !== document.documentElement).map(e => ({lang: e.lang, text: e.innerText.trim().slice(0, 40)})).slice(0, 50) }; })()
```

## 2. Images and SVG (1.1, 1.2, 1.3)

```js
(() => [...document.querySelectorAll('img, svg, [role=img], input[type=image], area, canvas')].map(e => ({
  tag: e.tagName.toLowerCase(), src: (e.currentSrc || e.getAttribute('src') || '').slice(-60), alt: e.getAttribute('alt'),
  ariaLabel: e.getAttribute('aria-label'), labelledby: e.getAttribute('aria-labelledby'), title: e.getAttribute('title'),
  role: e.getAttribute('role'), ariaHidden: e.getAttribute('aria-hidden'), svgTitle: e.tagName === 'svg' ? (e.querySelector('title')?.textContent || null) : undefined,
  inLink: !!e.closest('a,button'), visible: e.offsetWidth > 0 && getComputedStyle(e).visibility !== 'hidden', w: e.offsetWidth, h: e.offsetHeight })))()
```

## 3. Links and buttons with their computed accessible name (6.1, 6.2, 11.9, 7.1)

Chrome exposes `computedName` / `computedRole` on elements (Chrome 112+); fall back to a manual computation elsewhere.

```js
(() => { const name = e => e.computedName ?? (e.getAttribute('aria-label') || [...(e.getAttribute('aria-labelledby')||'').split(' ')].map(i => document.getElementById(i)?.innerText).join(' ').trim() || e.innerText.trim() || [...e.querySelectorAll('img[alt],svg title')].map(x => x.alt || x.textContent).join(' ').trim() || e.getAttribute('title') || '');
return [...document.querySelectorAll('a[href], button, [role=button], [role=link], input[type=submit], input[type=button], input[type=image], summary')].map(e => ({
  tag: e.tagName.toLowerCase(), role: e.computedRole ?? e.getAttribute('role'), name: name(e).slice(0, 80), visibleText: (e.innerText || e.value || '').trim().slice(0, 60),
  href: e.getAttribute('href'), target: e.getAttribute('target'), tabindex: e.getAttribute('tabindex'), visible: e.offsetWidth > 0 })).filter(x => x.visible); })()
```

Flag: empty `name` (6.2 / 11.9 / 7.1.3), a visible text not contained in the name (6.1.5 / 11.9.2), generic names, `href="#"` with click handlers (7.3).

## 4. Form fields and labels (11.1, 11.2, 11.10, 11.13)

```js
(() => [...document.querySelectorAll('input:not([type=hidden]):not([type=submit]):not([type=button]):not([type=reset]), select, textarea')].map(f => ({
  tag: f.tagName.toLowerCase(), type: f.type, id: f.id, name: f.name, labels: [...(f.labels || [])].map(l => l.innerText.trim().slice(0, 60)),
  ariaLabel: f.getAttribute('aria-label'), labelledby: f.getAttribute('aria-labelledby'), title: f.getAttribute('title'), placeholder: f.placeholder,
  computedName: f.computedName ?? null, required: f.required || f.getAttribute('aria-required') === 'true', invalid: f.getAttribute('aria-invalid'), describedby: f.getAttribute('aria-describedby'),
  autocomplete: f.getAttribute('autocomplete'), inFieldset: !!f.closest('fieldset,[role=group],[role=radiogroup]'), visible: f.offsetWidth > 0 })))()
```

## 5. Focus order and focus visibility (12.8, 12.9, 10.7)

Run, then press Tab repeatedly with the browser's keyboard tool and take a screenshot every few presses: the
script records what receives focus and whether its focus style differs from its blurred style.

```js
(() => { window.__focusLog = []; document.addEventListener('focusin', ev => { const e = ev.target; const r = e.getBoundingClientRect();
  const cs = getComputedStyle(e); window.__focusLog.push({ tag: e.tagName.toLowerCase(), text: (e.innerText || e.value || e.getAttribute('aria-label') || '').trim().slice(0, 50), x: Math.round(r.x), y: Math.round(r.y),
  outline: cs.outlineStyle + ' ' + cs.outlineWidth + ' ' + cs.outlineColor, boxShadow: cs.boxShadow, visible: r.width > 0 && r.height > 0 }); }, true); return 'focus logging started: press Tab, then read window.__focusLog'; })()
```

Read it later with `JSON.stringify(window.__focusLog)`. A sequence that jumps around the page, or an element whose
outline is `none 0px` with `boxShadow: none`, is evidence for 12.8 and 10.7; being unable to leave a component with
Tab or Escape is 12.9.

## 6. Text contrast from computed styles (3.2)

Samples every visible text node's colour against the nearest opaque background colour; transparent layers and images
are not resolved, so confirm low ratios with a contrast tool.

```js
(() => { const lum = c => { const [r,g,b] = c.match(/\d+(\.\d+)?/g).slice(0,3).map(v => v/255).map(v => v <= 0.03928 ? v/12.92 : ((v+0.055)/1.055)**2.4); return 0.2126*r+0.7152*g+0.0722*b; };
const bg = e => { for (let n = e; n; n = n.parentElement) { const c = getComputedStyle(n).backgroundColor; if (c && !/rgba\(\d+, \d+, \d+, 0\)/.test(c) && c !== 'transparent') return c; } return 'rgb(255, 255, 255)'; };
const out = []; const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
while (walker.nextNode()) { const t = walker.currentNode; if (!t.textContent.trim() || !t.parentElement || !t.parentElement.offsetWidth) continue; const e = t.parentElement; const cs = getComputedStyle(e);
  if (cs.visibility === 'hidden' || cs.display === 'none' || cs.opacity === '0') continue; const rb = e.getBoundingClientRect(); if (rb.right < 0 || rb.bottom < 0) continue; const fg = cs.color, b = bg(e); const L1 = lum(fg), L2 = lum(b); const ratio = (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
  const size = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight) >= 700; const large = size >= 24 || (bold && size >= 18.5); if (ratio < (large ? 3 : 4.5)) out.push({text: t.textContent.trim().slice(0, 40), fg, bg: b, ratio: +ratio.toFixed(2), size, bold}); }
return out.slice(0, 60); })()
```

## 7. Reflow and zoom (10.4, 10.11)

With the browser at 320 px wide (or 400 % zoom): `({scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth, overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1})` — horizontal overflow is 10.11 evidence. Text at 200 %: compare `document.body.innerText.length` before and after zoom; clipped or overlapping text is checked on screenshots.

## 8. Content on hover or focus, dialogs, live regions (10.13, 7.1, 7.5)

```js
(() => ({ dialogs: [...document.querySelectorAll('dialog,[role=dialog],[role=alertdialog]')].map(d => ({open: d.open ?? !d.hidden, name: d.getAttribute('aria-label') || d.getAttribute('aria-labelledby'), modal: d.getAttribute('aria-modal')})),
  live: [...document.querySelectorAll('[aria-live],[role=status],[role=alert],[role=log]')].map(e => ({role: e.getAttribute('role'), live: e.getAttribute('aria-live'), text: e.innerText.trim().slice(0, 60)})),
  titles: [...document.querySelectorAll('[title]')].filter(e => e.offsetWidth > 0).length, expandables: [...document.querySelectorAll('[aria-expanded]')].map(e => ({text: e.innerText.trim().slice(0, 40), expanded: e.getAttribute('aria-expanded'), controls: e.getAttribute('aria-controls')})) }))()
```

## 9. Whole rendered DOM for the scanner

`'<!DOCTYPE html>\n' + document.documentElement.outerHTML` — save it to a file and run `scan_html.py` on it when a
shell is available. Pages behind a login or after a cookie banner can only be captured this way or through the
browser's own reading tools.
