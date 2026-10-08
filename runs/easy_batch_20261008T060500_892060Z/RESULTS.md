# Five easy tasks: recorded results

Success requires valid initialization, video and official verifier PASS.
One frozen version; task seeds 42/43/44 by default. Three cases are a small sample.

Clean finish also requires the model's finish reply, with no runtime error.

| Task | Valid PASS / attempts | Clean finishes | Invalid evaluations |
| --- | --- | --- | --- |
| SystemWifiTurnOn | 0/0 | 0/0 | 0 |
| CameraTakePhoto | 0/0 | 0/0 | 0 |
| ClockTimerEntry | 1/2 | 1/2 | 0 |
| ContactsAddContact | 0/0 | 0/0 | 0 |
| SystemCopyToClipboard | 0/0 | 0/0 | 0 |

| Task | Seed | Outcome | Model finish | Steps | Seconds | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| ClockTimerEntry | 43 | PASS | True | 8 | 92.09 | [summary](../trial_ClockTimerEntry_20261008T060501_419942Z/summary.json) |
| ClockTimerEntry | 44 | FAIL | False | 10 | 125.08 | [summary](../trial_ClockTimerEntry_20261008T060634_132162Z/summary.json) |
