import { chromium } from 'playwright';
const browser = await chromium.launch({ channel: 'msedge' });
const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
const sid = '177eadd5-2417-4455-a73b-5c595d005079';
await page.addInitScript((s) => localStorage.setItem('session_id', s), sid);
const logs = [];
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
await page.goto('http://localhost:5173/exercise', { waitUntil: 'networkidle', timeout: 30000 });
await page.waitForTimeout(800);

// 只保留判断题：取消「选择题」「填空题」勾选
await page.getByText('选择题', { exact: true }).click();
await page.getByText('填空题', { exact: true }).click();
await page.waitForTimeout(300);

await page.getByRole('button', { name: '生成习题' }).click();
try { await page.waitForSelector('.option-item', { timeout: 45000 }); } catch {}
await page.waitForTimeout(500);

const metrics = await page.evaluate(() => {
  const group = document.querySelector('.options-group');
  const gr = group?.getBoundingClientRect();
  const items = [...document.querySelectorAll('.options-group .option-item')];
  return {
    groupLeft: gr?.left, groupWidth: gr?.width,
    items: items.map((el) => {
      const r = el.getBoundingClientRect();
      return { text: el.innerText?.trim(), itemLeft: Math.round(r.left), itemWidth: Math.round(r.width) };
    }),
  };
});
console.log('METRICS:', JSON.stringify(metrics, null, 2));
console.log('--- ERRORS ---', logs.length ? logs : '(none)');
await browser.close();
