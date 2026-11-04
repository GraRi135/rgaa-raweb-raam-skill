#!/usr/bin/env node
// Render a page with a real browser and print the DOM after JavaScript ran, so that
// scan_html.py can analyse single-page applications and client-rendered content.
//
//   node render_page.js https://example.lu/ > page.rendered.html
//   node render_page.js https://example.lu/ --wait 3000 --width 1280 --screenshot page.png
//   node render_page.js https://example.lu/ --mobile          (375x812, touch, mobile UA)
//   node render_page.js https://example.lu/ --zoom 200        (CSS zoom 200 %: evidence for 10.4 / 10.11)
//   node render_page.js https://example.lu/ --tab-order       (prints the sequence of focusable elements: 12.8 / 12.9)
//   node render_page.js --annotate findings.json --out shots/  (one clipped screenshot per finding: element outlined, markup badge)
//   node render_page.js --print report.html --pdf report.pdf   (print an HTML report to A4 PDF)
//
// --annotate reads a findings file (see references/report-builder.md): each finding with "url" and "selector" gets
// a PNG in --out and its "screenshot" field set; the updated file is written next to the input as *.annotated.json.
//
// Requires Playwright (npm i playwright  then  npx playwright install chromium), or a pre-installed
// browser; set PLAYWRIGHT_CHROMIUM_PATH to a Chrome/Chromium binary if auto-detection fails.
const args = process.argv.slice(2);
const opt = (name, def) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : def; };
const flag = name => args.includes(name);
const optValues = new Set(['--wait', '--width', '--height', '--zoom', '--screenshot', '--annotate', '--out', '--print', '--pdf', '--margin']);
const url = args.find((a, i) => !a.startsWith('--') && !(i > 0 && optValues.has(args[i - 1])));
for (const k of ['--wait', '--width', '--height', '--zoom', '--margin']) { const v = opt(k, null); if (v !== null && (v === true || isNaN(+v))) { console.error(k + ' expects a number, got ' + JSON.stringify(v)); process.exit(2); } }
if (!url && !opt('--annotate') && !opt('--print')) { console.error('usage: render_page.js <url> [--wait ms] [--width px] [--mobile] [--zoom pct] [--screenshot file] [--tab-order] | --annotate findings.json --out dir | --print report.html --pdf report.pdf'); process.exit(2); }

async function launch(pw) {
  const launchOpts = {};
  if (process.env.PLAYWRIGHT_CHROMIUM_PATH) launchOpts.executablePath = process.env.PLAYWRIGHT_CHROMIUM_PATH;
  return pw.chromium.launch(launchOpts);
}

// Draw a red outline around the element and a devtools-style badge with its start tag, then return the clip box.
const OVERLAY = ({sel, badgeText}) => {
  const el = document.querySelector(sel); if (!el) return null;
  el.scrollIntoView({block: 'center', inline: 'nearest'});
  const r = el.getBoundingClientRect(); if (r.width === 0 && r.height === 0) return {hidden: true};
  document.querySelectorAll('.__a11y_overlay').forEach(n => n.remove());
  const sx = window.scrollX, sy = window.scrollY;
  const box = document.createElement('div'); box.className = '__a11y_overlay';
  box.style.cssText = 'position:absolute;z-index:2147483646;pointer-events:none;border:3px solid #d0021b;box-shadow:0 0 0 2px #fff;border-radius:2px;left:' + (r.left + sx - 3) + 'px;top:' + (r.top + sy - 3) + 'px;width:' + (r.width + 3) + 'px;height:' + (r.height + 3) + 'px;';
  const badge = document.createElement('div'); badge.className = '__a11y_overlay'; badge.textContent = badgeText;
  badge.style.cssText = 'position:absolute;z-index:2147483647;pointer-events:none;font:12px/1.4 Menlo,Consolas,monospace;color:#fff;background:#1f1f1f;border:2px solid #d0021b;padding:2px 6px;max-width:' + Math.max(260, Math.min(640, r.width + 200)) + 'px;white-space:pre-wrap;word-break:break-all;left:' + Math.max(4, r.left + sx - 3) + 'px;top:0;';
  document.body.appendChild(box); document.body.appendChild(badge);
  // Place the badge entirely outside the outlined element: above it when there is room, else below it.
  const bh = badge.getBoundingClientRect().height;
  const above = (r.top + sy) > bh + 8;
  badge.style.top = (above ? (r.top + sy - bh - 6) : (r.top + sy + r.height + 8)) + 'px';
  const b = badge.getBoundingClientRect();
  const top = Math.min(r.top, b.top) + sy, left = Math.min(r.left, b.left) + sx, right = Math.max(r.right, b.right) + sx, bottom = Math.max(r.bottom, b.bottom) + sy;
  return {x: left, y: top, w: right - left, h: bottom - top, pageW: document.documentElement.scrollWidth, pageH: document.documentElement.scrollHeight};
};

