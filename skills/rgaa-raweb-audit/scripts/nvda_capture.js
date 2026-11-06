#!/usr/bin/env node
// nvda_capture.js — drive the real NVDA screen reader on a page and record what it says.
//
// Runs on Windows only (NVDA). Uses Guidepup (https://www.guidepup.dev, MIT) to control NVDA and read its speech,
// and Playwright to open the page in Firefox, Chrome or Edge (the NVDA pairings of the RAWeb / RGAA reference
// environment). Nothing here replaces the auditor: the transcript is evidence to read and quote.
//
//   node nvda_capture.js check                                   # is this machine ready? (Windows, NVDA, Guidepup, browsers)
//   node nvda_capture.js URL --page P01 [--browser firefox|chrome|edge|all] [--findings findings.json] [--out nvda/]
//   node nvda_capture.js --findings findings.json [--browser all] [--out nvda/]   # every page of the sample
//
// Per page and browser it records: the linear reading (NVDA "next" from the top of the document), the lists NVDA
// exposes (headings, links, landmarks, form fields, graphics, tables, lists), and for each finding of the page with a
// selector, what NVDA announces when the element gets the focus and when its line is read.
// Output: <out>/<page>-<browser>.json and .md. Then: python3 nvda_review.py <out>/ --findings findings.json
//
// Options: --max-items N (linear reading cap, default 400), --wait ms (after page load, default 1500),
//          --settle ms (after each command, default 250), --lang fr|en (NVDA interface language, for the .md labels),
//          --mock (no NVDA: phrases derived from the accessibility tree, to test the pipeline on any OS; add --headless on a server),
//          --browser chromium (Playwright's own Chromium, when Chrome is not installed).
//
// Setup on the Windows PC (once): install NVDA, Node and Playwright browsers, then in this folder
//   npm install @guidepup/guidepup playwright   and   npx @guidepup/setup setup
// Keep the session unlocked and do not touch keyboard or mouse during a capture: NVDA reads the focused window.
'use strict';
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const optValues = new Set(['--page', '--browser', '--findings', '--out', '--max-items', '--wait', '--settle', '--lang', '--title']);
const opt = (name, def) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : def; };
const flag = (name) => args.includes(name);
const positional = args.filter((a, i) => !a.startsWith('--') && !(i > 0 && optValues.has(args[i - 1])));
const mode = positional[0] === 'check' ? 'check' : 'capture';
const url = mode === 'capture' ? positional[0] : null;
const browsers = (opt('--browser', 'all') === 'all') ? ['firefox', 'chrome'] : opt('--browser').split(',');
const outDir = opt('--out', 'nvda');
const maxItems = +opt('--max-items', 400);
const waitMs = +opt('--wait', 1500);
const settleMs = +opt('--settle', 250);
const lang = opt('--lang', 'fr');
const mock = flag('--mock');

function loadGuidepup() {
  try { return require('@guidepup/guidepup'); } catch (e) {
    return null;
  }
}
function loadPlaywright() {
  try { return require('playwright'); } catch (e) { return null; }
}
const sleep = (ms) => new Promise(r => setTimeout(r, ms));
const norm = (s) => String(s || '').replace(/\s+/g, ' ').trim();

// ------------------------------------------------------------------ check
async function check() {
  const lines = [];
  const win = process.platform === 'win32';
  lines.push(`platform: ${process.platform} ${win ? '(ok)' : '(NVDA needs Windows; use --mock here to test the pipeline)'}`);
  lines.push(`node: ${process.version}`);
  const pw = loadPlaywright();
  lines.push(`playwright: ${pw ? 'found' : 'MISSING (npm install playwright, then npx playwright install firefox chromium)'}`);
  const g = loadGuidepup();
  lines.push(`@guidepup/guidepup: ${g ? 'found' : 'MISSING (npm install @guidepup/guidepup, then npx @guidepup/setup setup)'}`);
  if (g && win) {
    let det = 'unknown';
    try { det = g.nvda.detect() ? 'NVDA is the default screen reader' : 'NVDA not detected as default (installed? run npx @guidepup/setup setup)'; } catch (e) { det = 'detect failed: ' + e.message; }
    lines.push(`nvda: ${det}`);
  }
  if (pw) {
    for (const [name, launch] of [['firefox', () => pw.firefox.launch()], ['chrome', () => pw.chromium.launch({ channel: 'chrome' })], ['edge', () => pw.chromium.launch({ channel: 'msedge' })]]) {
      try { const b = await launch(); lines.push(`${name}: ok (${b.version()})`); await b.close(); } catch (e) { lines.push(`${name}: not available (${e.message.split('\n')[0]})`); }
    }
  }
  lines.push(win && g && pw ? 'ready: node nvda_capture.js URL --page P01 --findings findings.json' : 'not ready: fix the items marked MISSING / not available');
  console.log(lines.join('\n'));
}

