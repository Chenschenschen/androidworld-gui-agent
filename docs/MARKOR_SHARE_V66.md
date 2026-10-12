# Follow-up after the freeze: Markor shares the note itself (v66)

The final evaluation ([TEAM_FINAL_EVALUATION.md](TEAM_FINAL_EVALUATION.md), v65,
18/21) stays our main result. This page records one change made after that
freeze, evaluated on its own.

## Why

The official goal is "Create a new note in Markor named … with the following
text: …. Share the entire content of the note with the phone number … via SMS
using Simple SMS Messenger". The official verifier checks two things: the note
file (name and text) and a sent SMS with exactly that text to that number, with
Simple SMS Messenger in front. It does not check how the text got into the SMS.

The v65 Skill saved the note and then **typed the same text again** in Simple
SMS Messenger. The verifier accepted that (3/3), but the agent never took the
content from the note, which is the idea of the task. Markor's file share,
tried earlier in the integration package, attaches the file and turns the
message into an MMS that shows "Not sent" (verifier 0.5).

## What changed (v66, tag `markor-share-v66`)

Only [instructions/skills/markor_sms.md](../instructions/skills/markor_sms.md),
its offline test and the config version. The Skill now shares the note from
Markor's editor: **More options > Share > Plain Text > SMS Messenger**, enter
the number, confirm, and send; the message field already holds the note's text,
so the Skill says not to type it again. Share > File stays forbidden.

Before writing the Skill we checked the path by hand on the emulator: the share
sends a plain SMS, the exact body appears in `content://sms/sent`, and Simple
SMS Messenger is the app in front, as the verifier requires. The Skill is loaded
only for this task, so the other six tasks are not affected. 38 offline tests pass.

## Practice runs (seed 1, never an evaluation seed)

| # | Run ID | Outcome | Cause |
| --- | --- | --- | --- |
| 1 | `trial_MarkorCreateNoteAndSms_20261009T114650_857742Z` | setup error | Official Markor setup: "NEXT" not found (probably timing on the first cold start after boot; the intro showed NEXT when checked by hand) |
| 2 | `trial_MarkorCreateNoteAndSms_20261009T115008_052190Z` | setup error | "Allow access to manage all files" not found: Markor still had all-files access, which clearing app data does not remove |
| 3 | `trial_MarkorCreateNoteAndSms_20261009T115157_320390Z` | setup error | Markor setup passed; SMS setup: "SMS Messenger" not found, because it was still the default SMS app and the dialog never opened |
| 4 | `trial_MarkorCreateNoteAndSms_20261009T115425_342426Z` | setup error | Same step; the dialog opened but the UI dump timed out on it |
| 5 | `trial_MarkorCreateNoteAndSms_20261009T120306_179655Z` | error after 6 steps | `adb shell input text` hung for 35 minutes (observation time budget exhausted); the device was left in a bad state by our manual checks, so we restarted the emulator |
| 6 | `trial_MarkorCreateNoteAndSms_20261009T124404_261906Z` | **PASS**, 19 steps, no refusals | Followed the new Skill: Share > Plain Text > SMS Messenger > number > SMS. The first Markor launch showed the "All files access" page once (Back and Launch, two extra steps) |

Root cause of the setup errors: AndroidWorld keeps its app snapshots in
`/data/data/android_world/snapshots`, and Android deletes that folder at every
boot because it belongs to no installed app. After a boot the official setups
run again, and the Markor and SMS Messenger setups assume a fresh install. Before
run 6 we restarted the emulator and reset the two preconditions with adb
(Markor's `MANAGE_EXTERNAL_STORAGE` app-op back to default; the SMS role back to
Google Messages). The official setups then ran unchanged, and the emulator was
not restarted before the evaluation.

## Evaluation: seeds 42, 43, 44 (one batch, frozen v66, recorded)

Batch `eval_batch_20261009T125038_033286Z`; budget 40 steps, same model and
verifier as v65.

| Seed | Run ID | Steps / budget | Verifier | Failure class | Note |
| --- | --- | --- | --- | --- | --- |
| 42 | `trial_MarkorCreateNoteAndSms_20261009T125039_586151Z` | 18 / 40 | FAIL (0.5) | grounding | Note saved; shared with Share > Plain Text; number confirmed; the text was already in the message field. The model then said the SMS button was "at the top right" and tapped [940, 60] four times, hitting nothing, until the no-progress rule stopped the run. The button was at the right end of the message bar (about [930, 606]). [Screenshot](evidence/markor_v66/runs/trial_MarkorCreateNoteAndSms_20261009T125039_586151Z/step_016/observation_0/screen.png) |
| 43 | `trial_MarkorCreateNoteAndSms_20261009T125401_048355Z` | 18 / 40 | **PASS** | — | Same path; tapped SMS at [930, 936] (keyboard closed) |
| 44 | `trial_MarkorCreateNoteAndSms_20261009T125719_921778Z` | 18 / 40 | **PASS** | — | Same path; tapped SMS at [930, 599] (keyboard open) |

In all three runs the text was typed once, into the note, and then shared; no
run typed it into the SMS app. No action was refused.

## v65 and v66 side by side

| | v65 (types the text again) | v66 (shares the note) |
| --- | --- | --- |
| Verifier PASS | 3 / 3 | 2 / 3 |
| Runs that typed the text into the SMS app | 3 / 3 | 0 / 3 |
| Mean steps of passing runs | 17 | 18 |
| Failures | none | 1 grounding (SMS send button) |

Same seeds, model, step budget and verifier; only the Skill differs. Three runs
per side is a small sample, so the one failure does not show that the new path
is harder: it failed on the last tap, after the share itself had worked.

Fix layer for the seed 42 failure (not built; v66 stays frozen): program, check
that a tap lands on a control and otherwise refuse it with the nearest one, the
same fix as for the OsmAnd seed 366 grounding failure; or instruction, "the SMS
button is at the right end of the message field".

## Reproduce

```powershell
git checkout markor-share-v66
# after an emulator boot, so that the official setups can run:
adb shell appops set --uid net.gsantner.markor MANAGE_EXTERNAL_STORAGE default
adb shell cmd role add-role-holder android.app.role.SMS com.google.android.apps.messaging
.\.venv\Scripts\python.exe -X utf8 evaluate_tasks.py --tasks MarkorCreateNoteAndSms --seeds 42 43 44 --run-all-seeds
```

## Records

- Logs, summaries and configs of all nine runs, with a checksum manifest:
  [evidence/markor_v66/](evidence/markor_v66/)
- Screen recordings (not in git because of their size):
  `markor_share_v66_recordings.zip` next to the repository. Each folder is named role_seed_result__run ID (for example `official_s43_PASS__trial_...`); `official_*` are the evaluation runs, `practice_*` are not part of the result; README.txt explains it.
