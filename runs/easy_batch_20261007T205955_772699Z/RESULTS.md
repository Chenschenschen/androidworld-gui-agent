# Five easy tasks: recorded results

Success requires valid initialization, video and official verifier PASS.
One frozen version; task seeds 42/43/44 by default. Three cases are a small sample.

Clean finish also requires the model's finish reply, with no runtime error.

| Task | Valid PASS / attempts | Clean finishes | Invalid evaluations |
| --- | --- | --- | --- |
| SystemWifiTurnOn | 0/0 | 0/0 | 0 |
| CameraTakePhoto | 3/3 | 3/3 | 0 |
| ClockTimerEntry | 0/1 | 0/1 | 0 |
| ContactsAddContact | 0/0 | 0/0 | 0 |
| SystemCopyToClipboard | 0/0 | 0/0 | 0 |

| Task | Seed | Outcome | Model finish | Steps | Seconds | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| CameraTakePhoto | 42 | PASS | True | 4 | 25.25 | [summary](../trial_CameraTakePhoto_20261007T205956_380483Z/summary.json) |
| CameraTakePhoto | 43 | PASS | True | 4 | 23.55 | [summary](../trial_CameraTakePhoto_20261007T210022_327851Z/summary.json) |
| CameraTakePhoto | 44 | PASS | True | 4 | 23.47 | [summary](../trial_CameraTakePhoto_20261007T210046_571282Z/summary.json) |
| ClockTimerEntry | 42 | FAIL | False | 10 | 57.50 | [summary](../trial_ClockTimerEntry_20261007T210110_738453Z/summary.json) |
