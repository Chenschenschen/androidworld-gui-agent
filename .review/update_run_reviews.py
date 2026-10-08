"""Attach honest retrospective interpretations without changing original trial evidence."""

from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from probe_connection import save_json


def main():
    """Save specific failure evidence and exclude the invalid Wi-Fi starting state."""
    reviews = {
        "trial_ContactsAddContact_20261007T144105_002848Z": {
            "evaluation_valid": True, "verified_agent_success": False,
            "category": "validation_error", "failure_class": None,
            "evidence": ["step_001: native annotation accepted, Contacts opened",
                "step_003: tap opened Create contact form",
                "step_004: first-name field focused",
                "step_005: type:Camila returned twice without action:TYPE/value fields"],
            "official_verifier_score": 0.0,
            "conclusion": "Parser correction enabled four GUI actions; no task success improvement in the one matched pair.",
            "candidate_change": "Native action examples in the prompt; user choice pending"},
        "trial_SystemWifiTurnOn_20261007T144747_582753Z": {
            "evaluation_valid": False, "verified_agent_success": False,
            "category": "initialization_error", "failure_class": None,
            "initial_verifier_score": 1.0, "final_verifier_score": 1.0,
            "agent_actions": 0,
            "conclusion": "Verifier PASS was already satisfied; exclude from agent success counts.",
            "diagnostic": ".review/wifi_start_diagnostic.json",
            "correction": "Reset before official initialization, as in the official minimal runner; abort if initial score is not zero."},
    }
    # Write each interpretation once; the API replies, configs, and summaries stay intact.
    for name, review in reviews.items():
        target = PROJECT / "runs" / name / "analysis.json"
        if not target.exists():
            save_json(target, review)
    target = PROJECT / "runs/probe_20261007T143127_998674Z/classification_review.json"
    if not target.exists():
        save_json(target, {
            "original_interpretation": "General validator accepted COMPLETE as a legal terminal action.",
            "corrected_interpretation": "This probe required selecting Settings with CLICK. COMPLETE is a failed target probe.",
            "note": "validation.json was corrected during the live review; raw API response was unchanged.",
            "executed": False})


if __name__ == "__main__":
    main()
