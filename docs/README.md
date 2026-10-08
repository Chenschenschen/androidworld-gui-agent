# Documentation map

Start here rather than reading the design history from beginning to end.

| Current document | Purpose |
| --- | --- |
| [SETUP.md](SETUP.md) | Fresh Windows/Python/Android installation. |
| [RUNNING_TASKS.md](RUNNING_TASKS.md) | Independent execution and evidence fields. |
| [AGENT_WALKTHROUGH.md](AGENT_WALKTHROUGH.md) | Explain the current program's flow. |
| [AUTOGLM_API.md](AUTOGLM_API.md) | Z.ai endpoint, model selection and native protocol. |
| [WARMUP_RESULTS.md](WARMUP_RESULTS.md) | Recorded task gates and unresolved errors. |
| [LEADERBOARD_COMPARISON.md](LEADERBOARD_COMPARISON.md) | Primary-source comparison with strong Android World agents; proposed experiments. |
| [STEP_ASSESSMENT_EXPERIMENT.md](STEP_ASSESSMENT_EXPERIMENT.md) | Same-model M3A adaptation, diagnosed failures and current opt-in status. |
| [UPSTREAM_REFERENCE_COMPARISON.md](UPSTREAM_REFERENCE_COMPARISON.md) | Actual pinned PhoneAgent comparison, infrastructure repairs and trace-based conclusions. |
| [TASK_GUIDANCE_AND_GROUNDING.md](TASK_GUIDANCE_AND_GROUNDING.md) | Explicit warm-up procedures, opt-in v36 and the limits of current coordinate grounding. |
| [GENERAL_GUIDANCE_EXPERIMENT.md](GENERAL_GUIDANCE_EXPERIMENT.md) | Accepted reusable interaction-guidance design, v37 configuration and bounded live evidence. |
| [evidence/README.md](evidence/README.md) | Aggregate reports and the approved metadata/trajectory/screenshot subset. |
| [COURSE_AND_UPSTREAM_REVIEW.md](COURSE_AND_UPSTREAM_REVIEW.md) | D1–D4 principles, pinned official sources and repair ledger. |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | Rules for a justified change and bounded regression. |

The remaining documents preserve the sequence of experiments. Their older
version descriptions are historical, including local GELab/Ollama settings,
withdrawn keypad Type extensions and batches described as running at the time.
They are not today's defaults. The latest state is in the documents above and
`agent_config.json` (v35;25 offline checks, assessment disabled, measured
infrastructure repair; Timer/Clipboard comparison still failed).
The optional guided_config.json enables v36 procedures; 28 offline checks pass,
with no measured live guided result yet.

`PROJECT_DECISIONS.md`, `AGENT_DESIGN_DECISIONS.md` and `MATERIAL_REVIEW.md` are
append-only decision/source histories. `TRAJECTORY_FAILURE_ANALYSIS.md` retains
the original local-model v10 review. `HISTORICAL_SETUP.md` retains that original
environment record. `AUTOGLM_COMPLETION_REPAIR.md` preserves stopping repairs
and their actual outcomes.

References to `runs/`, `.review/` and `course_content/` in historical documents
point to the original local archive, which is not shipped in Git. The public
approved evidence subset, aggregate reports and source manifest provide portable evidence without pretending
to contain every screenshot or recording. Course materials themselves are not
redistributed.
