import { chromium } from 'playwright';
const browser = await chromium.launch({ channel: 'msedge' });
const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });

const sid = '177eadd5-2417-4455-a73b-5c595d005079';
await page.addInitScript((s) => localStorage.setItem('session_id', s), sid);

const logs = [];
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));

await page.goto('http://localhost:5173/exercise', { waitUntil: 'networkidle', timeout: 30000 });
await page.waitForTimeout(800);

// 只保留选择题，取消判断题/填空题勾选
await page.evaluate(() => {
  const checks = [...document.querySelectorAll('.el-checkbox')];
  // 通过点击取消 true_false 和 fill_blank
});
// 直接点击生成（默认三种都选，会生成混合题；第一题通常是 choice）
const genBtn = page.getByRole('button', { name: '生成习题' });
await genBtn.click();
console.log('clicked generate, waiting for question...');

try {
  await page.waitForSelector('.option-item', { timeout: 45000 });
} catch (e) {
  console.log('no .option-item appeared; logs:', logs);
}

await page.waitForTimeout(500);

// 测量选项布局
const metrics = await page.evaluate(() => {
  const group = document.querySelector('.options-group');
  const items = [...document.querySelectorAll('.option-item')];
  const gr = group?.getBoundingClientRect();
  return {
    groupLeft: gr?.left,
    groupWidth: gr?.width,
    items: items.map((el) => {
      const r = el.getBoundingClientRect();
      const label = el.querySelector('.el-radio__label');
      const lr = label?.getBoundingClientRect();
      return {
        text: el.innerText?.trim().slice(0, 20),
        itemLeft: r.left,
        itemWidth: r.width,
        labelLeft: lr?.left,
        csTextAlign: getComputedStyle(el).textAlign,
        csJustify: getComputedStyle(el).justifyContent,
        csDisplay: getComputedStyle(el).display,
      };
    }),
  };
});
console.log('METRICS:', JSON.stringify(metrics, null, 2));
await page.screenshot({ path: 'ex_before.png', fullPage: false });
console.log('--- ERRORS ---');
for (const l of logs) console.log(l);
if (!logs.length) console.log('(none)');
await browser.close();
