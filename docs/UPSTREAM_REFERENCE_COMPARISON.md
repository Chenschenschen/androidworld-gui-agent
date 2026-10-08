# Pinned upstream reference comparison

**Outcome: the native reference did not solve the failed warm-ups.** Four
comparable task trials were measured (one Timer and one Clipboard instance per arm), all
official FAIL. Three additional pre-model/prerequisite/recording attempts are
preserved separately. This is a small diagnostic comparison, not a reliability
evaluation. No new three-run success gate or harder-task expansion follows.

The user authorized the revised recommendation on 8 October: establish the
original AutoGLM reference first, compare it with our Android World adaptation,
and consider another model only after separating model and adapter errors.
This stage does not create a goal or introduce a different model.

Reference: zai-org/Open-AutoGLM commit
`86f55382982fb054e8fc98ca80609dff8a2cdc3c`, clean checkout under
`.tools/Open-AutoGLM`. The wrapper imports its actual PhoneAgent, ModelClient,
English prompt, conversation builder, screenshot and ADB action implementations.
It snapshots every Python source and the expanded native prompt in each run.
Its Apache-2.0 license remains in the original checkout.

| Property | Project v34 | Upstream reference v1 |
|---|---|---|
| Hosted model / sampling | AutoGLM multilingual, 0 / .85 / .2 / 3000 | Same |
| Step / agent time budget | 12 / 900 seconds for Timer and Clipboard | Same |
| Official initialization / seed / verifier / video | Shared runner | Shared runner |
| Image | Resized to maximum 1280 | Full native 1080×2400 screenshot |
| Prompt | Adapted prompt, visible completion, allowed apps | Original English prompt with host date |
| Observation text | Fresh checked GUI labels and actual prior result | Native current-app name |
| History | Adapted chronological conversation | Original upstream conversation |
| API | Standard-library nonstreaming | Original SDK streaming, openai 2.9.0 |
| Actions | Android World helpers with freshness checks | Original native ADB helpers and delays |
| Reflection | Disabled | Absent upstream |

This first comparison changes an integration bundle. A result can distinguish
the reference bundle from our adapter; it cannot attribute causality to one
prompt/image/backend difference without a later controlled test.

Necessary boundary deviations: only emulator-5554; checked single literal calls
and bounded arguments; no interactive takeover; API timeout capped at120 seconds
and retries disabled; no black fallback image sent to the model; parse, model or
execution errors never count as model completion. Recording and API evidence are
added. None supplies task progress, hidden verifier feedback or a GUI recipe.

Preflight found Pillow12.3.0 already meets upstream's >=12 requirement. The
project venv now has upstream's minimum SDK openai2.9.0. ADB Keyboard is absent
from the emulator. Native Type stops before dispatch if its prerequisite is
missing; do not substitute our typing implementation and call it native.
The original app map distinguishes Clock (`com.android.deskclock`) and
Google Clock (`com.google.android.deskclock`). Preserve any resulting launch
failure rather than silently modifying the reference map.

Run the reference with the same existing entry point:

```powershell
& .venv\Scripts\python.exe -X utf8 run_task.py --task ClockTimerEntry --seed 42 --config reference_config.json
```

The ordinary command without `--config` still selects our project agent. All
five task names share this runner; this adds one comparison adapter, not one
agent per task. Offline:20 existing checks plus3 reference boundary checks pass.
Live results must be appended below after inspecting original artifacts.

## Native Timer result and diagnosis before the comparison arm

`trial_ClockTimerEntry_20261008T110453_899546Z`, reference v2, seed42:
official FAIL, initial0/final0, no model finish,12 GUI actions/12 model calls,
65.188 agent seconds/69.094 total seconds; valid recording with no reported
video errors. Goal:20 hours,7 minutes,1 second, without starting the timer.

