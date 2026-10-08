# Published aggregate results

These reports contain only selected outcome fields from original local summaries,
not raw evidence. Full files in local `runs/` remain unchanged. Screenshots, task
inputs, model replies, XML, diagnostic trajectories, source snapshots and videos
are intentionally kept local.

| Selected batch | Included outcome |
| --- | --- |
| [v20 gate](batches/easy_batch_20261008T064328_366877Z/RESULTS.md) | Wi-Fi 3/3 and Camera 3/3 clean; Timer failure retained. |
| [v28 regressions](batches/easy_batch_20261008T081652_065024Z/RESULTS.md) | Contacts seed 42 clean; Timer seed 42 failed. |
| [v28 Contacts repeats](batches/easy_batch_20261008T082214_015428Z/RESULTS.md) | Seeds 43/44 clean on identical sources. |
| [v27 Clipboard regression](batches/easy_batch_20261008T081108_236581Z/RESULTS.md) | Model finish with official FAIL; preserved false completion. |

Each table has a machine-readable results.json with task/seed/run ID, version,
model-finish and verifier status, validity, steps, duration and stop reason.
These fields were checked against the originals. They allow readers to assess
the stated counts, but do not independently reproduce the private recordings.
The full recordings and completed-step artifacts were audited locally. Failure
analysis is in COURSE_AND_UPSTREAM_REVIEW.md and TRAJECTORY_FAILURE_ANALYSIS.md.

[offline_verification.json](offline_verification.json) records Contacts source
equality and a saved-trace replay of the v29 no-progress limit. The latter makes
no API/device calls and is not a live v29 success. The
[Clipboard probe outcome](clipboard_probe.json)
executed no action and still returned a false finish; it is not a benchmark run.

Read [WARMUP_RESULTS.md](../WARMUP_RESULTS.md) for definitions and limitations.
Three seeds are a small sample; successful results use explicitly named v20/v28
versions. Current v29 has no live success claim. No failed task is hidden to
manufacture a successful three-repeat gate.
