# Making changes

Use English, short functions, concise docstrings and comments explaining tricky
logic. Keep one agent and one explicit step loop. Read
[AGENT_WALKTHROUGH.md](docs/AGENT_WALKTHROUGH.md) before changing the control flow.

## Where the boundaries are

- The model chooses each allowed GUI action from current observations.
- The adapter parses pseudo-calls as data, validates arguments and executes once.
- Official reset/setup may prepare an instance; it must not complete the task.
- Model finish and official verifier outcome are recorded separately.
- API errors, action validation errors, environment errors and task failures are
  distinct. Do not turn any of them into an invented success.
- Do not feed the verifier result into the model, compute its next task action,
  replay a fixed sequence or execute model-generated code.

## Small experiment workflow

1. Read the actual failed trajectory: original input, raw reply, checked action,
   freshness, actual effect and final verification. Record the first causal error.
2. Cite the official source or course principle behind a proposed change in
   `docs/AGENT_DESIGN_DECISIONS.md`. Keep the change small and explain its limits.
3. Run the offline adapter checks. Then run one bounded trial on the affected task.
4. Stop and diagnose if that trial fails. Do not launch unchanged repeats.
5. After a clean regression, evaluate three seeds with frozen code/configuration.
   Keep all failures and mark manual interaction. Report the version and sample size.

Never edit runtime code or prompts while a recorded batch is active. Every run
already snapshots its settings and runtime sources; preserve those originals.
Update `docs/PROJECT_DECISIONS.md`, `docs/AGENT_DESIGN_DECISIONS.md` and
`docs/MATERIAL_REVIEW.md` as decisions and source reviews change.

## Local data and dependencies

Install only through `.venv\Scripts\python.exe -m pip`. Android World is pinned
separately by commit; retain its upstream license. Do not commit `.env`, API keys,
virtual environments, emulator images, APKs or temporary files. Full run evidence
is local; a result export must identify the original run IDs and included files.

Timer and Clipboard are currently unresolved model failures. Do not publish
their entry points or parser checks as evidence of successful completion.
