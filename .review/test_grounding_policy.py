"""Offline boundary checks for mode switching; all model responses are mocked."""

from datetime import datetime, timezone
import io
import json
from pathlib import Path
import shutil
import sys
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from compare_prompts import load_case
from gelab_agent import GelabAgent, parse_json_action, validate_action


def run_case(name, replies, expected_calls, expected_mode, expected_error=False):
    """Check a bounded mode transition without contacting Ollama or executing Android."""
    state, _ = load_case("trial_ContactsAddContact_20261007T144105_002848Z", "step_005", "test")
    output = PROJECT / ".review" / datetime.now(timezone.utc).strftime(f"test_{name}_%Y%m%dT%H%M%S_%fZ")
    output.mkdir()
    source = PROJECT / "runs/trial_ContactsAddContact_20261007T144105_002848Z/step_005/model_input.png"
    shutil.copyfile(source, output / "model_input.png")
    config = json.loads((PROJECT / "agent_config.json").read_text(encoding="utf-8"))
    config["action_format"] = "native"  # Exercise the already recorded native fallback path.
    class FakeEnv:
        """Return a saved state; no Android execution interface is provided."""
        def get_state(self, **kwargs):
            """Return the same immutable observation for the freshness check."""
            return state
    agent = GelabAgent(FakeEnv(), output, config, {})
    inputs = []
    def reply(request, **kwargs):
        """Capture the actual API payload and return the next mocked response."""
        inputs.append(json.loads(request.data))
        raw = replies[len(inputs) - 1]
        return io.StringIO(json.dumps({"message": {"content": raw}, "done_reason": "stop"}))
    with patch("gelab_agent.urllib.request.urlopen", side_effect=reply):
        try:
            _, action, mode = agent.choose_action(state, output, "test", {"step": 1})
            assert not expected_error
            assert mode == expected_mode
        except ValueError:
            assert expected_error
    assert len(inputs) == expected_calls
    assert all("images" not in payload["messages"][1] for payload in inputs[:2])
    if expected_calls == 3:
        assert "images" in inputs[2]["messages"][1]
        assert agent.corrections_this_step == 1
        assert len(agent.fallback_events) == 1
    print(name, "PASS", "calls", len(inputs))


def main():
    """Test original-index mapping, single correction, fallback, and rejection bounds."""
    state, _ = load_case("trial_ContactsAddContact_20261007T144105_002848Z", "step_005", "test")
    fields = parse_json_action('{"action":"TYPE","index":0,"value":"+10433218196","verify":"field selected"}', "tree")
    assert validate_action(fields, state, "tree")["text"] == "+10433218196"
    bad_replies = [
        '{"action":"CLICK","action":"TYPE","index":7,"value":"x","verify":"x"}',
        '{"action":"CLICK","index":true,"value":"","verify":"x"}',
        '{"action":"EXEC","index":0,"value":"unsafe","verify":"x"}',
    ]
    # JSON enforcement is not trusted alone: duplicate keys, wrong types/actions reject in Python.
    for raw in bad_replies:
        try:
            parse_json_action(raw, "tree")
            raise AssertionError("Invalid JSON action accepted")
        except ValueError:
            pass
    action = validate_action({"action": "CLICK", "index": "7"}, state, "tree")
    assert (action["x"], action["y"]) == tuple(map(int, state.ui_elements[7].bbox_pixels.center))
    state.ui_elements[7].is_enabled = False
    try:
        validate_action({"action": "CLICK", "index": "7"}, state, "tree")
        raise AssertionError("Disabled target accepted")
    except ValueError:
        pass
    print("JSON boundaries and exact phone text PASS")
    run_case("index_valid", ["action:CLICK\tindex:7"], 1, "tree")
    run_case("bounded_fallback", ["TYPE\tvalue:Camila", "TYPE\tvalue:Camila", "action:CLICK\tpoint:500,400"], 3, "screenshot")
    run_case("fallback_invalid_stops", ["CLICK\tindex:7", "CLICK\tindex:7", "action:EXEC\tvalue:unsafe"], 3, None, True)


if __name__ == "__main__":
    main()
