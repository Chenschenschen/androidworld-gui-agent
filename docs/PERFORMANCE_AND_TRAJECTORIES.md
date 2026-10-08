# Trajectory logs and local performance

Latest recorded Contacts trial: `trial_ContactsAddContact_20261007T173637_269613Z`, official FAIL, initial 0.0/final 0.0, 12 steps, 12 calls, 119.75 seconds, no manual intervention.
The retained default is `learning_single_name_v7_gpu22`. Earlier official PASS
runs demonstrate contact creation capability; the failures demonstrate that
our adapted prompt/interface is still fragile. Hard-task capability and
repeatability remain unproven. These are learning trials, not a frozen evaluation.

## Read a run

Open `trajectory.txt` to read the events in order. `trajectory.jsonl` has one
structured JSON event per line. Each event is appended and flushed immediately;
a later failure does not erase previous steps. `trajectory.py` adapts the
labelled blocks and flush in the course `minimal_agent_example.py`, lines 30-35.

Each step records the observation and screenshot/tree paths, the actual model
request file, visible raw reply, validation feedback, chosen action, execution
start, observed field values, and timing. A selected action is explicitly marked
not yet executed. The final event separates model completion from official
verification. Complete request JSON lives beside the trace; images are linked
instead of inserting base64. Source/config/task/model identity and videos are
saved with the same run ID. Older reconstructed traces are explicitly labelled
retrospective; their timestamps are reconstruction times.

## What failed, and what changed

- The earlier `165206_708350Z` trial stopped after 12 actions with an unsaved
  form. It tapped a keyboard Dash key and left a leading dash in Phone.
- Targeted TYPE selects, clears and enters an editable field in one checked
  Android World action. v3 entered the number, but tapped the Create contact
  heading instead of Save and declared completion. Official FAIL.
- Named label grounding resolves the model's exact target against the current
  tree. v4/GPU16 correctly selected Save and earned PASS in 110.70 seconds.
  Its original summary has an inaccurate grounding label; `analysis.json`
  records the correction, backed by source/config/action files.
- v4/GPU22 wandered through filters. Prompt wording also changed: this is not
  a controlled hardware-versus-quality comparison. v5 restricted target labels
  to interactive app controls and removed stale coordinates from model history.
  It saved a name without a number and falsely declared completion.
- v6 rejects editable-field CLICKs with explicit TYPE feedback. It entered the
  phone and saved, but the resulting name was `Camila da Silva da Silva`.
  Its prediction of success was false. We retain raw predictions in the trace
  but omit them from factual recent-action history.
- v7 changes only the conditional contact procedure from v6: full task name
  once in First name, Last name blank. Same task seed, sampling, GPU offload,
  action checks and budgets. The model chooses every target/value and Save.
  The official verifier determines whether that change worked. One paired
  comparison cannot establish broad reliability; three repeated evaluations
  per final selected task are still required.

The guide-only comparison did **not** improve success: v6 FAIL and v7 FAIL.
v7 selected the Phone contacts and Company filters, followed Privacy Policy
into Chrome, and repeatedly toggled its onboarding checkbox. The state changed
on each toggle, so unchanged-tree recovery did not fire; the global step budget
stopped the run. `analysis.json` records `wrong_app`, while the original runtime
summary leaves its failure class null. The latest default is a diagnostic
configuration, not an established successful baseline.

## GPU measurement

The same frozen tree and screenshot requests were sent with 16 and 22 GPU
layers. One warmup per setting was excluded; two cached tree repeats and one
image request were measured. No phone actions were executed by this probe.

| Offloaded layers | Peak device VRAM | Warm tree median | Screenshot request |
| --- | --- | --- | --- |
| 16 | 5,139 MiB / 62.8% | 7.16 s | 21.19 s |
| 22 | 6,393 MiB / 78.1% | 6.61 s | 19.25 s |

