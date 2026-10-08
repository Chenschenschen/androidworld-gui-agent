# Final evaluation: easy, medium and hard task, three runs each

This is the course evaluation required by D1 pp.6-7 (one task from each
difficulty row, three runs per task, every run screen-recorded) and Syllabus
p.1 (evaluation results, trajectory logs, failure analysis). All nine runs use
**one frozen version**; earlier task-specific results on other versions are
not mixed in.

## Setup

| Item | Value |
| --- | --- |
| Agent version | `autoglm_api_v42_full_resolution_effect` (commit `1752d65`), identical source hashes for every run (checked by `evaluate_tasks.py` before each trial) |
| Model | `autoglm-phone-multilingual` (AutoGLM-Phone-9B-Multilingual), hosted by Z.ai; temperature 0, top_p 0.85, max_tokens 3000 |
| Observation | Latest screenshot (resized to at most 1280 px) plus checked GUI notes; native AutoGLM pseudo-call actions validated in Python |
| Grounding | Model coordinates (0-1000 normalised), converted and checked by the adapter |
| Budgets | Contacts 16 steps / 900 s; Calendar 35 / 1200 s; OsmAnd 90 / 2700 s. Each request keeps the goal turn plus the latest 19 turns |
| Skill | `instructions/skills/osmand_track.md` plus a per-step search-term reminder, OsmAndTrack only (see [IMPROVEMENT_OSMAND.md](IMPROVEMENT_OSMAND.md)) |
| Success | Official Android World verifier PASS. The model's own `finish` is recorded separately and never counts as success |
| Environment | Android World at `2dfc5ca`, Python 3.11, Pixel 6 API 33 Google APIs image, headless emulator `-no-snapshot -grpc 8554 -camera-back emulated -camera-front emulated -gpu host -no-window` (why: [SETUP.md](SETUP.md) troubleshooting), Windows kept awake during the batch |
| Task seeds | 42, 43, 44 (seed fixes each task instance; see `task.json` in each run) |

