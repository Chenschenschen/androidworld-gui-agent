# Five easy tasks: recorded results

Success requires valid initialization, video and official verifier PASS.
One frozen version; task seeds 42/43/44 by default. Three cases are a small sample.

Clean finish also requires the model's finish reply, with no runtime error.

| Task | Valid PASS / attempts | Clean finishes | Invalid evaluations |
| --- | --- | --- | --- |
| SystemWifiTurnOn | 1/2 | 1/2 | 0 |
| CameraTakePhoto | 0/0 | 0/0 | 0 |
| ClockTimerEntry | 0/0 | 0/0 | 0 |
| ContactsAddContact | 0/0 | 0/0 | 0 |
| SystemCopyToClipboard | 0/0 | 0/0 | 0 |

| Task | Seed | Outcome | Model finish | Steps | Seconds | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SystemWifiTurnOn | 42 | PASS | True | 5 | 62.44 | [summary](../trial_SystemWifiTurnOn_20261008T062431_367115Z/summary.json) |
| SystemWifiTurnOn | 43 | FAIL | False | 0 | 8.75 | [summary](../trial_SystemWifiTurnOn_20261008T062534_516124Z/summary.json) |
