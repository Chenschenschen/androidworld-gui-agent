# FilesMoveFile: three linked moves

User requested cooking-recipe.md from project_easy to project_medium, then back,
then forward again, continuing only after clean success. Both folders were absent
on the emulator during read-only inspection. Standard FilesMoveFile initialization
was proposed, but automatic approval review rejected its whole-storage deletion
before any trial process started. The safer first trial uses official create_file
and mkdir utilities only for the named missing source file and destination folder.
It does not clear shared storage, create distractors or overwrite existing files.
All trials use official TaskEval base initialization for both task/evaluator,
preserving the actual file rather than clearing/recreating it. Source existence
and destination absence are checked before the linked initializer. This is a
user-requested linked sequence with scoped preparation, not three independently
reset standard benchmark samples. Host project files and other emulator files
are unaffected. No whole-storage clear utility runs in this file-task branch.

All moves must be model-selected GUI actions; the unchanged official MoveFile
verifier checks source absence/destination presence. No direct filesystem move,
verifier feedback or forced completion. Existing screenshot/XML grounding and
native loop remain; file task has a20-step bound for file navigation/verification.
Pinned sources: single/files.py, common_validators/file_validators.py,
task_eval.py, setup_device/apps.py and user_data_generation.py.

Runtime/settings freeze through the sequence. Stop and diagnose before a changed
retry if a trial fails. Exact inputs are editable JSON, not GUI action recipes.

```powershell
.\.venv\Scripts\python.exe -X utf8 run_task.py --task FilesMoveFile --seed 42 --config general_config.json --params task_inputs/files_easy_to_medium.json
.\.venv\Scripts\python.exe -X utf8 run_task.py --task FilesMoveFile --seed 43 --config general_config.json --params task_inputs/files_medium_to_easy.json --continue-state
.\.venv\Scripts\python.exe -X utf8 run_task.py --task FilesMoveFile --seed 44 --config general_config.json --params task_inputs/files_easy_to_medium.json --continue-state
```

## First attempt: diagnose before changed retry

trial_FilesMoveFile_20261008T140525_204594Z, v50: valid officialFAIL0.0,
12 GUI actions/16 calls, no finish; two recorded clips. Model chose Move to,
but step10 tapped the right-hand Recordings card while naming project_medium,
which the saved screenshot shows on the left. Step11 acknowledged Recordings,
returned to storage, then proposed the same wrong coordinates at step13.
Text labels were supplied, but non-clickable descendant folder titles lacked
observed centres; the clickable CardView parents were unlabeled. This is a
model grounding error plus insufficient supplied label grounding.

Step13 stopped on target changed twice. Both freshness screenshots were exactly
unchanged (global/target differences0.0). XML availability alternated, so the
selected node flipped between None and the same unlabeled CardView. This was
an own-code false guard, not two real screen changes.

Before retry, v51 gives observed text labels their actual bbox centres, including
folder titles inside clickable cards. It also allows existing visual fallback
when XML target availability changes but both scene and target differences are
at most0.001. Real changed XML identities remain checked; no uncertain execution
is replayed. No file-specific coordinate prescription or action recipe.
The file remains in project_easy; retry with --continue-state preserves it.

v51 retry trial_FilesMoveFile_20261008T141128_839535Z: valid officialFAIL,
three actions/four calls, no finish. At Downloads, the model correctly named
Show roots but emitted [499,224] three times, rather than supplied [68,79]. The
no-progress guard prevented the third repeated tap. Giving every static text a
tap centre made headings look actionable and did not establish correct grounding.

Before the changed v52 retry, centres again belong only to clickable/editable
controls. Clickable unnamed containers receive their real descendant text via
observed_label metadata (the same observed-label approach used for switches).
Thus a folder CardView carries project_medium and its centre; static headings
do not receive tap centres. Control notes explicitly mark clickable controls;
freshness compares derived observed-label metadata as part of target identity.
Identical-image XML fallback remains. No prescribed task actions or replay.

## v52 forward success, then reverse diagnosis

trial_FilesMoveFile_20261008T141450_696380Z: first direction cleanPASS,
initial0/final1, model finish at12,11 GUI actions/14 calls; valid recording and
no manual intervention. Named archive FILES_01_easy_to_medium_PASS_v52.
Afterward the file SHA256 was
82287c26534ac3697a68f703d49d49e00594c123ea5801d6ad164986759d4416.

