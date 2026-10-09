"""The 21 final runs (v65) in the course's log format (D1 p.49), one entry per run.

Facts come from each run's summary.json, action.json files and validation_error files; notes describe what the run did.
Used by build_deck.py (run-log slides) and build_run_log.py (the per-run log cards for the submission).
"""
REPO = "https://github.com/Chenschenschen/androidworld-gui-agent/blob/team-agent/docs/evidence/team/runs"
MODEL = "AutoGLM-Phone-9B-Multilingual (hosted, Z.ai)"
VERSION = "autoglm_api_v65_team_agent (tag team-agent-final-v65)"
ZIP = "team_agent_final_recordings_v65.zip"
ORDER = ["SystemWifiTurnOn", "ContactsAddContact", "SimpleSmsSend", "FilesMoveFile",
         "SimpleCalendarAddOneEvent", "MarkorCreateNoteAndSms", "OsmAndTrack"]
ROW = {"SystemWifiTurnOn": "Warm-up", "ContactsAddContact": "Warm-up", "SimpleSmsSend": "Real work", "FilesMoveFile": "Real work",
       "SimpleCalendarAddOneEvent": "Real work", "MarkorCreateNoteAndSms": "Multi-app", "OsmAndTrack": "Multi-app"}
OBS = {"SystemWifiTurnOn": "screenshot + Settings labels", "MarkorCreateNoteAndSms": "screenshot + text Skill",
       "OsmAndTrack": "screenshot + accessibility tree + coded Skill"}
BUDGET = {"SystemWifiTurnOn": 12, "ContactsAddContact": 16, "SimpleSmsSend": 20, "FilesMoveFile": 25,
          "SimpleCalendarAddOneEvent": 35, "MarkorCreateNoteAndSms": 40, "OsmAndTrack": 90}

