# Team final evaluation: one agent, seven tasks, three runs each (v65)

Course requirement (D1 pp.6-8, 49-50): one agent (a class with a single
`step()` method), at least one task from each difficulty row, three runs per
task, a screen recording of every evaluation run, one log row per run, and
failure classes from the fixed list. How this agent was assembled from the
three contributions: [TEAM_AGENT.md](TEAM_AGENT.md).

## Result

**18 of 21 runs passed the official Android World verifier**, on one frozen
version (tag `team-agent-final-v65`, identical source hashes in both batches).

| Course row | Task | Official PASS | Model finished | Steps (PASS runs) |
| --- | --- | --- | --- | --- |
| Warm-up (easy) | SystemWifiTurnOn | **3/3** | 3/3 | 5, 5, 5 |
| Warm-up (easy) | ContactsAddContact | **2/3** | 2/3 | 12, 11 |
| Real work (medium) | SimpleSmsSend | **3/3** | 3/3 | 9, 7, 7 |
| Real work (medium) | FilesMoveFile | **2/3** | 3/3 (one false completion) | 17, 13 |
| Real work (medium) | SimpleCalendarAddOneEvent | **3/3** | 3/3 | 20, 21, 16 |
| Multi-app (hard) | MarkorCreateNoteAndSms | **3/3** | 3/3 | 18, 18, 15 |
| Multi-app (hard) | OsmAndTrack (the slide's instance) | **2/3** | 2/3 | 22, 23 |

Three runs per task are a small sample: a 3/3 does not mean the task always
passes, and a 2/3 does not mean one in three fails.

## Setup

| Item | Value |
| --- | --- |
| Agent | `AutoGLMAgent` in [autoglm_agent.py](../autoglm_agent.py): `step()` reads the screen and the task, asks the model for one action, checks it, executes it and reports whether the model finished |
| Model | AutoGLM-Phone-9B-Multilingual, hosted by Z.ai (`autoglm-phone-multilingual`), temperature 0 |
| Actions and grounding | AutoGLM's native actions (`Tap`, `Type`, `Swipe`, `Launch`, `Back`, `Wait`, `finish`) with screen coordinates on a 0-1000 grid |
| Observation | Screenshot for every task; see the Observation column for the extra GUI labels some tasks receive |
| Skills | MarkorCreateNoteAndSms: text Skill with its procedure repeated each step. OsmAndTrack: Skill whose procedure runs as code (next step and tap centre computed from the GUI tree) plus screen checks |
| Success | Official Android World verifier PASS; the model's `finish` is recorded separately and never counts as success |
| Task seeds | 42, 43, 44 for the six tasks the slide gives as templates; 31, 314, 366 for OsmAndTrack, the three seeds that produce the slide's own instance "Ruggell, Liechtenstein and Bendern, Liechtenstein" |
| Step budgets | Wi-Fi 12, Contacts 16, SMS 20, Files 25, Calendar 35, Markor 40, OsmAnd 90 |
| Batches | [`eval_batch_20261008T215129_132839Z`](evidence/team/eval_batch_20261008T215129_132839Z/RESULTS.md) (six tasks), [`eval_batch_20261008T223002_941777Z`](evidence/team/eval_batch_20261008T223002_941777Z/RESULTS.md) (OsmAnd) |
| Environment | Android World `2dfc5ca`, Pixel 6 API 33 emulator (headless, host GPU), Windows |

## Run log (one row per run, D1 p.49)

Model in every row: `autoglm-phone-multilingual`. Grounding: coordinates;
where the step text lists GUI labels it gives their observed tap centres.
Recording: `runs/<run ID>/video_*.mp4`; all 38 clips of these 21 runs and of the 7 practice runs are in
`team_agent_final_recordings_v65.zip` (151 MB) next to the repository.

| Task | Run | Seed | Observation | Steps / budget | Verifier | Failure class | Clips | Note | Run ID |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SystemWifiTurnOn | 1 of 3 | 42 | screenshot + UIAutomator labels (Settings) | 5 / 12 | **PASS** | — | 1 | | `trial_SystemWifiTurnOn_20261008T215130_600754Z` |
| SystemWifiTurnOn | 2 of 3 | 43 | screenshot + UIAutomator labels (Settings) | 5 / 12 | **PASS** | — | 1 | | `trial_SystemWifiTurnOn_20261008T215246_616671Z` |
| SystemWifiTurnOn | 3 of 3 | 44 | screenshot + UIAutomator labels (Settings) | 5 / 12 | **PASS** | — | 1 | | `trial_SystemWifiTurnOn_20261008T215358_472883Z` |
| ContactsAddContact | 1 of 3 | 42 | screenshot | 12 / 16 | **PASS** | — | 1 | | `trial_ContactsAddContact_20261008T215508_628423Z` |
| ContactsAddContact | 2 of 3 | 43 | screenshot | 11 / 16 | **FAIL** | other: scrolled past the field | 1 | Name typed; two swipes moved the form past the Phone field to its end, four more in the same direction changed only the blinking cursor; no-progress stop | `trial_ContactsAddContact_20261008T215709_244163Z` |
| ContactsAddContact | 3 of 3 | 44 | screenshot | 11 / 16 | **PASS** | — | 1 | | `trial_ContactsAddContact_20261008T215831_022667Z` |
| SimpleSmsSend | 1 of 3 | 42 | screenshot | 9 / 20 | **PASS** | — | 1 | | `trial_SimpleSmsSend_20261008T215957_234873Z` |
| SimpleSmsSend | 2 of 3 | 43 | screenshot | 7 / 20 | **PASS** | — | 1 | | `trial_SimpleSmsSend_20261008T220116_423331Z` |
| SimpleSmsSend | 3 of 3 | 44 | screenshot | 7 / 20 | **PASS** | — | 1 | | `trial_SimpleSmsSend_20261008T220223_867500Z` |
| FilesMoveFile | 1 of 3 | 42 | screenshot | 17 / 25 | **PASS** | — | 1 | | `trial_FilesMoveFile_20261008T220333_997891Z` |
| FilesMoveFile | 2 of 3 | 43 | screenshot | 13 / 25 | **FAIL** | false_done | 1 | Moved the truncated "documentary_20..." distractor instead of documentary.mp4, then finished; analysed below | `trial_FilesMoveFile_20261008T220533_834164Z` |
| FilesMoveFile | 3 of 3 | 44 | screenshot | 13 / 25 | **PASS** | — | 1 | One malformed reply corrected | `trial_FilesMoveFile_20261008T220713_812951Z` |
| SimpleCalendarAddOneEvent | 1 of 3 | 42 | screenshot | 20 / 35 | **PASS** | — | 1 | One malformed reply corrected | `trial_SimpleCalendarAddOneEvent_20261008T220904_772591Z` |
| SimpleCalendarAddOneEvent | 2 of 3 | 43 | screenshot | 21 / 35 | **PASS** | — | 1 | One unsupported action corrected | `trial_SimpleCalendarAddOneEvent_20261008T221147_529159Z` |
| SimpleCalendarAddOneEvent | 3 of 3 | 44 | screenshot | 16 / 35 | **PASS** | — | 1 | | `trial_SimpleCalendarAddOneEvent_20261008T221423_161758Z` |
| MarkorCreateNoteAndSms | 1 of 3 | 42 | screenshot + Skill | 18 / 40 | **PASS** | — | 2 | | `trial_MarkorCreateNoteAndSms_20261008T221647_424207Z` |
| MarkorCreateNoteAndSms | 2 of 3 | 43 | screenshot + Skill | 18 / 40 | **PASS** | — | 2 | One truncated reply retried | `trial_MarkorCreateNoteAndSms_20261008T222123_918435Z` |
| MarkorCreateNoteAndSms | 3 of 3 | 44 | screenshot + Skill | 15 / 40 | **PASS** | — | 2 | | `trial_MarkorCreateNoteAndSms_20261008T222633_440045Z` |
| OsmAndTrack | 1 of 3 | 31 | screenshot + accessibility tree + coded Skill | 22 / 90 | **PASS** | — | 4 | OsmAnd's map, deleted by the FilesMoveFile initializations, was restored by the official setup before the run; Favorite Add and one unfocused Type refused | `trial_OsmAndTrack_20261008T223004_312422Z` |
| OsmAndTrack | 2 of 3 | 314 | screenshot + accessibility tree + coded Skill | 23 / 90 | **PASS** | — | 3 | One unfocused Type refused | `trial_OsmAndTrack_20261008T224202_113624Z` |
| OsmAndTrack | 3 of 3 | 366 | screenshot + accessibility tree + coded Skill | 16 / 90 | **FAIL** | grounding | 2 | First waypoint in the route; then tapped Clear at [941, 57] three times while the code stated its tap centre [941, 83]; the taps missed; no-progress stop | `trial_OsmAndTrack_20261008T225108_345362Z` |

Every run has its trajectory (`trajectory.txt`, `trajectory.jsonl`), task,
configuration and summary; exported copies are in [evidence/team/](evidence/team/).

## The three failures

Failure classes follow D1 p.50; a failure that fits none of the five is
labelled "other" with a description. Fix layers follow D4 p.27 and D5
pp.41-42. The version is frozen, so none of these was rerun or fixed for the
results above.

### FilesMoveFile, seed 43: `false_done` on a look-alike file (deep dive)

Goal: "Move the file documentary.mp4 from Alarms ... to the Movies ...".
Android World's initialization puts the file among distractors whose names
resemble it (here "documentary_2023...", "backup_docume...", "copy_morning_a...").

| Steps | What the model saw and did | Assessment |
| --- | --- | --- |
| 1-4 | Opened Files, the storage root, then Alarms | Correct |
| 5 | Files shows a grid; names are cut off ("documentary_20...", "backup_docume..."). The model long-pressed "documentary_20...", calling it "documentary_2023_03_14.mp4, which matches the required file documentary.mp4 (assuming it is named differently here)" | Chose the wrong object; the name it reports is partly invented |
| 6-11 | More options > Move to... > storage root > Movies > MOVE | Correct procedure on the wrong file |
| 12-13 | Waited for "Moving 1 item", said "The original documentary.mp4 is no longer present in the Alarms folder" and finished | `false_done`: the real file was never checked |

Screenshot of step 5: [screen.png](evidence/team/runs/trial_FilesMoveFile_20261008T220533_834164Z/step_005/observation_0/screen.png).

- **Class:** `false_done` (status complete, verifier FAIL); the root cause is
  choosing a look-alike object from truncated names.
- **Fix layers:** instruction ("switch to list view or search the exact name;
  never assume a renamed file") and program (before Move, check that the
  selected item's full name equals the requested one; D1 p.50's "a check step
  before status").

### ContactsAddContact, seed 43: scrolled past the field (other)

After typing "Hugo" and "Ali", the model swiped up to reach Phone. Two swipes
moved the form to its end ("More fields"), leaving Phone cut off at the top;
the model repeated the same swipe four more times, saying the field was "still
not visible", and the no-progress rule stopped the run. Screenshot:
[step 9](evidence/team/runs/trial_ContactsAddContact_20261008T215709_244163Z/step_009/observation_0/screen.png).
Our own feedback did not help: those four swipes changed only the blinking text
cursor (image difference about 0.00001), which our effect check counts as a
visible change, so the model was told each swipe had an effect. Class: other
(navigation; none of the five classes fits). Fix layer: program (ignore a
cursor-sized change when judging a swipe, and say "the list did not move;
scroll the other way").

### OsmAndTrack, seed 366: `grounding`

The route had Ruggell as point 1 (step 11). In the route search the code stated
"Tap Clear at tap center [941, 83]"; the model tapped [941, 57] (it quoted a
box that was not in the step text), just outside the button, three times, and the no-progress rule
stopped the run. The forwarder crash dialog had appeared at step 9 and was
closed. Class: `grounding` (the tap lands on nothing). Fix layer: program (snap
a tap that falls just outside a labelled control to that control, or refuse it
with the stated centre).

## Follow-up after the freeze: Markor shares the note (v66)

In the runs above the Markor Skill sent the note's text by typing it again in Simple SMS Messenger. The verifier accepts that, but the task asks to share the note's content. After the freeze we changed only that Skill to Markor's own Share > Plain Text and evaluated MarkorCreateNoteAndSms again with seeds 42, 43 and 44 (tag `markor-share-v66`): 2/3 passed, all three runs shared the note instead of typing the text again, and seed 42 failed on a grounding error at the SMS send button. The table above is unchanged. Details: [MARKOR_SHARE_V66.md](MARKOR_SHARE_V66.md).

## How this relates to the earlier results

| Result | Version | Status |
| --- | --- | --- |
| Contacts 3/3, Calendar 3/3, OsmAnd 0/3 (seeds 42-44) | v42 | Earlier course evaluation of Jia's branch ([FINAL_EVALUATION.md](FINAL_EVALUATION.md)) |
| OsmAnd 2/3 with the Skill vs 0/3 without (slide instance) | v61 | The documented improvement ([IMPROVEMENT_OSMAND.md](IMPROVEMENT_OSMAND.md)) |
| Wi-Fi, SMS, Files, Markor practice and teammates' runs | various | Development history ([TEAM_AGENT.md](TEAM_AGENT.md)) |
| **All seven tasks, 18/21** | **v65** | **This evaluation: one agent, one frozen version** |

## Reproduce

```powershell
git checkout team-agent-final-v65
.\.venv\Scripts\python.exe -X utf8 evaluate_tasks.py --tasks SystemWifiTurnOn ContactsAddContact SimpleSmsSend FilesMoveFile SimpleCalendarAddOneEvent MarkorCreateNoteAndSms --seeds 42 43 44 --run-all-seeds
.\.venv\Scripts\python.exe -X utf8 evaluate_tasks.py --tasks OsmAndTrack --seeds 31 314 366 --run-all-seeds
```
