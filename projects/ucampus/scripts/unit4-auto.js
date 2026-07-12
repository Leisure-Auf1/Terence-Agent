/**
 * Unit 4 full chain automation script
 * Handles multiple tasks with same name by direct DOM manipulation
 */
const puppeteer = require('puppeteer');
const COURSE_URL = 'https://ucloud.unipus.cn/app/cmgt/resource-detail/20000975215';
const CDP_URL = 'http://127.0.0.1:9222';

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function expandPanels(page) {
  await page.evaluate(() => {
    document.querySelectorAll('.ant-collapse-header').forEach(el => {
      if (el.getAttribute('aria-expanded') === 'false') el.click();
    });
  });
  await sleep(2000);
}

async function goCourse(page) {
  await page.goto(COURSE_URL, { waitUntil: 'networkidle2', timeout: 30000 });
  await sleep(3000);
  await expandPanels(page);
}

async function clickTaskByNameStatus(page, name, status) {
  return await page.evaluate(({ n, s }) => {
    const items = document.querySelectorAll('[class*="taskItemInnerLayout"]');
    for (const item of items) {
      if (item.offsetParent === null) continue;
      const ne = item.querySelector('[class*="taskTypeName"]');
      const se = item.querySelector('[class*="nodePassStateTip"]');
      if (!ne || !se) continue;
      if (ne.innerText.trim() === n && se.innerText.trim() === s) {
        item.scrollIntoView({ block: 'center' });
        const keys = Object.keys(item);
        const pk = keys.find(k => k.startsWith('__reactProps'));
        if (pk && item[pk]?.onClick) {
          item[pk].onClick({ preventDefault() {}, stopPropagation() {} });
        }
        item.click();
        return true;
      }
    }
    return false;
  }, { n: name, s: status });
}

async function dismissModals(page) {
  await page.evaluate(() => {
    document.querySelectorAll('.ant-modal-wrap, .ant-modal-mask, .ant-message').forEach(m => m.style.display = 'none');
    for (const b of document.querySelectorAll('button')) {
      if (b.offsetParent === null) continue;
      const t = b.innerText.trim();
      if (t === '我知道了' || t.includes('知道') || t === '确 定' || t === '同 意') {
        b.click();
        return;
      }
    }
  });
  await sleep(500);
}

async function clickContinue(page) {
  const found = await page.evaluate(() => {
    const all = document.querySelectorAll('button, a, span, div, [class*="btn"]');
    for (const el of all) {
      if (el.offsetParent === null) continue;
      const t = el.innerText.trim();
      if (t === '继续学习') {
        el.click();
        return true;
      }
    }
    return false;
  });
  if (found) {
    await sleep(3000);
    await dismissModals(page);
  }
  return found;
}

/** Auto-read: enter task, wait, navigate back */
async function handleAutoRead(page, name, status, waitMs = 10000) {
  console.log(`\n=== AUTO-READ: ${name} (${status}) ===`);
  await goCourse(page);
  
  const clicked = await clickTaskByNameStatus(page, name, status);
  if (!clicked) {
    console.log(`Could not click ${name} with status ${status}`);
    return false;
  }
  
  await sleep(5000); // wait for navigation
  
  // Stay on page to auto-complete
  console.log(`Waiting ${waitMs/1000}s for auto-read...`);
  await sleep(waitMs);
  
  // Navigate back
  await goCourse(page);
  console.log(`${name} auto-read done`);
  return true;
}

/** Fill a single textarea and submit */
async function handleTextarea(page, name, status, text) {
  console.log(`\n=== TEXTAREA: ${name} (${status}) ===`);
  await goCourse(page);
  
  const clicked = await clickTaskByNameStatus(page, name, status);
  if (!clicked) {
    console.log(`Could not click ${name}`);
    return false;
  }
  await sleep(4000);
  
  // Fill textarea
  await page.evaluate((txt) => {
    const ta = document.querySelector('textarea');
    if (!ta) return false;
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
    nativeInputValueSetter.call(ta, txt);
    ta.dispatchEvent(new Event('input', { bubbles: true }));
    ta.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
  }, text);
  await sleep(1000);
  
  // Click submit
  await page.evaluate(() => {
    const btns = document.querySelectorAll('a.btn, button, [class*="btn"]');
    for (const b of btns) {
      const t = b.innerText.trim();
      if (t.includes('提 交') || t.includes('提交')) {
        b.click();
        return;
      }
    }
  });
  await sleep(5000);
  
  await dismissModals(page);
  await clickContinue(page);
  await sleep(2000);
  return true;
}

