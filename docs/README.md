# Documentation map

Start here rather than reading the design history from beginning to end.

| Current document | Purpose |
| --- | --- |
| [TEAM_FINAL_EVALUATION.md](TEAM_FINAL_EVALUATION.md) | **Team final evaluation**: one agent, seven tasks, three runs each, one frozen version (v65), 18/21, with the three failures analysed. |
| [RUN_LOG.md](RUN_LOG.md) | **Run log of the final evaluation**: one card per task with the three runs side by side, in the course log fields (D1 p.49) plus a note, the recording clips, a trajectory link and the agent version. |
| [MARKOR_SHARE_V66.md](MARKOR_SHARE_V66.md) | **Follow-up after the freeze (v66)**: the Markor Skill shares the note itself (Share > Plain Text) instead of typing its text again; practice log, 3 recorded runs (2/3, one grounding failure) and v65/v66 comparison. |
| [../presentation/Team_Briefing_AndroidWorld_Agent.docx](../presentation/Team_Briefing_AndroidWorld_Agent.docx) | **Start here if you are new**: the story of the project and a slide-by-slide explanation of the presentation. |
| [../presentation/](../presentation/) | Final presentation: editable PowerPoint with embedded demo videos, speaker script (SCRIPT.md), Q&A preparation (QA.md), and the scripts and data that built it. |
| [TEAM_AGENT.md](TEAM_AGENT.md) | How the team agent was assembled from the three contributions, and its practice runs. |
| [FINAL_EVALUATION.md](FINAL_EVALUATION.md) | Earlier evaluation of Jia's branch: three tasks, three runs each (v42). |
| [IMPROVEMENT_OSMAND.md](IMPROVEMENT_OSMAND.md) | Documented improvement with before/after results (OsmAnd Skill), plus the additional v61 experiment on the slide's task (2/3 vs 0/3). |
| [FINAL_FAILURE_ANALYSIS.md](FINAL_FAILURE_ANALYSIS.md) | Step-by-step failure analysis and failure classes. |
| [MEDIUM_HARD_TRIALS.md](MEDIUM_HARD_TRIALS.md) | Every learning trial from v30 to v61 with cause and fix. |
| [SETUP.md](SETUP.md) | Fresh Windows/Python/Android installation. |
| [RUNNING_TASKS.md](RUNNING_TASKS.md) | Independent execution and evidence fields. |
| [AGENT_WALKTHROUGH.md](AGENT_WALKTHROUGH.md) | Explain the current program's flow. |
| [AUTOGLM_API.md](AUTOGLM_API.md) | Z.ai endpoint, model selection and native protocol. |
| [WARMUP_RESULTS.md](WARMUP_RESULTS.md) | Recorded task gates and unresolved errors. |
| [evidence/README.md](evidence/README.md) | Aggregate reports and the approved metadata/trajectory/screenshot subset. |
| [COURSE_AND_UPSTREAM_REVIEW.md](COURSE_AND_UPSTREAM_REVIEW.md) | D1–D4 principles, pinned official sources and repair ledger. |
| [../CONTRIBUTING.md](../CONTRIBUTING.md) | Rules for a justified change and bounded regression. |

The remaining documents preserve the sequence of experiments. Their older
version descriptions are historical, including local GELab/Ollama settings,
withdrawn keypad Type extensions and batches described as running at the time.
They are not today's defaults. The latest state is in the documents above and
`agent_config.json` (v42; 29 offline checks; final evaluation in FINAL_EVALUATION.md).

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
