# Five easy tasks: recorded results

Success requires valid initialization, video and official verifier PASS.
One frozen version; task seeds 42/43/44 by default. Three cases are a small sample.

Clean finish also requires the model's finish reply, with no runtime error.

| Task | Valid PASS / attempts | Clean finishes | Invalid evaluations |
| --- | --- | --- | --- |
| SystemWifiTurnOn | 3/3 | 3/3 | 0 |
| CameraTakePhoto | 1/2 | 1/2 | 0 |
| ClockTimerEntry | 0/0 | 0/0 | 0 |
| ContactsAddContact | 0/0 | 0/0 | 0 |
| SystemCopyToClipboard | 0/0 | 0/0 | 0 |

| Task | Seed | Outcome | Model finish | Steps | Seconds | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SystemWifiTurnOn | 42 | PASS | True | 5 | 57.88 | [summary](../trial_SystemWifiTurnOn_20261008T063136_028753Z/summary.json) |
| SystemWifiTurnOn | 43 | PASS | True | 5 | 56.59 | [summary](../trial_SystemWifiTurnOn_20261008T063234_548534Z/summary.json) |
| SystemWifiTurnOn | 44 | PASS | True | 5 | 56.72 | [summary](../trial_SystemWifiTurnOn_20261008T063331_739156Z/summary.json) |
| CameraTakePhoto | 42 | PASS | True | 5 | 44.38 | [summary](../trial_CameraTakePhoto_20261008T063429_067392Z/summary.json) |
| CameraTakePhoto | 43 | FAIL | False | 12 | 96.06 | [summary](../trial_CameraTakePhoto_20261008T063514_164428Z/summary.json) |
