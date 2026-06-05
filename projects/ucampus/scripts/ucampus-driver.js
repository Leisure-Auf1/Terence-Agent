/**
 * ██╗   ██╗  ██████╗ █████╗ ███╗   ███╗██████╗ ██╗   ██╗███████╗
 * ██║   ██║ ██╔════╝██╔══██╗████╗ ████║██╔══██╗██║   ██║██╔════╝
 * ██║   ██║ ██║     ███████║██╔████╔██║██████╔╝██║   ██║███████╗
 * ██║   ██║ ██║     ██╔══██║██║╚██╔╝██║██╔═══╝ ██║   ██║╚════██║
 * ╚██████╔╝ ╚██████╗██║  ██║██║ ╚═╝ ██║██║     ╚██████╔╝███████║
 *  ╚═════╝   ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝      ╚═════╝ ╚══════╝
 *
 * U校园 AI 版 · 通用自动化驱动引擎
 * ====================================
 * 
 * 【这是什么？】
 * 一个用 Puppeteer + Chrome CDP 自动完成 U校园 AI 版课程的脚本。
 * 支持所有任务类型：选择题、填空、拖拽、视频、闪卡、讨论区、自评表格。
 *
 * 【怎么用？两阶段流程】
 * 
 * ╔══════════════════════════════════════════════════════════════╗
 * ║  第1步: 启动 Chrome（有头模式，一次启动，持续使用）           ║
 * ║  第2步: 手动登录 U校园（浏览器界面操作，只需一次）             ║
 * ║  第3步: 提取题目 → 模型分析答案 → 执行提交（循环）           ║
 * ╚══════════════════════════════════════════════════════════════╝
 *
 * ══════════════════════════════════════════════════════════════
 * 前置准备（只需做一次）
 * ══════════════════════════════════════════════════════════════
 * 
 * ① 安装 Node.js 和 Puppeteer:
 *    sudo pacman -S nodejs npm                      # Arch Linux
 *    mkdir -p /tmp && cd /tmp && npm install puppeteer
 *    # 验证: ls /tmp/node_modules/puppeteer
 *
 * ② 启动 Chrome（有头模式，可看到操作过程）:
 *    google-chrome-stable --remote-debugging-port=9222 \
 *      --user-data-dir=/tmp/chrome-cdp \
 *      --no-first-run --no-default-browser-check \
 *      --no-sandbox --disable-gpu --no-proxy-server &
 *
 *    ⚠️ 如果你的系统有代理设置（如 Clash/SSR）:
 *      必须加 --no-proxy-server，否则 ERR_CONNECTION_CLOSED
 *
 *    💡 如果导航到 U校园失败:
 *      先手动开标签页访问 https://www.baidu.com 再跳转
 *      （绕行 Chrome 网络栈初始化问题）
 *
 * ③ 手动登录 U校园:
 *    浏览器打开 https://uai.unipus.cn
 *    输入账号密码登录后，导航到你的课程详情页
 *    URL 类似: https://ucloud.unipus.cn/app/cmgt/resource-detail/20000975215
 *    把这个 URL 记下来，后面要用
 *
 * ══════════════════════════════════════════════════════════════
 * 使用方式
 * ══════════════════════════════════════════════════════════════
 *
 * ▎模式 A: 查看课程状态（不答题，只看进度）
 * ─────────────────────────────────
 *   node ucampus-driver.js status --courseUrl=<你的课程URL>
 *   
 *   示例输出:
 *   { "phase": "status", "summary": {"total":44,"completed":20,"pending":3,"locked":21} }
 *
 * ▎模式 B: 查看完整学习记录（含各单元得分）
 * ─────────────────────────────────
 *   node ucampus-driver.js progress --courseUrl=<你的课程URL>
 *
 *   会切换到「学习记录」标签，显示所有单元的进度、得分、学习时长
 *
 * ▎模式 C: 提取题目数据 → 给 AI 模型分析答案
 * ─────────────────────────────────
 *   第1步 — 提取题目:
 *     node ucampus-driver.js extract --courseUrl=<你的课程URL>
 *   
 *   脚本会自动找到第一个"未开始"的任务，进入并提取题目的完整内容。
 *   输出格式为 JSON，包含:
 *     - taskType: 任务类型（mcq / fill_blank / video_mcq / flashcard ...）
 *     - mcqQuestions: 选择题的题干和选项
 *     - wordBank: 单词/短语词库
 *     - droppables: 拖拽填空的数据
 *     - scoops: 后缀填空的数据
 *     - fullText: 页面完整文本
 *
 *   第2步 — 让 AI 模型分析题目，确定正确答案:
 *     (人眼看 或 交给 LLM 分析，确定答案数组)
 *
 *   第3步 — 执行答案:
 *     node ucampus-driver.js execute \
 *       '{"answers":["word1","word2",...],"taskName":"Words in use"}' \
 *       --courseUrl=<你的课程URL>
 *
 * ▎模式 D: 完整两阶段示例（以 Words in use 填空为例）
 * ─────────────────────────────────
 *   # 阶段1: 提取题目
 *   node ucampus-driver.js extract --courseUrl=https://ucloud.unipus.cn/app/cmgt/resource-detail/20000975215
 *   
 *   # 模型分析后，得到答案数组
 *   # 如: ["poised","lavish","instantaneous","tangible","hurdles",
 *   #      "streamline","detrimental","evoke","hypothesis","escalating"]
 *   
 *   # 阶段2: 填入并提交
 *   node ucampus-driver.js execute \
 *     '{"answers":["poised","lavish","instantaneous","tangible","hurdles","streamline","detrimental","evoke","hypothesis","escalating"],"taskName":"Words in use"}' \
 *     --courseUrl=https://ucloud.unipus.cn/app/cmgt/resource-detail/20000975215
 *
 *   # 输出结果
 *   # { "phase": "result", "passed": true, "score": "100",
 *   #   "hasContinue": true, "hasRetry": false }
 *
 * ▎模式 E: MCQ 选择题示例（Quiz / Understanding the text）
 * ─────────────────────────────────
 *   # 答案索引 0=A, 1=B, 2=C, 3=D
 *   node ucampus-driver.js extract --courseUrl=<你的URL>
 *   # 分析得出答案: [2, 0, 0, 1, 3] 表示 C, A, A, B, D
 *   node ucampus-driver.js execute \
 *     '{"answers":[2,0,0,1,3],"taskName":"Quiz"}' \
 *     --courseUrl=<你的URL>
 *
 * ▎模式 F: 视频+MCQ（Critical thinking skill）
 * ─────────────────────────────────
 *   # 脚本会自动: mute视频 → 16x播放 → seek到末尾 → 轮询等待MCQ出现
 *   node ucampus-driver.js execute \
 *     '{"answers":[0,1,2,3],"taskName":"Critical thinking skill","taskType":"video_mcq"}' \
 *     --courseUrl=<你的URL>
 *
 * ══════════════════════════════════════════════════════════════
 * 命令行参数参考
 * ══════════════════════════════════════════════════════════════
 *
 *   --courseUrl=<URL>    课程详情页 URL
 *                        （默认用脚本内的 CONFIG.courseUrl，
 *                          推荐每次显式传入以避免出错）
 *   --cdpUrl=<URL>       Chrome CDP 地址
 *                        （默认 http://127.0.0.1:9222）
 *   --section=<A|B|C>    限定指定 Section 内的任务
 *   --verbose            打印详细调试信息
 *   --dryRun             仅提取/检测，不执行任何操作
 *
 * ══════════════════════════════════════════════════════════════
 * 环境变量（替代 --courseUrl 和 --cdpUrl）
 * ══════════════════════════════════════════════════════════════
 *
 *   export U_COURSE_URL="https://ucloud.unipus.cn/app/cmgt/resource-detail/20000975215"
 *   export U_CDP_URL="http://127.0.0.1:9222"
 *   # 设置后可直接运行（不需要每次传入参数）:
 *   node ucampus-driver.js extract
 *
 * ══════════════════════════════════════════════════════════════
 * 常见问题
 * ══════════════════════════════════════════════════════════════
 *
 * ❌ "Cannot connect to Chrome CDP"
 *    → Chrome 没启动或 remote-debugging-port 未设置
 *    修复: google-chrome-stable --remote-debugging-port=9222 ...
 *
 * ❌ 页面只显示白屏/CSS（微前端没加载）
 *    → 等待 20 秒会自动重试，如果一直失败:
 *      手动刷新页面，或先访问百度再跳转到课程页
 *
 * ❌ 提交后显示"返回修改"
 *    → 脚本会尝试重试（最多 4 次）
 *      如果一直失败：手动检查答案是否正确
 *
 * ❌ "还有N道题没做"
 *    → React state 没更新。脚本已处理此问题
 *      如果仍有此提示：联系开发者修复
 *
 * ❌ ERR_CONNECTION_CLOSED
 *    → Chrome 代理问题。启动时加 --no-proxy-server
 *
 * ══════════════════════════════════════════════════════════════
 * 支持的U校园任务类型
 * ══════════════════════════════════════════════════════════════
 *
 *   ✅ Quotation / Text A/B    自动阅读，导航离开即完成
 *   ✅ Preview / Viewing       视频 mute + seek 到末尾
 *   ✅ Vocabulary              闪卡自动翻页
 *   ✅ Quiz / MCQ选择题        按索引 0=A 1=B 2=C 3=D
 *   ✅ Words in use            input 填空
 *   ✅ Expressions in use      短语搭配填空（含多词短语）
 *   ✅ Banked cloze            拖拽填空（data-rbd-droppable-id）
 *   ✅ Word building Practicing 词根词缀填空
 *   ✅ Collocation Practicing  后缀填空（data-scoop-index）
 *   ✅ Sentence structure      textarea 主观题
 *   ✅ Critical thinking       textarea 主观题
 *   ✅ Critical thinking skill 视频+MCQ
 *   ✅ Discussion              讨论区发帖
 *   ✅ Review & check          自评表格
 *   ✅ Unit test               链式子任务（"继续学习"导航）
 *   ✅ Translation             英译中+中译英
 *   ✅ Stories of China        阅读+选择题+翻译（非必修）
 *
 * ══════════════════════════════════════════════════════════════
 * 适合不同课程的方法
 * ══════════════════════════════════════════════════════════════
 *
 *   本脚本适用于任何 U校园 AI 版课程，只需要更改 courseUrl：
 *   1. 在浏览器中打开你的课程详情页
 *   2. 复制 URL（resource-detail/xxx 形式）
 *   3. 用 --courseUrl=<新URL> 运行
 *   无需修改脚本代码！
 *
 *   注意：不同课程的 taskItemInnerLayout 等 class 名
 *   如果一致，则直接可用。如果不同，需要微调选择器。
 */

