# Recorded task results

Success requires valid initialization, video and official verifier PASS.
One frozen version; task seeds 42/43/44 by default. Three cases are a small sample.

Clean finish also requires the model's finish reply, with no runtime error.

| Task | Valid PASS / attempts | Clean finishes | Invalid evaluations |
| --- | --- | --- | --- |
| SystemWifiTurnOn | 3/3 | 3/3 | 0 |
| ContactsAddContact | 2/3 | 2/3 | 0 |
| SimpleSmsSend | 3/3 | 3/3 | 0 |
| FilesMoveFile | 2/3 | 2/3 | 0 |
| SimpleCalendarAddOneEvent | 3/3 | 3/3 | 0 |
| MarkorCreateNoteAndSms | 3/3 | 3/3 | 0 |

| Task | Seed | Outcome | Model finish | Steps | Seconds | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SystemWifiTurnOn | 42 | PASS | True | 5 | 74.44 | [summary](../trial_SystemWifiTurnOn_20261008T215130_600754Z/summary.json) |
| SystemWifiTurnOn | 43 | PASS | True | 5 | 70.59 | [summary](../trial_SystemWifiTurnOn_20261008T215246_616671Z/summary.json) |
| SystemWifiTurnOn | 44 | PASS | True | 5 | 68.80 | [summary](../trial_SystemWifiTurnOn_20261008T215358_472883Z/summary.json) |
| ContactsAddContact | 42 | PASS | True | 12 | 119.66 | [summary](../trial_ContactsAddContact_20261008T215508_628423Z/summary.json) |
| ContactsAddContact | 43 | FAIL | False | 11 | 80.88 | [summary](../trial_ContactsAddContact_20261008T215709_244163Z/summary.json) |
| ContactsAddContact | 44 | PASS | True | 11 | 85.02 | [summary](../trial_ContactsAddContact_20261008T215831_022667Z/summary.json) |
| SimpleSmsSend | 42 | PASS | True | 9 | 78.19 | [summary](../trial_SimpleSmsSend_20261008T215957_234873Z/summary.json) |
| SimpleSmsSend | 43 | PASS | True | 7 | 66.52 | [summary](../trial_SimpleSmsSend_20261008T220116_423331Z/summary.json) |
| SimpleSmsSend | 44 | PASS | True | 7 | 68.88 | [summary](../trial_SimpleSmsSend_20261008T220223_867500Z/summary.json) |
| FilesMoveFile | 42 | PASS | True | 17 | 118.45 | [summary](../trial_FilesMoveFile_20261008T220333_997891Z/summary.json) |
| FilesMoveFile | 43 | FAIL | True | 13 | 98.91 | [summary](../trial_FilesMoveFile_20261008T220533_834164Z/summary.json) |
| FilesMoveFile | 44 | PASS | True | 13 | 109.69 | [summary](../trial_FilesMoveFile_20261008T220713_812951Z/summary.json) |
| SimpleCalendarAddOneEvent | 42 | PASS | True | 20 | 161.84 | [summary](../trial_SimpleCalendarAddOneEvent_20261008T220904_772591Z/summary.json) |
| SimpleCalendarAddOneEvent | 43 | PASS | True | 21 | 154.31 | [summary](../trial_SimpleCalendarAddOneEvent_20261008T221147_529159Z/summary.json) |
| SimpleCalendarAddOneEvent | 44 | PASS | True | 16 | 142.67 | [summary](../trial_SimpleCalendarAddOneEvent_20261008T221423_161758Z/summary.json) |
| MarkorCreateNoteAndSms | 42 | PASS | True | 18 | 265.88 | [summary](../trial_MarkorCreateNoteAndSms_20261008T221647_424207Z/summary.json) |
| MarkorCreateNoteAndSms | 43 | PASS | True | 18 | 307.78 | [summary](../trial_MarkorCreateNoteAndSms_20261008T222123_918435Z/summary.json) |
| MarkorCreateNoteAndSms | 44 | PASS | True | 15 | 208.28 | [summary](../trial_MarkorCreateNoteAndSms_20261008T222633_440045Z/summary.json) |
