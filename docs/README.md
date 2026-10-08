# Documentation map

Start here rather than reading the design history from beginning to end.

| Current document | Purpose |
| --- | --- |
| [SETUP.md](SETUP.md) | Fresh Windows/Python/Android installation. |
| [RUNNING_TASKS.md](RUNNING_TASKS.md) | Independent execution and evidence fields. |
| [AGENT_WALKTHROUGH.md](AGENT_WALKTHROUGH.md) | Explain the current program's flow. |
| [AUTOGLM_API.md](AUTOGLM_API.md) | Z.ai endpoint, model selection and native protocol. |
| [WARMUP_RESULTS.md](WARMUP_RESULTS.md) | Recorded task gates and unresolved errors. |
| [evidence/README.md](evidence/README.md) | Aggregate reports; screenshots, inputs and full traces/videos stay local. |
| [COURSE_AND_UPSTREAM_REVIEW.md](COURSE_AND_UPSTREAM_REVIEW.md) | D1–D4 principles, pinned official sources and repair ledger. |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | Rules for a justified change and bounded regression. |

The remaining documents preserve the sequence of experiments. Their older
version descriptions are historical, including local GELab/Ollama settings,
withdrawn keypad Type extensions and batches described as running at the time.
They are not today's defaults. The latest state is in the documents above and
`agent_config.json` (v29; 16 offline checks, no live v29 success claim).

`PROJECT_DECISIONS.md`, `AGENT_DESIGN_DECISIONS.md` and `MATERIAL_REVIEW.md` are
append-only decision/source histories. `TRAJECTORY_FAILURE_ANALYSIS.md` retains
the original local-model v10 review. `HISTORICAL_SETUP.md` retains that original
environment record. `AUTOGLM_COMPLETION_REPAIR.md` preserves stopping repairs
and their actual outcomes.

References to `runs/`, `.review/` and `course_content/` in historical documents
point to the original local archive, which is not shipped in Git. The public
aggregate reports and source manifest provide a portable summary without pretending
to contain every screenshot or recording. Course materials themselves are not
redistributed.