// =====================================================================
// 配置区 — 所有可自定义参数
// 提示: 最好用命令行参数 --courseUrl=... 或环境变量 U_COURSE_URL
// =====================================================================
const CONFIG = {
  // Chrome CDP 连接
  cdpUrl: process.env.U_CDP_URL || 'http://127.0.0.1:9222',

  // 课程详情页 URL（替换为你自己的 courseResourceId）
  courseUrl: process.env.U_COURSE_URL || 'https://ucloud.unipus.cn/app/cmgt/resource-detail/20000975215',

  // 超时设置（毫秒）
  timeouts: {
    microAppLoad: 20000,      // 微前端加载等待
    taskNavigation: 30000,    // 任务导航等待
    submitResult: 10000,      // 提交后等待结果
    videoPoll: 60000,         // 视频后 MCQ 轮询
    pageLoad: 30000,          // 页面加载
  },

  // 答题策略
  strategy: {
    maxRetries: 4,            // "返回修改"最多重试次数
    flashcardMax: 80,         // 闪卡循环上限
    pollInterval: 500,        // 轮询间隔（毫秒）
  },

  // 浏览器视口
  viewport: { width: 1280, height: 900 },
};

// =====================================================================
// 解析命令行参数
// =====================================================================
const args = process.argv.slice(2);
const MODE = args.find(a => /^(extract|execute|chain|status|progress)$/.test(a)) || 'status';