// ------------------------------------------------------------------ NVDA driver (real or mock)
function realDriver(g) {
  const nvda = g.nvda;
  const kc = nvda.keyboardCommands;
  return {
    name: 'NVDA', mock: false,
    version: () => { try { return nvda.version; } catch (e) { return ''; } },
    start: () => nvda.start({ capture: true }),
    stop: () => nvda.stop(),
    top: async () => { await nvda.press('Control+Home'); await sleep(settleMs); return norm(await nvda.lastSpokenPhrase()); },
    next: async () => { await nvda.next(); await sleep(settleMs); return { spoken: norm(await nvda.lastSpokenPhrase()), item: norm(await nvda.itemText()) }; },
    jump: async (what) => {
      const map = { headings: () => nvda.nextHeading(), links: () => nvda.nextLink(), landmarks: () => nvda.nextLandmark(),
        formFields: () => nvda.perform(kc.moveToNextFormField), graphics: () => nvda.perform(kc.moveToNextGraphic),
        tables: () => nvda.perform(kc.moveToNextTable), lists: () => nvda.perform(kc.moveToNextList), buttons: () => nvda.perform(kc.moveToNextButton) };
      await map[what](); await sleep(settleMs);
      return { spoken: norm(await nvda.lastSpokenPhrase()), item: norm(await nvda.itemText()) };
    },
    reportFocus: async () => { await nvda.perform(kc.reportCurrentFocus); await sleep(settleMs); return norm(await nvda.lastSpokenPhrase()); },
    readLine: async () => { await nvda.perform(kc.readLine); await sleep(settleMs); return norm(await nvda.lastSpokenPhrase()); },
    clear: () => nvda.clearSpokenPhraseLog(),
    log: () => nvda.spokenPhraseLog(),
  };
}