/** Handle MCQ (multiple choice) */
async function handleMCQ(page, name, status, answers) {
  console.log(`\n=== MCQ: ${name} (${status}) ===`);
  await goCourse(page);
  
  const clicked = await clickTaskByNameStatus(page, name, status);
  if (!clicked) {
    console.log(`Could not click ${name}`);
    return false;
  }
  await sleep(4000);
  
  // Click MCQ options by index
  for (let i = 0; i < answers.length; i++) {
    const idx = answers[i];
    const clicked = await page.evaluate(({ qIdx, optIdx }) => {
      const qs = document.querySelectorAll('[class*="choiceItem"], [class*="questionContainer"], [class*="mcqItem"]');
      // Try finding by question groups
      const items = document.querySelectorAll('[class*="ant-radio-wrapper"], [class*="radio"], label');
      let count = 0;
      for (const item of items) {
        if (item.offsetParent === null) continue;
        if (item.querySelector('input[type="radio"]') || item.classList.contains('ant-radio-wrapper')) {
          // This is a radio option
          const parent = item.closest('[class*="questionItem"], [class*="mcqItem"], .ant-col, [class*="item"]');
          // Count questions
          count++;
          if (count === qIdx * 4 + optIdx + 1) {
            item.click();
            return true;
          }
        }
      }
      return false;
    }, { qIdx: i, optIdx: idx });
    await sleep(500);
  }
  
  await sleep(1000);
  
  // Submit
  await page.evaluate(() => {
    const btns = document.querySelectorAll('a.btn, button, [class*="btn"]');
    for (const b of btns) {
      const t = b.innerText.trim().replace(/\s/g, '');
      if (t.includes('提交')) {
        b.click();
        return;
      }
    }
  });
  await sleep(5000);
  
  await dismissModals(page);
  await clickContinue(page);
  await sleep(2000);
  return true;
}

/** Handle fill_blank with input fields */
async function handleFillBlank(page, name, status, answers) {
  console.log(`\n=== FILL_BLANK: ${name} (${status}) ===`);
  await goCourse(page);
  
  const clicked = await clickTaskByNameStatus(page, name, status);
  if (!clicked) {
    console.log(`Could not click ${name}`);
    return false;
  }
  await sleep(4000);
  
  // Fill in input fields
  for (let i = 0; i < answers.length; i++) {
    const filled = await page.evaluate(({ idx, ans }) => {
      const inputs = document.querySelectorAll('input[type="text"], input:not([type])');
      // Use the input at this index
      if (idx < inputs.length && inputs[idx].offsetParent !== null) {
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeInputValueSetter.call(inputs[idx], ans);
        inputs[idx].dispatchEvent(new Event('input', { bubbles: true }));
        inputs[idx].dispatchEvent(new Event('change', { bubbles: true }));
        return true;
      }
      return false;
    }, { idx: i, ans: answers[i] });
    await sleep(300);
  }
  
  await sleep(1000);
  
  // Submit
  await page.evaluate(() => {
    const btns = document.querySelectorAll('a.btn, button, [class*="btn"]');
    for (const b of btns) {
      const t = b.innerText.trim().replace(/\s/g, '');
      if (t.includes('提交')) {
        b.click();
        return;
      }
    }
  });
  await sleep(5000);
  
  await dismissModals(page);
  await clickContinue(page);
  await sleep(2000);
  return true;
}