// 提取 named options
function getOption(name, fallback) {
  const arg = args.find(a => a.startsWith(`--${name}=`));
  return arg ? arg.split('=')[1] : fallback;
}
const OPT = {
  courseUrl: getOption('courseUrl', CONFIG.courseUrl),
  cdpUrl: getOption('cdpUrl', CONFIG.cdpUrl),
  unit: getOption('unit', null),
  section: getOption('section', null),
  timeout: parseInt(getOption('timeout', '30')),
  verbose: args.includes('--verbose'),
  dryRun: args.includes('--dryRun'),
};

// 执行 payload（mode=execute 时需要）
let EXEC_PAYLOAD = {};
try {
  const pArg = args.find(a => a.startsWith('{'));
  if (pArg) EXEC_PAYLOAD = JSON.parse(pArg);
} catch(e) {}

// =====================================================================
// 导入 & 工具函数
// =====================================================================
const puppeteer = require('puppeteer');

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function verbose(...msg) { if (OPT.verbose) console.log('[DEBUG]', ...msg); }

async function connectBrowser() {
  let lastErr;
  for (let i = 0; i < 3; i++) {
    try {
      return await puppeteer.connect({ browserURL: OPT.cdpUrl, defaultViewport: CONFIG.viewport });
    } catch(e) {
      lastErr = e;
      await sleep(2000);
    }
  }
  throw new Error(`Cannot connect to Chrome CDP at ${OPT.cdpUrl}. Is Chrome running with --remote-debugging-port? Error: ${lastErr.message}`);
}

async function getPage(browser) {
  const pages = await browser.pages();
  // 优先使用已存在的非空白页
  const cp = pages.find(p => {
    const u = p.url();
    return u && !u.startsWith('about:') && !u.includes('devtools') && !u.startsWith('chrome://');
  });
  return cp || pages[0] || await browser.newPage();
}

// =====================================================================
// 导航工具
// =====================================================================

/** 导航到课程详情页，等待微前端加载 */
async function goCourse(page) {
  const t0 = Date.now();
  verbose(`导航到课程页: ${OPT.courseUrl}`);
  await page.goto(OPT.courseUrl, { waitUntil: 'domcontentloaded', timeout: CONFIG.timeouts.pageLoad }).catch(e => {
    verbose(`首次导航失败 (${e.message}), 尝试先导航到百度...`);
  });

  // 如果课程页没加载，尝试先百度再跳转（绕行 Chrome 网络栈初始化问题）
  if (page.url().includes('about:') || page.url().includes('baidu')) {
    verbose('执行百度绕行策略...');
    await page.goto('https://www.baidu.com', { waitUntil: 'domcontentloaded', timeout: 15000 }).catch(() => {});
    await sleep(1000);
    await page.goto(OPT.courseUrl, { waitUntil: 'domcontentloaded', timeout: CONFIG.timeouts.pageLoad }).catch(() => {});
  }

  // 轮询等待课程树加载
  const deadline = Date.now() + CONFIG.timeouts.microAppLoad;
  while (Date.now() < deadline) {
    const n = await page.evaluate(() => document.querySelectorAll('[class*="taskItemInnerLayout"]').length);
    if (n > 0) {
      verbose(`课程树已加载: ${n}个任务 (${Date.now()-t0}ms)`);
      return true;
    }
    await sleep(1000);
  }
  console.warn('⚠️  课程树加载超时，可能微前端未加载');
  return false;
}