# (task, run number, seed, run_id, steps, verifier, failure class, clips, short note for the slide, full note)
RUNS = [
 ("SystemWifiTurnOn", 1, 42, "trial_SystemWifiTurnOn_20261008T215130_600754Z", 5, "PASS", "", 1,
  "Settings > Internet > Wi-Fi on; finished",
  "Launched Settings, opened Network & internet, then Internet, switched Wi-Fi on and finished after seeing the switch ON."),
 ("SystemWifiTurnOn", 2, 43, "trial_SystemWifiTurnOn_20261008T215246_616671Z", 5, "PASS", "", 1,
  "Same 5-step path; finished",
  "Same five-step path as run 1; no refusals."),
 ("SystemWifiTurnOn", 3, 44, "trial_SystemWifiTurnOn_20261008T215358_472883Z", 5, "PASS", "", 1,
  "Same 5-step path; finished",
  "Same five-step path; the model noted the switch was OFF before tapping it and ON afterwards."),
 ("ContactsAddContact", 1, 42, "trial_ContactsAddContact_20261008T215508_628423Z", 12, "PASS", "", 1,
  "Name, scroll, number, Save; finished",
  "Opened Contacts, tapped +, typed first and last name (Camila da Silva), scrolled once, typed the number and saved."),
 ("ContactsAddContact", 2, 43, "trial_ContactsAddContact_20261008T215709_244163Z", 11, "FAIL", "other: navigation", 1,
  "Swiped past Phone field; no-progress stop",
  "Typed Hugo and Ali, then two swipes moved the form past the Phone field to its end; four more swipes changed only the "
  "blinking cursor (our effect check counted it as a change). Stopped by the no-progress rule; the contact was never saved."),
 ("ContactsAddContact", 3, 44, "trial_ContactsAddContact_20261008T215831_022667Z", 11, "PASS", "", 1,
  "Name, scroll, number, Save; finished",
  "Same procedure as run 1 (Maya Martin); one scroll reached the Phone field; saved and finished."),
 ("SimpleSmsSend", 1, 42, "trial_SimpleSmsSend_20261008T215957_234873Z", 9, "PASS", "", 1,
  "New conversation, number, message, send",
  "Launched Simple SMS Messenger, started a conversation, typed the number, confirmed it, typed the message and sent it."),
 ("SimpleSmsSend", 2, 43, "trial_SimpleSmsSend_20261008T220116_423331Z", 7, "PASS", "", 1,
  "Chinese app name resolved; sent in 7 steps",
  "The model gave the app name in Chinese; with one app allowed the runner resolved it. Number, message, send in 7 steps."),
 ("SimpleSmsSend", 3, 44, "trial_SimpleSmsSend_20261008T220223_867500Z", 7, "PASS", "", 1,
  "Chinese app name resolved; sent in 7 steps",
  "Same as run 2: app name given in Chinese and resolved; message sent in 7 steps."),
 ("FilesMoveFile", 1, 42, "trial_FilesMoveFile_20261008T220333_997891Z", 17, "PASS", "", 1,
  "Scrolled to file, Move to, MOVE; finished",
  "Opened the source folder, scrolled to sci_fi_book.mp3, long-pressed it, chose Move to..., opened Audiobooks, tapped MOVE, "
  "waited for the move and finished."),
 ("FilesMoveFile", 2, 43, "trial_FilesMoveFile_20261008T220533_834164Z", 13, "FAIL", "false_done", 1,
  "Moved look-alike file, then finished",
  "In the grid view the names were cut off; the model picked “documentary_20...” (“assuming it is named differently "
  "here”), moved it to Movies and finished. The real documentary.mp4 never moved, so the verifier failed it."),
 ("FilesMoveFile", 3, 44, "trial_FilesMoveFile_20261008T220713_812951Z", 13, "PASS", "", 1,
  "Same procedure; 1 malformed reply corrected",
  "Same procedure as run 1; one malformed reply (not exactly one action) was refused and corrected in the same step."),
 ("SimpleCalendarAddOneEvent", 1, 42, "trial_SimpleCalendarAddOneEvent_20261008T220904_772591Z", 20, "PASS", "", 1,
  "Title, text, date, time, length; 1 fix",
  "App name given in Chinese and resolved; typed title and description, set date, start hour and duration, saved. "
  "One malformed reply was corrected."),
 ("SimpleCalendarAddOneEvent", 2, 43, "trial_SimpleCalendarAddOneEvent_20261008T221147_529159Z", 21, "PASS", "", 1,
  "Saved event; 1 unsupported action fixed",
  "Same procedure; one unsupported action was refused and corrected; event saved with the right date, time and length."),
 ("SimpleCalendarAddOneEvent", 3, 44, "trial_SimpleCalendarAddOneEvent_20261008T221423_161758Z", 16, "PASS", "", 1,
  "Saved event in 16 steps; no refusals",
  "Same procedure in 16 steps with no refusals."),
 ("MarkorCreateNoteAndSms", 1, 42, "trial_MarkorCreateNoteAndSms_20261008T221647_424207Z", 18, "PASS", "", 2,
  "Note saved; SMS app via alias; plain SMS",
  "Created the note with the right name and text and saved it; launched Simple SMS Messenger by a Chinese name (resolved by "
  "the alias table); typed the same text into a new plain SMS and sent it."),
 ("MarkorCreateNoteAndSms", 2, 43, "trial_MarkorCreateNoteAndSms_20261008T222123_918435Z", 18, "PASS", "", 2,
  "Name + .txt, saved, plain SMS; 1 retry",
  "Typed the name, replaced the extension with .txt, typed and saved the text, then sent it as a plain SMS. One truncated "
  "model reply was retried."),
 ("MarkorCreateNoteAndSms", 3, 44, "trial_MarkorCreateNoteAndSms_20261008T222633_440045Z", 15, "PASS", "", 2,
  "The 15-step run shown on the trajectory slide",
  "The run shown step by step on the trajectory slide: new file, name and extension, text, Save, SMS app, number, same text, SMS button."),
 ("OsmAndTrack", 1, 31, "trial_OsmAndTrack_20261008T223004_312422Z", 22, "PASS", "", 4,
  "Map restored first; Ruggell, Bendern, Done",
  "Before the run the runner restored OsmAnd's map (the Files runs had cleared storage). Three radius increases and one scroll "
  "found the Ruggell village; Actions > Plan a route; searched Bendern, SHOW ON THE MAP, Back x3, Add, Done. The Favorite button "
  "and one unfocused Type were refused."),
 ("OsmAndTrack", 2, 314, "trial_OsmAndTrack_20261008T224202_113624Z", 23, "PASS", "", 3,
  "Same route; crash dialog closed; 1 refusal",
  "Same procedure as run 1; the accessibility service's “keeps stopping” dialog appeared and the model closed it; one "
  "unfocused Type was refused."),
 ("OsmAndTrack", 3, 366, "trial_OsmAndTrack_20261008T225108_345362Z", 16, "FAIL", "grounding", 2,
  "Point 1 done; Clear missed 3x; stopped",
  "Ruggell became route point 1 and the crash dialog was closed; in the second search the code stated “Tap Clear at "
  "[941, 83]” but the model tapped [941, 57], the top edge of the button, three times with no effect. No-progress stop."),
]


def trajectory_url(run_id):
    return f"{REPO}/{run_id}/trajectory.txt"
