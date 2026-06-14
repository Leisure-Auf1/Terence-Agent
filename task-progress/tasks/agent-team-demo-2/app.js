'use strict';

/* ============================================================
 * 代跑代课·校园互助 — 应用逻辑
 * 单文件 app.js，基于 localStorage 的纯前端 SPA
 * ============================================================ */

// ======================== 数据层 ========================

/**
 * 从 localStorage 读取 campus_tasks
 * @returns {Array} 任务数组
 */
function getTasks() {
  try {
    const data = localStorage.getItem('campus_tasks');
    return data ? JSON.parse(data) : [];
  } catch (_) {
    return [];
  }
}

/**
 * 保存任务数组到 localStorage
 * @param {Array} tasks
 */
function saveTasks(tasks) {
  localStorage.setItem('campus_tasks', JSON.stringify(tasks));
}

/**
 * 从 localStorage 读取 campus_nickname
 * @returns {string} 昵称，未设置时返回空字符串
 */
function getNickname() {
  return localStorage.getItem('campus_nickname') || '';
}

/**
 * 保存昵称到 localStorage
 * @param {string} name
 */
function saveNickname(name) {
  localStorage.setItem('campus_nickname', name);
}

/**
 * 判断用户是否已设置昵称
 * @returns {boolean}
 */
function isLoggedIn() {
  return getNickname() !== '';
}

/**
 * 生成唯一任务 ID：task_时间戳_随机4位
 * @returns {string}
 */
function generateId() {
  const now = Date.now();
  const rand = Math.random().toString(36).substring(2, 6).padEnd(4, '0');
  return 'task_' + now + '_' + rand;
}

// ======================== 演示数据 ========================

/**
 * 首次加载时写入 4 条预置演示数据
 * 发布者均为虚构昵称，无真实姓名
 */
function initDemoData() {
  const existing = getTasks();
  if (existing.length > 0) return;

  const now = Date.now();
  const demo = [
    {
      id: 'task_' + (now - 400000) + '_demo',
      type: 'errand',
      typeLabel: '代跑',
      courseName: '高等数学作业',
      dateTime: '2025-06-10T14:30',
      location: '二教 301',
      price: '15',
      contact: '微信: help1',
      note: '帮忙去老师办公室交作业',
      publisher: '校园跑腿侠',
      status: 'open',
      takenBy: null,
      createdAt: now - 400000
    },
    {
      id: 'task_' + (now - 300000) + '_demo',
      type: 'class',
      typeLabel: '代课',
      courseName: '大学英语',
      dateTime: '2025-06-11T08:00',
      location: '外语楼 205',
      price: '25',
      contact: 'QQ: 123456',
      note: '需要回答问题',
      publisher: '代课达人',
      status: 'open',
      takenBy: null,
      createdAt: now - 300000
    },
    {
      id: 'task_' + (now - 200000) + '_demo',
      type: 'errand',
      typeLabel: '代跑',
      courseName: '体育打卡',
      dateTime: '2025-06-12T06:30',
      location: '北区操场',
      price: '10',
      contact: '短信: 138xxxx',
      note: '跑步 2 公里配速不限',
      publisher: '早起鸟',
      status: 'open',
      takenBy: null,
      createdAt: now - 200000
    },
    {
      id: 'task_' + (now - 100000) + '_demo',
      type: 'class',
      typeLabel: '代课',
      courseName: '毛概',
      dateTime: '2025-06-13T14:00',
      location: '阶梯教室 A',
      price: '20',
      contact: '微信: maogai',
      note: '坐后排不提问',
      publisher: '热心同学',
      status: 'taken',
      takenBy: '帮忙小哥',
      createdAt: now - 100000
    }
  ];

  saveTasks(demo);
}

// ======================== Toast 通知 ========================

/**
 * 显示 Toast 通知
 * @param {string} message - 通知文字
 * @param {string} [type='info'] - 类型：'success' | 'error' | 'info'
 */
