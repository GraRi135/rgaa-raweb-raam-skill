#!/usr/bin/env node
// Render a page with a real browser and print the DOM after JavaScript ran, so that
// scan_html.py can analyse single-page applications and client-rendered content.
//
//   node render_page.js https://example.lu/ > page.rendered.html
//   node render_page.js https://example.lu/ --wait 3000 --width 1280 --screenshot page.png
//   node render_page.js https://example.lu/ --mobile          (375x812, touch, mobile UA)
//   node render_page.js https://example.lu/ --zoom 200        (CSS zoom 200 %: evidence for 10.4 / 10.11)
//   node render_page.js https://example.lu/ --tab-order       (prints the sequence of focusable elements: 12.8 / 12.9)
//
// Requires Playwright (npm i playwright  then  npx playwright install chromium), or a pre-installed
// browser; set PLAYWRIGHT_CHROMIUM_PATH to a Chrome/Chromium binary if auto-detection fails.
const args = process.argv.slice(2);
const url = args.find(a => !a.startsWith('--'));
if (!url) { console.error('usage: render_page.js <url> [--wait ms] [--width px] [--mobile] [--zoom pct] [--screenshot file] [--tab-order]'); process.exit(2); }
const opt = (name, def) => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : def; };
const flag = name => args.includes(name);

(async () => {
  let pw;
  try { pw = require('playwright'); } catch (e) { console.error('playwright is not installed: npm i playwright && npx playwright install chromium'); process.exit(3); }
  const launch = {};
  if (process.env.PLAYWRIGHT_CHROMIUM_PATH) launch.executablePath = process.env.PLAYWRIGHT_CHROMIUM_PATH;
  const browser = await pw.chromium.launch(launch);
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
    const order = [];
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
