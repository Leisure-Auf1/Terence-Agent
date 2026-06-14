# 测试用例-需求对应表

| 需求 | 测试用例 | 覆盖情况 |
|------|----------|---------|
| 添加任务成功 | `TestAdd.test_add_success` | ✅ |
| 添加空标题（边界情况） | `TestAdd.test_add_empty_title` | ✅ |
| 查看空任务列表 | `TestList.test_list_empty` | ✅ |
| 查看多个任务 | `TestList.test_list_multiple` | ✅ |
| 完成存在的任务 | `TestDone.test_done_existing` | ✅ |
| 完成不存在的任务 | `TestDone.test_done_nonexistent` | ✅ |
| 已完成任务不重复完成 | `TestDone.test_done_already_done` | ✅ |
| 任务编号自动递增 | `TestIdIncrement.test_ids_auto_increment` | ✅ |
| 添加后自动创建 JSON 文件 | `TestPersistence.test_file_created_after_add` | ✅ |
| JSON 文件不存在时自动处理 | `TestPersistence.test_file_auto_create_empty` | ✅ |
| 数据保存后重新读取一致 | `TestPersistence.test_save_and_reload` | ✅ |
| JSON 文件损坏时友好提示 | `TestPersistence.test_corrupted_file` | ✅ |
| 模型默认状态为 pending | `TestModel.test_task_default_status` | ✅ |
| 标记完成状态变更正确 | `TestModel.test_task_mark_done` | ✅ |

## Bug 引入-修复记录

**引入的 bug**：将 `done` 功能写成了删除功能。
- 修改 `task_service.done()`：使用 `tasks.pop(i)` 代替 `t["status"] = "done"`
- 结果：`test_done_existing` 报 `IndexError`（任务列表为空），`test_done_already_done` 报 `AssertionError`（找不到已删除的任务）

**修复**：改回 `t["status"] = "done"`，并增加已完成状态的判断逻辑。