Reverse trial_FilesMoveFile_20261008T141900_675904Z: valid officialFAIL,
nine actions/eleven calls, no finish; stopped before step10 destination tap.
Identical screenshot pixels, but raw captures028/030 associate card bounds
[551,1297][1016,1424] with child Android at [675,587][821,644], far outside the
card. Capture029 correctly associates project_easy at [675,1332][911,1389].
Our label derivation trusted a geometrically inconsistent UIAutomator hierarchy;
the resulting metadata flip caused the freshness stop. File remains in medium.

Before the changed reverse retry, v53 rejects clickable-container XML whose
text bounds lie outside that container. Existing supplemental capture handles
this as an observation error and uses a fresh screenshot. Do not relabel with
out-of-card text or weaken comparisons between two valid labeled controls.
Offline regression reproduces the raw stale-title geometry and confirms
rejection. Preserve source file, GUI-only moves and original failed evidence.

## Continuation: re-establish a recorded linked sequence

The v53 reverse setup at trial_FilesMoveFile_20261008T153255_926287Z
stopped before model calls: the recipe was already in project_easy, with its
original SHA256. This transition is absent from the requested recipe trajectory
and has unknown provenance; it is not counted as agent success. A question about
emulator interaction remains unanswered. Base app snapshots restore private app
data, not these external-storage folders. Original summaries remain unchanged.

Additional folders found on continuation include a separate valid v52 PASS at
trial_FilesMoveFile_20261008T143528_860048Z for sci_fi_book.mp3 from Recordings to
Audiobooks. That different task instance does not count toward the requested
recipe sequence. The 144918/145147/150528 setup-only attempts are NOT_RUN,
not task failures or successes; all are preserved.

On the user's next continuation, read-only checks again found the original
recipe only in project_easy. Start a new, frozen v53 linked sequence there using
--continue-state for every direction: forward42, reverse43, forward44. No file
recreation, relocation or deletion prepares this sequence. Stop on failure,
diagnose the saved trajectory before changing/retrying, and retain the earlier
forward success separately. Only recorded official PASS plus model completion
and valid videos counts. This is scoped linked evaluation, not three independent
standard benchmark resets.

The user subsequently confirmed: "Yes, I moved it back." Record this as manual
preparation before the new sequence, not a successful recorded reverse move.
The original failed reverse summary is preserved; no manual interaction during
that recorded run was reported. The new v53 forward starts from the confirmed
manually restored source and must perform all three moves through the agent.

### Fresh v53 sequence, first result

trial_FilesMoveFile_20261008T153825_684536Z: forward seed42 clean PASS,
initial0/final1, model finish at step20,19 GUI actions/20 calls,296.594 seconds.
The move occurred at step11. Source was visibly empty at step12 and destination
contained the recipe at step15, but the model checked the folders again before
finally finishing. This is a successful bounded run, with unnecessary repeated
verification; it does not establish efficient stopping. No runtime error or
recording error. Read-only checks after completion found only the medium copy
with the original SHA256. Named archive FILES_V53_01_easy_to_medium_PASS:
all348 copied files match; clips fully decoded at332/238 frames.
Reverse starts with the same frozen v53 sources/settings, preserving the file.

trial_FilesMoveFile_20261008T154346_710337Z: reverse seed43 clean PASS,
initial0/final1, model finish at step12,11 GUI actions/13 calls,191 seconds.
One unexecuted format correction produced the standalone finish; it was a
model decision, not Python-inferred completion. No runtime/recording errors.
Post-run read-only checks found only the easy copy with the original SHA256.
Named archive FILES_V53_02_medium_to_easy_PASS: all221 copied files match;
clips fully decoded at298/5 frames. Final forward starts unchanged at seed44.

### Final v53 forward failure: diagnose before changed retry