// The mock derives phrases from the accessibility tree (Playwright aria snapshot). It exists to test the pipeline
// where NVDA cannot run; its output is NOT screen-reader evidence and is labelled as such.
function mockDriver(getPage) {
  let items = [], pos = -1; const L = lang === 'fr';
  const roleWords = { heading: L ? 'titre' : 'heading', link: L ? 'lien' : 'link', button: L ? 'bouton' : 'button', textbox: L ? 'édition' : 'edit', img: L ? 'graphique' : 'graphic',
    checkbox: L ? 'case à cocher' : 'check box', radio: L ? 'bouton radio' : 'radio button', combobox: L ? 'liste déroulante' : 'combo box', list: L ? 'liste' : 'list', listitem: '', table: L ? 'tableau' : 'table',
    navigation: L ? 'navigation repère' : 'navigation landmark', main: L ? 'principal repère' : 'main landmark', banner: L ? 'bannière repère' : 'banner landmark', contentinfo: L ? 'informations sur le contenu repère' : 'content info landmark', region: L ? 'région' : 'region', text: '' };
  async function build() {
    const page = getPage();
    const snap = await page.locator('body').ariaSnapshot();
    items = [];
    for (const raw of snap.split('\n')) {
      const m = raw.match(/^\s*-\s*([a-z]+)(?:\s+"([^"]*)")?(?:\s*\[level=(\d)\])?(?::\s*(.*))?$/);
      if (!m) continue;
      const [, role, name, level, text] = m;
      const w = roleWords[role] !== undefined ? roleWords[role] : role;
      const label = name || text || '';
      const spoken = role === 'heading' ? `${w} ${L ? 'niveau' : 'level'} ${level || ''} ${label}` : `${w} ${label}`.trim();
      items.push({ role, spoken: norm(spoken), item: norm(label), level: level ? +level : null });
    }
  }
  return {
    name: 'mock (accessibility tree, not NVDA)', mock: true, version: () => 'mock',
    start: async () => {}, stop: async () => {},
    top: async () => { await build(); pos = -1; return items.length ? items[0].spoken : ''; },
    next: async () => { pos = Math.min(pos + 1, items.length - 1); return items[pos] || { spoken: '', item: '' }; },
    jump: async (what) => {
      const roles = { headings: ['heading'], links: ['link'], landmarks: ['navigation', 'main', 'banner', 'contentinfo', 'region'], formFields: ['textbox', 'checkbox', 'radio', 'combobox', 'button'], graphics: ['img'], tables: ['table'], lists: ['list'], buttons: ['button'] }[what];
      for (let i = pos + 1; i < items.length; i++) if (roles.includes(items[i].role)) { pos = i; return items[i]; }
      return { spoken: L ? 'pas de suivant' : 'no next', item: '' };
    },
    reportFocus: async () => { const page = getPage(); return norm(await page.evaluate(() => { const a = document.activeElement; if (!a) return ''; const n = a.getAttribute('aria-label') || a.textContent || a.value || ''; return (a.tagName || '').toLowerCase() + ' ' + n.trim().slice(0, 80); })); },
    readLine: async () => (items[Math.max(pos, 0)] || { spoken: '' }).spoken,
    clear: async () => {}, log: async () => items.map(i => i.spoken),
  };
}

// ------------------------------------------------------------------ capture
const FOCUSABLE = /^(a|button|input|select|textarea|summary|iframe)$/i;
const NO_NEXT = /^(no next|pas de .* suivant|aucun(e)? .* suivant|no (more|previous)|bottom|bas)\b/i;

async function launchBrowser(pw, name) {
  // NVDA needs a visible, focused window; --headless is accepted only with --mock (pipeline tests on a server).
  const headless = mock && flag('--headless');
  if (name === 'firefox') return pw.firefox.launch({ headless });
  if (name === 'edge') return pw.chromium.launch({ headless, channel: 'msedge', args: ['--force-renderer-accessibility'] });
  if (name === 'chromium') return pw.chromium.launch({ headless, args: ['--force-renderer-accessibility'] });
  return pw.chromium.launch({ headless, channel: 'chrome', args: ['--force-renderer-accessibility'] });
}

