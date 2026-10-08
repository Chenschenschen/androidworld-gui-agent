# Published results and approved evidence

The aggregate reports below contain selected outcome fields. Following the
user's explicit approval on 8 October 2026, the previously blocked evidence
subset is also published. Full original files in local `runs/` remain unchanged.

## Original evidence subset

[export_manifest.json](export_manifest.json) lists 156 exported files, their
original relative paths, byte counts and SHA256 hashes. All copied files are
checked against the originals and Git bytes. The subset contains 12 trial
summaries plus task/configuration/version metadata across four selected batches:

- [v20 original results](runs/easy_batch_20261008T064328_366877Z/RESULTS.md)
- [v28 original regressions](runs/easy_batch_20261008T081652_065024Z/RESULTS.md)
- [v28 original Contacts repeats](runs/easy_batch_20261008T082214_015428Z/RESULTS.md)
- [v27 original Clipboard regression](runs/easy_batch_20261008T081108_236581Z/RESULTS.md)

The latest failed Timer and Clipboard trials also include original readable and
JSONL trajectories, checked execution/result records and before/after screenshots.
The original [saved-screen probe result](runs/actual_control_feedback_probe_20261008T081535_861953Z/result.json)
is preserved. These diagnostic records include synthetic task inputs and visible
model replies; they are retained as evidence, not interpreted as success.

This is a subset: full recordings, API request/reply files, XML and complete
source snapshots are not included. Some original paths in traces refer to the
larger local archive. Those paths are historical, not installation settings.
Credentials, environments, dependency checkouts and course originals are excluded.

## Aggregate reports

| Selected batch | Included outcome |
| --- | --- |
| [v20 gate](batches/easy_batch_20261008T064328_366877Z/RESULTS.md) | Wi-Fi 3/3 and Camera 3/3 clean; Timer failure retained. |
| [v28 regressions](batches/easy_batch_20261008T081652_065024Z/RESULTS.md) | Contacts seed 42 clean; Timer seed 42 failed. |
| [v28 Contacts repeats](batches/easy_batch_20261008T082214_015428Z/RESULTS.md) | Seeds 43/44 clean on identical sources. |
| [v27 Clipboard regression](batches/easy_batch_20261008T081108_236581Z/RESULTS.md) | Model finish with official FAIL; preserved false completion. |

Each table has a machine-readable results.json with task/seed/run ID, version,
model-finish and verifier status, validity, steps, duration and stop reason.
These fields were checked against the originals. They allow readers to assess
the stated counts; full recordings remain in the local archive.
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
