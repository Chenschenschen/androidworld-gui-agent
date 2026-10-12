# Run log: final evaluation (final agent v66)

One card per task; the three runs are the columns. Fields follow the course's run log (D1 p.49), plus a note that explains the run, a link to its readable trajectory log and the agent version. Success is the official AndroidWorld verifier. Markor runs come from v66 (the Skill shares the note); the other tasks from v65, whose code is the same for them. Recordings are not in Git because of their size; every clip is in `team_agent_final_recordings_v66.zip`, one folder per run named task_seed_result__run ID. Summary and analysis: [TEAM_FINAL_EVALUATION.md](TEAM_FINAL_EVALUATION.md).


## SystemWifiTurnOn (Warm-up): 3/3

| Field | Run 1 of 3 | Run 2 of 3 | Run 3 of 3 |
| --- | --- | --- | --- |
| task | SystemWifiTurnOn | SystemWifiTurnOn | SystemWifiTurnOn |
| run | 1 of 3 (seed 42) | 2 of 3 (seed 43) | 3 of 3 (seed 44) |
| model | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) |
| observation | screenshot + Settings labels | screenshot + Settings labels | screenshot + Settings labels |
| grounding | coordinates (0-1000 grid) | coordinates (0-1000 grid) | coordinates (0-1000 grid) |
| steps | 5 (budget 12) | 5 (budget 12) | 5 (budget 12) |
| verifier | **PASS** | **PASS** | **PASS** |
| failure_class | — | — | — |
| recording | video_001.mp4 in team_agent_final_recordings_v66.zip / SystemWifiTurnOn_s42_PASS__trial_SystemWifiTurnOn_20261008T215130_600754Z | video_001.mp4 in team_agent_final_recordings_v66.zip / SystemWifiTurnOn_s43_PASS__trial_SystemWifiTurnOn_20261008T215246_616671Z | video_001.mp4 in team_agent_final_recordings_v66.zip / SystemWifiTurnOn_s44_PASS__trial_SystemWifiTurnOn_20261008T215358_472883Z |
| note | Launched Settings, opened Network & internet, then Internet, switched Wi-Fi on and finished after seeing the switch ON. | Same five-step path as run 1; no refusals. | Same five-step path; the model noted the switch was OFF before tapping it and ON afterwards. |
| trajectory | [Readable trajectory log](evidence/team/runs/trial_SystemWifiTurnOn_20261008T215130_600754Z/trajectory.txt) | [Readable trajectory log](evidence/team/runs/trial_SystemWifiTurnOn_20261008T215246_616671Z/trajectory.txt) | [Readable trajectory log](evidence/team/runs/trial_SystemWifiTurnOn_20261008T215358_472883Z/trajectory.txt) |
| agent version | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) |

## ContactsAddContact (Warm-up): 2/3

| Field | Run 1 of 3 | Run 2 of 3 | Run 3 of 3 |
| --- | --- | --- | --- |
| task | ContactsAddContact | ContactsAddContact | ContactsAddContact |
| run | 1 of 3 (seed 42) | 2 of 3 (seed 43) | 3 of 3 (seed 44) |
| model | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) |
| observation | screenshot | screenshot | screenshot |
| grounding | coordinates (0-1000 grid) | coordinates (0-1000 grid) | coordinates (0-1000 grid) |
| steps | 12 (budget 16) | 11 (budget 16) | 11 (budget 16) |
| verifier | **PASS** | **FAIL** | **PASS** |
| failure_class | — | other: navigation | — |
| recording | video_001.mp4 in team_agent_final_recordings_v66.zip / ContactsAddContact_s42_PASS__trial_ContactsAddContact_20261008T215508_628423Z | video_001.mp4 in team_agent_final_recordings_v66.zip / ContactsAddContact_s43_FAIL__trial_ContactsAddContact_20261008T215709_244163Z | video_001.mp4 in team_agent_final_recordings_v66.zip / ContactsAddContact_s44_PASS__trial_ContactsAddContact_20261008T215831_022667Z |
| note | Opened Contacts, tapped +, typed first and last name (Camila da Silva), scrolled once, typed the number and saved. | Typed Hugo and Ali, then two swipes moved the form past the Phone field to its end; four more swipes changed only the blinking cursor (our effect check counted it as a change). Stopped by the no-progress rule; the contact was never saved. | Same procedure as run 1 (Maya Martin); one scroll reached the Phone field; saved and finished. |
| trajectory | [Readable trajectory log](evidence/team/runs/trial_ContactsAddContact_20261008T215508_628423Z/trajectory.txt) | [Readable trajectory log](evidence/team/runs/trial_ContactsAddContact_20261008T215709_244163Z/trajectory.txt) | [Readable trajectory log](evidence/team/runs/trial_ContactsAddContact_20261008T215831_022667Z/trajectory.txt) |
| agent version | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) |