/** Fill all inputs on the page with sequential answers */
async function handleInputFill(page, name, status, answers) {
  console.log(`\n=== INPUT FILL: ${name} (${status}) ===`);
  await goCourse(page);
  
  const clicked = await clickTaskByNameStatus(page, name, status);
  if (!clicked) {
    console.log(`Could not click ${name}`);
    return false;
  }
  await sleep(4000);
  
  // Find all input fields
  const inputCount = await page.evaluate(() => {
    return document.querySelectorAll('input').length;
  });
  console.log(`Found ${inputCount} input fields`);
  
  // Fill answers
  for (let i = 0; i < Math.min(answers.length, inputCount); i++) {
    await page.evaluate(({ idx, ans }) => {
      const inputs = document.querySelectorAll('input');
      if (idx < inputs.length) {
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeInputValueSetter.call(inputs[idx], ans);
        inputs[idx].dispatchEvent(new Event('input', { bubbles: true }));
        inputs[idx].dispatchEvent(new Event('change', { bubbles: true }));
      }
    }, { idx: i, ans: answers[i] });
    await sleep(200);
  }
  
  await sleep(1000);
  
  // Submit
  await page.evaluate(() => {
    const btns = document.querySelectorAll('a.btn, button, [class*="btn"]');
    for (const b of btns) {
      const t = b.innerText.trim().replace(/\s/g, '');
      if (t.includes('提交')) {
        b.click();
        return;
      }
    }
  });
  await sleep(5000);
  
  await dismissModals(page);
  await clickContinue(page);
  await sleep(2000);
  return true;
}

/** Handle video (mute + fast-forward + end) */
async function handleVideo(page, name, status) {
  console.log(`\n=== VIDEO: ${name} (${status}) ===`);
  await goCourse(page);
  
  const clicked = await clickTaskByNameStatus(page, name, status);
  if (!clicked) {
    console.log(`Could not click ${name}`);
    return false;
  }
  await sleep(5000);
  
  // Mute and fast-forward video
  await page.evaluate(() => {
    const vids = document.querySelectorAll('video');
    vids.forEach(v => {
      v.muted = true;
      v.playbackRate = 16;
      v.currentTime = v.duration || 99999;
    });
  });
  await sleep(2000);
  
  // Dispatch ended event
  await page.evaluate(() => {
    const vids = document.querySelectorAll('video');
    vids.forEach(v => {
      v.dispatchEvent(new Event('ended', { bubbles: true }));
    });
  });
  await sleep(3000);
  
  await dismissModals(page);
  await clickContinue(page);
  await sleep(2000);
  return true;
}

/** Handle subjective (textarea) - write single answer */
async function handleSubjective(page, name, status, text) {
  return await handleTextarea(page, name, status, text);
}

/** Handle banked cloze (drag-drop) - fill with text */
async function handleBankedCloze(page, name, status, answers) {
  console.log(`\n=== BANKED CLOZE: ${name} (${status}) ===`);
  await goCourse(page);
  
  const clicked = await clickTaskByNameStatus(page, name, status);
  if (!clicked) {
    console.log(`Could not click ${name}`);
    return false;
  }
  await sleep(4000);
  
  // Fill droppable areas by typing into inputs
  const inputCount = await page.evaluate(() => document.querySelectorAll('input').length);
  console.log(`Found ${inputCount} inputs`);
  
  for (let i = 0; i < Math.min(answers.length, inputCount); i++) {
    await page.evaluate(({ idx, ans }) => {
      const inputs = document.querySelectorAll('input');
      if (idx < inputs.length) {
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        nativeInputValueSetter.call(inputs[idx], ans);
        inputs[idx].dispatchEvent(new Event('input', { bubbles: true }));
        inputs[idx].dispatchEvent(new Event('change', { bubbles: true }));
      }
    }, { idx: i, ans: answers[i] });
    await sleep(200);
  }
  
  // Submit
  await page.evaluate(() => {
    const btns = document.querySelectorAll('a.btn, button, [class*="btn"]');
    for (const b of btns) {
      const t = b.innerText.trim().replace(/\s/g, '');
      if (t.includes('提交')) {
        b.click();
        return;
      }
    }
  });
  await sleep(5000);
  
  await dismissModals(page);
  await clickContinue(page);
  await sleep(2000);
  return true;
}

/** Handle Flashcard (vocabulary) */
async function handleFlashcard(page, name, status) {
  console.log(`\n=== FLASHCARD: ${name} (${status}) ===`);
  await goCourse(page);
  
  const clicked = await clickTaskByNameStatus(page, name, status);
  if (!clicked) {
    console.log(`Could not click ${name}`);
    return false;
  }
  await sleep(4000);
  
  // Click through flashcards
  for (let i = 0; i < 30; i++) {
    const clicked = await page.evaluate(() => {
      const btns = document.querySelectorAll('button, a, [class*="btn"], span, div');
      for (const b of btns) {
        const t = b.innerText.trim();
        if ((t === '下一个' || t === '下一张' || t.includes('下一') || t === '知道了' || t === '翻转' || t === '翻卡') && b.offsetParent !== null) {
          b.click();
          return t;
        }
      }
      return false;
    });
    if (!clicked) break;
    await sleep(800);
  }
  
  await sleep(2000);
  await dismissModals(page);
  await goCourse(page);
  return true;
}

