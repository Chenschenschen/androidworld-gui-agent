# Five easy tasks: recorded results

Success requires valid initialization, video and official verifier PASS.
One frozen version; task seeds 42/43/44 by default. Three cases are a small sample.

Clean finish also requires the model's finish reply, with no runtime error.

| Task | Valid PASS / attempts | Clean finishes | Invalid evaluations |
| --- | --- | --- | --- |
| SystemWifiTurnOn | 0/0 | 0/0 | 0 |
| CameraTakePhoto | 0/0 | 0/0 | 0 |
| ClockTimerEntry | 0/1 | 0/1 | 0 |
| ContactsAddContact | 1/1 | 1/1 | 0 |
| SystemCopyToClipboard | 0/0 | 0/0 | 0 |

| Task | Seed | Outcome | Model finish | Steps | Seconds | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| ContactsAddContact | 42 | PASS | True | 11 | 71.44 | [summary](../trial_ContactsAddContact_20261008T081652_701104Z/summary.json) |
| ClockTimerEntry | 42 | FAIL | False | 12 | 149.36 | [summary](../trial_ClockTimerEntry_20261008T081804_857919Z/summary.json) |