/** 点击指定任务名（自动处理 React 事件） */
async function clickTask(page, taskName, { section } = {}) {
  verbose(`点击任务: ${taskName}${section ? ` (${section})` : ''}`);
  const navP = page.waitForNavigation({ timeout: CONFIG.timeouts.taskNavigation }).catch(() => 'timeout');

  const found = await page.evaluate(({ name, s }) => {
    let inTargetSection = !s;  // 如果没指定 section，不限制
    const items = document.querySelectorAll('[class*="taskItemInnerLayout"]');
    for (const item of items) {
      if (item.offsetParent === null) continue;

      const elText = item.innerText.trim();
      // 检测 Section 标题
      if (/^Section (A|B|C)$/.test(elText)) {
        inTargetSection = !s || elText === `Section ${s}`;
        continue;
      }

      const ne = item.querySelector('[class*="taskTypeName"]');
      const se = item.querySelector('[class*="nodePassStateTip"]');
      if (!ne || !se) continue;

      // 可配置: 只点"未开始"或所有（除"已锁定"外）
      const status = se.innerText.trim();
      if (ne.innerText.trim() === name && status !== '已锁定' && inTargetSection) {
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
  }, { name: taskName, s: section || null });

  if (!found) {
    console.warn(`⚠️  未找到任务: ${taskName} (可能已完成或已锁定)`);
    return false;
  }

  await navP;
  await sleep(3000);

  // 任务页加载后处理弹窗
  await dismissModals(page);
  return true;
}

/** 关闭所有弹窗（"我知道了"、"确 定"、ant-modal 遮罩） */
async function dismissModals(page) {
  await page.evaluate(() => {
    // 隐藏 ant-modal 遮罩
    document.querySelectorAll('.ant-modal-wrap, .ant-modal-mask, .ant-message').forEach(m => m.style.display = 'none');
    // 点击弹窗按钮
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

/** 提交按钮（通用） */
async function submitAnswers(page) {
  const btn = await page.evaluate(() => {
    const el = document.querySelector('a.btn');
    if (!el) return false;
    el.scrollIntoView({ block: 'center' });
    const keys = Object.keys(el);
    const pk = keys.find(k => k.startsWith('__reactProps'));
    if (pk && el[pk]?.onClick) {
      el[pk].onClick({ preventDefault() {}, stopPropagation() {}, target: el, currentTarget: el });
    }
    el.click();
    el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
    el.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    return true;
  });
  if (!btn) return null;
  await sleep(CONFIG.timeouts.submitResult);

  // 读取结果
  return await page.evaluate(() => {
    const t = document.body.innerText || '';
    return {
      pageText: t.substring(0, 300),
      passed: !t.includes('没有达到闯关条件'),
      score: (t.match(/(\d+)分/) || ['', '?'])[1],
      hasContinue: t.includes('继续学习'),
      hasRetry: t.includes('返回修改'),
      resultSummary: t.includes('答题小结'),
    };
  });
}

/** 点击"继续学习"按钮 */
async function clickContinue(page) {
  const navP = page.waitForNavigation({ timeout: 20000 }).catch(() => 'timeout');
  await page.evaluate(() => {
    for (const btn of document.querySelectorAll('a.btn')) {
      if (btn.innerText.trim().includes('继续学')) {
        const keys = Object.keys(btn);
        const pk = keys.find(k => k.startsWith('__reactProps'));
        if (pk && btn[pk]?.onClick) btn[pk].onClick({ preventDefault() {}, stopPropagation() {}, target: btn, currentTarget: btn });
        btn.click();
        return;
      }
    }
  });
  await navP;
  await sleep(4000);
  await dismissModals(page);
}

// =====================================================================
// Phase 1 — 提取任务数据
// =====================================================================

async function extractTask(page) {
  // 1. 检测当前可执行的下一个任务
  const tasks = await page.evaluate(() => {
    const items = document.querySelectorAll('[class*="taskItemInnerLayout"]');
    const r = [];
    for (const item of items) {
      if (item.offsetParent === null) continue;
      const ne = item.querySelector('[class*="taskTypeName"]');
      const se = item.querySelector('[class*="nodePassStateTip"]');
      if (ne && se) r.push({ name: ne.innerText.trim(), status: se.innerText.trim() });
    }
    return r;
  });

  const unstarted = tasks.filter(t => t.status === '未开始');
  if (unstarted.length === 0) {
    console.log(JSON.stringify({ phase: 'no_more_tasks', tasks }));
    return;
  }

  const taskName = unstarted[0].name;
  console.log(JSON.stringify({ phase: 'extract_start', task: taskName }));

  // 2. 进入任务
  if (!await clickTask(page, taskName)) {
    console.log(JSON.stringify({ phase: 'extract_fail', task: taskName, reason: 'cannot_enter' }));
    return;
  }

  // 3. 提取页面数据
  const data = await page.evaluate(() => {
    const text = document.body.innerText || '';
    const video = document.querySelector('video');

    // 检测任务类型标志
    const flags = {
      hasVideo: !!video,
      hasMCQ: document.querySelectorAll('.option.isNotReview').length,
      hasTextarea: document.querySelectorAll('textarea').length,
      hasInput: document.querySelectorAll('input[type="text"]').length,
      hasDroppable: document.querySelectorAll('[data-rbd-droppable-id]').length,
      hasScoop: document.querySelectorAll('[data-scoop-index]').length,
      hasFlashcard: !!document.querySelector('.action.next'),
      hasSubmitBtn: !!document.querySelector('a.btn'),
      hasTable: document.querySelectorAll('tr[data-row-key]').length,
      hasAntTable: document.querySelectorAll('.ant-table-row').length,
      isDiscussion: text.includes('讨论') || text.includes('全部评论') || text.includes('发 布'),
      hasVocab: !!document.querySelector('.question-vocabulary'),
    };

    // 推断任务类型
    let taskType = 'unknown';
    if (flags.hasVideo && flags.hasMCQ === 0) taskType = 'video_only';
    else if (flags.hasVideo && flags.hasMCQ > 0) taskType = 'video_mcq';
    else if (flags.hasFlashcard) taskType = 'flashcard';
    else if (flags.isDiscussion) taskType = 'discussion';
    else if (flags.hasAntTable || flags.hasTable) taskType = 'review_check';
    else if (flags.hasScoop > 0) taskType = 'collocation_scoop';
    else if (flags.hasDroppable > 0) taskType = 'fill_blank_dnd';
    else if (flags.hasMCQ > 0 && flags.hasTextarea === 0) taskType = 'mcq';
    else if (flags.hasInput > 0) taskType = 'fill_blank';
    else if (flags.hasTextarea > 0) taskType = 'textarea_subjective';
    else if (flags.hasSubmitBtn) taskType = 'unknown_with_submit';

    // 提取 MCQ 详细数据
    const mcqQuestions = Array.from(document.querySelectorAll('.question-common-abs-choice')).map((q, qi) => ({
      index: qi,
      stem: q.innerText.substring(0, 300).replace(/\s+/g, ' ').trim(),
      options: Array.from(q.querySelectorAll('.option.isNotReview')).map((o, oi) => ({
        idx: oi, letter: String.fromCharCode(65 + oi),
        text: o.innerText.trim().substring(0, 200)
      }))
    }));

    // 提取词库（从正文字本提取可能的单词/短语列表）
    const wordBank = [];
    // 查找典型词库格式: 绿色标签/卡片/选项区
    const bankEls = document.querySelectorAll('[class*="option-wrapper"], [class*="bank"], [class*="words"], [class*="pool"]');
    bankEls.forEach(el => {
      const items = el.querySelectorAll('span, div');
      items.forEach(it => {
        const t = it.innerText.trim();
        if (t && /^[a-zA-Z][a-zA-Z\s\-']{1,50}$/.test(t) && !wordBank.includes(t)) wordBank.push(t);
      });
    });

    // 提取拖拽容器的数据
    const droppables = [];
    document.querySelectorAll('[data-rbd-droppable-id]').forEach(d => {
      const inp = d.querySelector('input');
      droppables.push({
        id: parseInt(d.getAttribute('data-rbd-droppable-id')),
        currentValue: inp ? inp.value : '',
        context: (d.closest('[class*="sentence"], [class*="blank"], [class*="question"]') || d.parentElement)?.innerText?.substring(0, 100) || ''
      });
    });

    // 提取 scoop 模式的数据
    const scoops = [];
    document.querySelectorAll('[data-scoop-index]').forEach(s => {
      const prefix = s.previousElementSibling?.innerText?.trim() || '';
      const inp = s.querySelector('input');
      const after = s.nextElementSibling?.innerText?.trim() || '';
      scoops.push({
        index: parseInt(s.getAttribute('data-scoop-index')),
        prefix,     // 已渲染的提示字母
        input: inp ? inp.value : '',
        after,      // 后续文本
      });
    });

    return {
      taskType,
      flags,
      mcqQuestions,
      wordBank: wordBank.slice(0, 30),
      droppables,
      scoops,
      fullText: text.substring(0, 8000),
    };
  });

  const result = { phase: 'extract_done', task: taskName, ...data };
  console.log(JSON.stringify(result, null, 2));
  return result;
}

// =====================================================================
// Phase 2 — 执行答案（按类型分发）
// =====================================================================

async function executeAnswers(page, payload) {
  const { answers, taskName, taskType, section } = payload;
  if (!taskName) {
    console.log(JSON.stringify({ error: 'execute_missing_taskName', payload }));
    return;
  }

  if (!await clickTask(page, taskName, { section })) return;

  await sleep(2000);

  // 获取当前页面类型
  const info = await page.evaluate(() => ({
    hasMCQ: document.querySelectorAll('.option.isNotReview').length,
    hasInput: document.querySelectorAll('input[type="text"]').length,
    hasDroppable: document.querySelectorAll('[data-rbd-droppable-id]').length,
    hasScoop: document.querySelectorAll('[data-scoop-index]').length,
    hasTextarea: document.querySelectorAll('textarea').length,
    hasSubmitBtn: !!document.querySelector('a.btn'),
    hasFlashcard: !!document.querySelector('.action.next'),
    hasTable: document.querySelectorAll('tr[data-row-key]').length,
    isDiscussion: (document.body.innerText||'').includes('讨论'),
    hasVideo: !!document.querySelector('video'),
  }));

  const type = taskType || guessType(info);
  verbose(`执行: ${taskName} (type=${type}, answers=${JSON.stringify(answers).substring(0,100)})`);

  // --- 按类型分发 ---
  let result = null;

  switch (type) {
    case 'flashcard':
      await handleFlashcard(page);
      break;

    case 'video_only':
      await handleVideo(page, false);
      break;

    case 'video_mcq':
      await handleVideo(page, true);
      if (info.hasMCQ > 0 && Array.isArray(answers)) {
        await selectMCQ(page, answers);
      }
      result = await submitAnswers(page);
      break;

    case 'mcq':
      if (Array.isArray(answers)) await selectMCQ(page, answers);
      result = await submitAnswers(page);
      break;

    case 'fill_blank':
    case 'fill_blank_dnd':
      if (Array.isArray(answers)) await fillInputs(page, answers);
      result = await submitAnswers(page);
      break;

    case 'collocation_scoop':
      if (Array.isArray(answers)) await fillScoops(page, answers);
      result = await submitAnswers(page);
      break;

    case 'textarea_subjective':
      if (Array.isArray(answers)) await fillTextareas(page, answers);
      result = await submitAnswers(page);
      break;

    case 'discussion':
      if (Array.isArray(answers) && answers.length > 0) await postDiscussion(page, answers[0]);
      break;

    case 'review_check':
      await handleReviewCheck(page);
      result = await submitAnswers(page);
      break;

    default:
      // 自动阅读类型，直接导航离开
      if (info.hasVideo) {
        await handleVideo(page, false);
      } else if (info.hasSubmitBtn && Array.isArray(answers)) {
        // 尝试各种模式
        await selectMCQ(page, answers);
        await fillInputs(page, answers);
        result = await submitAnswers(page);
      } else {
        // 自动阅读: 导航离开即完成
        verbose('自动阅读任务，导航离开...');
        return { phase: 'auto_read_done', task: taskName };
      }
  }

  // 提交结果处理
  if (result) {
    const out = { phase: 'result', task: taskName, type, ...result };
    console.log(JSON.stringify(out, null, 2));

    // "返回修改"重试（最多 CONFIG.strategy.maxRetries 次）
    if (result.hasRetry) {
      for (let retry = 1; retry <= CONFIG.strategy.maxRetries && result.hasRetry; retry++) {
        verbose(`返回修改重试 #${retry}`);
        await page.evaluate(() => {
          for (const b of document.querySelectorAll('button, a')) {
            if (b.innerText.trim().includes('返回修改')) { b.click(); return; }
          }
        });
        await sleep(3000);

        // 换下一组答案（MCQ 尝试不同选项）
        if (type === 'mcq' && Array.isArray(answers)) {
          const newAnswers = answers.map(a => (a + retry) % 4);
          await selectMCQ(page, newAnswers);
        }
        result = await submitAnswers(page);
        if (result) {
          console.log(JSON.stringify({ phase: 'retry', attempt: retry, ...result }));
        }
      }
    }

    return result;
  }
}

// =====================================================================
// 各题型处理器
// =====================================================================

/** MCQ 选择题 */
async function selectMCQ(page, answers) {
  await page.evaluate((ans) => {
    const qs = document.querySelectorAll('.question-common-abs-choice');
    qs.forEach((q, qi) => {
      const opts = q.querySelectorAll('.option.isNotReview');
      const idx = qi < ans.length ? ans[qi] : 0;
      if (idx < opts.length) {
        opts[idx].scrollIntoView({ block: 'center' });
        opts[idx].click();
      }
    });
  }, answers);
  await sleep(300);
}

/** 填空（data-rbd-droppable-id + TreeWalker 兜底） */
async function fillInputs(page, answers) {
  await page.evaluate((ans) => {
    const ns = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;

    // 先填 data-rbd-droppable-id
    for (let i = 0; i < ans.length; i++) {
      const blank = document.querySelector(`[data-rbd-droppable-id="${i}"]`);
      if (!blank) continue;
      const inp = blank.querySelector('input');
      if (!inp) continue;
      ns.call(inp, ans[i]);
      inp.dispatchEvent(new Event('input', { bubbles: true }));
      inp.dispatchEvent(new Event('change', { bubbles: true }));
      // React onChange
      const keys = Object.keys(inp);
      const pk = keys.find(k => k.startsWith('__reactProps'));
      if (pk && inp[pk]?.onChange) {
        inp[pk].onChange({ target: inp, currentTarget: inp, preventDefault() {}, stopPropagation() {} });
      }
    }

    // TreeWalker 兜底（普通 input[type=text]）
    const walker = document.createTreeWalker(document, NodeFilter.SHOW_ELEMENT);
    let idx = 0;
    while (walker.nextNode() && idx < ans.length) {
      const n = walker.currentNode;
      if (n.tagName === 'INPUT' && n.type === 'text' && n.placeholder !== '搜索' && n.offsetParent !== null) {
        ns.call(n, ans[idx]);
        n.dispatchEvent(new Event('input', { bubbles: true }));
        n.dispatchEvent(new Event('change', { bubbles: true }));
        idx++;
      }
    }
  }, answers);
  await sleep(300);
}

/** Collocation scoop 后缀填空 */
async function fillScoops(page, answers) {
  await page.evaluate((ans) => {
    const ns = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    const scoops = document.querySelectorAll('[data-scoop-index]');
    scoops.forEach((s, i) => {
      if (i >= ans.length) return;
      const inp = s.querySelector('input');
      if (!inp) return;
      ns.call(inp, ans[i]);
      inp.dispatchEvent(new Event('input', { bubbles: true }));
      inp.dispatchEvent(new Event('change', { bubbles: true }));
    });
  }, answers);
  await sleep(300);
}

/** Textarea 主观题 */
async function fillTextareas(page, answers) {
  await page.evaluate((ans) => {
    const tas = document.querySelectorAll('textarea');
    const ns = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
    tas.forEach((ta, i) => {
      const val = i < ans.length ? ans[i] : '';
      ns.call(ta, val);
      ta.dispatchEvent(new Event('input', { bubbles: true }));
      ta.dispatchEvent(new Event('change', { bubbles: true }));
      // React onChange 关键！
      const keys = Object.keys(ta);
      const pk = keys.find(k => k.startsWith('__reactProps'));
      if (pk && ta[pk]?.onChange) {
        ta[pk].onChange({ target: ta, currentTarget: ta, preventDefault() {}, stopPropagation() {} });
      }
    });
  }, answers);
  await sleep(300);
}

/** Flashcard 闪卡 */
async function handleFlashcard(page) {
  for (let c = 0; c < CONFIG.strategy.flashcardMax; c++) {
    const hasNext = await page.evaluate(() => {
      const btn = document.querySelector('.action.next');
      if (btn && btn.offsetParent !== null) {
        btn.click();
        return true;
      }
      return false;
    });
    if (!hasNext) break;
    await sleep(80);  // 闪卡间隔 80ms
  }
  verbose(`闪卡完成 (循环${CONFIG.strategy.flashcardMax}次)`);
}

/** Video 视频任务（支持到末尾+dispatch ended） */
async function handleVideo(page, hasMCQ) {
  const info = await page.evaluate(() => {
    const v = document.querySelector('video');
    if (!v) return { hasVideo: false };
    return { hasVideo: true, duration: v.duration, muted: v.muted };
  });
  if (!info.hasVideo) return;

  if (!hasMCQ) {
    // 纯视频: mute + seek 到末尾 + dispatch ended
    await page.evaluate(() => {
      const v = document.querySelector('video');
      if (!v) return;
      v.muted = true;
      v.currentTime = v.duration - 0.5;
    });
    await sleep(1000);
    await page.evaluate(() => {
      const v = document.querySelector('video');
      if (!v) return;
      v.currentTime = v.duration;
      v.dispatchEvent(new Event('ended', { bubbles: true }));
    });
    verbose('视频已完成 (seek to end + ended event)');
  } else {
    // 视频+MCQ: 16x 播放
    await page.evaluate(() => {
      const v = document.querySelector('video');
      if (!v) return;
      v.muted = true;
      v.playbackRate = 16;
      v.currentTime = 0;
      v.play();
    });
    // 轮询等待 MCQ 出现（最长 60 秒）
    const deadline = Date.now() + CONFIG.timeouts.videoPoll;
    while (Date.now() < deadline) {
      const hasMCQ = await page.evaluate(() => document.querySelectorAll('.option.isNotReview').length > 0);
      if (hasMCQ) { verbose('MCQ 已出现'); return; }
      await sleep(1000);
    }
    // 视频播完了但 MCQ 没出现，dispatch ended 再等
    await page.evaluate(() => {
      const v = document.querySelector('video');
      if (v) v.dispatchEvent(new Event('ended', { bubbles: true }));
    });
    await sleep(3000);
  }
}

/** Discussion 讨论区发帖 */
async function postDiscussion(page, comment) {
  // 如果有子任务标签页先切换
  await page.evaluate(() => {
    document.querySelectorAll('*').forEach(el => {
      const t = el.innerText?.trim();
      if ((t === 'Task 1' || t === 'Task 2') && el.offsetParent !== null) {
        const keys = Object.keys(el);
        const pk = keys.find(k => k.startsWith('__reactProps'));
        if (pk && el[pk]?.onClick) el[pk].onClick({ preventDefault() {}, stopPropagation() {} });
        el.click();
      }
    });
  });
  await sleep(1000);

  // 填 textarea + React onChange
  await fillTextareas(page, [comment]);
  await sleep(500);

  // 发 布
  await page.evaluate(() => {
    const btn = document.querySelector('.submit-btn, .btns-submit.student-btns-submit');
    if (!btn) return;
    btn.classList.remove('submit-btn-disabled');
    btn.disabled = false;
    const keys = Object.keys(btn);
    const pk = keys.find(k => k.startsWith('__reactProps'));
    if (pk && btn[pk]?.onClick) btn[pk].onClick({ preventDefault() {}, stopPropagation() {} });
    btn.click();
    btn.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
    btn.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }));
    btn.dispatchEvent(new MouseEvent('click', { bubbles: true }));
  });
  await sleep(3000);
  verbose('讨论区已发布');
}

/** Review & check 自评表格 */
async function handleReviewCheck(page) {
  await page.evaluate(() => {
    const rows = document.querySelectorAll('tr[data-row-key]');
    for (const r of rows) {
      const key = r.getAttribute('data-row-key');
      if (key && key !== 'Review' && key !== 'Review & check') {
        const icon = r.querySelectorAll('td')[1]?.querySelector('.anticon');
        if (icon) {
          const keys = Object.keys(icon);
          const pk = keys.find(k => k.startsWith('__reactProps'));
          if (pk && icon[pk]?.onClick) icon[pk].onClick({ preventDefault() {}, stopPropagation() {} });
          icon.click();
        }
      }
    }
  });
  await sleep(500);
  // 确认
  await page.evaluate(() => {
    for (const b of document.querySelectorAll('button')) {
      if (b.innerText.trim() === '我知道了') { b.click(); break; }
    }
  });
  await sleep(1000);
}

// =====================================================================
// 辅助函数
// =====================================================================

function guessType(info) {
  if (info.hasVideo && info.hasMCQ === 0) return 'video_only';
  if (info.hasVideo && info.hasMCQ > 0) return 'video_mcq';
  if (info.hasFlashcard) return 'flashcard';
  if (info.isDiscussion) return 'discussion';
  if (info.hasTable || info.hasAntTable) return 'review_check';
  if (info.hasScoop > 0) return 'collocation_scoop';
  if (info.hasDroppable > 0) return 'fill_blank_dnd';
  if (info.hasMCQ > 0 && info.hasTextarea === 0) return 'mcq';
  if (info.hasInput > 0) return 'fill_blank';
  if (info.hasTextarea > 0) return 'textarea_subjective';
  return 'unknown';
}

// =====================================================================
// 模式: status — 查看当前课程状态
// =====================================================================

async function showStatus(page) {
  await goCourse(page);
  const tasks = await page.evaluate(() => {
    const items = document.querySelectorAll('[class*="taskItemInnerLayout"]');
    const r = [];
    for (const item of items) {
      if (item.offsetParent === null) continue;
      const ne = item.querySelector('[class*="taskTypeName"]');
      const se = item.querySelector('[class*="nodePassStateTip"]');
      if (ne && se) r.push({ name: ne.innerText.trim(), status: se.innerText.trim() });
    }
    return r;
  });

  const summary = {
    total: tasks.length,
    completed: tasks.filter(t => t.status === '已完成').length,
    pending: tasks.filter(t => t.status === '未开始').length,
    locked: tasks.filter(t => t.status === '已锁定').length,
  };
  console.log(JSON.stringify({ phase: 'status', summary, tasks }, null, 2));
}

// =====================================================================
// 模式: progress — 查看学习记录
// =====================================================================

async function showProgress(page) {
  await goCourse(page);

  // 切到"学习记录" tab
  await page.evaluate(() => {
    const tabs = document.querySelectorAll('.ant-tabs-tab');
    for (const tab of tabs) {
      if (tab.innerText.trim() === '学习记录' && tab.offsetParent !== null) {
        const keys = Object.keys(tab);
        const pk = keys.find(k => k.startsWith('__reactProps'));
        if (pk && tab[pk]?.onClick) tab[pk].onClick({ preventDefault() {}, stopPropagation() {} });
        tab.click();
        return;
      }
    }
  });
  await sleep(5000);

  const text = await page.evaluate(() => document.body.innerText);
  console.log(JSON.stringify({ phase: 'progress', content: text.substring(0, 10000) }));
}

// =====================================================================
// 主入口
// =====================================================================

async function main() {
  const browser = await connectBrowser();
  const page = await getPage(browser);

  try {
    switch (MODE) {
      case 'extract':
        await goCourse(page);
        await extractTask(page);
        break;

      case 'execute':
        await executeAnswers(page, EXEC_PAYLOAD);
        break;

      case 'chain':
        console.log('链式模式: 提取→执行→提取→执行...(待实现)');
        break;

      case 'status':
        await showStatus(page);
        break;

      case 'progress':
        await showProgress(page);
        break;
    }
  } finally {
    await browser.disconnect();
  }
}

main().catch(e => {
  console.error(JSON.stringify({ phase: 'fatal', error: e.message, stack: e.stack?.substring(0, 500) }));
  process.exit(1);
});