trial_FilesMoveFile_20261008T154721_039629Z: valid FAIL0,20 actions/20 calls,
no finish, stopped on the unchanged20-step budget (303.765 seconds; two videos).
At step4, read-only UIAutomator dump exited137. Screenshot shows project_easy
on the right and Podcasts on the left, but model named project_easy and tapped
the left point[275,618]. Steps5-13 repeated this folder/breadcrumb cycle.
Some later captures rejected stale out-of-parent XML titles; screenshot-only
fallback supplied no checked centres. At14 the model finally selected the right
folder, selected recipe15, Move to17, destination20; MOVE was never dispatched.
Official FAIL is genuine, not a verifier/recording error. File remains in easy.
The frozen v53 sequence is2/3, not3/3. Do not hide this failure.

Proposed v54 changes one observation mechanism: allow at most one further
read-only XML capture when the first errors or changes during capture. Capture
IDs/logs stay unique; both bad reads still yield fresh screenshot fallback.
No GUI action retries, fixed coordinates, verifier feedback or step-budget
increase. Check the concrete failed-read/successful-read and two-failed-read
cases offline before a changed final forward retry preserving the same recipe.

Implemented v54; all42 offline checks pass before the changed live retry. New
test verifies exactly two read calls, distinct captures/logs, valid labels after
one failure, and screenshot fallback after two failures. Initial new test used
Windows sandbox temp and failed on permissions; corrected its fixture to project
.tools/tmp and actual State dataclass before running inference. No runtime bug
or model trial was involved in that fixture failure. Sampling, native prompt,
completion condition, task inputs and20-step budget remain unchanged.

### v54 retry result and final state

trial_FilesMoveFile_20261008T155433_701814Z: final forward seed44 clean PASS,
initial0/final1, model finish at19,18 GUI actions/19 calls,305.64 seconds.
Step4's first capture rejected inconsistent geometry; its one additional read
returned valid labels, and the model selected the right project_easy card.
GUI MOVE executed at11. Later verification still involved unnecessary navigation;
at19 the model saw the destination recipe and issued standalone finish. No
runtime/recording errors. Two exact duplicate native calls collapsed without
replaying actions. No verifier information entered the model context.

Final read-only check: source absent, recipe present only in project_medium,
21 bytes and the original SHA256. All three requested directions now have clean
successful recordings after one failed third attempt and its repair:

| Direction | Seed/version | Model finish | Official result | Seconds |
| --- | --- | --- | --- | --- |
| easy -> medium |42/v53|20|PASS|296.594|
| medium -> easy |43/v53|12|PASS|191.000|
| easy -> medium, repaired retry |44/v54|19|PASS|305.640|

This fresh linked stage had three successes in four attempts (75%): frozen v53
was2/3, v54 retry1/1. It is not a frozen3/3 gate or independent benchmark sample.
User manual preparation preceded the sequence; no interaction during these
recordings was reported. The improvement prevented the recorded source-folder
grounding failure in one retry, but does not establish general reliability or
faster completion. Earlier failed trajectories and different-version successes
remain preserved. Named archive FILES_V54_03_easy_to_medium_PASS has348 identical
files and fully decoded clips at348/226 frames. The local audit parsed1208 JSON
artifacts across13 preserved Files attempts and fully decoded16 videos; see
evidence/files_move_audit.json.42 offline checks passed before the live retry.

## User self-run HTTP400,8 October

trial_FilesMoveFile_20261008T170139_366588Z stopped on its first model call,
zero GUI actions. Official initial0/final0, valid recording; this is an API
failure, not evidence of model grounding failure. Saved action_0_api_error.json
contains HTTP400/provider1210, generic invalid-parameter message. Console hid
the provider detail behind the standard traceback; preserve original artifacts.
Request metadata and system prompt exactly match the earlier successful v54
step1. Endpoint/model remain the upstream prescribed values, PNG is valid
576x1280. No specific invalid field is identified by the response.

After inspecting the error, an API-only diagnostic reconstructed that exact
saved request and image using the same credentials. It returned HTTP200,
model autoglm-phone-multilingual, finish_reason stop in2.015 seconds:
runs/api400_diagnostic_20261008T170547_780149Z. No returned action was executed;
this is request acceptance, not another task PASS. A temporary service rejection
is the supported inference; the exact backend cause remains unknown. Do not
change sampling/model/prompts or invent a parameter repair without evidence.
Current read-only check found recipe only in easy, ready for the user's forward
run. v56 adds console/readable-trajectory provider error details with key
redaction, no automatic API or GUI replay. Original full video remains valid.
