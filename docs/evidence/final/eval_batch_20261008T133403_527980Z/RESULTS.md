# Recorded task results

Success requires valid initialization, video and official verifier PASS.
One frozen version; task seeds 42/43/44 by default. Three cases are a small sample.

Clean finish also requires the model's finish reply, with no runtime error.

| Task | Valid PASS / attempts | Clean finishes | Invalid evaluations |
| --- | --- | --- | --- |
| ContactsAddContact | 3/3 | 3/3 | 0 |
| SimpleCalendarAddOneEvent | 3/3 | 3/3 | 0 |
| OsmAndTrack | 0/3 | 0/3 | 0 |

| Task | Seed | Outcome | Model finish | Steps | Seconds | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| ContactsAddContact | 42 | PASS | True | 13 | 132.97 | [summary](../trial_ContactsAddContact_20261008T133405_016539Z/summary.json) |
| ContactsAddContact | 43 | PASS | True | 11 | 77.50 | [summary](../trial_ContactsAddContact_20261008T133619_620636Z/summary.json) |
| ContactsAddContact | 44 | PASS | True | 12 | 79.47 | [summary](../trial_ContactsAddContact_20261008T133738_098779Z/summary.json) |
| SimpleCalendarAddOneEvent | 42 | PASS | True | 20 | 159.20 | [summary](../trial_SimpleCalendarAddOneEvent_20261008T133858_768284Z/summary.json) |
| SimpleCalendarAddOneEvent | 43 | PASS | True | 21 | 241.33 | [summary](../trial_SimpleCalendarAddOneEvent_20261008T134140_371059Z/summary.json) |
| SimpleCalendarAddOneEvent | 44 | PASS | True | 17 | 186.12 | [summary](../trial_SimpleCalendarAddOneEvent_20261008T134543_875203Z/summary.json) |
| OsmAndTrack | 42 | FAIL | False | 17 | 194.41 | [summary](../trial_OsmAndTrack_20261008T134852_193100Z/summary.json) |
| OsmAndTrack | 43 | FAIL | False | 14 | 165.03 | [summary](../trial_OsmAndTrack_20261008T135208_398127Z/summary.json) |
| OsmAndTrack | 44 | FAIL | False | 22 | 164.75 | [summary](../trial_OsmAndTrack_20261008T135454_519070Z/summary.json) |
