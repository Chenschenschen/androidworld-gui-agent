# Why the five easy-task trials failed

Latest user-run Camera190644 stopped after one launch-icon tap: next Home
observation changed to launch splash, then onboarding; model called logo a
shutter. Both stale choices blocked, official FAIL. Diagnosis and prepared
v57 checked Camera-label repair: CAMERA_SELF_RUN_REPAIR.md. No new live PASS.

8 October upstream-reference diagnosis: the pinned native PhoneAgent also
failed Timer seed42 (`trial_ClockTimerEntry_20261008T110453_899546Z`). Step7
appends7 after20, skipping padded zeros; step9 sees00h20m77s but confuses which
field77 belongs to and treats appending0 as a field correction. Original
screenshots and replies are preserved. The preceding attempt failed before
inference on a Windows import error, fixed only after recording its cause.
See [UPSTREAM_REFERENCE_COMPARISON.md](UPSTREAM_REFERENCE_COMPARISON.md).

Completed comparison: native Clipboard copied a visibly selected domain instead
of the whole email, then false-finished. The corrected project Clipboard arm
cycled More options→Settings→Back without typing until its step limit. Project
Timer repeated zeros until the no-progress guard stopped it. An invalid earlier
Clipboard arm lost recording after a cold-launch timeout and inferred ADB
server restart; its short clip is preserved but excluded. Single-attempt launch
and live-recorder monitoring fix this transport fault, not those model decisions.

Latest source-backed improvement experiment: same-model M3A before/after
assessment did not solve Timer/Clipboard. Each protocol/semantic failure was
inspected and recorded before its changed check. Concrete steps, source-contract
corrections, full video audit and opt-in status are in
[STEP_ASSESSMENT_EXPERIMENT.md](STEP_ASSESSMENT_EXPERIMENT.md). Original
trajectories and summaries are unchanged; current default assessment is off.

8 October continuation: the original v10 analysis below remains historical.
The hosted AutoGLM failure ledger, pinned GitHub sources and all 174 D1–D4
pages' implementation mapping are in
[COURSE_AND_UPSTREAM_REVIEW.md](COURSE_AND_UPSTREAM_REVIEW.md). The latest
recorded gates are [WARMUP_RESULTS.md](WARMUP_RESULTS.md): Wi-Fi/Camera v20
and Contacts v28 each passed three clean trials; Timer and Clipboard remain
unresolved. Each failed trial stopped for trajectory diagnosis before a changed
bounded regression. No unchanged failing task is currently being retried.
The v29 offline no-progress bound limits wasted cycles, not false completion.

Reviewed on 7 October 2026. Scope: all 15 trials in frozen v10 batch
`easy_batch_20261007T191040_731527Z`, all 78 saved model responses, their actual
requests, parsed/checked actions, execution results and screenshot transitions.
Also compared the earlier official Contacts PASS for the same seed 42.
No new model calls or emulator actions were made for this review. Original
measurements, summaries and videos remain unchanged.

The current implementation is not reliable even on these easy tasks. The
trajectories reveal faults in our observation/recovery/action contract as well
as genuine model mistakes. The raw 1/15 success rate is not an isolated measure
of GELab-Zero's capability because several runs supplied incomplete or
inconsistent observations and stopped before task actions could execute.

## Every trial: first useful failure and final stop