async function annotate(pw) {
  const fs = require('fs'); const path = require('path');
  const file = opt('--annotate'); const outDir = opt('--out', 'screenshots'); const margin = +opt('--margin', 60);
  fs.mkdirSync(outDir, {recursive: true});
  const data = JSON.parse(fs.readFileSync(file, 'utf8'));
  const findings = Array.isArray(data) ? data : (data.findings || []);
  const browser = await launch(pw);
  const ctx = await browser.newContext({viewport: {width: +opt('--width', 1280), height: +opt('--height', 900)}});
  const page = await ctx.newPage(); let current = null; let done = 0, skipped = 0;
  for (const f of findings) {
    if (!f.url || !f.selector) { skipped++; continue; }
    try {
      // A "url" that is not a URL (no scheme) is a local HTML file, relative to the findings file.
      const pageUrl = /^[a-z][a-z0-9+.-]*:/i.test(f.url) ? f.url : 'file://' + path.resolve(path.dirname(path.resolve(file)), f.url);
      if (current !== pageUrl) { await page.goto(pageUrl, {waitUntil: 'networkidle', timeout: 60000}).catch(() => {}); await page.waitForTimeout(+opt('--wait', 800)); current = pageUrl; }
      // Optional per-finding preparation: "click" (a selector, or a list of them) opens a menu, tab or accordion panel
      // before the element is outlined; the page is reloaded for the next finding so the click does not leak.
      // "hover" moves the pointer over selectors (hover-driven menus); "focus" + "press" (default "Enter") drive a
      // keyboard-only trigger; "wait" (ms, default 400) lets transitions finish. A failed step is noted in
      // screenshot_note and the screenshot is attempted anyway.
      const list = v => (Array.isArray(v) ? v : [v]); const pause = f.wait != null ? +f.wait : 400; const notes = [];
      if (f.hover) { for (const c of list(f.hover)) { await page.hover(c, {timeout: 5000}).catch(e => notes.push('hover failed on ' + c + ': ' + e.message.split('\n')[0])); await page.waitForTimeout(pause); } current = null; }
      if (f.click) { for (const c of list(f.click)) { await page.click(c, {timeout: 5000}).catch(e => notes.push('click failed on ' + c + ': ' + e.message.split('\n')[0])); await page.waitForTimeout(pause); } current = null; }
      if (f.focus) { await page.focus(f.focus, {timeout: 5000}).catch(e => notes.push('focus failed on ' + f.focus + ': ' + e.message.split('\n')[0])); for (const k of list(f.press || 'Enter')) { await page.keyboard.press(k); await page.waitForTimeout(pause); } current = null; }
      if (notes.length) f.screenshot_note = notes.join('; ');
      const m = f.margin != null ? +f.margin : margin;
      const badge = f.badge || (f.element ? String(f.element).slice(0, 160) : f.selector);
      const box = await page.evaluate(OVERLAY, {sel: f.selector, badgeText: badge});
      if (!box || box.hidden) { f.screenshot_note = box ? 'element not visible (hidden or zero size)' : 'selector not found on the rendered page'; skipped++; continue; }
      const x = Math.max(0, box.x - m), y = Math.max(0, box.y - m);
      const w = Math.min(box.pageW - x, box.w + 2 * m), h = Math.min(box.pageH - y, box.h + 2 * m);
      const name = (f.id || ('finding-' + (done + 1))).replace(/[^A-Za-z0-9_-]+/g, '-') + '.png';
      const target = path.resolve(outDir, name);
      await page.screenshot({path: target, fullPage: true, clip: {x, y, width: Math.max(w, 40), height: Math.max(h, 40)}});
      f.screenshot = path.relative(path.dirname(path.resolve(file)), target); if (!notes.length) delete f.screenshot_note; done++;
      await page.evaluate(() => document.querySelectorAll('.__a11y_overlay').forEach(n => n.remove()));
    } catch (e) { f.screenshot_note = 'screenshot failed: ' + e.message.split('\n')[0]; skipped++; }
  }
  await browser.close();
  const outFile = /\.annotated\.json$/.test(file) ? file : file.replace(/\.json$/, '') + '.annotated.json';
  fs.writeFileSync(outFile, JSON.stringify(data, null, 1));
  console.log(`annotated ${done} finding(s), skipped ${skipped}; wrote ${outFile}`);
}