async function capturePage(pw, drv, browserName, pageUrl, pageId, pageTitle, findings, onPage) {
  const browser = await launchBrowser(pw, browserName);
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await ctx.newPage();
  if (onPage) onPage(page);
  const rec = { page: pageId, title: pageTitle || '', url: pageUrl, browser: browserName, browserVersion: browser.version(), screenReader: drv.name, screenReaderVersion: drv.version(),
    date: new Date().toISOString(), lang, mock: drv.mock, linear: [], lists: {}, findings: [], notes: [] };
  try {
    await page.goto(pageUrl, { waitUntil: 'networkidle', timeout: 60000 }).catch(e => rec.notes.push('load: ' + e.message.split('\n')[0]));
    await page.bringToFront();
    await sleep(waitMs);
    // 1. linear reading from the top
    await drv.clear();
    rec.top = await drv.top();
    let last = null, repeats = 0;
    for (let i = 0; i < maxItems; i++) {
      const r = await drv.next();
      if (r.spoken === last) { repeats++; if (repeats >= 3) break; } else repeats = 0;   // the last line repeats at the end of the document
      last = r.spoken;
      rec.linear.push({ i: i + 1, spoken: r.spoken, item: r.item });
    }
    if (rec.linear.length >= maxItems) rec.notes.push(`linear reading stopped at --max-items ${maxItems}`);
    // 2. structure lists
    for (const what of ['headings', 'links', 'landmarks', 'formFields', 'graphics', 'tables', 'lists']) {
      await drv.top(); const out = []; let prev = null, same = 0;
      for (let i = 0; i < 200; i++) {
        const r = await drv.jump(what);
        if (!r.spoken || NO_NEXT.test(r.spoken)) break;
        if (r.spoken === prev) { same++; if (same >= 1) break; } else same = 0;
        prev = r.spoken; out.push({ spoken: r.spoken, item: r.item });
      }
      rec.lists[what] = out;
    }
    // 3. per-finding checks
    for (const f of findings) {
      const entry = { id: f.id, criterion: f.criterion, test: f.test, selector: f.selector, expect: f.expect || null };
      if (!f.selector) { entry.note = 'no selector'; rec.findings.push(entry); continue; }
      try {
        const loc = page.locator(f.selector).first();
        if (await loc.count() === 0) { entry.note = 'selector not found'; rec.findings.push(entry); continue; }
        await loc.scrollIntoViewIfNeeded().catch(() => {});
        entry.visible = await loc.isVisible();
        entry.tag = await loc.evaluate(e => e.tagName.toLowerCase());
        entry.focusable = await loc.evaluate(e => { const t = e.tagName.toLowerCase(); const ti = e.getAttribute('tabindex'); return (/^(a|button|input|select|textarea|summary|iframe)$/.test(t) && !(t === 'a' && !e.hasAttribute('href'))) || (ti !== null && +ti >= 0); });
        await drv.clear();
        if (entry.focusable) { await loc.focus(); }
        else { await loc.evaluate(e => { e.setAttribute('data-nvda-tmp', '1'); e.tabIndex = -1; e.focus(); }); }
        await sleep(settleMs);
        entry.onFocus = await drv.reportFocus();
        entry.lineRead = await drv.readLine();
        if (!entry.focusable) await loc.evaluate(e => { e.removeAttribute('tabindex'); e.removeAttribute('data-nvda-tmp'); }).catch(() => {});
        const heard = `${entry.onFocus} | ${entry.lineRead}`;
        if (f.expect) { try { entry.verdict = new RegExp(f.expect, 'i').test(heard) ? 'expected announcement heard' : 'expected announcement NOT heard'; } catch (e) { entry.verdict = 'bad expect regex'; } }
        else entry.verdict = 'to read';
      } catch (e) { entry.note = 'check failed: ' + e.message.split('\n')[0]; }
      rec.findings.push(entry);
    }
    rec.fullLog = await drv.log();
  } finally {
    await browser.close().catch(() => {});
  }
  return rec;
}

function toMarkdown(rec) {
  const L = lang === 'fr';
  const h = [];
  h.push(`# ${L ? 'Lecteur d\'écran' : 'Screen reader'} — ${rec.page} ${rec.title ? '· ' + rec.title : ''} — ${rec.browser} ${rec.browserVersion}`);
  h.push('');
  h.push(`${L ? 'Outil' : 'Tool'} : ${rec.screenReader} ${rec.screenReaderVersion} · ${rec.date} · ${rec.url}`);
  if (rec.mock) h.push(`**${L ? 'MODE SIMULÉ : ces phrases viennent de l\'arbre d\'accessibilité, pas de NVDA. Ce n\'est pas une preuve de restitution.' : 'MOCK MODE: phrases come from the accessibility tree, not from NVDA. This is not screen-reader evidence.'}**`);
  if (rec.notes.length) h.push(`${L ? 'Notes' : 'Notes'} : ${rec.notes.join(' ; ')}`);
  h.push('', `## ${L ? 'Lecture linéaire' : 'Linear reading'} (${rec.linear.length})`, '');
  rec.linear.forEach(x => h.push(`${x.i}. ${x.spoken}`));
  for (const [k, v] of Object.entries(rec.lists)) { h.push('', `## ${k} (${v.length})`, ''); v.forEach((x, i) => h.push(`${i + 1}. ${x.spoken}`)); }
  if (rec.findings.length) {
    h.push('', `## ${L ? 'Constats' : 'Findings'}`, '');
    for (const f of rec.findings) {
      h.push(`### ${f.id} — ${f.criterion || ''} ${f.test || ''}`);
      h.push(`- ${L ? 'sélecteur' : 'selector'} : \`${f.selector || ''}\`${f.note ? ' — ' + f.note : ''}`);
      if (f.onFocus !== undefined) h.push(`- ${L ? 'au focus' : 'on focus'} : « ${f.onFocus} »`);
      if (f.lineRead !== undefined) h.push(`- ${L ? 'ligne lue' : 'line read'} : « ${f.lineRead} »`);
      if (f.verdict) h.push(`- ${L ? 'verdict' : 'verdict'} : ${f.verdict}${f.expect ? ' (' + (L ? 'attendu' : 'expected') + ' /' + f.expect + '/)' : ''}`);
      h.push('');
    }
  }
  return h.join('\n') + '\n';
}

