"""
ai_harness — CampusTask AI Harness 工程

用 mock 模型模拟自然语言管理任务。
流程：
  用户输入 → prompt_builder → mock_model → parse_model_output
  → guardrail → execute_tool → write_trace → 结果
"""

import json
import os
import random
from datetime import datetime

# ── 配置 ───────────────────────────────────────────────────────
TRACE_FILE = "trace.jsonl"
VALID_ACTIONS = {"add_task", "list_tasks", "done_task", "delete_all_tasks", "help"}
DANGEROUS_ACTIONS = {"delete_all_tasks"}


# ── 模块 1：prompt_builder ─────────────────────────────────────

def prompt_builder(user_input, task_state=None):
    """构造发送给模型的 prompt

    将用户自然语言输入和当前任务列表上下文打包为结构化的提示文本。
    """
    context = ""
    if task_state:
        pending = [t for t in task_state if t.get("status") == "pending"]
        if pending:
            titles = "、".join(t["title"] for t in pending[:5])
            context = f"\n当前待办任务（共{len(pending)}项）：{titles}"
        else:
            context = "\n当前没有待办任务。"

    prompt = (
        f"你是 CampusTask 任务管理助手。根据用户的自然语言输入，"
        f"输出 JSON 格式的动作指令。{context}"
        f"\n\n可用的动作："
        f"\n- add_task: 添加任务（args: title, deadline）"
        f"\n- list_tasks: 列出任务（无参数）"
        f"\n- done_task: 完成任务（args: task_id）"
        f"\n- delete_all_tasks: 删除所有任务（危险操作）"
        f"\n- help: 帮助信息"
        f"\n\n用户输入：{user_input}"
        f"\n\n请只输出 JSON，格式："
        f'\n{{"action": "动作名", "args": {{"参数名": "参数值"}}}}'
    )
    return prompt


# ── 模块 2：mock_model ─────────────────────────────────────────

def mock_model(prompt):
    """模拟模型输出（不调用真实 LLM API）

    基于简单的关键词匹配返回模拟结果。
    """
    # 提取用户输入：取"用户输入："之后到换行或结尾的部分
    user_input = prompt.split("用户输入：")[-1].split("\n")[0].strip()

    # 添加任务
    if any(w in user_input for w in ["添加", "新增", "创建", "加一个", "帮我加"]):
        title = user_input
        for prefix in ["帮我添加", "帮我加", "添加", "新增", "创建", "加一个"]:
            if prefix in title:
                title = title.split(prefix, 1)[-1].strip()
        title = title.split("，")[0].split("。")[0].strip() or "新任务"
        deadline = ""
        if "截止" in user_input or "明天" in user_input or "下" in user_input:
            deadline = "2026-06-15" if "明天" in user_input else ""
            if "截止" in user_input:
                deadline = user_input.split("截止")[-1].split("的")[0].strip()
                deadline = deadline.replace("日期", "").replace("是", "").strip()
                if not deadline:
                    deadline = "2026-06-20"
        return json.dumps({"action": "add_task", "args": {"title": title, "deadline": deadline}}, ensure_ascii=False)

    # 列出任务
    if any(w in user_input for w in ["列出", "查看", "列表", "显示", "有什么", "有哪些", "还没完成"]):
        if "没完成" in user_input or "待办" in user_input or "未完成" in user_input:
            return json.dumps({"action": "list_tasks", "args": {"filter": "pending"}}, ensure_ascii=False)
        return json.dumps({"action": "list_tasks", "args": {}}, ensure_ascii=False)

    # 完成任务
    if any(w in user_input for w in ["完成", "标记", "做完"]) and ("第" in user_input or any(c.isdigit() for c in user_input)):
        import re
        nums = re.findall(r"\d+", user_input)
        task_id = int(nums[0]) if nums else 1
        return json.dumps({"action": "done_task", "args": {"task_id": task_id}}, ensure_ascii=False)

    # 删除所有任务（危险操作）
    if "删除所有" in user_input or "全部删除" in user_input or "清空" in user_input:
        return json.dumps({"action": "delete_all_tasks", "args": {}}, ensure_ascii=False)

    # 默认回复帮助
    return json.dumps({"action": "help", "args": {}}, ensure_ascii=False)


# ── 模块 3：parse_model_output ─────────────────────────────────

def parse_model_output(model_output):
    """解析模型输出的 JSON 字符串为动作指令

    返回 dict: {"action": str, "args": dict} 或 {"error": "描述"}
    """
    try:
        data = json.loads(model_output)
    except json.JSONDecodeError:
        return {"action": "help", "args": {}, "error": "模型输出不是合法 JSON"}

    action = data.get("action", "")
    args = data.get("args", {})

    if action not in VALID_ACTIONS:
        return {"action": "help", "args": {}, "error": f"未知动作：{action}"}

    return {"action": action, "args": args}


# ── 模块 4：guardrail ──────────────────────────────────────────

def guardrail(action):
    """安全检查：判断动作是否可以执行

    返回: {"pass": True/False, "reason": str}
    """
    if action["action"] in DANGEROUS_ACTIONS:
        return {
            "pass": False,
            "reason": "⚠️ 危险操作拒绝执行：「删除所有任务」需要人工手动确认。"
                       "请在 CampusTask 中执行：rm tasks.json",
        }
    return {"pass": True, "reason": ""}


