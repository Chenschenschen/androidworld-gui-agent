# Five easy tasks: recorded results

Success requires valid initialization, video and official verifier PASS.
One frozen version; task seeds 42/43/44 by default. Three cases are a small sample.

Clean finish also requires the model's finish reply, with no runtime error.

| Task | Valid PASS / attempts | Clean finishes | Invalid evaluations |
| --- | --- | --- | --- |
| SystemWifiTurnOn | 3/3 | 3/3 | 0 |
| CameraTakePhoto | 0/1 | 0/1 | 0 |
| ClockTimerEntry | 0/0 | 0/0 | 0 |
| ContactsAddContact | 0/0 | 0/0 | 0 |
| SystemCopyToClipboard | 0/0 | 0/0 | 0 |

| Task | Seed | Outcome | Model finish | Steps | Seconds | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SystemWifiTurnOn | 42 | PASS | True | 5 | 58.16 | [summary](../trial_SystemWifiTurnOn_20261007T205329_721894Z/summary.json) |
| SystemWifiTurnOn | 43 | PASS | True | 5 | 57.67 | [summary](../trial_SystemWifiTurnOn_20261007T205428_552420Z/summary.json) |
| SystemWifiTurnOn | 44 | PASS | True | 5 | 59.39 | [summary](../trial_SystemWifiTurnOn_20261007T205526_888786Z/summary.json) |
| CameraTakePhoto | 42 | FAIL | False | 12 | 76.31 | [summary](../trial_CameraTakePhoto_20261007T205626_958365Z/summary.json) |
