---
name: task-progress
description: '任务进度同步系统 — 每个复杂任务实时写入进度文件，支持跨会话恢复。新对话加载进度文件即可恢复上下文'
category: devops
tags: [core, progress, tracking]
related_skills: [architecture-constraints, error-registry]
---

# 任务进度同步系统 (Task Progress Sync)

> 确保模型在任何时刻中断、新开对话、或增加上下文资源时，能立即认清自己的任务进度。

## 核心机制

```
每个复杂任务（3+ 步骤）自动创建进度文件
  ↓
每个步骤完成后追加更新
  ↓
遇到阻塞时记录+尝试替代
  ↓
新对话/新上下文时：先找进度文件 → 恢复 → 继续
```

## 进度文件位置

```
~/.hermes/tasks/<task-id>/            ← 每个任务独立目录
├── progress.md                        ← 主进度文件（标准格式）
├── artifacts/                         ← 产出文件（截图/代码/日志）
└── context/                           ← 额外上下文（答案库/测试结果）
```

## 进度文件格式 (progress.md)

```markdown
# 任务进度: <任务名称>
- 任务ID: <唯一ID>
- 创建: <时间戳>
- 更新: <时间戳>
- 阶段: <当前阶段>

## ☑️ 已完成
- [x] 步骤1: <描述> → ✅ <分数/结果>
- [x] 步骤2: <描述> → ✅ <分数/结果>

## 🔄 进行中
- [ ] 步骤3: <当前在做什么>

## ⏳ 待办
- [ ] 步骤4: ...
- [ ] 步骤5: ...

## 🚧 阻塞/错误
| 步骤 | 问题 | 修复/替代 | 状态 |
|:----|:-----|:----------|:----:|
| xxx | xxx | xxx | 已修复/待处理 |

## 🧠 关键决策
- 为什么选 A 不选 B: ...
- 替代方案: ...

## 📁 产出物
- 代码: `/path/to/file`
- 截图: `/path/to/screenshot.png`
- 测试结果: ...

## ♻️ 恢复上下文 (跨会话用)
> 新对话加载此文件后应继续做的事：
> 1. 当前停在步骤3
> 2. 下一步是...
> 3. 注意不要重复已完成步骤
```

## 使用流程 (自动执行)

加载此技能后，开始复杂任务时自动执行：

```python
# 伪代码 — 每个复杂任务的第一步
from datetime import datetime
import os
import json

TASKS_DIR = os.path.expanduser('~/.hermes/tasks')

def init_progress(task_name, steps):
    task_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task_name[:20]}"
    task_dir = f"{TASKS_DIR}/{task_id}"
    os.makedirs(f"{task_dir}/artifacts", exist_ok=True)
    os.makedirs(f"{task_dir}/context", exist_ok=True)
    
    progress = {
        'task_name': task_name,
        'task_id': task_id,
        'created': datetime.now().isoformat(),
        'updated': datetime.now().isoformat(),
        'phase': 'init',
        'completed': [],
        'in_progress': [],
        'pending': steps,
        'blockers': [],
        'decisions': [],
        'artifacts': [],
        'resume_context': ''
    }
    return task_dir, progress

def update_progress(task_dir, field, value):
    """更新进度文件 — 每步完成后调用"""
    path = f"{task_dir}/progress.md"
    # ... 追加更新
    print(f"📝 进度更新: {task_dir}")
```

## 实际用法 (执行时 inline)

在 Hermes 会话中手动执行时：

```bash
# 第一步：创建进度目录
mkdir -p ~/.hermes/tasks/unit3-complete/artifacts

# 第二步：写进度文件
cat > ~/.hermes/tasks/unit3-complete/progress.md << 'EOF'
# 任务进度: Unit 3 任务完成
- 任务ID: unit3-complete
- 创建: 2026-06-05
- 更新: 2026-06-05
- 阶段: 任务链执行

## ☑️ 已完成
- [x] Sentence structure Task 2 → 主观题已提交
- [x] Collocation Learning → 自动完成
- [x] Collocation Practicing → 75分 (9/12)
- [x] Review & check → 完成
- [x] Unit test Vocabulary → 100分
- [x] Unit test Banked cloze → 100分
- [x] Unit test Reading → 100分
- [x] Unit test Translation → 94分

## 🔄 进行中
- [ ] (完成)

## ⏳ 待办
- [ ] Unit 1: Unit project (非必修)
- [ ] Unit 2: Stories of China + Translation + Unit project (非必修)

## ♻️ 恢复上下文
> 40/45 任务已完成。剩余5个均为非必修。
EOF

# 后续步骤：追加更新
cat >> ~/.hermes/tasks/unit3-complete/progress.md << 'EOF'
## 🧠 关键决策
- 分层策略: 先做必修链 → Unit test → 最后非必修
- 题型: 倒装条件句直接用 inverted structure
- 翻译主观题 94分

## 📁 产出物
- 登录脚本: /tmp/u-campus-login.js
- 答题脚本: /tmp/u-vocab-answers.js
- 最终检查: /tmp/u-final-check.js
- 截图: ~/.hermes/skills/browser-automation/screenshots/ (未截图)
EOF
```

## 跨会话恢复

新对话中先执行：

```bash
# 查看所有进行中的任务
ls ~/.hermes/tasks/*/progress.md 2>/dev/null

# 加载进度文件
cat ~/.hermes/tasks/<task-id>/progress.md
```

然后模型读取进度文件后自动：
1. 识别当前阶段（已完成 vs 待办）
2. 跳过已完成步骤
3. 从「进行中」或「待办」继续
4. 检查阻塞项是否已修复
5. 加载产出物上下文

## 提示词模板 (模型自省)

当加载进度文件后，模型应自问：

```
1. 进度文件告诉我已完成什么？ → 不要重复
2. 进行中/待办的是什么？ → 从这开始
3. 有什么阻塞/错误？ → 先检查是否已修复
4. 关键决策是什么？ → 保持一致性
5. 产出物在哪？ → 加载上下文
```

---

## 配套: error-registry 联动

遇到阻塞时 → 查 error-registry 找已知修复 → 尝试修复 → 更新进度文件的 `🚧 阻塞/错误` 和 `🧠 关键决策`