async function main() {
  if (mode === 'check') return check();
  const findingsFile = opt('--findings', null);
  let doc = { findings: [], sample: [] };
  if (findingsFile) doc = JSON.parse(fs.readFileSync(findingsFile, 'utf8'));
  const allFindings = Array.isArray(doc) ? doc : (doc.findings || []);
  const pages = [];
  if (url) pages.push({ id: opt('--page', 'P01'), title: opt('--title', ''), url });
  else {
    for (const s of (doc.sample || [])) if (s.url && /^[a-z][a-z0-9+.-]*:/i.test(s.url)) pages.push({ id: s.id, title: s.title || '', url: s.url });
    if (!pages.length) { console.error('usage: node nvda_capture.js URL --page P01 [--findings findings.json] | --findings findings.json (sample with URLs) | check'); process.exit(2); }
  }
  const pw = loadPlaywright(); if (!pw) { console.error('playwright is not installed: npm install playwright && npx playwright install firefox chromium'); process.exit(2); }
  let drv;
  if (mock) drv = null; // created per page (needs the page)
  else {
    if (process.platform !== 'win32') { console.error('NVDA runs on Windows only. On this machine use --mock to test the pipeline, or run this script on the Windows PC.'); process.exit(2); }
    const g = loadGuidepup(); if (!g) { console.error('@guidepup/guidepup is not installed: npm install @guidepup/guidepup && npx @guidepup/setup setup'); process.exit(2); }
    drv = realDriver(g);
  }
  fs.mkdirSync(outDir, { recursive: true });
  const same = (a, b) => a.replace(/#.*$/, '').replace(/\/$/, '') === b.replace(/#.*$/, '').replace(/\/$/, '');
  const written = [];
  if (drv) { console.log('starting NVDA…'); await drv.start(); }
  try {
    for (const p of pages) {
      const findings = allFindings.filter(f => f.selector && (f.url ? same(f.url, p.url) : (f.pages || []).includes(p.id)));
      for (const b of browsers) {
        console.log(`${p.id} ${p.url} — ${b} — ${findings.length} finding(s)`);
        let pageRef = null; const d = drv || mockDriver(() => pageRef);
        const rec = await capturePage(pw, d, b, p.url, p.id, p.title, findings, pg => { pageRef = pg; });
        const base = path.join(outDir, `${p.id}-${b}`.replace(/[^A-Za-z0-9_-]+/g, '-'));
        fs.writeFileSync(base + '.json', JSON.stringify(rec, null, 1));
        fs.writeFileSync(base + '.md', toMarkdown(rec));
        written.push(base + '.json');
        console.log(`  wrote ${base}.json (${rec.linear.length} lines, ${Object.values(rec.lists).reduce((a, v) => a + v.length, 0)} list items, ${rec.findings.length} finding checks)`);
      }
    }
  } finally { if (drv) await drv.stop().catch(() => {}); }
  console.log(`done: ${written.length} capture(s) in ${outDir}/ — next: python3 nvda_review.py ${outDir}/${findingsFile ? ' --findings ' + findingsFile : ''}`);
}

main().catch(e => { console.error(e && e.stack || e); process.exit(1); });