Inspected all12 original replies, requests, parsed actions and native execution
results, plus the full step9 screenshot. Step5 invents the string `20271`.
After correctly observing `00h00m20s`, step7 taps7 instead of inserting the
remaining padded zeros. Step8 thinks another7 will set the minutes to07.
Step9 screenshot actually shows `00h20m77s`: the reply reads those values but
then treats77 as minutes and assumes appending0 will correct that field.
It produces `20h77m01s` by step11 and only begins deleting at step12.
These are keypad-state/planning errors with real visible input, not Python
overriding the next digit. The original screenshot policy did not remove them.

Native integration caveat: step1 Launch Clock maps to an absent package; the
unmodified helper reports True despite no launch. Step2 opens the visible Clock
icon. This wastes a step, but the later explicit wrong digit decisions occur
after successful entry into the correct app. The comparator will retain equal
budgets; this small sample cannot establish overall model inadequacy or isolate
image resolution as the cause. No identical failed reference retry follows.
Next is the separately defined project-v34 arm, official reset, same seed/model,
sampling/budgets, with its existing prompt/observations unchanged.

## First pre-model failure and correction

`trial_ClockTimerEntry_20261008T110331_988395Z`: zero model calls and zero GUI
actions. The trajectory records UnicodeEncodeError while importing the unused
Chinese prompt date expression before English PhoneAgent construction. Its
very short recording was invalid too. This is infrastructure evidence, not
model capability. Equivalent Windows-safe date interpolation is applied only
in memory to that unused Chinese module; the clean checkout and English prompt
stay unchanged. Import preflight passed before the corrected v2 trial.

## Project Timer comparator and next independent case

`trial_ClockTimerEntry_20261008T110722_819990Z`, project v34, seed42:
official FAIL, initial0/final0, no finish;10 GUI actions,11 model calls,
131.438 agent seconds/135.516 total seconds. The unchanged no-progress guard
rejects step11 before execution. Recording has no reported errors.
Original requests contain the exact target200701 and visible digit counts;
replies5–10 repeatedly choose0 and say they are moving toward07 minutes.
This fills the display with20h00m00s. Subsequent zeros have no visible effect,
and the existing cycle bound stops it. No action replay or Timer retry follows.

Both integration bundles fail this instance, with distinct wrong choices.
Native model misinterprets digit shifting; the adapted model perseverates in
its history despite exact numeric input and accurate observed display. These
results support a concrete planning/history weakness for this instance, not a
blanket statement that the model lacks vision or cannot perform easy tasks.

The separately defined Clipboard seed43 comparison follows. Before any trial,
install/enable only the official native keyboard prerequisite from the package
linked by Open-AutoGLM README_en.md. Repository senzhk/ADBKeyBoard commit
`d7b27288bc8c1c8348a79ea6896bd7352c30a9fc`; original ADBKeyboard.apk SHA256
`e698adea5633135a067b038f9a0cf41baa4de09888713a81593fb2b9682cdc59`.
Native Type will still switch/restore the IME itself. Installation is emulator
infrastructure preparation; it supplies no clipboard value or task completion.

### Clipboard prerequisite failure, preserved before a changed retry

`trial_SystemCopyToClipboard_20261008T111031_420458Z`:7 dispatched GUI actions,
8 requests, no finish, official FAIL,52.078 total seconds. The model searched
Settings for clipboard. Step8 chose Type("clipboard") in Settings search, but the
checked boundary stopped it before execution because ADB Keyboard was absent
from the enabled-IME list. No text/clipboard value was written by a controller.
`step_008/boundary_error.json` preserves that original cause; upstream's fallback
finish then triggered a secondary parser mismatch. The runner's validation
error label describes that secondary exception, not the prerequisite cause.

The APK installed successfully, but the immediately following ime-enable
command returned Unknown input method. The trial should not have started.
Read-only diagnosis then found the registered service in `ime list -a -s`,
while the enabled list still lacked it. Re-enabling after registration succeeded,
and enabled-IME/default-keyboard checks passed. Reference v3 adds an enabled-IME
and import preflight before initialization/video, and preserves the first boundary
cause through upstream fallback handling. Its model prompt, images, conversation,
sampling and action policy remain identical. This is a corrected infrastructure
trial, not an unchanged retry or evidence that the model cannot copy text.

