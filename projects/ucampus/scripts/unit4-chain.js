/**
 * Unit 4 "Man and nature" - Complete remaining chain
 * Structure analysis → Learning (auto-read) → Sample (tabs) → Practicing (writing)
 * → Section B → Unit review → Unit test
 */
const puppeteer = require('puppeteer');
const COURSE_URL = 'https://ucloud.unipus.cn/app/cmgt/resource-detail/20000975215';
const CDP_URL = 'http://127.0.0.1:9222';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function expandAllPanels(page) {
  try {
    const collapsed = await page.$$('.ant-collapse-header');
    for (const el of collapsed) {
      try {
        await el.click();
        await sleep(300);
      } catch (e) {}
    }
  } catch (e) {}
}

async function waitForPageReady(page) {
  await sleep(2000);
  await expandAllPanels(page);
  await sleep(1000);
}

async function getStatus() {
  const browser = await puppeteer.connect({ browserURL: CDP_URL });
  const pages = await browser.pages();
  const page = pages[0] || await browser.newPage();
  
  await page.goto(COURSE_URL, { waitUntil: 'networkidle2', timeout: 30000 });
  await waitForPageReady(page);
  
  // Find all task items
  const tasks = await page.evaluate(() => {
    const items = document.querySelectorAll('[class*="taskItem"], [class*="TaskItem"], [class*="card"], [class*="ant-card"], [class*="list-item"]');
    const results = [];
    items.forEach(item => {
      const text = item.textContent.trim();
      const nameMatch = text.match(/^(.+?)(?:已完成|未开始|已锁定)/);
      const statusMatch = text.match(/(已完成|未开始|已锁定)/);
      if (nameMatch && statusMatch) {
        results.push({ name: nameMatch[1].trim(), status: statusMatch[1] });
      }
    });
    return results;
  });
  
  console.log('Tasks found:', JSON.stringify(tasks, null, 2));
  await browser.disconnect();
  return tasks;
}

async function handleAutoRead(taskName) {
  console.log(`\n=== AUTO-READ: ${taskName} ===`);
  const browser = await puppeteer.connect({ browserURL: CDP_URL });
  const pages = await browser.pages();
  const page = pages[0] || await browser.newPage();
  
  await page.goto(COURSE_URL, { waitUntil: 'networkidle2', timeout: 30000 });
  await waitForPageReady(page);
  
  // Find the task and click it
  const tasks = await page.evaluate(() => {
    const els = document.querySelectorAll('span, div, a, button');
    const results = [];
    els.forEach(el => {
      if (el.textContent.includes('Learning') && !results.some(r => r.text === el.textContent.trim())) {
        results.push({ text: el.textContent.trim(), tag: el.tagName });
      }
    });
    return results;
  });
  console.log('Learning elements:', JSON.stringify(tasks));
  
  // Try clicking the task link/button
  const clicked = await page.evaluate((name) => {
    const all = document.querySelectorAll('span, div, a, button, li');
    for (const el of all) {
      if (el.textContent.trim() === name && el.offsetParent !== null) {
        el.click();
        return true;
      }
    }
    return false;
  }, taskName);
  console.log(`Clicked ${taskName}: ${clicked}`);
  
  await sleep(3000);
  
  // Check if new tab/window opened
  const newPages = await browser.pages();
  let taskPage = page;
  for (const p of newPages) {
    if (p.url() !== page.url() && p.url() !== 'about:blank') {
      taskPage = p;
      break;
    }
  }
  
  // Wait for content to load (auto-read: just stay for 10s)
  console.log('Waiting 10 seconds for auto-read...');
  await sleep(10000);
  
  // Navigate back to course page
  await taskPage.goto(COURSE_URL, { waitUntil: 'networkidle2', timeout: 30000 });
  await waitForPageReady(page);
  console.log('Auto-read complete, back to course page');
  
  await browser.disconnect();
}

async function main() {
  console.log('=== UNIT 4 COMPLETE CHAIN ===\n');
  
  // Step 1: Handle Structure analysis "Learning" (auto-read)
  await handleAutoRead('Learning');
  
  // Check status after
  const s1 = await getStatus();
  
  await browser.disconnect();
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
