#!/usr/bin/env python3
"""main — CampusTask 命令行交互层"""

import sys
import task_service


def _list(custom_tasks=None):
    """显示任务列表，可传入自定义排序的任务列表"""
    if custom_tasks is None:
        tasks = task_service.list_all()
    else:
        tasks = custom_tasks
    if not tasks:
        print("📋 任务列表为空")
        return
    print(f"{'编号':<6}{'状态':<10}{'deadline':<14}{'创建时间':<22}{'标题'}")
    print("-" * 70)
    for t in tasks:
        status = "✓ 已完成" if t.is_done() else "○ 待处理"
        dl = t.deadline if t.deadline else "-"
        print(f"{t.id:<6}{status:<10}{dl:<14}{t.created_at:<22}{t.title}")


def _list_filtered(filter_status):
    """按状态过滤并显示任务列表"""
    tasks = task_service.list_all(status=filter_status)
    if not tasks:
        print(f"📋 没有{filter_status}的任务")
        return
    _list(tasks)


def _list_sorted_by_deadline():
    """按 deadline 排序显示"""
    tasks = task_service.list_sorted_by_deadline()
    if not tasks:
        print("📋 任务列表为空")
        return
    print(f"{'编号':<6}{'状态':<10}{'deadline':<14}{'创建时间':<22}{'标题'}")
    print("-" * 70)
    for t in tasks:
        status = "✓ 已完成" if t.is_done() else "○ 待处理"
        dl = t.deadline if t.deadline else "-"
        print(f"{t.id:<6}{status:<10}{dl:<14}{t.created_at:<22}{t.title}")


def _add(title, deadline=""):
    try:
        task = task_service.add(title, deadline)
        msg = f"[✓] 任务已添加：{task.title}（编号：{task.id}）"
        if deadline:
            msg += f" [截止：{deadline}]"
        print(msg)
    except ValueError as e:
        print(f"[✗] {e}")


def _done(task_id_str):
    try:
        task_id = int(task_id_str)
    except ValueError:
        print("[✗] 错误：任务编号必须是数字")
        return
    print(task_service.done(task_id))


def _export(filepath):
    """导出任务为 CSV 文件"""
    try:
        task_service.export_csv(filepath)
        print(f"[✓] 已导出到 {filepath}")
    except Exception as e:
        print(f"[✗] 导出失败：{e}")


def _usage():
    print("用法：")
    print('  python main.py add "任务标题" [--deadline 日期]   # 添加任务')
    print("  python main.py list [--pending|--done]            # 列出/过滤任务")
    print("  python main.py list --sort deadline               # 按 deadline 排序")
    print("  python main.py done <编号>                        # 完成任务")
    print("  python main.py export <文件名.csv>                 # 导出 CSV")
    print("  python main.py                                    # 列出所有任务")


COMMANDS = {"add": _add, "list": _list, "done": _done, "export": _export}


def _parse_add_args(args):
    """解析 add 命令的参数，支持 --deadline 选项"""
    title = args[0] if args else ""
    deadline = ""
    if "--deadline" in args:
        idx = args.index("--deadline")
        args.pop(idx)
        deadline = args.pop(idx) if idx < len(args) else ""
    return title, deadline


def main():
    if len(sys.argv) == 1:
        _list()
    elif len(sys.argv) >= 2 and sys.argv[1] in COMMANDS:
        cmd = COMMANDS[sys.argv[1]]
        args = sys.argv[2:]
        if cmd is _add:
            if len(args) < 1 or args[0].startswith("--"):
                print('[✗] 用法：python main.py add "标题" [--deadline 日期]')
                return
            title, deadline = _parse_add_args(args)
            _add(title, deadline)
        elif cmd is _list:
            if len(args) == 0:
                _list()
            elif len(args) == 1:
                if args[0] == "--pending":
                    _list_filtered("pending")
                elif args[0] == "--done":
                    _list_filtered("done")
                elif args[0] == "--sort" or "--sort" in args:
                    _list_sorted_by_deadline()
                else:
                    print(f"[✗] 未知选项：{args[0]}")
            elif len(args) == 2 and args[0] == "--sort" and args[1] == "deadline":
                _list_sorted_by_deadline()
        elif cmd is _done and len(args) != 1:
            print("[✗] 用法：python main.py done <编号>")
        elif cmd is _export and len(args) != 1:
            print("[✗] 用法：python main.py export <文件名.csv>")
        else:
            cmd(*args)
    else:
        _usage()


if __name__ == "__main__":
    main()
