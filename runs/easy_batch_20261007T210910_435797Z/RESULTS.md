# Five easy tasks: recorded results

Success requires valid initialization, video and official verifier PASS.
One frozen version; task seeds 42/43/44 by default. Three cases are a small sample.

Clean finish also requires the model's finish reply, with no runtime error.

| Task | Valid PASS / attempts | Clean finishes | Invalid evaluations |
| --- | --- | --- | --- |
| SystemWifiTurnOn | 0/0 | 0/0 | 0 |
| CameraTakePhoto | 0/0 | 0/0 | 0 |
| ClockTimerEntry | 1/3 | 1/3 | 0 |
| ContactsAddContact | 0/3 | 0/3 | 3 |
| SystemCopyToClipboard | 0/3 | 0/3 | 0 |

| Task | Seed | Outcome | Model finish | Steps | Seconds | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| ClockTimerEntry | 42 | FAIL | False | 9 | 116.92 | [summary](../trial_ClockTimerEntry_20261007T210910_992181Z/summary.json) |
| ClockTimerEntry | 43 | PASS | True | 8 | 91.47 | [summary](../trial_ClockTimerEntry_20261007T211108_555352Z/summary.json) |
| ClockTimerEntry | 44 | FAIL | False | 10 | 121.91 | [summary](../trial_ClockTimerEntry_20261007T211240_628935Z/summary.json) |
| ContactsAddContact | 42 | NOT_RUN (invalid) | False | 0 | 23.61 | [summary](../trial_ContactsAddContact_20261007T211443_160403Z/summary.json) |
| ContactsAddContact | 43 | NOT_RUN (invalid) | False | 0 | 22.09 | [summary](../trial_ContactsAddContact_20261007T211507_489929Z/summary.json) |
| ContactsAddContact | 44 | NOT_RUN (invalid) | False | 0 | 21.78 | [summary](../trial_ContactsAddContact_20261007T211530_303827Z/summary.json) |
| SystemCopyToClipboard | 42 | FAIL | False | 6 | 81.58 | [summary](../trial_SystemCopyToClipboard_20261007T211552_824415Z/summary.json) |
| SystemCopyToClipboard | 43 | FAIL | False | 12 | 78.30 | [summary](../trial_SystemCopyToClipboard_20261007T211715_106089Z/summary.json) |
| SystemCopyToClipboard | 44 | FAIL | False | 12 | 80.55 | [summary](../trial_SystemCopyToClipboard_20261007T211834_111221Z/summary.json) |