## SimpleSmsSend (Real work): 3/3

| Field | Run 1 of 3 | Run 2 of 3 | Run 3 of 3 |
| --- | --- | --- | --- |
| task | SimpleSmsSend | SimpleSmsSend | SimpleSmsSend |
| run | 1 of 3 (seed 42) | 2 of 3 (seed 43) | 3 of 3 (seed 44) |
| model | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) |
| observation | screenshot | screenshot | screenshot |
| grounding | coordinates (0-1000 grid) | coordinates (0-1000 grid) | coordinates (0-1000 grid) |
| steps | 9 (budget 20) | 7 (budget 20) | 7 (budget 20) |
| verifier | **PASS** | **PASS** | **PASS** |
| failure_class | — | — | — |
| recording | video_001.mp4 in team_agent_final_recordings_v66.zip / SimpleSmsSend_s42_PASS__trial_SimpleSmsSend_20261008T215957_234873Z | video_001.mp4 in team_agent_final_recordings_v66.zip / SimpleSmsSend_s43_PASS__trial_SimpleSmsSend_20261008T220116_423331Z | video_001.mp4 in team_agent_final_recordings_v66.zip / SimpleSmsSend_s44_PASS__trial_SimpleSmsSend_20261008T220223_867500Z |
| note | Launched Simple SMS Messenger, started a conversation, typed the number, confirmed it, typed the message and sent it. | The model gave the app name in Chinese; with one app allowed the runner resolved it. Number, message, send in 7 steps. | Same as run 2: app name given in Chinese and resolved; message sent in 7 steps. |
| trajectory | [Readable trajectory log](evidence/team/runs/trial_SimpleSmsSend_20261008T215957_234873Z/trajectory.txt) | [Readable trajectory log](evidence/team/runs/trial_SimpleSmsSend_20261008T220116_423331Z/trajectory.txt) | [Readable trajectory log](evidence/team/runs/trial_SimpleSmsSend_20261008T220223_867500Z/trajectory.txt) |
| agent version | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) |

## FilesMoveFile (Real work): 2/3

| Field | Run 1 of 3 | Run 2 of 3 | Run 3 of 3 |
| --- | --- | --- | --- |
| task | FilesMoveFile | FilesMoveFile | FilesMoveFile |
| run | 1 of 3 (seed 42) | 2 of 3 (seed 43) | 3 of 3 (seed 44) |
| model | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) |
| observation | screenshot | screenshot | screenshot |
| grounding | coordinates (0-1000 grid) | coordinates (0-1000 grid) | coordinates (0-1000 grid) |
| steps | 17 (budget 25) | 13 (budget 25) | 13 (budget 25) |
| verifier | **PASS** | **FAIL** | **PASS** |
| failure_class | — | false_done | — |
| recording | video_001.mp4 in team_agent_final_recordings_v66.zip / FilesMoveFile_s42_PASS__trial_FilesMoveFile_20261008T220333_997891Z | video_001.mp4 in team_agent_final_recordings_v66.zip / FilesMoveFile_s43_FAIL__trial_FilesMoveFile_20261008T220533_834164Z | video_001.mp4 in team_agent_final_recordings_v66.zip / FilesMoveFile_s44_PASS__trial_FilesMoveFile_20261008T220713_812951Z |
| note | Opened the source folder, scrolled to sci_fi_book.mp3, long-pressed it, chose Move to..., opened Audiobooks, tapped MOVE, waited for the move and finished. | In the grid view the names were cut off; the model picked “documentary_20...” (“assuming it is named differently here”), moved it to Movies and finished. The real documentary.mp4 never moved, so the verifier failed it. | Same procedure as run 1; one malformed reply (not exactly one action) was refused and corrected in the same step. |
| trajectory | [Readable trajectory log](evidence/team/runs/trial_FilesMoveFile_20261008T220333_997891Z/trajectory.txt) | [Readable trajectory log](evidence/team/runs/trial_FilesMoveFile_20261008T220533_834164Z/trajectory.txt) | [Readable trajectory log](evidence/team/runs/trial_FilesMoveFile_20261008T220713_812951Z/trajectory.txt) |
| agent version | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) |

