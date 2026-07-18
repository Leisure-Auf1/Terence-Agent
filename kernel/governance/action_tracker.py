"""B.6.4 — Action Tracker: proposal → decision → execution → result audit."""

import time, os, json

ACTION_DIR = os.path.expanduser("~/.hermes/runtime/governance/actions")
HISTORY_DIR = os.path.expanduser("~/.hermes/runtime/governance/history")
os.makedirs(ACTION_DIR, exist_ok=True)
os.makedirs(HISTORY_DIR, exist_ok=True)

def create_action(proposal_id: str, decision: str, executor: str = "kernel") -> dict:
    action = {
        "action_id": f"act-{int(time.time())}",
        "proposal_id": proposal_id,
        "decision": decision,
        "executor": executor,
        "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "completed": None,
        "result": "pending"
    }
    fname = os.path.join(ACTION_DIR, f"{action['action_id']}.json")
    with open(fname, "w") as f:
        json.dump(action, f, indent=2)
    return action

def update_result(action_id: str, result: str) -> dict:
    fname = os.path.join(ACTION_DIR, f"{action_id}.json")
    if not os.path.exists(fname): return {"error": "Action not found"}
    with open(fname) as f: action = json.load(f)
    action["result"] = result
    action["completed"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(fname, "w") as f: json.dump(action, f, indent=2)
    # Archive to history
    hist_file = os.path.join(HISTORY_DIR, f"{action_id}.json")
    with open(hist_file, "w") as f: json.dump(action, f, indent=2)
    return action

def get_history(limit: int = 50) -> list:
    results = []
    for fname in sorted(os.listdir(HISTORY_DIR)):
        if fname.endswith(".json"):
            with open(os.path.join(HISTORY_DIR, fname)) as f:
                results.append(json.load(f))
    return results[-limit:]
