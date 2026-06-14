"""__main__ — CampusTask 包入口：python -m campus_task <命令>"""

import argparse
import logging
import sys

from . import __version__
from . import task_service

# ── 日志配置 ───────────────────────────────────────────────────
_LOG_FILE = "campus_task.log"
_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=_LOG_FORMAT,
    handlers=[
        logging.FileHandler(_LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger("campus_task")


# ── 显示函数 ──────────────────────────────────────────────────

def _show_tasks(tasks, header=True):
    if not tasks:
        print("📋 任务列表为空")
        return
    if header:
        print(f"{'编号':<6}{'状态':<10}{'deadline':<14}{'创建时间':<22}{'标题'}")
        print("-" * 70)
    for t in tasks:
        status = "✓ 已完成" if t.is_done() else "○ 待处理"
        dl = t.deadline if t.deadline else "-"
        print(f"{t.id:<6}{status:<10}{dl:<14}{t.created_at:<22}{t.title}")


# ── 子命令处理函数 ─────────────────────────────────────────────

def cmd_add(args):
    try:
        task = task_service.add(args.title, args.deadline)
        msg = f"[✓] 任务已添加：{task.title}（编号：{task.id}）"
        if args.deadline:
            msg += f" [截止：{args.deadline}]"
        logger.info("添加任务: id=%d title=%s", task.id, task.title)
        print(msg)
    except ValueError as e:
        logger.error("添加任务失败: %s", e)
        print(f"[✗] {e}")


def cmd_list(args):
    if args.sort == "deadline":
        tasks = task_service.list_sorted_by_deadline()
    elif args.filter == "pending":
        tasks = task_service.list_all(status="pending")
    elif args.filter == "done":
        tasks = task_service.list_all(status="done")
    else:
        tasks = task_service.list_all()
    _show_tasks(tasks)


def cmd_done(args):
    result = task_service.done(args.task_id)
    if "已完成" in result:
        logger.info("完成任务: id=%d", args.task_id)
    print(result)


def cmd_export(args):
    try:
        task_service.export_csv(args.filepath)
        logger.info("导出 CSV: %s", args.filepath)
        print(f"[✓] 已导出到 {args.filepath}")
    except Exception as e:
        logger.error("导出失败: %s", e)
        print(f"[✗] 导出失败：{e}")


# ── 主解析器 ──────────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(
        prog="campus-task",
        description="校园任务清单命令行工具",
        epilog="更多信息见 USER_GUIDE.md",
    )
    parser.add_argument(
        "--version", action="version", version=f"campus-task {__version__}"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add", help="添加新任务")
    p_add.add_argument("title", help="任务标题")
    p_add.add_argument("--deadline", default="", help="截止日期，如 2026-06-20")
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = sub.add_parser("list", help="列出任务")
    p_list.add_argument("--filter", choices=["pending", "done"], help="按状态过滤")
    p_list.add_argument("--sort", choices=["deadline"], help="排序方式")
    p_list.set_defaults(func=cmd_list)

    # done
    p_done = sub.add_parser("done", help="完成任务")
    p_done.add_argument("task_id", type=int, help="任务编号")
    p_done.set_defaults(func=cmd_done)

    # export
    p_export = sub.add_parser("export", help="导出为 CSV")
    p_export.add_argument("filepath", help="CSV 文件路径")
    p_export.set_defaults(func=cmd_export)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    logger.debug("命令: %s, 参数: %s", args.command, args)
    args.func(args)


if __name__ == "__main__":
    main()
