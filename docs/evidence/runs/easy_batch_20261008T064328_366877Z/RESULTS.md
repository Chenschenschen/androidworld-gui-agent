# Five easy tasks: recorded results

Success requires valid initialization, video and official verifier PASS.
One frozen version; task seeds 42/43/44 by default. Three cases are a small sample.

Clean finish also requires the model's finish reply, with no runtime error.

| Task | Valid PASS / attempts | Clean finishes | Invalid evaluations |
| --- | --- | --- | --- |
| SystemWifiTurnOn | 3/3 | 3/3 | 0 |
| CameraTakePhoto | 3/3 | 3/3 | 0 |
| ClockTimerEntry | 0/1 | 0/1 | 0 |
| ContactsAddContact | 0/0 | 0/0 | 0 |
| SystemCopyToClipboard | 0/0 | 0/0 | 0 |

| Task | Seed | Outcome | Model finish | Steps | Seconds | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SystemWifiTurnOn | 42 | PASS | True | 5 | 61.08 | [summary](../trial_SystemWifiTurnOn_20261008T064329_088037Z/summary.json) |
| SystemWifiTurnOn | 43 | PASS | True | 5 | 58.77 | [summary](../trial_SystemWifiTurnOn_20261008T064430_869000Z/summary.json) |
| SystemWifiTurnOn | 44 | PASS | True | 5 | 59.55 | [summary](../trial_SystemWifiTurnOn_20261008T064530_270073Z/summary.json) |
| CameraTakePhoto | 42 | PASS | True | 4 | 29.55 | [summary](../trial_CameraTakePhoto_20261008T064630_447465Z/summary.json) |
| CameraTakePhoto | 43 | PASS | True | 4 | 30.34 | [summary](../trial_CameraTakePhoto_20261008T064700_740386Z/summary.json) |
| CameraTakePhoto | 44 | PASS | True | 4 | 34.16 | [summary](../trial_CameraTakePhoto_20261008T064731_890637Z/summary.json) |
| ClockTimerEntry | 42 | FAIL | False | 10 | 136.34 | [summary](../trial_ClockTimerEntry_20261008T064806_804154Z/summary.json) |