| Task / seed | First evidenced problem | Final outcome / stop |
| --- | --- | --- |
| Wi-Fi 42 | None prevented completion; GUI toggle visibly turns on | PASS, five steps |
| Wi-Fi 43 | Step 1 tree describes a forwarder crash modal while its screenshot shows Home; selected point falls on Messages in the fresh Home tree | FAIL, freshness guard blocks first tap |
| Wi-Fi 44 | Step 1 intended Settings tap actually points to Messages; whole-tree check also treats a time-widget change as a screen change | FAIL, freshness guard blocks first tap |
| Camera 42 | Step 2 supplies Shutter in the tree while screenshot/video show loading; tap produces no changed app controls | FAIL, model declares COMPLETE at step 3 |
| Camera 43 | Same loading/control mismatch and unchanged shutter result | FAIL, COMPLETE at step 3 |
| Camera 44 | Same loading/control mismatch and unchanged shutter result | FAIL, COMPLETE at step 3 |
| Timer 42 | Step 3 leaves a correctly opened Timer screen for Clock; step 4 selects Alarm | FAIL, COMPLETE in an alarm time editor at step 12 |
| Timer 43 | Step 5 presses another `1` instead of the next required digit; later presses more wrong digits and leaves Timer | FAIL, empty target then malformed image coordinate at step 10 |
| Timer 44 | Step 3 opens More options instead of entering timer digits | FAIL, empty target then malformed image coordinate at step 4 |
| Contacts 42 | Steps 4–5 edit name fields even though the exact full name was already correct | FAIL, unchanged Phone target blocked by keyboard-suggestion changes at step 6 |
| Contacts 43 | Step 2 screenshot shows Contacts but the tree contains only System UI; no app target can be selected | FAIL, updated tree causes fallback to stop before an image request |
| Contacts 44 | Same status-bar-only input despite visible Contacts controls | FAIL, updated tree causes fallback to stop before an image request |
| Clipboard 42 | Opens Clipper, whose screen contains instructions rather than an editable text field; model invents a field | FAIL, empty target then malformed image coordinate at step 2 |
| Clipboard 43 | After opening Chrome, step 2 screenshot shows the browser but tree contains only System UI | FAIL, updated tree causes fallback to stop before an image request |
| Clipboard 44 | Opens Clipper, invents an input route; step 2 image tap changes nothing | FAIL, TYPE point is outside any editable field at step 3 |

Terminal summaries contain six environment/execution exceptions, four argument
validation errors and four false completion declarations, plus one PASS. Those
are stop reasons, not mutually exclusive root causes. For example Contacts 42
has a model value error before its final harness exception. There are 26 logged
validation errors across the 78 calls, including corrected errors.

Per-run links are in the batch's [RESULTS.md](../runs/easy_batch_20261007T191040_731527Z/RESULTS.md).
The separate [all-step evidence inventory](../runs/easy_batch_20261007T191040_731527Z/diagnosis/all_steps.json)
contains response/request references, task values and actual observations.

## 1. We treated a status bar as a usable task observation

Confirmed in Contacts seeds 43/44 and Clipboard seed 43, all at step 2.
`tree.json` contains only `com.android.systemui` entries. The screenshots show
Contacts' create button or Chrome's search/address field. None of those controls
is supplied in the model's tree input, and no image is attached to these calls.

The code's `choose_action()` usability test accepts any visible label with
bounds, including clock, battery and network labels. The later target schema
correctly excludes System UI. Consequently it offers only the empty target
string. A grounded CLICK/TYPE cannot succeed from that input. Retrying the same
input is not a recovery.

The correction budget is spent on empty-target errors. The fallback then gets
a fresh state, finds that its tree has changed, and raises an exception before
requesting a screenshot action. At that point no selected task action has been
executed; the changed observation should be a chance to restart from fresh
evidence within a small limit. It should not automatically end the trial.

Source: [usability and fallback checks](../gelab_agent.py:423), and
[target filtering](../gelab_agent.py:92).
Visual evidence: [Contacts screens](../runs/easy_batch_20261007T191040_731527Z/diagnosis/contacts.png)
and [Clipboard screens](../runs/easy_batch_20261007T191040_731527Z/diagnosis/clipboard.png).

## 2. Our freshness guard compares the entire scene

Contacts 42 step 6's Phone field has identical label, bounds and enabled state
before and after inference. Only Gboard clipboard suggestions change. The
whole-tree signature includes those suggestions and blocks the phone entry.
The number is therefore never entered; Save is never executed in that run.

Wi-Fi 44 step 1 has an unchanged Home layout. Its meaningful tree difference is
the time widget changing from `50:51` to `50:52`. The guard blocks the tap for
that change too. However the proposed tap itself is wrong: point `154,654`
becomes physical `(166,1570)`, inside Messages. Settings has bounds
`x=813..1023, y=1479..1751`. Fixing the guard alone would not make that action
correct.

