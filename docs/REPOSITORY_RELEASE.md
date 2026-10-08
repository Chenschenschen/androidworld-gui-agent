# Repository preparation, 8 October 2026

Prepared the existing v29 implementation for
https://github.com/Chenschenschen/androidworld-gui-agent at the user's request.
No runtime source, model contract, sampling or task-control behavior changed
during this publication stage. No model calls or task trials were run.

Added a fresh-checkout README, current Windows setup guide, `.env.example`,
contribution/documentation guides, Apache 2.0 license and upstream attribution.
The original setup record remains in HISTORICAL_SETUP.md. Android World is a
separate checkout pinned to 2dfc5ca3dc590efe9c72ce768f2b04182f2f75c7; `.venv`,
`.env`, `.tools`, `.review`, course originals and full local runs are ignored.

The public aggregate export covers 12 original trial outcomes across four
selected batches, including failures. It contains only whitelisted outcome
fields, not screenshots, task inputs, model replies, diagnostic logs or videos.
Original complete evidence and the earlier private export remain local.

Automatic approval review rejected the first proposed push because its raw
screenshots and diagnostic artifacts could contain non-public data. Those files
were removed from the unpublished root commit before retrying with the reduced
publication scope. The original local evidence was preserved.

Subsequent user authorization, 8 October: the user explicitly approved uploading
the previously blocked files. Restore the original 156-file evidence subset and
its SHA256 export manifest in a new commit, including selected test-emulator
screenshots, task metadata and diagnostic trajectories. Credentials and the
remaining excluded archives stay local. Check every exported file against the
original and scan the exact tracked payload for the project API key before push.
No runtime behavior, model call or task trial changes in this publication step.

Validation before publication:

- All 16 offline adapter checks passed.
- `pip check` found no broken requirements in the project environment.
- A fresh dependency-resolution dry run with `--ignore-installed` resolved the
  complete lock and local pinned Android World package without installing them.
- The exact staged files contained no project API key or raw evidence payload;
  excluded folders were absent. Aggregate fields match the original results.
  Current reader-navigation links were checked.

These checks validate packaging and existing offline behavior. They do not
establish fresh-machine emulator compatibility or successful live v29 trials.
Recorded task-specific results remain Wi-Fi/Camera v20 and Contacts v28 each
3/3 clean, with Timer/Clipboard unresolved. Read WARMUP_RESULTS.md.

Post-push fresh-clone check found one fixture fault: the XML pairing test assumed
the ignored .tools/tmp directory already existed. Its original traceback was
preserved locally. The test now creates its own temporary parent before use;
the agent runtime is unchanged. This check uses the installed project
dependencies and no API/emulator calls, not a new-machine live evaluation.
