"""Attach retrospective interpretations without changing original trial summaries."""

import json
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from probe_connection import save_json


def main():
    """Add specific failure diagnoses and count actual image-bearing request logs."""
    cases = {
        "trial_ContactsAddContact_20261007T152803_891284Z": {
            "category": "validation_error", "failure_class": None,
            "evidence": "Two image fallbacks permitted two GUI actions; step 3 exhausted fallback budget after invalid native tree replies."},
        "trial_ContactsAddContact_20261007T153448_933813Z": {
            "category": "stale_observation_stop", "failure_class": "lost_value",
            "evidence": "Step 5 typed Camila; step 7 typed only da from da Silva. Phone and save never executed. Step 9 selected Cancel but freshness guard stopped execution.",
            "limitation": "The mismatching fresh observation was not saved; do not invent its changed element."},
    }
    # Review completed runs only, preserving their original raw requests/replies/results.
    for name, analysis in cases.items():
        folder = PROJECT / "runs" / name
        image_calls = 0
        tree_calls = 0
        # Count the logged API payloads, not assumptions from the configured policy.
        for path in folder.glob("step_*/*/request_*.json"):
            request = json.loads(path.read_text(encoding="utf-8"))
            if any(message.get("images") for message in request["messages"]):
                image_calls += 1
            else:
                tree_calls += 1
        analysis.update(official_verifier_score=0.0, verified_agent_success=False,
                        tree_calls=tree_calls, image_calls=image_calls)
        target = folder / "analysis.json"
        if not target.exists():
            save_json(target, analysis)
        print(name, analysis)


if __name__ == "__main__":
    main()