### Corrected native Clipboard result and diagnosis before comparison

`trial_SystemCopyToClipboard_20261008T111249_290736Z`, reference v3, seed43:
official FAIL, initial0/final0, model finish,8 steps/8 calls/7 GUI actions,
51.234 agent seconds/63.719 total seconds, no recording errors.
All8 replies/actions were inspected. Native Type correctly enters the whole
`john.doe@example.com` into Settings search. A long press selects only the
domain. The original step7 screenshot shows highlight/selection handles around
`example.com`, with `john.doe@` outside the selection. The model says the text
is selected, taps the real Copy menu, and then declares the whole email copied
because the menu disappeared. Official verifier fails. This is lost_value plus
false_done, with a visible partial selection; no hidden verifier feedback is
available to the model. Native typing works after prerequisite repair.
Do not rerun this failed native policy unchanged. The next independent arm is
project v34, same official seed/reset/model/sampling/budgets.

### Invalid project Clipboard arm and transport correction

`trial_SystemCopyToClipboard_20261008T111502_200837Z`: official FAIL,3 GUI
actions/5 calls, no finish,58.469 total seconds; evaluation invalid due to
recording loss. Preserve the original summary. Recovered original clip
`recovered_video_001.mp4` covers only about10.18 seconds, not the agent phase.
Original responses after the first corrected Chrome launch repeatedly choose
Launch Chrome despite observing its home page and visible editable address bar;
the fourth proposed launch is rejected by the existing no-progress guard.

Console records a5-second cold Chrome launch timeout. Inspected Android Env's
actual AdbController.execute_command: on the first timeout it restarts ADB
(`kill-server`, `start-server`) and retries. The recorder then exits; the runner
noticed only at final kill, when its PID no longer existed. Recent logcat and
the original MP4 are retained locally. Inference from the timeout, actual retry
source and short clip: the ADB server restart explains lost video, distinct
from model perseveration.

Corrected bounded arm keeps v34 model policy/prompt/observations. Only Chrome
launch transport uses the same official component and am-start command in one
direct ADB call with30-second timeout and no retry/server restart. Recorder
readiness now monitors process exit every.25 seconds instead of blindly waiting
174 seconds. No model hints or task recipe added. Config comparison_config.json
preserves this transport variant; default agent settings stay unchanged until
the measured outcome is reviewed.25 offline checks pass, including early
recorder exit and launch-timeout non-replay regressions. A clean corrected
Clipboard arm is required before counting the paired result.

### Corrected project Clipboard result and final comparison

`trial_SystemCopyToClipboard_20261008T112059_418312Z`, transport v35, seed43:
official FAIL, initial0/final0, no finish,12 GUI actions/12 calls,
194.360 agent seconds/207.594 total seconds; two videos and no recording errors.
Chrome launch now returns once without timeout or ADB restart. Original replies
and resulting screens show a cycle: More options → Chrome Settings → Back,
repeated until the12-step limit. The model says another approach is needed but
repeats the same cycle. It never types or copies the supplied email. The existing
no-visible-effect guard cannot catch a cycle with changing screens; the step
budget still bounds it. The policy is frozen during the trial; no fabricated
task recipe or post-failure rerun follows.

| Task / seed | Original native policy | Project policy | Valid outcome |
|---|---|---|---|
| Timer /42 | Wrong keypad padding and field interpretation;12 actions, no finish | Repeated zero taps;10 actions, no-progress stop | Both FAIL |
| Clipboard /43 | Copies selected domain only;7 actions, false finish | Cycles through menus;12 actions, no finish, corrected transport | Both FAIL |

The reference improves neither task to verified completion. Native full-resolution
images do not remove the Timer planning error, and native Clipboard can type and
reach Copy but mistakes a partial selection for the requested whole value.
The project adapter also has real faults: prior infrastructure assumptions,
perseveration despite factual feedback, and cycle detection limited to no-effect
actions. A different model has not been compared, so this does not establish
which alternative would succeed or that every failure belongs to the model.
Reported upstream/leaderboard scores concern other evaluation setups and cannot
be substituted for our observed results.

