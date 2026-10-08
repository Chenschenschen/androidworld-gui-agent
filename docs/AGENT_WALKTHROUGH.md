# Explain the agent

This is one Python agent controlling a test Android emulator through Android
World. Z.ai hosts `autoglm-phone-multilingual`; no local language model is needed.
The model selects the GUI action and declares completion. Android World's
official task verifier independently checks the result afterward.

## Files to read

| File | Purpose |
| --- | --- |
| `run_task.py` | Prepare/reset an official task, start video, run bounded steps, verify and save the summary. |
| `autoglm_agent.py` | Observe, request one model decision, validate/ground it, execute once and record the next state. |
| `instructions/autoglm.md` | Explain allowed operations and completion-first behavior to the model. |
| `agent_config.json` | Freeze the model, prompt version, sampling, observation settings and budgets. |
| `android_compat.py` | Keep Windows APK handling and unique, checked UIAutomator captures working. |
| `trajectory.py` | Write readable and structured evidence immediately. |
| `evaluate_tasks.py` | Schedule three official trials per selected task; it chooses no GUI actions. |
| `run.ps1` | Check readiness and launch the project Python interpreter. |

Original GELab code and course examples are retained as historical material.

## One step

1. Observe the current screenshot. Settings, Clock and Chrome may receive a fresh
   official GUI tree, accepted only when paired with an unchanged fresh image.
2. Send the current image, original goal, exact requested values, visible GUI
   properties and executed conversation to the model. Older images are removed.
3. Parse the returned pseudo-call as **data**, never Python code. Allow only
   known operations and literal, checked arguments. Exact duplicate calls mean
   one unique decision; different calls are rejected.
4. Convert a normalized point or ordered model-selected box to screen pixels.
   Check the chosen target against a fresh observation before dispatch.
5. Execute one checked Android GUI action and record the actual next observation.
   Type replaces focused text without adding Enter. An uncertain dispatch is
   never replayed automatically.
6. Repeat until the model returns `finish`, an error occurs, or the step/time
   budget is reached. A budget stop is not task completion.

The agent permits one invalid-reply correction and one reconsideration of an
unexecuted stale target. Every completed step retains its input, reply, parsed
action, execution start, next screenshot and timing.

## What completion means

| Task | Visible goal supplied to the model |
| --- | --- |
| Wi-Fi | Settings' Wi-Fi switch is ON. Internet connectivity is not required. |
| Camera | One shutter capture has a new thumbnail/photo result; do not capture again. |
| Timer | Exact requested hours/minutes/seconds are entered, and the timer remains unstarted. |
| Contacts | Exact name/phone are saved and visible in the saved contact. |
| Clipboard | Entire exact text was selected, Copy was tapped, and its selection menu closed. A chip/toast is optional. |

Clock's `01h 33m 33s` observation can be rendered as digit buffer `13333`, count
5. Python does not compare that buffer to the target or choose a next digit.
The original requested duration and its literal HHMMSS value remain in context;
there is no Python-computed next-digit instruction or keypad Type exception.
Likewise, `text_to_copy` describes the requested clipboard value; it is not a
read of current clipboard contents. Original official parameters stay in logs.

## Explain the result honestly

`agent_done` records model finish. `verifier` records official PASS/FAIL/ERROR.
`clean_agent_success` requires both, valid initialization/video, and no runtime
error. A plausible screenshot or a verifier PASS at the step limit is insufficient
for this stage. Three trials are a small sample, not general reliability.

See [RUNNING_TASKS.md](RUNNING_TASKS.md) for standalone commands and
[AUTOGLM_COMPLETION_REPAIR.md](AUTOGLM_COMPLETION_REPAIR.md) for preserved failures,
protocol changes and live evidence. Easy warm-ups do not replace the remaining
medium/hard course tasks or their evaluations.