## SimpleCalendarAddOneEvent (Real work): 3/3

| Field | Run 1 of 3 | Run 2 of 3 | Run 3 of 3 |
| --- | --- | --- | --- |
| task | SimpleCalendarAddOneEvent | SimpleCalendarAddOneEvent | SimpleCalendarAddOneEvent |
| run | 1 of 3 (seed 42) | 2 of 3 (seed 43) | 3 of 3 (seed 44) |
| model | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) |
| observation | screenshot | screenshot | screenshot |
| grounding | coordinates (0-1000 grid) | coordinates (0-1000 grid) | coordinates (0-1000 grid) |
| steps | 20 (budget 35) | 21 (budget 35) | 16 (budget 35) |
| verifier | **PASS** | **PASS** | **PASS** |
| failure_class | — | — | — |
| recording | video_001.mp4 in team_agent_final_recordings_v66.zip / SimpleCalendarAddOneEvent_s42_PASS__trial_SimpleCalendarAddOneEvent_20261008T220904_772591Z | video_001.mp4 in team_agent_final_recordings_v66.zip / SimpleCalendarAddOneEvent_s43_PASS__trial_SimpleCalendarAddOneEvent_20261008T221147_529159Z | video_001.mp4 in team_agent_final_recordings_v66.zip / SimpleCalendarAddOneEvent_s44_PASS__trial_SimpleCalendarAddOneEvent_20261008T221423_161758Z |
| note | App name given in Chinese and resolved; typed title and description, set date, start hour and duration, saved. One malformed reply was corrected. | Same procedure; one unsupported action was refused and corrected; event saved with the right date, time and length. | Same procedure in 16 steps with no refusals. |
| trajectory | [Readable trajectory log](evidence/team/runs/trial_SimpleCalendarAddOneEvent_20261008T220904_772591Z/trajectory.txt) | [Readable trajectory log](evidence/team/runs/trial_SimpleCalendarAddOneEvent_20261008T221147_529159Z/trajectory.txt) | [Readable trajectory log](evidence/team/runs/trial_SimpleCalendarAddOneEvent_20261008T221423_161758Z/trajectory.txt) |
| agent version | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) |

## MarkorCreateNoteAndSms (Multi-app): 2/3

