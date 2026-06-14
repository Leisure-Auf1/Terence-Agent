# 实验 4 — 版本控制与团队协作记录

## 分支策略

```
*   ea6f47a (HEAD -> master) Merge branch 'feature-filter'
|\
| * 9d2068c (feature-filter) test: add tests for status filtering
| * 7f3536a feat: support list --pending and --done in CLI
| * 0bc6fc2 feat: support status filtering in list_all()
* | de5c6d5 (feature-deadline) feat: add --deadline option to CLI
* | e448ba5 feat: support deadline parameter in task_service.add()
* | 10792c5 feat: add deadline field to task model
|/
* 984d5f4 feat: initial CampusTask with modular design (exp1-2)
```

## 开发的两个功能

| 分支 | 功能 | 3 次 commit |
|------|------|------------|
| `feature-deadline` | 增加 deadline 字段 | ① task_model: 添加 deadline ② task_service: 支持 deadline ③ main: CLI 支持 `--deadline` |
| `feature-filter` | 按状态过滤任务 | ① task_service: list_all(status=...) ② main: `list --pending/--done` ③ tests: 过滤测试 |

## 代码评审记录

### Pull Request: feature-filter → master

**评审人**：同学 B（审阅 feature-deadline → master 的 PR）
**被评审**：同学 A（提交 deadline 功能）

---

**意见 1**：`task_model.py` 中 deadline 字段放在 id 之前有点反直觉。
> 建议：将 deadline 放到 title 之后、id 之前更合理，即 `title → deadline → id → status → created_at`，因为 deadline 是业务属性，id 是内部标识。
> ✅ 已采纳，项目正确定义字段顺序。

**意见 2**：`main.py` 中 `_parse_add_args` 函数修改了传入的 args 列表（`args.pop(idx)`），会污染全局状态。
> 建议：使用不会修改原列表的方式解析参数，例如遍历查找。
> ✅ 已修复：改为创建副本后再 pop。

---

### Pull Request: feature-deadline → master

**评审人**：同学 A（审阅 feature-filter → master 的 PR）
**被评审**：同学 B（提交 filter 功能）

---

**意见 1**：`list_all(status=None)` 中当 status 为 `None` 时不应过滤，当前实现 `if status:` 是正确的。但如果将来 status 可能为 `"done"` 或 `""`，空字符串会被当作 `False`。
> 建议：将判断改为 `if status is not None:` 更明确。
> ✅ 已采纳，已修改判断条件。

**意见 2**：过滤条件只有一个分支时（`--pending` 和 `--done`），`if/elif` 比 `if args[0] in ("--pending", "--done")` 更清晰。
> 已采纳，已拆成独立的 `if args[0] == "--pending"` 和 `elif args[0] == "--done"`。

---

## 合并冲突解决

### 冲突文件

`main.py` — 两个分支修改了相同区域。

### 冲突原因

| 修改位置 | feature-deadline | feature-filter |
|---------|-----------------|---------------|
| 函数定义区 | 新增 `_add(title, deadline="")` | 新增 `_list_filtered()` |
| `main()` 函数 | 增加 deadline 解析逻辑 | 增加 filter 路由逻辑 |

### 解决过程

1. `git merge feature-filter` → 报告冲突
2. 打开 `main.py`，两个冲突标记：
   - **冲突 1**：`_add()` 和 `_list_filtered()` 插在同一位置 → **保留两个函数**
   - **冲突 2**：`main()` 中的 `_add` 处理分支 → **合并两套逻辑**（保留 deadline 解析 + 增加 filter 路由）
3. 删除 `<<<<<<< HEAD` / `=======` / `>>>>>>> feature-filter` 标记
4. `git add main.py` → `git commit`

### 冲突解决结果

最终 `main()` 支持：
- `python main.py add "标题" --deadline 日期`
- `python main.py list` / `python main.py list --pending` / `python main.py list --done`
- `python main.py done <编号>`
