"""Verify saved Contacts gates and replay the Timer guard without device/API calls."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from autoglm_agent import repeated_without_progress


def read_json(path):
    """Read one original evidence file without modifying it."""
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    """Check immutable trial results and write a separate derived evidence record."""
    batches = [ROOT / "runs" / name for name in (
        "easy_batch_20261008T081652_065024Z", "easy_batch_20261008T082214_015428Z")]
    fingerprints = [read_json(batch / "batch.json")["source_hashes"] for batch in batches]
    assert fingerprints[0] == fingerprints[1], "Contacts source versions differ"
    contacts = []
    # Inspect all three named trials; never combine a failed run with a replacement.
    for name in ("trial_ContactsAddContact_20261008T081652_701104Z",
                 "trial_ContactsAddContact_20261008T082214_643123Z",
                 "trial_ContactsAddContact_20261008T082325_354857Z"):
        summary = read_json(ROOT / "runs" / name / "summary.json")
        assert summary["clean_agent_success"] and summary["steps"] == 11
        contacts.append({"run_id": name, "steps": summary["steps"],
                         "duration_seconds": summary["duration_seconds"]})
    timer = ROOT / "runs/trial_ClockTimerEntry_20261008T081804_857919Z"
    actions, results, blocked_step = [], [], None
    # Replay saved decisions against the new control bound only; execute nothing.
    for line in (timer / "trajectory.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record["event"] == "EXECUTION START":
            # The observed-result action is semantic text without coordinates;
            # compare the original checked execution decisions instead.
            action = record["data"]
            if repeated_without_progress(action, actions, results):
                blocked_step = record["step"]
                break
            actions.append(action)
        elif record["event"] == "OBSERVED RESULT":
            results.append(record["data"])
    assert blocked_step == 12, "Guard does not stop the recorded Timer cycle"
    evidence = {"contacts_frozen_sources_match": True, "contacts_clean_trials": contacts,
                "v29_timer_guard_counterfactual_block_before_step": blocked_step,
                "device_actions": 0, "model_calls": 0,
                "limitation": "Offline replay only; Timer still failed and no live v29 success is established."}
    destination = ROOT / ".tools/final_evidence_20261008.json"
    destination.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    main()