| Field | Run 1 of 3 | Run 2 of 3 | Run 3 of 3 |
| --- | --- | --- | --- |
| task | MarkorCreateNoteAndSms | MarkorCreateNoteAndSms | MarkorCreateNoteAndSms |
| run | 1 of 3 (seed 42) | 2 of 3 (seed 43) | 3 of 3 (seed 44) |
| model | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) |
| observation | screenshot + text Skill | screenshot + text Skill | screenshot + text Skill |
| grounding | coordinates (0-1000 grid) | coordinates (0-1000 grid) | coordinates (0-1000 grid) |
| steps | 18 (budget 40) | 18 (budget 40) | 18 (budget 40) |
| verifier | **FAIL** | **PASS** | **PASS** |
| failure_class | grounding | — | — |
| recording | video_001.mp4 in team_agent_final_recordings_v66.zip / MarkorCreateNoteAndSms_s42_FAIL__trial_MarkorCreateNoteAndSms_20261009T125039_586151Z | video_001.mp4 in team_agent_final_recordings_v66.zip / MarkorCreateNoteAndSms_s43_PASS__trial_MarkorCreateNoteAndSms_20261009T125401_048355Z | video_001.mp4, video_002.mp4 in team_agent_final_recordings_v66.zip / MarkorCreateNoteAndSms_s44_PASS__trial_MarkorCreateNoteAndSms_20261009T125719_921778Z |
| note | Note saved; Share > Plain Text sent its text to SMS Messenger; number confirmed. The model then said the SMS button was at the top right and tapped [940, 60] four times; the button was at the right of the message bar. No-progress stop. | New file, name and .txt, text, Save; More options > Share > Plain Text > SMS Messenger; number and checkmark; the text was already in the message field, so it only tapped SMS. | Same path as run 2: the note's text was shared with Share > Plain Text, not typed again; SMS sent in 18 steps. |
| trajectory | [Readable trajectory log](evidence/markor_v66/runs/trial_MarkorCreateNoteAndSms_20261009T125039_586151Z/trajectory.txt) | [Readable trajectory log](evidence/markor_v66/runs/trial_MarkorCreateNoteAndSms_20261009T125401_048355Z/trajectory.txt) | [Readable trajectory log](evidence/markor_v66/runs/trial_MarkorCreateNoteAndSms_20261009T125719_921778Z/trajectory.txt) |
| agent version | autoglm_api_v66_markor_share (tag team-agent-final-v66) | autoglm_api_v66_markor_share (tag team-agent-final-v66) | autoglm_api_v66_markor_share (tag team-agent-final-v66) |

## OsmAndTrack (Multi-app): 2/3

| Field | Run 1 of 3 | Run 2 of 3 | Run 3 of 3 |
| --- | --- | --- | --- |
| task | OsmAndTrack | OsmAndTrack | OsmAndTrack |
| run | 1 of 3 (seed 31) | 2 of 3 (seed 314) | 3 of 3 (seed 366) |
| model | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) | AutoGLM-Phone-9B-Multilingual (hosted, Z.ai) |
| observation | screenshot + accessibility tree + coded Skill | screenshot + accessibility tree + coded Skill | screenshot + accessibility tree + coded Skill |
| grounding | coordinates (0-1000 grid) | coordinates (0-1000 grid) | coordinates (0-1000 grid) |
| steps | 22 (budget 90) | 23 (budget 90) | 16 (budget 90) |
| verifier | **PASS** | **PASS** | **FAIL** |
| failure_class | — | — | grounding |
| recording | video_001.mp4, video_002.mp4, video_003.mp4, video_004.mp4 in team_agent_final_recordings_v66.zip / OsmAndTrack_s31_PASS__trial_OsmAndTrack_20261008T223004_312422Z | video_001.mp4, video_002.mp4, video_003.mp4 in team_agent_final_recordings_v66.zip / OsmAndTrack_s314_PASS__trial_OsmAndTrack_20261008T224202_113624Z | video_001.mp4, video_002.mp4 in team_agent_final_recordings_v66.zip / OsmAndTrack_s366_FAIL__trial_OsmAndTrack_20261008T225108_345362Z |
| note | Before the run the runner restored OsmAnd's map (the Files runs had cleared storage). Three radius increases and one scroll found the Ruggell village; Actions > Plan a route; searched Bendern, SHOW ON THE MAP, Back x3, Add, Done. The Favorite button and one unfocused Type were refused. | Same procedure as run 1; the accessibility service's “keeps stopping” dialog appeared and the model closed it; one unfocused Type was refused. Shown on slide 10. | Ruggell became route point 1 and the crash dialog was closed; in the second search the code stated “Tap Clear at [941, 83]” but the model tapped [941, 57], the top edge of the button, three times with no effect. No-progress stop. |
| trajectory | [Readable trajectory log](evidence/team/runs/trial_OsmAndTrack_20261008T223004_312422Z/trajectory.txt) | [Readable trajectory log](evidence/team/runs/trial_OsmAndTrack_20261008T224202_113624Z/trajectory.txt) | [Readable trajectory log](evidence/team/runs/trial_OsmAndTrack_20261008T225108_345362Z/trajectory.txt) |
| agent version | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) | autoglm_api_v65_team_agent (tag team-agent-final-v65; same code as v66 for this task) |