# ── 模块 5：execute_tool ───────────────────────────────────────

def execute_tool(action):
    """执行解析后的工具调用

    action: {"action": str, "args": dict}
    返回执行结果字符串。
    """
    act = action["action"]
    args = action.get("args", {})

    # 导入 campus_task 服务模块
    # 使用绝对导入，确保可直接运行
    from task_service import add, list_all, done

    if act == "add_task":
        title = args.get("title", "新任务")
        deadline = args.get("deadline", "")
        try:
            task = add(title, deadline)
            msg = f"添加任务成功：{task.title}（编号 {task.id}）"
            if deadline:
                msg += f"，截止 {deadline}"
            return msg
        except ValueError as e:
            return f"添加任务失败：{e}"

    elif act == "list_tasks":
        tasks = list_all()
        if not tasks:
            return "当前没有任务。"
        filter_status = args.get("filter")
        if filter_status:
            tasks = [t for t in tasks if t.status == filter_status]
            if not tasks:
                return f"没有{filter_status}的任务。"
        lines = [f"  {t.id}. [{t.status}] {t.title}" for t in tasks]
        return "当前任务：\n" + "\n".join(lines) + f"\n共 {len(tasks)} 项"

    elif act == "done_task":
        task_id = args.get("task_id")
        if not task_id:
            return "缺少任务编号。"
        result = done(task_id)
        return result

    elif act == "delete_all_tasks":
        return "❌ 操作被安全护栏拦截，已拒绝。"

    elif act == "help":
        return (
            "可用命令：\n"
            "  - 添加任务：帮我把 <标题> 添加到任务列表\n"
            "  - 查看任务：列出我的任务\n"
            "  - 完成任务：把第 3 个任务标记为完成\n"
            "  - 帮助：你能做什么？"
        )

    return f"未知操作：{act}"


# ── 模块 6：write_trace ────────────────────────────────────────

def write_trace(event):
    """将一次运行的完整事件写入 trace.jsonl

    event 包含：用户输入、prompt、模型输出、解析后动作、guardrail、执行结果
    """
    event["timestamp"] = datetime.now().isoformat()
    with open(TRACE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


# ── 模块 7：run_eval ───────────────────────────────────────────

def run_eval(eval_cases):
    """运行评测集，返回统计结果

    eval_cases: [{"input": str, "expected_action": str}, ...]
    返回: {"total": N, "passed": N, "accuracy": float, "details": [...]}
    """
    passed = 0
    total = len(eval_cases)
    details = []

    for case in eval_cases:
        user_input = case["input"]
        expected = case["expected_action"]

        prompt = prompt_builder(user_input)
        raw = mock_model(prompt)
        parsed = parse_model_output(raw)
        actual = parsed.get("action", "unknown")

        ok = actual == expected
        if ok:
            passed += 1

        details.append({
            "input": user_input,
            "expected": expected,
            "actual": actual,
            "passed": ok,
        })

    accuracy = passed / total if total > 0 else 0.0
    return {
        "total": total,
        "passed": passed,
        "accuracy": accuracy,
        "details": details,
    }


# ── 交互式运行 ─────────────────────────────────────────────────

def run_once(user_input):
    """一次完整流程：输入→prompt→模型→解析→护栏→执行→记录"""
    from task_storage import load_all

    task_state = load_all()
    prompt = prompt_builder(user_input, task_state)
    raw = mock_model(prompt)
    parsed = parse_model_output(raw)
    check = guardrail(parsed)

    if not check["pass"]:
        result = check["reason"]
    else:
        result = execute_tool(parsed)

    event = {
        "user_input": user_input,
        "prompt": prompt,
        "model_output": raw,
        "parsed_action": parsed,
        "guardrail": check,
        "result": result,
    }
    write_trace(event)

    print(f"🤖 {result}")
    return event


def interactive():
    """交互式 AI 助手"""
    print("=" * 50)
    print("CampusTask AI 助手（Mock 模式）")
    print("输入 'exit' 退出，输入 'eval' 运行评测")
    print("=" * 50)
    while True:
        try:
            user_input = input("\n🧑 你说：").strip()
            if user_input.lower() in ("exit", "quit", "退出"):
                print("👋 再见！")
                break
            if user_input.lower() == "eval":
                run_eval_interactive()
                continue
            if not user_input:
                continue
            run_once(user_input)
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except EOFError:
            break


def run_eval_interactive():
    """交互式运行评测"""
    cases = load_eval_cases()
    if not cases:
        print("❌ 未找到 eval_cases.json")
        return
    result = run_eval(cases)
    print("\n📊 评测结果")
    print(f"  总用例：{result['total']}")
    print(f"  通过：{result['passed']}")
    print(f"  准确率：{result['accuracy']:.0%}")
    print("\n详情：")
    for d in result["details"]:
        icon = "✅" if d["passed"] else "❌"
        print(f"  {icon} 输入：{d['input']}")
        print(f"     期望：{d['expected']} → 实际：{d['actual']}")


def load_eval_cases():
    """从 eval_cases.json 加载评测集"""
    try:
        with open("eval_cases.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


# ── 主入口 ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # 命令行模式：python ai_harness.py "用户输入"
        run_once(" ".join(sys.argv[1:]))
    else:
        interactive()
