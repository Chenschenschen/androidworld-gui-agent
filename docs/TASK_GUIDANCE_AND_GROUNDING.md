# Explicit task procedures and current grounding

The user requested explicit task recommendations on 8 October, replacing the
previous preference for minimal completion-only guidance. This authorizes
procedural hints in the model's context. It does not authorize Python replaying
GUI actions, choosing the next digit, giving hidden verifier feedback, sending
messages or forcing completion. One agent/step and one runner remain.

## Five current warm-ups

The actual editable model guidance is [task_guides.md](../instructions/task_guides.md).
Only the selected section is supplied with each action request, together with
the original task inputs, current screenshot, fresh GUI labels and history.

| Task | Starting app and recommended route | Completion evidence |
|---|---|---|
| Wi-Fi | Settings → Network & internet → Internet/Wi-Fi; read switch and enable only if OFF | Fresh Wi-Fi ON state; a network connection is unnecessary |
| Photo | Camera → ready Photo preview → one shutter tap | One capture plus new thumbnail/preview; never another capture to check |
| Timer | Clock → Timer; understand right-aligned HHMMSS buffer, compare prefix and pick one next digit; delete a wrong suffix | Exact hours/minutes/seconds, Start still available, unstarted |
| Contact | Contacts → Create contact → exact field values → Save | Saved name and phone match; unsaved filled form is insufficient |
| Clipboard | Markor → QuickNote editor → exact text → long press → Select all → Copy | The entire requested value was selected before Copy; visible clipboard preview if available |

Clipboard is a text-entry/selection operation, not a search for a clipboard
manager. Chrome was chosen earlier only as an available editable field; the
model then explored unrelated browser menus. Markor directly supports editing
and copying text, and already belongs to the agreed later course scope.
[Markor's own documentation](https://github.com/gsantner/markor) lists QuickNote
and copy-to-clipboard support. Its official Android World setup/install/snapshot
is reused; preparation is separate from benchmark GUI actions.

Messages is installed on this emulator and is a reasonable alternative using
an unsent draft. Its recipient/onboarding path has not been verified in this
runner; it is not advertised as an available fallback in this variant. Markor
avoids a recipient and Send button. No message is sent by the clipboard route.

## Grounding: yes, with a specific limitation

Current grounding has three parts:

1. AutoGLM maps the screenshot to a normalized point or box. Python checks
   its range/shape and converts it to emulator pixels; a box uses its centre.
2. Fresh paired UIAutomator data supplies labels, editable/focused flags and
   normalized control centres in supported packages. Markor is included in the
   guided variant. The model is told to use the centre of a matching label.
3. Before execution, the agent reobserves and checks the selected GUI identity
   and nearby pixels; a stale target is discarded with bounded reobservation.

This does not independently verify the model's semantic intent. The native
reply has coordinates, not a required label/index. A tap can be in range and
fresh yet refer to the wrong field. If no UI element is matched, the check uses
image freshness only. Camera/Contacts currently use screenshot grounding;
the original Settings/Clock/Chrome packages use the checked XML supplement.
There is no separate grounding model or automatic label-to-action resolver.

We retained native AutoGLM coordinates because that is its trained action
contract. Globally using Android World's accessibility-forwarder tree caused
recorded idle/crash/stale-observation failures. The bounded fresh XML supplement
preserves the successful repair instead of returning to that failing backend.
Adding an independent semantic-grounding mechanism would be a separate change;
these procedures improve intent clarity without pretending that coordinate
validation alone proves the intended control was hit.

## Source basis and evaluation distinction

- Course D2 step3_skill_status.py loads procedural guidance separately from
  code-maintained factual status. This implementation follows that small pattern.
- D4 goal clarity, actionable observations, verification and bounded recovery
  explain why routes, exact values and observable stopping conditions matter.
- [Pinned M3A guidance](https://github.com/google-research/android_world/blob/2dfc5ca3dc590efe9c72ce768f2b04182f2f75c7/android_world/agents/m3a.py)
  explains visible target selection, complete text selection and easiest routes.
- [AutoGLM native contract](https://github.com/zai-org/Open-AutoGLM/blob/86f55382982fb054e8fc98ca80609dff8a2cdc3c/phone_agent/config/prompts_en.py)
  defines screenshot coordinates and Type on the focused text field.
- Timer mechanics and the partial-domain selection warning are derived from
  our recorded actual GUI failures, not presented as verbatim upstream recipes.

These are our user-authorized task-specific procedures. They are not the
original reference policy. Report any later results as **guided task trials**;
do not compare them to unguided leaderboard scores as if the input were equal.
The official verifier still judges outcome after the model stops. Guidance
preparation alone establishes no improvement or reliable success rate.

## Configuration and independent execution

`guided_config.json` enables v36 procedures and the Markor Clipboard route.
Default `agent_config.json` remains the recorded v35 baseline. No live guided
trial has been run; 28 offline checks pass, including selected-guide request
assembly and task-specific Timer values. No package or second agent was added.

From the project folder, use the same Python entry point for every task:

```powershell
.\.venv\Scripts\python.exe -X utf8 run_task.py --task SystemCopyToClipboard --seed 43 --config guided_config.json
```

Replace only `--task` and `--seed` for another warm-up. The first guided Clipboard
run will install/set up Markor through Android World's official app preparation
because it is not currently installed. This setup is outside the recorded agent
actions; initialization restores a clean editor snapshot on later runs. The
selected guide and configuration are saved with each run's source snapshot.
Guided Clipboard configurations with a different editor are rejected rather
than providing the model a route to an unavailable app.
