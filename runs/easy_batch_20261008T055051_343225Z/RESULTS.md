# Five easy tasks: recorded results

Success requires valid initialization, video and official verifier PASS.
One frozen version; task seeds 42/43/44 by default. Three cases are a small sample.

Clean finish also requires the model's finish reply, with no runtime error.

| Task | Valid PASS / attempts | Clean finishes | Invalid evaluations |
| --- | --- | --- | --- |
| SystemWifiTurnOn | 0/0 | 0/0 | 0 |
| CameraTakePhoto | 0/0 | 0/0 | 0 |
| ClockTimerEntry | 0/0 | 0/0 | 0 |
| ContactsAddContact | 1/1 | 1/1 | 0 |
| SystemCopyToClipboard | 0/1 | 0/1 | 0 |

| Task | Seed | Outcome | Model finish | Steps | Seconds | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| ContactsAddContact | 42 | PASS | True | 12 | 95.78 | [summary](../trial_ContactsAddContact_20261008T055051_890271Z/summary.json) |
| SystemCopyToClipboard | 42 | FAIL | False | 4 | 34.19 | [summary](../trial_SystemCopyToClipboard_20261008T055228_288420Z/summary.json) |
