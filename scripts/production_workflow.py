#!/usr/bin/env python3
"""Phase P.0.4 — Hermes Production Workflow Runner.

真实 workflow 通过 Kernel 全管道执行（非模拟、非画图）：

  resolver.resolve_capabilities  → 意图匹配候选技能
  permission_gate.check_permission → 层级门控
  context_manager.load_context   → 加载真实 SKILL.md 上下文
  <real action>                  → 执行真实生产动作（shell 命令，真实计时）
  telemetry.collector + event_store → 真实遥测落盘
  health_engine.evaluate         → 执行后健康评估

用法:
  python3 scripts/production_workflow.py daily-production-report
  python3 scripts/production_workflow.py --list
"""

import json
import os
import subprocess
import sys
import time

KERNEL = os.path.expanduser("~/.hermes/kernel")
REPO = os.path.expanduser("~/Terence-Agent")
WF_DIR = os.path.join(REPO, "production", "workflows")
RUN_DIR = os.path.join(REPO, "production", "runs")

sys.path.insert(0, KERNEL)

from resolver.capability_resolver import resolve_capabilities, _load_registry  # noqa: E402
from runtime.permission_gate import check_permission, REQUIREMENTS  # noqa: E402
from runtime.context_manager import load_context, use_context, release_context  # noqa: E402
from telemetry.collector import collect, validate_schema  # noqa: E402
from telemetry.event_store import append_event  # noqa: E402
from health.health_engine import evaluate  # noqa: E402


def load_workflow(name):
    """加载 workflow 定义（轻量 YAML 子集解析，无第三方依赖）。"""
    path = os.path.join(WF_DIR, f"{name}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"workflow 未定义: {path}")
    return json.load(open(path))


def registry_meta(skill_id):
    reg = _load_registry()
    for s in reg["skills"]:
        if s["name"] == skill_id:
            return s
    return {}


def run_step(step, caller_tier, caller_scope):
    """单步执行：kernel 全管道 + 真实动作。"""
    sid = step["skill"]
    intent = step["intent"]
    print(f"\n▶ Step: {step['name']}  (skill={sid})")

    # ── Stage 1: Resolver ──
    cands = resolve_capabilities(intent, caller_scope=caller_scope)
    top = [c["skill_id"] for c in cands[:5]]
    hit = sid in top
    print(f"  [resolver]   {len(cands)} 候选, top5={top} → {'✅ 命中' if hit else '⚠️ 指定技能未进 top5，按显式绑定继续'}")

    # ── Stage 2: Permission Gate ──
    perm = check_permission(caller_tier, REQUIREMENTS["execute_skill"], "execute_skill")
    print(f"  [permission] {'✅' if perm['allowed'] else '❌'} {perm['reason']}")
    if not perm["allowed"]:
        return {"status": "PERMISSION_DENIED", "skill_id": sid, "execution_id": f"exec-{int(time.time())}"}

    # ── Stage 3: Context Load（真实 SKILL.md）──
    meta = registry_meta(sid)
    ctx = load_context(sid, meta.get("mount", "routed"), meta.get("path"))
    if ctx["status"] != "CONTEXT_READY":
        print(f"  [context]    ❌ {ctx.get('error')}")
        return {"status": "CONTEXT_LOAD_FAILED", "skill_id": sid,
                "execution_id": f"exec-{int(time.time())}", "error": ctx.get("error")}
    context_id = ctx["context"]["context_id"]
    use_context(context_id)
    print(f"  [context]    ✅ {context_id} — SKILL.md {ctx['context'].get('content_sha256','')[:12]}…")

    # ── Stage 4: 真实动作执行 ──
    execution_id = f"exec-{int(time.time()*1000)}"
    t0 = time.time()
    proc = subprocess.run(["bash", "-c", step["action"]], capture_output=True,
                          text=True, timeout=step.get("timeout_s", 300), cwd=REPO)
    duration_ms = int((time.time() - t0) * 1000)
    ok = proc.returncode == 0
    tail = (proc.stdout.strip().splitlines() or ["<no output>"])[-1]
    print(f"  [execute]    {'✅' if ok else '❌'} rc={proc.returncode} {duration_ms}ms — {tail[:100]}")
    release_context(context_id)

    result = {
        "status": "SUCCESS" if ok else "FAILED",
        "execution_id": execution_id,
        "skill_id": sid,
        "duration_ms": duration_ms,
        "error": None if ok else (proc.stderr.strip().splitlines() or ["nonzero exit"])[-1],
        "error_class": None if ok else "F6",
        "log": {"stages": [{"stage": "execution", "attempt": 1,
                            "result": "SUCCESS" if ok else "ERROR"}]},
    }

    # ── Stage 5: Telemetry（真实落盘）──
    rec = collect(result, skill_namespace=meta.get("namespace", ""), caller_scope=caller_scope)
    assert validate_schema(rec), "telemetry record schema invalid"
    stored = append_event(rec)
    print(f"  [telemetry]  ✅ 事件已落盘 → {os.path.basename(stored['file'])}")

    # ── Stage 6: Health（执行后评估）──
    h = evaluate(sid)
    print(f"  [health]     {h['state']} score={h['score']}")

    result["health"] = {"state": h["state"], "score": h["score"]}
    return result


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "--list":
        print("可用 workflows:")
        for f in sorted(os.listdir(WF_DIR)):
            if f.endswith(".json"):
                wf = json.load(open(os.path.join(WF_DIR, f)))
                print(f"  {f[:-5]:35s} — {wf.get('description','')}")
        return 0

    name = sys.argv[1]
    wf = load_workflow(name)
    caller_tier = wf.get("caller_tier", 1)
    caller_scope = wf.get("caller_scope", "adapter")

    print(f"══ Workflow: {wf['name']} ══")
    print(f"   {wf.get('description','')}")
    print(f"   caller: tier={caller_tier} scope={caller_scope} · steps={len(wf['steps'])}")

    t0 = time.time()
    results = []
    for step in wf["steps"]:
        r = run_step(step, caller_tier, caller_scope)
        results.append({"step": step["name"], **{k: r.get(k) for k in
                        ("status", "execution_id", "skill_id", "duration_ms", "health")}})
        if r["status"] != "SUCCESS" and step.get("critical", True):
            print(f"\n🔴 关键步骤失败: {step['name']} — 中止 workflow")
            break

    elapsed = round((time.time() - t0) * 1000)
    n_ok = sum(1 for r in results if r["status"] == "SUCCESS")
    verdict = "SUCCESS" if n_ok == len(wf["steps"]) else "FAILED"

    # 运行记录落盘（仓库内，可审计）
    os.makedirs(RUN_DIR, exist_ok=True)
    run_id = f"run-{time.strftime('%Y%m%d-%H%M%S')}"
    run_record = {
        "run_id": run_id, "workflow": name, "verdict": verdict,
        "steps_total": len(wf["steps"]), "steps_success": n_ok,
        "elapsed_ms": elapsed,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results": results,
    }
    rpath = os.path.join(RUN_DIR, f"{run_id}-{name}.json")
    with open(rpath, "w") as f:
        json.dump(run_record, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\n══ Workflow {verdict}: {n_ok}/{len(wf['steps'])} steps · {elapsed}ms ══")
    print(f"📝 运行记录: {rpath}")
    return 0 if verdict == "SUCCESS" else 1


if __name__ == "__main__":
    sys.exit(main())