/** Handle review & check - click all Got it buttons */
async function handleReviewCheck(page) {
  console.log(`\n=== REVIEW & CHECK ===`);
  await goCourse(page);
  
  const clicked = await clickTaskByNameStatus(page, 'Review & check', '未开始');
  if (!clicked) {
    console.log('Could not click Review & check');
    return false;
  }
  await sleep(5000);
  
  // Click all got-it buttons
  let clickedCount = 0;
  for (let i = 0; i < 50; i++) {
    const found = await page.evaluate(() => {
      const btns = document.querySelectorAll('button, a, span, div, [class*="btn"], [class*="icon"], [class*="anticon"]');
      for (const b of btns) {
        const t = b.innerText.trim();
        if ((t === '我知道了' || t === 'Got it' || b.className.includes('anticon')) && b.offsetParent !== null) {
          b.click();
          return t;
        }
      }
      return false;
    });
    if (!found) break;
    clickedCount++;
    await sleep(500);
  }
  console.log(`Clicked ${clickedCount} elements`);
  
  await sleep(2000);
  await dismissModals(page);
  await clickContinue(page);
  await sleep(2000);
  return true;
}

async function checkStatus(page) {
  await goCourse(page);
  const tasks = await page.evaluate(() => {
    const results = [];
    const items = document.querySelectorAll('[class*="taskItemInnerLayout"]');
    items.forEach(item => {
      if (item.offsetParent === null) return;
      const ne = item.querySelector('[class*="taskTypeName"]');
      const se = item.querySelector('[class*="nodePassStateTip"]');
      if (ne && se) {
        results.push({ name: ne.innerText.trim(), status: se.innerText.trim() });
      }
    });
    return results;
  });
  return tasks;
}

async function main() {
  const browser = await puppeteer.connect({ browserURL: CDP_URL });
  const pages = await browser.pages();
  const page = pages[0];
  
  console.log('=== UNIT 4 COMPLETE CHAIN ===\n');
  
  // Check current status
  let tasks = await checkStatus(page);
  console.log('Current status:');
  tasks.forEach(t => console.log(`  ${t.name}: ${t.status}`));
  
  // Find pending (未开始) tasks
  const pending = tasks.filter(t => t.status === '未开始');
  console.log(`\nPending tasks: ${pending.length}`);
  pending.forEach(t => console.log(`  ${t.name}`));
  
  // ---- Process tasks in order ----
  
  // 1. Section B → Reading skills → Practicing (MCQ?)
  // Let's handle the first Practicing that is 未开始
  const firstPending = pending[0];
  console.log(`\nNext task: ${firstPending.name} (${firstPending.status})`);
  
  // For now, let me just manually investigate what task type it is
  await goCourse(page);
  
  const clicked = await clickTaskByNameStatus(page, firstPending.name, firstPending.status);
  if (clicked) {
    await sleep(5000);
    const info = await page.evaluate(() => {
      const text = document.body.innerText;
      const hasMCQ = text.includes('A.') && text.includes('B.') && text.includes('C.') && text.includes('D.');
      const hasTextarea = document.querySelector('textarea') !== null;
      const hasVideo = document.querySelector('video') !== null;
      const hasInput = document.querySelectorAll('input').length > 0;
      const hasFlashcard = text.includes('Vocabulary') && (text.includes('card') || text.includes('flash'));
      const inputCount = document.querySelectorAll('input').length;
      const btnTexts = Array.from(document.querySelectorAll('a.btn, button, [class*="btn"]')).map(b => b.innerText.trim()).filter(t => t);
      return {
        url: window.location.href.substring(0, 200),
        hasMCQ, hasTextarea, hasVideo, hasInput, inputCount,
        btnTexts,
        excerpt: text.substring(0, 800)
      };
    });
    console.log('Task info:', JSON.stringify(info, null, 2));
  }
  
  await browser.disconnect();
}

main().catch(e => { console.error(e); process.exit(1); });
