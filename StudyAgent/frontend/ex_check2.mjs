import { chromium } from 'playwright';
const browser = await chromium.launch({ channel: 'msedge' });
const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
const sid = '177eadd5-2417-4455-a73b-5c595d005079';
await page.addInitScript((s) => localStorage.setItem('session_id', s), sid);
const logs = [];
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
await page.goto('http://localhost:5173/exercise', { waitUntil: 'networkidle', timeout: 30000 });
await page.waitForTimeout(800);
await page.getByRole('button', { name: '生成习题' }).click();
try { await page.waitForSelector('.option-item', { timeout: 45000 }); } catch {}
await page.waitForTimeout(500);
const metrics = await page.evaluate(() => {
  const group = document.querySelector('.choice-options');
  const gr = group?.getBoundingClientRect();
  const items = [...document.querySelectorAll('.choice-options .option-item')];
  return {
    groupLeft: gr?.left, groupWidth: gr?.width,
    items: items.map((el) => {
      const r = el.getBoundingClientRect();
      const lr = el.querySelector('.el-radio__label')?.getBoundingClientRect();
      return { text: el.innerText?.trim().slice(0,16), itemLeft: Math.round(r.left), itemWidth: Math.round(r.width), labelLeft: Math.round(lr?.left) };
    }),
  };
});
console.log('METRICS:', JSON.stringify(metrics, null, 2));
await page.screenshot({ path: 'ex_after.png' });
console.log('--- ERRORS ---', logs.length ? logs : '(none)');
await browser.close();
