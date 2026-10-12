# Team agent: one agent for all seven tasks

Branch `team-agent`, built on Jia's branch (v62) on 8 October 2026. The three
original contributions stay unchanged: branch `Jia`, branch `hayati` and the
integration package `amber_agent_integration_20261008`. This branch makes one
agent, the `AutoGLMAgent` class in [autoglm_agent.py](../autoglm_agent.py)
with its single `step()` method, run all seven chosen tasks.

| Course row (D1 p.7) | Task | Where the support came from |
| --- | --- | --- |
| Warm-up (easy) | SystemWifiTurnOn | Already in the shared runner (v20) |
| Warm-up (easy) | ContactsAddContact | Already in the shared runner (v14-v42) |
| Real work (medium) | SimpleSmsSend | Added here; lessons from branch `hayati` |
| Real work (medium) | FilesMoveFile | Added here; lessons from branch `hayati` |
| Real work (medium) | SimpleCalendarAddOneEvent | Jia, v30-v42 |
| Multi-app (hard) | MarkorCreateNoteAndSms | Added here; Skill from the integration package's runs |
| Multi-app (hard) | OsmAndTrack | Jia, v30-v62 (program-layer Skill) |

## What was taken from the other contributions

We ported **lessons**, not whole code bases: the `hayati` branch changes the
same two core files in conflicting ways, and the integration package uses a
different agent (Open-AutoGLM `PhoneAgent` with its own runner). Fixes were
ported only when a practice run here showed the same failure.

- **SimpleSmsSend (hayati):** passing runs needed no special initialization;
  the documented failures were a stale tap that typed into the wrong field
  (fixed there with UIAutomator labels for the SMS app) and a Launch name
  translated into Chinese (fixed there with aliases). Our runner already
  resolves a translated name when only one app is allowed.
- **FilesMoveFile (hayati):** hayati avoided the official initialization
  because it deletes every file in shared storage, and used a custom one.
  We keep the official initialization (benchmark standard) and protect the one
  file it would break for us, OsmAnd's offline map (see below).
- **MarkorCreateNoteAndSms (integration package):** its failure analysis found
  that Markor's Share menu attaches the file and makes an MMS that is "Not sent"
  (`false_done`), and that the model looped in Markor after a Launch that did
  not bring Simple SMS Messenger to the front. Its legitimate fixes became the
  Skill [instructions/skills/markor_sms.md](../instructions/skills/markor_sms.md).
  Its runner also called the official verifier during an episode and fed the
  result back to the model; that is ground-truth feedback and was **not**
  ported, and runs that relied on it are not used as results.

## Changes in this branch

| Version | Change | Why |
| --- | --- | --- |
| v63 | Three tasks added to the runner: apps, visible completion rules, step budgets (SMS 20, Files 25, Markor 40; reference 6/10/9). FilesMoveFile's `noise_candidates` withheld from the model (setup data, like Calendar's rows) | New tasks |
| v64 | The input-method focus check accepts Markor's editor (`HighlightingEditor`) | Practice run 4 below |
| v64 | Markor Skill, with its procedure repeated each step | Integration package's failure analysis; a system-prompt Skill alone was ignored on OsmAnd (v40) |
| v64 | OsmAnd's screen checks and coded procedure run for OsmAndTrack only | They are task-specific; the comma rule would have refused Markor text |
| v64 | Before an OsmAnd run, the map file `Liechtenstein_europe.obf` is checked and the official OsmAnd setup re-run if it is missing | FilesMoveFile's official initialization runs `find /storage/emulated/0/ -type f -delete`, which also removes OsmAnd's map (the app snapshot covers only `/data/data`) |
| v65 | Recorded Chinese translations of "Simple SMS Messenger" resolve through an alias table (still checked against the allowed apps) | Practice run 5 below; the same fix as branch `hayati` v48 |

Existing tasks keep their code paths; the final evaluation re-runs all seven
tasks on one frozen version so that this is measured, not assumed.

## Practice runs (seeds outside the evaluation set)

| # | Run ID | Version | Task, seed | Outcome | Cause | Change made |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `trial_SystemWifiTurnOn_20261008T212843_267494Z` | v63 | Wi-Fi, 1 | PASS, 5 steps, 115 s | — | — |
| 2 | `trial_SimpleSmsSend_20261008T213039_700745Z` | v63 | SMS, 1 | PASS, 13 steps, 143 s | Opened the system Messages app first (not the default SMS app), went back, then reached Simple SMS Messenger through the app drawer; one malformed reply corrected | None (a detour, not a failure) |
| 3 | `trial_FilesMoveFile_20261008T213303_734689Z` | v63 | Files, 1 | PASS, 17 steps, 115 s, official initialization | Looked for Move in the wrong menu once (Info screen), then found "Move to..." after a long press | None |
| 4 | `trial_MarkorCreateNoteAndSms_20261008T213459_657766Z` | v63 | Markor, 1 | FAIL, `validation_error` after 9 steps | Note created with the right name and Plain Text type; in the open editor our focus check refused Type because Android reported the focused view as `HighlightingEditor`, which the check did not recognise as a text field; the model's correction used pixel coordinates outside 0-1000, the second invalid reply in that step ended the run | v64 focus check and Markor Skill |
| 5 | `trial_MarkorCreateNoteAndSms_20261008T213903_095859Z` | v64 | Markor, 1 | FAIL, `validation_error` after 9 steps | Created and saved the note correctly (name, Plain Text type, text, Save) following the Skill; then sent Launch with Simple SMS Messenger translated into Chinese twice. With two apps allowed the name cannot be resolved by elimination, so both replies were refused | v65 alias table |
| 6 | `trial_MarkorCreateNoteAndSms_20261008T214123_738381Z` | v65 | Markor, 1 | **PASS**, 16 steps, 126 s, model finished | Followed the Skill: + in Markor, typed the name, replaced the extension field ".md" with ".txt", typed and saved the text; Launch with a shorter Chinese name for Simple SMS Messenger resolved through the alias table; Start a conversation, number, checkmark, typed the same text and tapped the SMS send button. No refusals | — |
| 7 | `trial_OsmAndTrack_20261008T214359_935135Z` | v65 | OsmAnd, 8 (regression and map restore) | **PASS**, 21 steps, 399 s, model finished | The FilesMoveFile practice had deleted OsmAnd's map; the runner logged OSMAND MAP MISSING, re-ran the official OsmAnd setup (map restored, checked on the device) and the run then passed as in v59-v62. The forwarder crash dialog appeared once and was closed | Frozen as v65 |

v65 is frozen as tag `team-agent-final-v65` for the evaluation of six tasks in [TEAM_FINAL_EVALUATION.md](TEAM_FINAL_EVALUATION.md). v66 (tag `team-agent-final-v66`) changes only the Markor Skill so that it shares the note (Share > Plain Text) instead of typing its text again; Markor's final runs come from v66 ([MARKOR_SHARE_V66.md](MARKOR_SHARE_V66.md)).
