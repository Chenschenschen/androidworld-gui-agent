# SimpleSmsSend, 8 October 2026

One screenshot-based trial requested by the user. Existing general_config.json,
hosted autoglm-phone-multilingual, seed42, native actions, no task procedure or
separate reflection. Added only the runner's official task/app mapping and a
visible sent-message completion condition. Source: pinned Android World
single/sms.py, common_validators/sms_validators.py and setup_device/apps.py.
The official verifier checks a recent sent message and the foreground SMS app.

First attempt: trial_SimpleSmsSend_20261008T130519_446713Z. Invalid setup,
zero model calls/actions, no recording, verifier NOT_RUN. Its traceback identifies
the official SMS setup's am start -W command exceeding the SDK's five-second
timeout. The default SMS setting already names com.simplemobiletools.smsmessenger.
This is an environment launch failure, not evidence about model capability.

Before retry: keep single-attempt dispatch and give only SDK am start commands
a minimum 30-second timeout. Other commands retain their existing bounds. No
uncertain command is automatically replayed and ADB is not restarted. Preserve
the first attempt unchanged. Runtime sources and prompts freeze during the retry.

## Recorded result

trial_SimpleSmsSend_20261008T130636_231233Z: **PASS**, initial score0.0/final1.0,
model finish at step10, nine GUI actions and eleven model calls. Valid recording,
no manual intervention, no runtime or recording errors. Total131.53 seconds;
agent phase89.17 seconds. The agent typed +11043321819 and the exact message
"I think, therefore I am.", tapped Send, observed the outgoing bubble/checkmark
and independently chose finish. No task procedure or extra assessment call.
Screenshots only for SMS: no SMS accessibility-tree supplement was supplied.
Native ADB Keyboard transported both fields without Enter and restored Gboard.

All100 JSON artifacts parse and contain no API credential; the saved video fully
decodes (237 frames,87.86 seconds).36 offline checks pass, including the launch
timeout's one-dispatch regression. This is one clean success, not three-run
reliability. The earlier failed setup remains separate and unchanged.

Reproduce from the project folder, with the emulator running:

```powershell
.\.venv\Scripts\python.exe -X utf8 run_task.py --task SimpleSmsSend --seed 42 --config general_config.json
```

## Additional trials: seed43 diagnosis before seed44

User requested two further runs. Seed43,
trial_SimpleSmsSend_20261008T131434_882794Z, is a valid officialFAIL0.0,
no model finish,11 GUI actions/13 calls, stopped before a twelfth dispatch by
the no-progress guard. Recording is valid; originals are unchanged.

First causal error: step4 observation shows New conversation with the recipient
field and Maya Martin (+18126340319) underneath. Before dispatch, freshness_0
already shows Maya Martin's conversation. The checker accepted this different
screen because mean global difference0.03606 and target difference0.04538
were below0.08 and both tree targets were absent. Thus a stale tap was allowed.
Step5 typed the requested +10427517979 into the message body; step7 replaced it
with the requested text, and step8 sent it in the wrong conversation. This is
an own-code freshness fault followed by model lost_value/grounding failure.

Step9 also emitted malformed finish syntax; its correction switched to Tap.
Steps10–12 claimed completion in prose but emitted more Send taps. That separate
native-output inconsistency remains unresolved; Python must not infer finish
from prose or verifier feedback.

Before the second requested run (seed44), change only the existing global
freshness threshold from0.08 to0.01, matching the visual settling tolerance.
Replay of step4's recorded check must reject the stale scene at this bound.
No new prompt, procedure or framework. general_config.json identifies this
variant as v46_sms_freshness. Results across variants are not a frozen3/3 claim.

## Seed44 and final result of the requested two additional runs

trial_SimpleSmsSend_20261008T131850_007058Z: valid officialFAIL0.0, zero GUI
actions, two model calls, no finish. The model returned Launch with the translated
app value "简单短信消息发送器". The correction explicitly supplied the allowed
"simple sms messenger"; the model acknowledged that exact name in prose but
returned the same Chinese value again. The strict app-name validator stopped it.
This is a model action-contract failure, not an installation or API failure.
The tighter freshness threshold was not exercised by a dispatched action.
No alias guessing, parser weakening or additional retry was performed.

| Seed | Variant | Official result | Model finish | Agent seconds |
| --- | --- | --- | --- | --- |
|42|v45|PASS|Yes|89.17|
|43|v45|FAIL|No|102.02|
|44|v46 freshness candidate|FAIL|No|11.55|