function showToast(message, type) {
  type = type || 'info';
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast toast--' + type;
  toast.textContent = message;

  container.appendChild(toast);

  // 触发过渡动画
  // 2.5s 后淡出移除
  setTimeout(function () {
    toast.classList.add('toast-out');
    setTimeout(function () {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 350);
  }, 2500);
}

// ======================== 昵称系统 ========================

/**
 * 打开昵称设置弹窗，预填当前昵称
 */
function openNicknameModal() {
  const modal = document.getElementById('nickname-modal');
  const input = document.getElementById('nickname-input');
  if (!modal || !input) return;

  input.value = getNickname();
  modal.classList.remove('hidden');
  setTimeout(function () {
    input.focus();
    input.select();
  }, 100);
}

/**
 * 关闭昵称设置弹窗
 */
function closeNicknameModal() {
  const modal = document.getElementById('nickname-modal');
  if (modal) {
    modal.classList.add('hidden');
  }
}

/**
 * 确认昵称：读取输入 → 保存 → 关闭 → 刷新显示 → Toast
 */
function confirmNickname() {
  const input = document.getElementById('nickname-input');
  if (!input) return;

  const name = input.value.trim();
  if (!name) {
    showToast('昵称不能为空', 'error');
    return;
  }

  saveNickname(name);
  updateNicknameDisplay();
  closeNicknameModal();
  showToast('昵称设置成功', 'success');
}

/**
 * 更新导航栏昵称显示文字
 */
function updateNicknameDisplay() {
  const btn = document.getElementById('nickname-btn');
  if (!btn) return;

  const nickname = getNickname();
  if (nickname) {
    btn.textContent = '昵称：' + nickname;
  } else {
    btn.textContent = '设置昵称';
  }
}

// ======================== Tab 切换 ========================

/**
 * 切换 Tab
 * @param {string} tabName - 'publish' | 'list' | 'mine'
 */
function switchTab(tabName) {
  // 切换 Tab 按钮选中态
  const tabBtns = document.querySelectorAll('.tab-btn');
  for (let i = 0; i < tabBtns.length; i++) {
    const btn = tabBtns[i];
    if (btn.dataset.tab === tabName) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  }

  // 切换面板显示
  const panels = document.querySelectorAll('.tab-panel');
  for (let j = 0; j < panels.length; j++) {
    const panel = panels[j];
    if (panel.dataset.panel === tabName) {
      panel.classList.add('active');
    } else {
      panel.classList.remove('active');
    }
  }

  // 根据 Tab 执行对应渲染
  if (tabName === 'list') {
    const activeFilter = document.querySelector('.filter-btn.active');
    const filter = activeFilter ? activeFilter.dataset.filter : 'all';
    renderAllTasks(filter);
  } else if (tabName === 'mine') {
    if (!isLoggedIn()) {
      showToast('请先设置昵称', 'error');
      switchTab('list');
      return;
    }
    renderMineTasks();
  }
}

// ======================== 表单发布 ========================

/**
 * 表单验证：全部必填字段非空
 * @returns {boolean|string} true 或错误消息
 */
function validateForm() {
  const course = document.getElementById('form-course');
  const datetime = document.getElementById('form-datetime');
  const location = document.getElementById('form-location');
  const price = document.getElementById('form-price');
  const contact = document.getElementById('form-contact');

  if (!course.value.trim()) return '请输入课程名称';
  if (!datetime.value) return '请选择日期时间';
  if (!location.value.trim()) return '请输入地点';
  if (!price.value || parseFloat(price.value) < 0) return '请输入有效酬劳';
  if (!contact.value.trim()) return '请输入联系方式';

  return true;
}

/**
 * 发布表单提交处理
 * @param {Event} e
 */
function handlePublish(e) {
  e.preventDefault();

  // 校验是否已设置昵称
  if (!isLoggedIn()) {
    showToast('请先设置昵称', 'error');
    return;
  }

  // 表单验证
  const validation = validateForm();
  if (validation !== true) {
    showToast(validation, 'error');
    return;
  }

  // 获取选中的类型
  const typeBtn = document.querySelector('.type-btn.active');
  const taskType = typeBtn ? typeBtn.dataset.type : 'errand';

  // 构造 Task 对象
  const task = {
    id: generateId(),
    type: taskType,
    typeLabel: taskType === 'errand' ? '代跑' : '代课',
    courseName: document.getElementById('form-course').value.trim(),
    dateTime: document.getElementById('form-datetime').value,
    location: document.getElementById('form-location').value.trim(),
    price: document.getElementById('form-price').value,
    contact: document.getElementById('form-contact').value.trim(),
    note: document.getElementById('form-note').value.trim() || '',
    publisher: getNickname(),
    status: 'open',
    takenBy: null,
    createdAt: Date.now()
  };

  // 保存
  const tasks = getTasks();
  tasks.push(task);
  saveTasks(tasks);

  // 重置表单
  document.getElementById('publish-form').reset();
  // 重置类型按钮为默认选中代跑
  const typeBtns = document.querySelectorAll('.type-btn');
  for (let i = 0; i < typeBtns.length; i++) {
    typeBtns[i].classList.toggle('active', typeBtns[i].dataset.type === 'errand');
  }

  showToast('发布成功！', 'success');
  switchTab('list');
}

// ======================== 渲染任务卡片 ========================

/**
 * 生成单张任务卡片的 HTML
 * @param {Object} task
 * @returns {string} HTML 字符串
 */
function renderTaskCard(task) {
  const typeClass = 'task-type--' + task.type;
  const statusOpen = task.status === 'open';
  const statusClass = statusOpen ? 'task-status--open' : 'task-status--taken';
  const statusText = statusOpen ? '可接单' : '已被接';

  const currentUser = getNickname();
  const isOwner = currentUser && task.publisher === currentUser;
  const canAcceptTask = task.status === 'open' && !isOwner && task.takenBy === null;

  let acceptBtnHtml;
  if (canAcceptTask) {
    acceptBtnHtml = '<button class="btn btn-accept" data-task-id="' + task.id + '">接单</button>';
  } else if (isOwner) {
    acceptBtnHtml = '<button class="btn btn-accept btn-accept--disabled" disabled>自己的发布</button>';
  } else {
    acceptBtnHtml = '<button class="btn btn-accept btn-accept--disabled" disabled>不可接单</button>';
  }

  const dateDisplay = task.dateTime ? task.dateTime.replace('T', ' ') : '';

  // 备注行
  let noteHtml = '';
  if (task.note) {
    noteHtml = '<p class="task-note">备注：' + escapeHtml(task.note) + '</p>';
  }

  return '<div class="task-card" data-task-id="' + task.id + '">' +
    '<div class="task-card__header">' +
      '<span class="task-type-badge ' + typeClass + '">' + escapeHtml(task.typeLabel) + '</span>' +
      '<span class="task-status-badge ' + statusClass + '">' + statusText + '</span>' +
      '<span class="task-publisher">发布者：' + escapeHtml(task.publisher) + '</span>' +
    '</div>' +
    '<div class="task-card__body">' +
      '<h3 class="task-course">' + escapeHtml(task.courseName) + '</h3>' +
      '<div class="task-detail">' +
        '<span class="task-detail__item">📅 ' + escapeHtml(dateDisplay) + '</span>' +
        '<span class="task-detail__item">📍 ' + escapeHtml(task.location) + '</span>' +
        '<span class="task-detail__item">💰 ' + escapeHtml(task.price) + ' 元</span>' +
        '<span class="task-detail__item">📞 ' + escapeHtml(task.contact) + '</span>' +
      '</div>' +
      noteHtml +
    '</div>' +
    '<div class="task-card__footer">' +
      acceptBtnHtml +
    '</div>' +
  '</div>';
}

/**
 * 简单的 HTML 转义（防止 XSS）
 * @param {string} str
 * @returns {string}
 */
function escapeHtml(str) {
  if (typeof str !== 'string') return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/**
 * 渲染全部/筛选后的任务卡片到 #task-list
 * @param {string} [filter='all'] - 'all' | 'errand' | 'class'
 */
function renderAllTasks(filter) {
  filter = filter || 'all';
  const container = document.getElementById('task-list');
  if (!container) return;

  let tasks = getTasks();

  // 筛选
  if (filter !== 'all') {
    tasks = tasks.filter(function (t) {
      return t.type === filter;
    });
  }

  // 按 createdAt 降序排列
  tasks.sort(function (a, b) {
    return b.createdAt - a.createdAt;
  });

  // 生成 HTML
  let html = '';
  for (let i = 0; i < tasks.length; i++) {
    html += renderTaskCard(tasks[i]);
  }

  container.innerHTML = html;

  if (tasks.length === 0) {
    container.innerHTML = '<div class="empty-hint">暂无相关需求</div>';
  }
}

/**
 * 渲染当前用户发布的任务到 #mine-list
 */
function renderMineTasks() {
  const container = document.getElementById('mine-list');
  if (!container) return;

  const currentUser = getNickname();
  const tasks = getTasks().filter(function (t) {
    return t.publisher === currentUser;
  });

  // 按 createdAt 降序排列
  tasks.sort(function (a, b) {
    return b.createdAt - a.createdAt;
  });

  let html = '';
  for (let i = 0; i < tasks.length; i++) {
    html += renderTaskCard(tasks[i]);
  }

  container.innerHTML = html;

  if (tasks.length === 0) {
    container.innerHTML = '<div class="empty-hint">你还没有发布过需求</div>';
  }
}

// ======================== 接单逻辑 ========================

/**
 * 判定任务是否可被当前用户接单
 * @param {Object} task
 * @param {string} currentUser
 * @returns {boolean}
 */
function canAccept(task, currentUser) {
  return task.status === 'open' && task.publisher !== currentUser && task.takenBy === null;
}

/**
 * 接单逻辑
 * @param {string} taskId
 */
function handleAccept(taskId) {
  // 校验是否已设置昵称
  if (!isLoggedIn()) {
    showToast('请先设置昵称', 'error');
    return;
  }

  const tasks = getTasks();
  let task = null;
  let taskIndex = -1;

  for (let i = 0; i < tasks.length; i++) {
    if (tasks[i].id === taskId) {
      task = tasks[i];
      taskIndex = i;
      break;
    }
  }

  if (!task) {
    showToast('任务不存在', 'error');
    return;
  }

  const currentUser = getNickname();

  // 校验能否接单
  if (!canAccept(task, currentUser)) {
    if (task.status !== 'open') {
      showToast('该需求已被接', 'error');
    } else if (task.publisher === currentUser) {
      showToast('不能接自己的单', 'error');
    } else {
      showToast('该需求已被接', 'error');
    }
    return;
  }

  // 执行接单
  task.status = 'taken';
  task.takenBy = currentUser;
  tasks[taskIndex] = task;
  saveTasks(tasks);

  showToast('接单成功！', 'success');

  // 刷新当前显示的列表
  const activePanel = document.querySelector('.tab-panel.active');
  if (activePanel) {
    const panelName = activePanel.dataset.panel;
    if (panelName === 'list') {
      const activeFilter = document.querySelector('.filter-btn.active');
      renderAllTasks(activeFilter ? activeFilter.dataset.filter : 'all');
    } else if (panelName === 'mine') {
      renderMineTasks();
    }
  }
}

// ======================== 应用初始化 ========================

/**
 * 应用入口
 */
function initApp() {
  // 初始化演示数据
  initDemoData();

  // 更新昵称显示
  updateNicknameDisplay();

  // ---- 事件绑定 ----

  // 昵称按钮
  const nicknameBtn = document.getElementById('nickname-btn');
  if (nicknameBtn) {
    nicknameBtn.addEventListener('click', openNicknameModal);
  }

  // 昵称弹窗确认
  const nicknameConfirm = document.getElementById('nickname-confirm');
  if (nicknameConfirm) {
    nicknameConfirm.addEventListener('click', confirmNickname);
  }

  // 昵称弹窗取消
  const nicknameCancel = document.getElementById('nickname-cancel');
  if (nicknameCancel) {
    nicknameCancel.addEventListener('click', closeNicknameModal);
  }

  // 昵称弹窗遮罩点击关闭（点击遮罩本身）
  const nicknameModal = document.getElementById('nickname-modal');
  if (nicknameModal) {
    nicknameModal.addEventListener('click', function (e) {
      if (e.target === nicknameModal) {
        closeNicknameModal();
      }
    });
  }

  // Tab 导航委托
  const tabNav = document.getElementById('tab-nav');
  if (tabNav) {
    tabNav.addEventListener('click', function (e) {
      const btn = e.target.closest('.tab-btn');
      if (btn && btn.dataset.tab) {
        switchTab(btn.dataset.tab);
      }
    });
  }

  // 发布表单提交
  const publishForm = document.getElementById('publish-form');
  if (publishForm) {
    publishForm.addEventListener('submit', handlePublish);
  }

  // 类型按钮切换（委托到表单）
  const formContainer = document.querySelector('#panel-publish');
  if (formContainer) {
    formContainer.addEventListener('click', function (e) {
      const btn = e.target.closest('.type-btn');
      if (btn) {
        const allBtns = formContainer.querySelectorAll('.type-btn');
        for (let i = 0; i < allBtns.length; i++) {
          allBtns[i].classList.remove('active');
        }
        btn.classList.add('active');
      }
    });
  }

  // 筛选按钮切换（委托到 filter-bar）
  const filterBar = document.getElementById('filter-bar');
  if (filterBar) {
    filterBar.addEventListener('click', function (e) {
      const btn = e.target.closest('.filter-btn');
      if (btn && btn.dataset.filter) {
        const allBtns = filterBar.querySelectorAll('.filter-btn');
        for (let i = 0; i < allBtns.length; i++) {
          allBtns[i].classList.remove('active');
        }
        btn.classList.add('active');
        renderAllTasks(btn.dataset.filter);
      }
    });
  }

  // 任务列表 - 委托接单按钮点击
  const taskList = document.getElementById('task-list');
  if (taskList) {
    taskList.addEventListener('click', function (e) {
      const btn = e.target.closest('.btn-accept');
      if (btn && !btn.disabled && btn.dataset.taskId) {
        handleAccept(btn.dataset.taskId);
      }
    });
  }

  // 我的发布列表 - 委托接单按钮点击
  const mineList = document.getElementById('mine-list');
  if (mineList) {
    mineList.addEventListener('click', function (e) {
      const btn = e.target.closest('.btn-accept');
      if (btn && !btn.disabled && btn.dataset.taskId) {
        handleAccept(btn.dataset.taskId);
      }
    });
  }

  // 默认显示"需求列表"Tab
  switchTab('list');
}

// DOM 就绪后启动
document.addEventListener('DOMContentLoaded', initApp);
