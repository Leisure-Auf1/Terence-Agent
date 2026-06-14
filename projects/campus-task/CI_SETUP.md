# 实验 6 — 持续集成与质量门禁

## 配置说明

### pyproject.toml

项目配置文件，声明：
- 项目名 `campus-task`，版本 `0.2.0`
- Python >= 3.10
- 可选依赖 `[dev]`：`pytest>=8.0`
- pytest 配置：`testpaths = ["tests"]`

### GitHub Actions 工作流

文件：`.github/workflows/test.yml`

**触发条件**：
- `push` 到 `master` 分支
- `pull_request` 到 `master` 分支

**测试矩阵**：Python 3.10 ~ 3.13 四个版本

**步骤**：
1. `actions/checkout@v4` — 检出代码
2. `actions/setup-python@v5` — 安装指定 Python 版本
3. `pip install pytest` — 安装依赖
4. `pytest tests/ -v` — 运行全部测试

## 失败→修复记录

### 🔴 第一次提交（故意失败）

在 `tests/test_campus_task.py` 中添加：
```python
def test_ci_fail_demo(self):
    """🔴 CI 失败演示"""
    assert 1 + 1 == 3
```

**结果**：19 passed, 1 failed
```
FAILED tests/test_campus_task.py::TestIteration::test_ci_fail_demo - assert (1 + 1) == 3
```

### 🟢 第二次提交（修复）

删除失败的测试用例 `test_ci_fail_demo`。

**结果**：19 passed 全部通过
```
============================== 19 passed in 0.02s ==============================
```

### 关键经验

CI 的意义在于：**机器自动检查**，不用人工记得去跑测试。每次 push/PR 自动运行，发现回归问题即时阻断，避免有问题的代码合并到主分支。