One clean success among three requested trials (33.3%), across two variants.
The unchanged v45 cases are1/2. This does not establish a reliability gate or a
live successful freshness repair. Both new videos fully decode (seed43:268
frames/101.49 seconds; seed44:3 frames/9.9 seconds). All128 new JSON files parse
and contain no API key. See evidence/sms_additional_trials_audit.json.
All original summaries remain unchanged. No trial or new task is running.

## User-requested retry: v47

Before retry, preserve the recorded diagnoses above. Retain the tighter0.01
global freshness threshold. Clarify literal app/action arguments and standalone
finish in the existing native prompt; invalid Launch feedback now supplies valid
pseudo-call examples using the allowed values. Invalid-action feedback reminds
the model of standalone finish syntax. These clarify the pinned AutoGLM native
contract (config/prompts_en.py); they do not infer actions from prose, translate
unknown app strings, bypass validation or prescribe an SMS route.

Retry seed43, then seed44 if the clean-completion gate passes. Runtime/prompts
freeze while running. This evaluates the repairs together, not isolated prompt
effect or established reliability. Screenshot-only SMS observations remain.

v47 seed43, trial_SimpleSmsSend_20261008T132430_837967Z: valid officialFAIL,
zero GUI actions, two calls, no finish. Exact syntax examples did not change
the returned app value: both replies used "简单短信消息". Prompt-only correction
did not repair this contract mismatch. The new offline correction fixture initially
lacked a logging output path; fixed only the fixture after trial start, with no
runtime/prompt edit during the run.37 offline checks then passed. Starting the
trial before checking that test result was a sequencing mistake.

Before the next retry, v48 adds an exact app-name mapping for the two recorded
Chinese translations and pinned upstream SimpleSMSMessenger identifier to
Android World's simple sms messenger. Open-AutoGLM config/apps.py uses a finite
app-name/package dictionary; these Chinese SMS names are our observed adapter
additions, not claimed upstream aliases. Canonical name must still be task-allowed;
unknown names remain rejected. Original native reply and normalized action are
both logged. No GUI decision is inferred or replayed. Retain v47 prompt and0.01
freshness; test the same seed43 before attempting44.

v48 seed43, trial_SimpleSmsSend_20261008T132625_711688Z: valid officialFAIL,
two actions/four calls. Launch mapping worked. Step3 discarded an old main-list
tap when New conversation appeared. Its second observation still showed that
same recipient screen; freshness_1 showed the same field with keyboard now open.
Target patch difference was0.0, but mean global difference0.02430 exceeded0.01,
so the trial stopped before another action. The stricter scalar threshold blocks
a harmless keyboard transition and is insufficient as the intended repair.

Before retry, v49 enables the existing checked XML supplement for the SMS package
and restores global bound0.08. Preserve screenshot input plus observed labels,
hint/editable/focus properties and normalized centres; no extra model call.
Empty editable fields were erroneously omitted by screen_controls; include them
and their observed hint so an empty recipient field remains visible in the model
context. Also reject a target that appears only in the fresh tree, rather than
treating absence in the earlier tree as automatic identity agreement. Existing
different-target identity checks reject recipient-field/contact-row mismatches.
This is the existing grounding path, not a task procedure or semantic controller.

## v49 outcome: both failed seeds repaired in the measured pair

| Seed | Run ID | Initial/final verifier | Model finish | Steps | Agent seconds |
| --- | --- | --- | --- | --- | --- |
|43|trial_SimpleSmsSend_20261008T132854_166582Z|0.0/1.0 PASS|Yes|7|121.36|
|44|trial_SimpleSmsSend_20261008T133321_726192Z|0.0/1.0 PASS|Yes|7|123.84|

Identical runtime sources, prompts and settings were verified across the final
pair. Each run used six GUI actions/nine calls, two discarded stale decisions,
model-chosen finish, no extra assessment call, no manual intervention and no
runtime/recording errors. Fresh SMS labels and normalized centres were actually
supplied; typing and GUI Send produced the requested recipient/message.39 offline
checks pass. The final videos fully decode (317 and338 frames,120.62 and122.99
seconds). All203 JSON artifacts from v47/v48/v49 attempts parse and contain no
API key. Audit: evidence/sms_retry_audit.json. Original failed runs are unchanged.

Comparable original failed seeds43/44:0/2 clean; final v49 retries:2/2 clean.
Repairs were staged together, so these results do not isolate a single cause's
effect. Prompt-only v47 and scalar-threshold v48 failed and remain evidence.
Earlier seed42 PASS used v45; v49 has two clean runs, not a frozen three-run gate.
No trial is running. Reproduction command above selects the latest v49 settings.