async function printPdf(pw) {
  const fs = require('fs'); const path = require('path');
  const html = path.resolve(opt('--print')); const pdf = opt('--pdf', html.replace(/\.html?$/, '') + '.pdf');
  const browser = await launch(pw); const page = await browser.newPage();
  await page.goto('file://' + html, {waitUntil: 'load'}); await page.emulateMedia({media: 'print'});
  await page.pdf({path: pdf, format: 'A4', printBackground: true, tagged: true, outline: true, margin: {top: '18mm', bottom: '18mm', left: '16mm', right: '16mm'},
    displayHeaderFooter: true, headerTemplate: '<span></span>', footerTemplate: '<div style="font:9px sans-serif;width:100%;text-align:center;color:#555"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'});
  await browser.close(); console.log('wrote ' + pdf);
}

(async () => {
  let pw;
  try { pw = require('playwright'); } catch (e) { console.error('playwright is not installed: npm i playwright && npx playwright install chromium'); process.exit(3); }
  if (opt('--annotate')) return annotate(pw);
  if (opt('--print')) return printPdf(pw);
  const browser = await launch(pw);
  const ctx = flag('--mobile')
    ? await browser.newContext({ ...pw.devices['iPhone 13'] })
    : await browser.newContext({ viewport: { width: +opt('--width', 1280), height: +opt('--height', 900) } });
  const page = await ctx.newPage();
  const consoleErrors = [];
  page.on('pageerror', e => consoleErrors.push(String(e)));
  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 }).catch(e => console.error('goto:', e.message));
  await page.waitForTimeout(+opt('--wait', 1000));
  const zoom = opt('--zoom', null);
  if (zoom) await page.evaluate(z => { document.documentElement.style.zoom = z + '%'; }, zoom);
  const shot = opt('--screenshot', null);
  if (shot) await page.screenshot({ path: shot, fullPage: true });
  if (flag('--tab-order')) {
    const order = []; let repeats = 0;
    for (let i = 0; i < 300; i++) {
      await page.keyboard.press('Tab');
      const info = await page.evaluate(() => {
        const e = document.activeElement; if (!e || e === document.body) return null;
        const r = e.getBoundingClientRect();
        const cs = getComputedStyle(e);
        return { tag: e.tagName.toLowerCase(), id: e.id, role: e.getAttribute('role'), text: (e.innerText || e.value || e.getAttribute('aria-label') || '').trim().slice(0, 60),
                 x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height), outline: cs.outlineStyle + ' ' + cs.outlineWidth, visible: r.width > 0 && r.height > 0 };
      });
      if (!info) break;
      const sig = JSON.stringify(info);
      // Composite controls (date inputs, media players, embedded editors) keep document.activeElement while Tab moves inside them.
      if (order.length && order[order.length - 1] === sig) {
        if (++repeats >= 8) { order.push('"(focus stayed on the same element for 8 Tab presses: keyboard trap? check 12.9 by hand)"'); break; }
        continue;
      }
      repeats = 0;
      if (order.length && order[0] === sig) break; // cycled back to start
      if (order.includes(sig) && order.length > 2) { order.push('"(loop detected: possible keyboard trap or repeated focus)"'); break; }
      order.push(sig);
    }
    console.log(JSON.stringify({ url, tabOrder: order.map(s => JSON.parse(s)), pageErrors: consoleErrors }, null, 1));
  } else {
    const html = await page.evaluate(() => '<!DOCTYPE html>\n' + document.documentElement.outerHTML);
    process.stdout.write(html);
    if (consoleErrors.length) console.error('page errors:', consoleErrors.join('\n'));
  }
  await browser.close();
})();