Tree time fell about 7.7%, screenshot time about 9.1%. Replies were identical,
including the wrong screenshot target. This measures a small speed improvement,
not an intelligence improvement. The 80% preference is interpreted as approximate
VRAM use; instantaneous GPU compute utilization cannot be fixed to 80%.
Evidence: [probe summary](../runs/gpu_offload_20261007T170529_775400Z/summary.json).

The BF16 engine residency reported by Ollama is about 9.9 GB, exceeding the
4070 Laptop's 8,188 MiB VRAM. Partial offload leaves CPU work. Screenshot prompt
processing alone took about 12.5 seconds in the GPU22 probe. In the older
156.88-second failed run, 13 model requests consumed 114.72 seconds (73%). The
remainder includes capture/stabilization, GUI execution, verification and recording;
we have not separately profiled every component. Repeated incorrect decisions
add requests and make total runtime worse. Warm-run loading was a small share.

## New recorded trials

| Version / evidence | Verifier | Steps incl. stop | Model calls | Total seconds | Model API wall seconds |
| --- | --- | --- | --- | --- | --- |
| [learning_targeted_type_v3_gpu16](../runs/trial_ContactsAddContact_20261007T171029_450783Z/summary.json) | FAIL | 8 | 8 | 109.11 | 77.31 |
| [learning_label_grounding_v4_gpu16](../runs/trial_ContactsAddContact_20261007T171621_506135Z/summary.json) | PASS | 8 | 8 | 110.70 | 77.47 |
| [learning_label_grounding_v4_gpu22](../runs/trial_ContactsAddContact_20261007T172052_755250Z/summary.json) | FAIL | 12 | 14 | 150.44 | 113.75 |
| [learning_contact_process_v5_gpu22](../runs/trial_ContactsAddContact_20261007T172714_503543Z/summary.json) | FAIL | 12 | 14 | 151.88 | 106.34 |
| [learning_direct_type_v6_gpu22](../runs/trial_ContactsAddContact_20261007T173342_439614Z/summary.json) | FAIL | 7 | 10 | 105.80 | 73.70 |
| [learning_single_name_v7_gpu22](../runs/trial_ContactsAddContact_20261007T173637_269613Z/summary.json) | FAIL | 12 | 12 | 119.75 | 80.92 |

The model is useful enough to have completed Contacts under our harness, but
these mixed-version trials do not establish reliable autonomous performance.
First repeat the same frozen version, then a new task seed, before expanding.
Keep tree-first and the bounded image fallback. Do not switch models, quantize,
or add a framework without discussing that separate decision.

Before another live repeat, the recommended next experiment is a frozen
same-task comparison of screenshot input and tree-first using the current clean
history/typing contract. The tree adaptation may be contributing to semantic
errors, but the present runs do not isolate that cause. Show complete saved
values and actual Save/COMPLETE decisions; compare verifier outcomes and runtime.

## Run it yourself

From the project folder, with Ollama and AndroidWorldAvd running:

```powershell
.\run.ps1 -CheckOnly
.\run.ps1 -Task ContactsAddContact -Seed 42
```

Or use `.venv\Scripts\python.exe -X utf8 run_task.py --task ContactsAddContact --seed 42`.
Every invocation creates a unique run folder. Watch the TXT log while it runs.
Read `verified_agent_success` in the final summary; process completion is separate.
See [complete launch instructions](RUNNING_TASKS.md).
# Latest five-task evaluation — 7 October 2026

The completed v10 batch `easy_batch_20261007T191040_731527Z` records three task
seeds per easy task: Wi-Fi 1/3, Camera 0/3, Timer 0/3, Contacts 0/3, Clipboard
0/3. All fifteen logs/request references/videos were audited. None establishes
three successful repeats. Infrastructure problems and genuine model errors both
occur; do not interpret the raw rates as an isolated model capability score.
See [FIVE_TASK_EVALUATION.md](FIVE_TASK_EVALUATION.md) for exact evidence,
before/after limits and reproduction commands. Earlier measurements below
remain historical and use different versions.