Wi-Fi 43 is a separate case: the before tree contains an AccessibilityForwarder
crash modal, while the before screenshot and fresh screenshot show Home. We
cannot prove from this trace exactly when that modal appeared/disappeared. The
observation pair is inconsistent, and the tap also points into Messages on
Home. Earlier wording attributing **both** Wi-Fi failures to crash dialogs is
superseded by this per-seed analysis.

Source: [whole-tree signature](../gelab_agent.py:196) and
[execution freshness check](../gelab_agent.py:505).
Evidence: [Wi-Fi screens](../runs/easy_batch_20261007T191040_731527Z/diagnosis/wifi.png),
original `tree.json` and `execution_observation.json` for the named steps.

## 3. Camera never showed a ready camera in the saved evidence

All three Camera trials follow AWAKE Camera → CLICK Shutter → COMPLETE.
The accessibility controls remain unchanged after the shutter tap. The images
show a camera loading screen rather than a visible preview/shutter layout.
The earlier extracted video frame also shows loading, so this is not solely an
image export problem. The exact camera startup/rendering cause is still unknown.

The model only receives the tree in these runs. It can select the advertised
Shutter target, but cannot see the loading screenshot. It then asserts that a
photo exists without observed evidence. One response even says the test need
only verify actions rather than the photo's existence. That claim is wrong;
the official verifier returns zero in all three runs.

Our feedback says only `dispatch returned`. It does not mean the app performed
the intended action. The current screenshot fallback handles target/format
errors and repeated actions, but does not catch this first no-effect action
followed by COMPLETE. A visible control in a tree is not sufficient evidence
of app readiness or task success.

Evidence: [Camera screens](../runs/easy_batch_20261007T191040_731527Z/diagnosis/camera.png)
and each run's step 2 result / step 3 raw response.

## 4. Timer has genuine task-planning and value mistakes

Seed 42 requests `20h 07m 01s`, unstarted. Step 2 opens Timer correctly; the
screenshot and tree agree. At step 3 the model deliberately selects Clock,
then Alarm. It eventually declares completion with the alarm editor open at
`20:10`. This failure is not explained by an absent task goal or broken tap
conversion. It chose the wrong route despite a useful observation.

The compact tree also drops `is_selected`: the raw Timer navigation element
has `is_selected: true`, but that fact is omitted from the model's tree text.
Keeping active-tab state would improve the input, though it does not prove the
model would choose correctly.

Seed 43 requests `01h 18m 44s`. Initial `1,1` keypad taps can be the beginning
of `11844`; step 5 taps another `1` rather than `8`. Its reply's `value` says
`9` while its executable `target` says `1`. The code executes target `1`, as
documented. Later values and predicted displays diverge further. Seed 44 opens
the menu instead of entering `13h 33m 34s`. The eventual coordinate errors are
secondary to those earlier navigation/value mistakes.

The CLICK reply has both a free-form `value` and an actual target. They can
contradict each other. The interpreter must keep one authoritative target;
we should simplify the reply contract rather than infer intent from whichever
argument sounds plausible.

Evidence: [Timer seed 42 screens](../runs/easy_batch_20261007T191040_731527Z/diagnosis/timer42.png),
seed 43 steps 3–9, seed 44 steps 2–4. No recorded executed Start action appears
in the completed batch audit; none of these trials set the correct timer.

## 5. Contact values were present, but our action policy added harmful pressure

Seed 42 step 3 enters `Camila da Silva` into First name correctly. At step 4 the
model tries CLICK Last name. Our `direct_type_only` rule rejects an ordinary
field-focus tap and says to use TYPE with the field and exact value instead.
The corrected response types `Camila` into Last name. Step 5's corrected TYPE
replaces First name with `da Silva` while its explanation claims the correct
full name will remain. The screenshots confirm the incorrect edits.

The exact name/number, recent actual field values and conditional contact guide
are all in the saved requests. The guide explicitly says to leave Last name
blank and retain already-correct values. This is not a missing memory or missing
skill-file failure. The model ignores relevant instructions. Our focus-tap ban
also turns ordinary focus requests into text-replacement corrections, making
the interaction more brittle.

