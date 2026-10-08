# Before/after assessment experiment, 8 October 2026

User authorized adapting the researched method to failed Timer and Clipboard
tests before advancing. This is one existing agent with the same hosted
AutoGLM model, native action prompt, sampling and GUI execution contracts.

## Purpose and implementation

Adapt the pinned official M3A SUMMARY_PROMPT_TEMPLATE: after a dispatched
non-finish action, ask the model to compare actual before/after screenshots,
GUI properties, original goal, previous explanation and actual selected control.
Save its short visible assessment and include it in the next action request.
Sources: [M3A](https://github.com/google-research/android_world/blob/2dfc5ca3dc590efe9c72ce768f2b04182f2f75c7/android_world/agents/m3a.py),
[prior comparison](LEADERBOARD_COMPARISON.md), D3 feedback/D4 progress checks in
[course mapping](COURSE_AND_UPSTREAM_REVIEW.md).

Assessment requests never dispatch a GUI action, change a task state directly,
or receive an official verifier score. Finish remains the action model's decision;
there is no separate completion-review gate in this experiment. The existing
12-step/900-second task bounds remain. Calls are bounded by the finite step,
correction and reobservation limits and the shared deadline. Additional requests
increase latency and usage. Full dispatched-action evidence is saved before
assessment, so an API/format failure cannot lose it or replay uncertain actions.
Snapshot the assessment prompt in each trial and batch source fingerprints.

## Probe failure: diagnose before retry

`step_assessment_probe_20261008T095742_351562Z`, Timer step5 from preserved
v28 seed42. API accepted two images and returned a reply in 2.66 seconds. The
visible prose correctly identified actual `00h 02m 07s` versus target `20h 07m 01s`,
then incorrectly recommended another `1` and appended `do(action="Tap",...)`.
Our new assessment parser rejected that call, so the probe stopped before the
Clipboard case. No operation was executed; this is an assessment-output contract
failure, not an Android World evaluation or successful recovery.

Correction before another request: accept the native reply's existing visible
prose as assessment, discarding standalone operation lines as inert data. Keep
pure operation-only responses invalid. Do not fabricate a correct summary,
extract hidden reasoning or execute the discarded proposal. Save discarded
lines and raw replies. The summary may itself be wrong; test its effect rather
than assuming the method solved the task. The task action prompt is unchanged.

## Verification and evaluation status

Eighteen offline checks passed before the probe, including distinct before/after
inputs, assessment presence in the next action request, and no executable
assessment output. Protocol correction and live results will be recorded below.

v31 parser correction passed all18 checks. The changed saved-evidence probe
`step_assessment_probe_20261008T095936_238890Z` accepted both two-image responses
and dispatched nothing. Timer's summary recognizes the wrong value but still
proposes wrong1; Clipboard again incorrectly claims that Clear input copied
the email, referring to the unrelated old suggestion. Thus the reflection
method is not established as a semantic repair. Do not rerun either saved-state
probe unchanged or claim it passes a recovery/completion gate. One fresh live
Timer trial will test a different question: whether assessment after every
earlier step prevents the first wrong action. It is not a replay of these saved
decisions. Diagnose the live trace before any further run.

Baseline failures: Timer v28 seed42 omitted zero at step5 and finished no task;
Clipboard v27 seed43 selected Clear input and false-finished. Baseline successful
gates remain v20 Wi-Fi/Camera and v28 Contacts. No current frozen 15/15 claim.
Run a comparable bounded case for each failed task, then repeat successful
cases on three seeds before expanding. Stop and diagnose any failure first.

## Timer live failure: recorded before the independent Clipboard trial

v31 seed42, [summary](../runs/trial_ClockTimerEntry_20261008T100055_458184Z/summary.json):
valid evaluation, officialFAIL, model finish=false,12 steps,27 API calls
(12 assessments),260.78 seconds, two video clips and no recording error.
The same seed/prompt/sampling/12-step v28 baseline failed in149.36 seconds
with12 calls; v29 also added a no-effect cycle bound between these versions.
This single comparison establishes no statistical speed or reliability claim.

First error: step4 observed20; its assessment listed200701 yet recommended7.
Step5 followed that recommendation, skipping the required zero. Later
assessments misinterpreted hours/minutes/seconds and suggested wrong repairs.
Steps8/9 used backspace, so this was attempted recovery rather than solely an
unchanged-tap loop. Step9 even calls07 seconds correct for a target of01.
Final screenshot and GUI tree agree on20h70m01s, with Start still available.
The model never finished. Calls at steps10–12 hit3000 output tokens; their one
allowed unexecuted corrections returned checked actions. Original replies,
usage, invalid replies and all assessments remain saved.

Diagnosis: model value/sequencing and recovery failure, compounded by incorrect
assessment feedback. This is not a fresh-tree mismatch, direct task-state write,
or verifier failure. Do not rerun Timer unchanged or increase steps to disguise
this failure. The method did not repair Timer and added cost. An independent
first live Clipboard case tests whether ongoing early feedback prevents its
different grounding/false-completion error; this is not a repeated Timer trial.

## Clipboard live failure and source-contract correction

v31 seed43, [summary](../runs/trial_SystemCopyToClipboard_20261008T100628_570867Z/summary.json):
valid evaluation, officialFAIL, model finish=true,2 steps,4 calls (1 assessment),
38.80 seconds, valid recording. First unavailable Launch google was corrected
to chrome. After Launch, assessment claimed there was no input/copy functionality
and assumed the supplied email must be found in an unspecified other app. The
next action finished with a request for clarification, although the original
goal and inputs already contained the email. The screenshot visibly has Chrome's
Search or type web address field. No Type/selection/Copy occurred. This is
wrong task interpretation and premature stop, recorded as false_done by our
native finish mapping; the finish message itself asks for help rather than
claiming a successful copy. Do not rerun this v31 trial unchanged.

Source comparison after failure exposed an implementation omission: official
M3A SUMMARY_PROMPT_TEMPLATE starts with PROMPT_PREFIX, which explains the
agent role and available action capabilities. Our standalone summary prompt
omitted that shared context. This is a confirmed source difference and a
plausible contributor to the erroneous task interpretation, not a proven sole
cause. v32 supplies the same native agent/action context, allowed apps and exact
task inputs before the read-only assessment instructions, matching that M3A
structure. Last instructions still request assessment; any operation output
remains inert. No new app-specific procedure, coordinate controller, model,
sampling or completion gate is added. Correct this omission, check offline,
then one bounded comparable Clipboard regression; no unchanged replay.

v32 regression `trial_SystemCopyToClipboard_20261008T100911_808026Z` stopped
at step1: both calls supplied an unavailable app; the correction copied literal
`app_name` from the generic example. OfficialFAIL,0 completed steps,2 calls,
0 assessments,16.66 seconds and valid recording. This is model argument/contract
failure before the new mechanism; it does not evaluate the shared-prefix
assessment. Preserve it separately from v31's semantic failure. No unchanged
task retry. Use the changed v32 assessment on the saved failure states instead,
without dispatching a Launch or inventing an app-selection fallback. The generic
example-copy failure remains unresolved and must be corrected/tested before
another full Clipboard trial.

The changed v32 saved probe `step_assessment_probe_20261008T101147_854103Z`
still proposes wrong1 for Timer. Clipboard invents a `Copy text` GUI node with
bounds that appear in neither supplied before/after tree; it also incorrectly
claims the cleared field still contains the email. Shared context alone is not
an established fix. Preserve these hallucinations and do not repeat the probe.

v33 addresses the separately diagnosed example-copy error: render the existing
native Launch example with a real member of the supplied app list, in both
action and assessment context. This parameterizes the existing upstream-style
example; it adds no task recipe or automatic Launch fallback. The model still
chooses the action and invalid app arguments are still rejected. One bounded
Clipboard regression follows this recorded contract repair; do not count it
as a single-variable estimate of reflection's contribution.

v33 check `trial_SystemCopyToClipboard_20261008T101351_637369Z` launched Chrome
after one corrected unavailable app. Its first assessment hit3000 output tokens
and was rejected as truncated. OfficialFAIL, no model finish,3 calls and48.02
seconds. Original summary steps=0 means zero fully returned agent steps, not
zero GUI operations: execution_start/result prove **one actual Launch**. No
Type/selection/Copy happened. Original summary remains unchanged; the audit
records the real dispatch count. New summaries explicitly count dispatched GUI
actions and classify assessment failures separately, without replaying actions.

## Outcome and current default

| Trial | GUI actions | Assessments attempted | Official outcome | Model finish |
| --- | --- | --- | --- | --- |
| Timer42 v31 | 12 | 12 | FAIL; wrong value, step limit | No |
| Clipboard43 v31 | 1 | 1 | FAIL; wrong task interpretation | Yes; asks for clarification |
| Clipboard43 v32 | 0 | 0 | FAIL; unavailable app arguments | No |
| Clipboard43 v33 | 1 | 1 | FAIL; truncated assessment | No |

No successful live gate, no three-repeat reliability claim, no later course
task expansion. These are different variants, not a frozen repeatability batch.
The evidence shows this same-model adaptation did not solve the failures; it
does not show that the M3A mechanism is ineffective with every model. Model
assessment hypotheses cannot replace observed state or the official verifier.

v34 keeps the method implemented but disabled by default (`step_assessment=false`).
The separate assessment_config.json retains the final v33 opt-in settings for
inspection/reproduction of the unsuccessful experiment. Original per-run source
and configuration snapshots are authoritative; subsequent diagnostic bookkeeping
fixes are not retroactively part of those trials. Do not treat this config as
a recommended successful setup or rerun the failed task unchanged. The existing
checked GUI loop remains the normal independent Python entry point.

Twenty offline checks pass, including actual dispatch preservation after a failed
assessment. Readiness from C:/Users/koc passed with no model call. All four trials'
JSON and videos were audited; full recordings decode, all prompts are snapshotted,
credentials are absent and readable requests contain no base64. Dispatch counts
are12/1/0/1. [Audit](evidence/step_assessment_audit.json). Original videos, images,
raw replies, API usage, source snapshots and initial/final verifiers remain local.

## Causal attribution follow-up: model versus agent

The user's follow-up asks whether the model or agent is insufficient. The
evidence establishes immediate errors, not a model-only causal explanation.

- Timer v31: the supplied GUI correctly shows20 and the goal specifies200701;
  the model recommends7 and the adapter correctly taps7. This is a model
  sequencing decision error under our supplied context, not incorrect execution.
  v31 did not yet include the later shared action-output prefix, so that later
  conflict cannot explain its original error.
- v32/v33 assessment: our adaptation reused the entire native action prompt,
  including strict operation-output instructions, then requested summary-only
  output. This is a confirmed agent prompt inconsistency. It is a plausible
  contributor to protocol/length failures; the trials do not isolate its effect.
  The official M3A shared prefix was not an instruction to copy our whole
  AutoGLM action-output contract into another role.
- Assessment prose enters history under the wording Actual observed result.
  Although the JSON key says model_assessment, the outer wording mixes inferred
  hypotheses with device facts. Preserve these as separate types of information
  in any future revision. Wrong suggested repairs can contaminate later decisions.
- All native finish calls map to goal_status=complete. The Clipboard message
  asking for clarification shows why model stopped and goal achieved must remain
  distinct. The independent verifier correctly kept this trial FAIL.
- v33 generated the same clipboard sentence31 times before hitting3000 tokens.
  More output budget would permit a longer loop, not establish a better summary.

Recommendation, not an adopted change: first remove the assessment output-contract
conflict and separate observed evidence, model hypotheses and stop semantics.
Then compare the current model with a more capable multimodal model on identical
saved failure observations using one fixed checked action interface. Include
correct states as well as errors, with no verifier feedback in model input.
Follow any useful result with a bounded live comparison and three seeds. Keep
one agent and the independent Python entry point. Model replacement or a separate
review model remains a user decision; no new provider/model call was made here.
These small mixed-version trials cannot identify a percentage contribution from
model capacity versus harness design, or prove a limitation of every9B model.