The evaluated code is tagged `final-eval-v42` (`git checkout final-eval-v42`). Later work on
OsmAndTrack only (v43-v62) is reported separately: practice runs in
[MEDIUM_HARD_TRIALS.md](MEDIUM_HARD_TRIALS.md) and an additional frozen evaluation of v61 on the
course slide's instance (2/3 with the Skill, 0/3 without) in
[IMPROVEMENT_OSMAND.md](IMPROVEMENT_OSMAND.md#additional-experiment-v61-on-the-slide-instance).

Command (one batch, all nine runs, no stop after a failure):

```powershell
.\.venv\Scripts\python.exe -X utf8 evaluate_tasks.py --tasks ContactsAddContact SimpleCalendarAddOneEvent OsmAndTrack --seeds 42 43 44 --run-all-seeds
```

## Results

Batch [`eval_batch_20261008T133403_527980Z`](evidence/final/eval_batch_20261008T133403_527980Z/RESULTS.md),
8 October 2026, 13:34-13:58 UTC. All nine runs: valid initialization, valid
recording, no recorder notes, no runtime or verifier errors.

| Task (difficulty) | Official PASS | Model finished | Mean steps | Mean duration |
| --- | --- | --- | --- | --- |
| ContactsAddContact (easy, 5 reference steps) | **3/3** | 3/3 | 12.0 / 16 | 96.7 s |
| SimpleCalendarAddOneEvent (medium, 17) | **3/3** | 3/3 | 19.3 / 35 | 195.5 s |
| OsmAndTrack (hard, 60) | **0/3** | 0/3 | 17.7 / 90 | 174.7 s |
| **All** | **6/9** | 6/9 | | 155.6 s |

Every PASS ended with the model's own finish and every FAIL ended without one:
no `false_done` occurred. Three runs per task are a small sample; the rates
describe these instances, not general reliability.

### Run log (fields as in D1 p.49)

| Task | Run | Model | Observation | Grounding | Steps (budget) | Verifier | Failure class | Recording | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ContactsAddContact | seed 42 | autoglm-phone-multilingual | screenshot | model coordinates | 13 (16) | PASS | - | `trial_ContactsAddContact_20261008T133405_016539Z/video_001.mp4` | 39k prompt tokens |
| ContactsAddContact | seed 43 | same | same | same | 11 (16) | PASS | - | `..._20261008T133619_620636Z/video_001.mp4` | |
| ContactsAddContact | seed 44 | same | same | same | 12 (16) | PASS | - | `..._20261008T133738_098779Z/video_001.mp4` | |
| SimpleCalendarAddOneEvent | seed 42 | same | same | same | 20 (35) | PASS | - | `trial_SimpleCalendarAddOneEvent_20261008T133858_768284Z/video_001.mp4` | 18 Oct, 00:00, 45 min |
| SimpleCalendarAddOneEvent | seed 43 | same | same | same | 21 (35) | PASS | - | `..._20261008T134140_371059Z/video_001-002.mp4` | two invalid replies (truncated reply, unsupported action) corrected without execution |
| SimpleCalendarAddOneEvent | seed 44 | same | same | same | 17 (35) | PASS | - | `..._20261008T134543_875203Z/video_001.mp4` | |
| OsmAndTrack | seed 42 (4 waypoints) | same | same | same | 17 (90) | FAIL | `grounding` | `trial_OsmAndTrack_20261008T134852_193100Z/video_001-002.mp4` | Chose "Bendern (Guidepost)", a same-name signpost, and made it route point 1; "Balzers" typed into an unfocused field, then described results that were not shown; see [FINAL_FAILURE_ANALYSIS.md](FINAL_FAILURE_ANALYSIS.md) |
| OsmAndTrack | seed 43 (2) | same | same | same | 14 (90) | FAIL | other: wrong feature | `..._20261008T135208_398127Z/video_001.mp4` | Found Oberplanken, then saved it as a Favorite three times (the Skill states that Add is a Favorite) |
| OsmAndTrack | seed 44 (3) | same | same | same | 22 (90) | FAIL | other: search strategy | `..._20261008T135454_519070Z/video_001.mp4` | Widened the radius once, then switched between later waypoints instead of finding the first |

All runs stopped either by the model's finish (PASS) or by the bounded
no-progress stop (`control_no_progress`, FAIL); none reached its step or time
budget. Run folders contain `summary.json`, `task.json`, readable and JSONL
trajectories, every request/response, before/after screenshots and the video.

### Interpretation

- **Easy and medium tasks are reliable on these instances.** Contacts needs
  about 2.4 times its reference steps (opening the app, focusing fields, saving
  and checking); Calendar finishes close to its 17 reference steps.
- **The hard task fails, but not at the start.** With the Skill, all three runs
  searched by place name; seed 43 opened the place itself and seed 42 started a
  route, but with a same-name guidepost instead of the village. Without the Skill (same code, see
  [IMPROVEMENT_OSMAND.md](IMPROVEMENT_OSMAND.md)) no run selected a place.
- **The course's five GUI failure classes cover only one of the three OsmAnd
  failures.** The others are knowledge/strategy failures in a complex app
  (choosing the wrong feature, a poor search plan). We label them as "other"
  rather than forcing them into a class.
- Infrastructure faults found before the final batch (black frames, ADB server
  restarts killing the recorder, slow cold starts, a provider prompt limit)
  are listed with their fixes in [MEDIUM_HARD_TRIALS.md](MEDIUM_HARD_TRIALS.md).
  None occurred in the final batch.

### Cost and time

Prompt tokens per run: Contacts 31-39k, Calendar 61-99k, OsmAnd 69-136k
(the provider reported 66-70% of OsmAnd prompt tokens as cached).
The full batch of nine runs took 24 minutes of wall-clock time.