Compare the earlier genuine [Contacts seed 42 PASS](../runs/trial_ContactsAddContact_20261007T171621_506135Z/trajectory.txt):
tap First name → TYPE full name → tap Phone → TYPE number → Save → COMPLETE.
That version allowed the normal focus taps. It used eight calls total; the
current failed seed 42 uses ten calls and stops before saving. Other settings
also changed, so this is diagnostic evidence, not a controlled proof that the
focus-tap ban alone caused failure.

Source: [focus-tap rejection](../gelab_agent.py:398).
Evidence: Contacts seed 42 steps 3–6, including `request_1.json` correction
messages, raw responses and after-field values.

## 6. Clipper is not the editable GUI the model imagines

Seeds 42/44 choose Clipper. Its screen contains service status and ADB broadcast
instructions, with no editable input. The model invents a text field, clipboard
button or input dialog. In seed 44 an image tap produces no change, then TYPE
points into noneditable instruction text. The validator correctly refuses it.
No COPY operation executes in these three trials.

Our available-app list exposes both Clipper and Chrome without explaining their
roles. Clipper supports official clipboard initialization/verification; a GUI
agent must use an actual editable app and select/copy the exact task text. The
GUI route has not been demonstrated. It needs a small task procedure or clearer
tool description, and a tested typing/selection flow. Do not execute Clipper's
ADB instructions as model-generated commands or count direct clipboard writes
as GUI-agent success.

Some image replies contain invalid coordinate strings, such as `190 352` or
`700,947}, `. These are valid JSON string values but invalid coordinates. The
schema allows an arbitrary point string, so JSON validity alone cannot prevent
them. Argument validation worked; removing it would execute guesses.

## What this evidence does and does not establish

- No saved response has `done_reason: length`; maximum reported output is 85
  tokens under the 256-token limit. Maximum reported prompt count is 2,424 under
  the configured 4,096 context. There is no recorded truncation explaining these
  mistakes. These counts are not a full model architecture/memory audit.
- Exact task values are in the failed Timer and Contacts requests. Adding more
  persistent memory does not fix an absent app tree or an overbroad stop check.
- Local inference latency makes observations older, but GPU speed is not an
  evidenced explanation for selecting Alarm, rewriting a correct name or
  inventing Clipper controls. Speed tuning remains paused.
- The successful Wi-Fi run and correctly entered Contact name prove parts of
  capture/model/grounding/dispatch work. They do not establish reliability.
- The trained model's competence under a faithful native protocol has not been
  isolated by these trials. This custom tree/JSON interface has genuine model
  semantic errors as well as integration faults. No model switch is justified
  solely by this mixed batch.

## Small repair order, with checks before another evaluation batch

These are proposals, not runtime changes made during this read-only review.

1. **Observation gate and recovery:** count actionable app controls using the
   same filter as grounding. When they are absent, capture a fresh observation
   once or use a fresh screenshot; do not spend model corrections on an empty
   target list. Log each capture with its own observation ID.
2. **Target freshness:** before a delayed tap/type, check the chosen control's
   identity, bounds and editable state against the fresh screen. Keep checking
   for real app/modal changes. Unrelated time and keyboard suggestions must not
   abort an unchanged target. Never replay uncertain executed actions.
3. **Readiness and results:** isolate the forwarder/XML freshness issue and
   Camera loading in small infrastructure probes. The official XML dumper uses
   a reused file and does not check the dump request's response before reading;
   this is a source-backed stale-file risk, not a proven cause of a specific
   run. Check dump success/freshness. Log no-effect results, and let screenshots
   help before accepting unsupported completion claims.
4. **Simpler model contract:** test allowing ordinary field-focus CLICK again
   with the same seed/model/settings, as one variable. Retain exact values and
   checked TYPE. Preserve active-tab state. Add only a concise timer-keypad or
   editable-app clipboard procedure if a useful-observation trial still needs
   it. Test each change separately; do not bundle them as a claimed causal gain.
5. Run one official Contacts trial and inspect its trace before repeating three
   cases. Then advance through one task at a time. Retain all outcomes. Do not
   run another fifteen-case batch before the observation probes pass.

The correction/recovery changes fit the existing one-agent step loop. They do
not require a new framework, agents, vector memory, fine-tuning or cloud model.
