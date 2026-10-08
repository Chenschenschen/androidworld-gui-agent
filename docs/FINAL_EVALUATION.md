# Final evaluation: easy, medium and hard task, three runs each

This is the course evaluation required by D1 pp.6-7 (one task from each
difficulty row, three runs per task, every run screen-recorded) and Syllabus
p.1 (evaluation results, trajectory logs, failure analysis). All nine runs use
**one frozen version**; earlier task-specific results on other versions are
not mixed in.

## Setup

| Item | Value |
| --- | --- |
| Agent version | `autoglm_api_v36_bounded_splash_waits` (commit `8f6233e`), identical source hashes for every run (checked by `evaluate_tasks.py` before each trial) |
| Model | `autoglm-phone-multilingual` (AutoGLM-Phone-9B-Multilingual), hosted by Z.ai; temperature 0, top_p 0.85, max_tokens 3000 |
| Observation | Latest screenshot (resized to at most 1280 px) plus checked GUI notes; native AutoGLM pseudo-call actions validated in Python |
| Grounding | Model coordinates (0-1000 normalised), converted and checked by the adapter |
| Budgets | Contacts 16 steps / 900 s; Calendar 35 / 1200 s; OsmAnd 90 / 2700 s |
| Skill | `instructions/skills/osmand_track.md`, OsmAndTrack only (see [IMPROVEMENT_OSMAND.md](IMPROVEMENT_OSMAND.md)) |
| Success | Official Android World verifier PASS. The model's own `finish` is recorded separately and never counts as success |
| Environment | Android World at `2dfc5ca`, Python 3.11, Pixel 6 API 33 Google APIs image, emulator flags `-no-snapshot -grpc 8554 -camera-back emulated -camera-front emulated -gpu swiftshader_indirect` |
| Task seeds | 42, 43, 44 (seed fixes each task instance; see `task.json` in each run) |

Command (one batch, all nine runs, no stop after a failure):

```powershell
.\.venv\Scripts\python.exe -X utf8 evaluate_tasks.py --tasks ContactsAddContact SimpleCalendarAddOneEvent OsmAndTrack --seeds 42 43 44 --run-all-seeds
```

<!-- Results are added after the batch finishes. -->