Next proposed stage: a bounded policy/model comparison using these preserved
failure states and the same runner, then an explicitly scoped course goal covering
linked easy/medium/hard tasks. A goal organizes persistent work; it does not
guarantee correct decisions. No new model or goal is adopted by this report.

## Reproduce without separate scripts per task

Project defaults now use the measured v35 infrastructure repair (assessment off).
comparison_config.json preserves that trial's settings. All tasks use
the same run_task.py, class selection through config only:

```powershell
# Existing project policy with the measured recording/Chrome transport repair
& .venv\Scripts\python.exe -X utf8 run_task.py --task SystemCopyToClipboard --seed 43 --config comparison_config.json

# Official native reference (after the setup below)
& .venv\Scripts\python.exe -X utf8 run_task.py --task SystemCopyToClipboard --seed 43 --config reference_config.json
```

These commands document the recorded variants, not an instruction to repeat a
known failed configuration unchanged. Each failure requires diagnosis and a
justified change first. To prepare the optional reference on another machine:

```powershell
git clone https://github.com/zai-org/Open-AutoGLM.git .tools/Open-AutoGLM
git -C .tools/Open-AutoGLM checkout 86f55382982fb054e8fc98ca80609dff8a2cdc3c
& .venv\Scripts\python.exe -m pip install openai==2.9.0
git clone https://github.com/senzhk/ADBKeyBoard.git .tools/ADBKeyBoard
git -C .tools/ADBKeyBoard checkout d7b27288bc8c1c8348a79ea6896bd7352c30a9fc
$comparisonAdb = Join-Path $env:LOCALAPPDATA 'Android/Sdk/platform-tools/adb.exe'
& $comparisonAdb -s emulator-5554 install .tools/ADBKeyBoard/ADBKeyboard.apk
# Wait for registration: the all-IME list must show the service before enabling.
& $comparisonAdb -s emulator-5554 shell ime list -a -s
& $comparisonAdb -s emulator-5554 shell ime enable com.android.adbkeyboard/.AdbIME
& $comparisonAdb -s emulator-5554 shell ime list -s
```

Follow [the pinned upstream setup guide](https://github.com/zai-org/Open-AutoGLM/blob/86f55382982fb054e8fc98ca80609dff8a2cdc3c/README_en.md)
and [keyboard instructions](https://github.com/senzhk/ADBKeyBoard/tree/d7b27288bc8c1c8348a79ea6896bd7352c30a9fc).
Project setup, .env and emulator prerequisites remain docs/SETUP.md. The enabled
list must contain `com.android.adbkeyboard/.AdbIME`; installation success alone
is insufficient. Keep each external license. No local model is started.

## Evidence audit and adopted infrastructure repair

The measured v35 launch transport and live-recorder monitoring are retained in
the normal runnable default. These repair real infrastructure faults and make
recording failure visible promptly; they establish no new task success claim.
Default tasks still share one project agent; the reference is optional.

[Seven-attempt audit](evidence/upstream_reference_audit.json): all444 JSON files
parse; readable requests contain neither the actual API key nor embedded image
data. Every completed valid clip decodes fully. The initial import-error clip
is invalid, and the recovered10.18-second clip cannot establish coverage of its
45.922-second agent phase. Both are retained. The keyboard-prerequisite trial
has evaluation_valid=true in its original summary (initialization and video
were valid), but is excluded from the four comparable capability trials because
native typing could not execute. No original summary was rewritten.

[Policy AST hashes](evidence/reference_policy_hashes.json) confirm identical
native_prompt, completion_condition, ask_action, request_model, observe,
supplement_controls and assessment_text functions across project Timer v34,
invalid Clipboard v34 and corrected Clipboard v35. The adapted native prompt
file is identical too. The transport repair changed dispatch and recording,
not the model's decision input construction.25 offline regressions pass.
Independent run.ps1 -CheckOnly passed from outside the project. All trials are
finished; local Ollama remains off.

