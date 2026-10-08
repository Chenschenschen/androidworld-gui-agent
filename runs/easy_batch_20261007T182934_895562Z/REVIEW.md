# Manual interaction reported during this batch

The user confirmed they were interacting with the emulator during these trials.
The exact affected time range is unknown. Preserve all original summaries,
videos and traces, but **exclude this batch from unattended three-repeat
capability claims**. Original automatic `manual_intervention: false` and
`evaluation_valid: true` fields do not reflect this subsequently reported fact.

Camera seed 42 specifically changed from Camera to Recents during model inference;
the freshness guard correctly stopped its pending shutter action. It was not a
spontaneous model action or a false freshness stop. Other observed outcomes remain
diagnostic evidence but cannot establish the requested repeatability.

The source-hash check stops scheduling after the active trial, without interrupting
its recording/verifier cleanup. A fresh frozen batch will run with the emulator
left untouched. This changes the evaluation conditions, not the model settings.
