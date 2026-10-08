# Camera self-run diagnosis,8 October2026

Original trial_CameraTakePhoto_20261008T190644_339849Z: valid official FAIL0,
one GUI action/three model calls, no finish,24.219 seconds. API succeeded and
recording_complete.mp4 exists. Original evidence remains unchanged.

Step1 model tapped the actual Camera Home icon. Next observation still showed
Home; model proposed the same icon tap. Freshness0 showed the Camera launch
logo, so this unexecuted tap was discarded. Reobserved model called the splash
logo a shutter and proposed[499,501]. Freshness1 showed the actual first-use
Remember photo locations? page with NEXT, so this tap was also discarded and
the one-reobservation bound stopped the run. Neither proposed step2 tap executed.
This combines delayed application startup, a model splash/control grounding
error, and a bounded recovery exhausted by successive legitimate transitions.
It is not the earlier API400 issue or proof of virtual-camera hardware failure.

The configured checked GUI-label supplement omitted com.android.camera2, even
though the observed current activity had that package. Proposed repair uses
the existing XML capture/geometry/settling/read-recovery path for Camera as for
Settings, Clock, SMS and Files. Supply actual onboarding controls and shutter
labels from observations; do not prescribe NEXT/shutter coordinates or disable
the freshness check. Model still chooses every action, including Wait/finish.
Keep sampling, completion criteria, step and retry budgets unchanged. Read-only
validation and offline checks precede the user's changed run. No task recipe,
photo filesystem creation, forced finish or GUI execution replay is introduced.

Pinned CameraApp setup grants permissions, launches Camera and attempts to click
NEXT during first-use preparation, then closes the app. The runner accepts an
existing installed app/snapshot without repeating that setup; the actual trial
still encountered onboarding. Its precise cached-state origin is not proven.
CameraTakePhoto initializes by clearing only official test photo/video
directories and records initial files; success requires exactly one new photo
in the official folder. Private app snapshot can restore first-use state, so
first-use controls may still need actual observed agent navigation, not success.

v57 enables only com.android.camera2 in the existing supplemental package list.
Read-only dump .tools/camera_readcheck_20261008.xml from the actual emulator
parsed successfully: Remember photo locations?, checked location option and
NEXT at its observed centre. No GUI action or model request occurred in this
check. All43 offline checks pass before the user's changed retry. No live v57
task success is claimed. Same self-run command:

```powershell
.\.venv\Scripts\python.exe -X utf8 run_task.py --task CameraTakePhoto --seed 42 --config general_config.json
```
