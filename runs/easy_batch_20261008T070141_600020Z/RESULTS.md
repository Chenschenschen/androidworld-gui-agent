# Five easy tasks: recorded results

Success requires valid initialization, video and official verifier PASS.
One frozen version; task seeds 42/43/44 by default. Three cases are a small sample.

Clean finish also requires the model's finish reply, with no runtime error.

| Task | Valid PASS / attempts | Clean finishes | Invalid evaluations |
| --- | --- | --- | --- |
| SystemWifiTurnOn | 0/0 | 0/0 | 0 |
| CameraTakePhoto | 0/0 | 0/0 | 0 |
| ClockTimerEntry | 0/0 | 0/0 | 0 |
| ContactsAddContact | 0/0 | 0/0 | 0 |
| SystemCopyToClipboard | 1/2 | 1/2 | 0 |

| Task | Seed | Outcome | Model finish | Steps | Seconds | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| SystemCopyToClipboard | 42 | PASS | True | 6 | 49.97 | [summary](../trial_SystemCopyToClipboard_20261008T070142_134919Z/summary.json) |
| SystemCopyToClipboard | 43 | FAIL | False | 6 | 52.53 | [summary](../trial_SystemCopyToClipboard_20261008T070232_847659Z/summary.json) |
