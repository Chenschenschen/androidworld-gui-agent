# Medium and hard tasks: learning trials, 8 October 2026

This log covers the stage after the warm-ups: `SimpleCalendarAddOneEvent`
(medium, 17 reference steps) and `OsmAndTrack` (hard, 60 reference steps),
plus a fresh-machine `ContactsAddContact` reproduction. Learning trials find
problems; they are not the final evaluation (see
[FINAL_EVALUATION.md](FINAL_EVALUATION.md)). Every trial is kept, including
infrastructure failures. Each failure was diagnosed from its trajectory before
the next run, following [AGENTS.md](../AGENTS.md).

Machine: Windows 10, Intel Core i5-1135G7 (Iris Xe, no discrete GPU), 16 GB RAM.
Emulator: `AndroidWorldAvd`, Pixel 6, API 33 Google APIs x86_64 image,
WHPX acceleration. Rendering: windowed host GPU (trials 1-3), software
`swiftshader_indirect` (trials 4-16), headless host GPU (`-gpu host -no-window`, from trial 17 and the final evaluation). Model: hosted `autoglm-phone-multilingual` (Z.ai),
temperature 0. Task seeds generate the task instance; see each `task.json`.

## Trial log

| # | Run ID | Version | Task, seed | Outcome | Cause | Change made |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `trial_ContactsAddContact_20261008T105024_701006Z` | v30 | Contacts, 42 | Setup error before any model call | First Contacts launch on a fresh emulator: `uiautomator dump` briefly returned `ERROR: null root node`; the strict fresh-XML adapter raised and aborted Android World's own 10-second wait loop | `android_compat.py` retries an unconfirmed dump up to three times; still never reads an unconfirmed file |
| 2 | `trial_ContactsAddContact_20261008T105438_871304Z` | v30 | Contacts, 42 | **Clean PASS**, 12 steps, 140 s | Fresh-machine reproduction of the teammate's v28 result | None |
| 3 | `trial_SimpleCalendarAddOneEvent_20261008T110130_988608Z` | v30 | Calendar, 42 | FAIL, `control_no_progress` after 4 steps | **Infrastructure:** every screenshot was all black (max pixel 0). `adb screencap` was black too; the emulator log repeated `glReadPixels ... error 0x506`. The model reasoned about a "black loading screen" and waited | Emulator restarted with `-gpu swiftshader_indirect`; v31 stops on an all-black frame as `rendering_infrastructure_error` |
| 4 | `trial_SimpleCalendarAddOneEvent_20261008T110618_405933Z` | v30 | Calendar, 42 | Validation error at step 1; recording invalid | The model's `Launch` used a Chinese translation of "Simple Calendar Pro", also after the correction listing the allowed value. Separately the recorder's stop timed out once (not reproducible in four manual tests; the run is correctly marked invalid) | v31 `launch_name()` (see below) |
| 5 | `trial_SimpleCalendarAddOneEvent_20261008T111150_520085Z` | v31 (alias draft) | Calendar, 42 | Validation error at step 1 | A *different* Chinese translation ("Simple Calendar Professional Edition"). A per-name alias table cannot keep up | Alias table replaced by a general rule: a non-Latin Launch name resolves only when exactly one app is allowed |
| 6 | `trial_SimpleCalendarAddOneEvent_20261008T111334_367105Z` | v31 | Calendar, 42 | **Clean PASS**, 20 steps, 149 s | Title, description, date (18 Oct), 00:00 start and 45-minute duration entered and saved | None |
| 7 | `trial_OsmAndTrack_20261008T111626_419084Z` | v31 | OsmAnd, 43 (2 waypoints) | FAIL, `control_no_progress` after 6 steps; recording invalid | Opened Menu > Plan a route > Create new route, then tapped **Add** expecting a search dialog. In OsmAnd, Add places a point at the centre crosshair, which was in the Gulf of Guinea (default world view). The first Add worked (`points: 1`, verified afterwards), but the counter and dot appeared after the observation; repeated Adds at the same spot add nothing, so the cycle stop ended the run. Separately the device recorder ended before the run did (`kill -2` found no process) | v32 recorder polling (below); OsmAnd knowledge investigated manually (next section) |
| 8 | `eval_batch_20261008T113903_850432Z` (3 runs) | v32 | OsmAnd, 42/43/44 | 0/3; seed 43 recording-invalid | Same strategy in every run: Menu > Plan a route > Create new route, then repeated **Add** on the default world view until the cycle stop (6 steps). In all three runs the recorder ended right after the Launch action; v32 replaced the clip for seeds 42 and 44, but for seed 43 no clip had been written | Kept as a learning record only; superseded as baseline because recording was affected |
| 9 | `trial_OsmAndTrack_20261008T114612_032845Z` | v32 | OsmAnd, 44 | FAIL, same Add cycle | Diagnostic run with the device log cleared first. adbd logged `host-34: connection terminated` at the moment the recorder ended; the console logged `Failed to execute ADB command (try 1 of 3): ... am start -W -n net.osmand/...` | **Root cause:** Android World launches with a 5 s timeout; the cold OsmAnd start was slower, and android_env's retry runs `adb kill-server`, dropping the recorder's ADB connection. v33 launches with a 30 s timeout |
| 10 | `eval_batch_20261008T115318_201667Z` (3 runs) | v33 | OsmAnd, 42/43/44, no Skill | 0/3; seed 42 recording-invalid | Launch fix confirmed (no launch timeout). Seed 42 searched by name but saved a Favorite, then looped for 66 steps (search "Balzers" > raise radius > clear > retype) until the 75th step; a slow `input text` then timed out and android_env's `adb kill-server` ended the recorder. Seeds 43/44: the Add cycle | v34 keeps the ADB server on retries (`keep_adb_server`) |
| 11 | `eval_batch_20261008T121911_015516Z` (stopped) | v34 | OsmAnd, 42, no Skill | Recording-invalid after 1 step; batch stopped by us during seed 43 | The recorder's stderr: `unable to configure video/avc codec at 540x1200 (err=-38)`. The PID existed briefly, so the old readiness check released GUI actions before the encoder had failed | v35 confirms each clip survives start-up for 1.5 s, else starts a new one (up to three times). Verified by forcing an impossible size on the first clip: a logged note, then a valid second clip |
| 12 | `trial_OsmAndTrack_20261008T122441_689821Z` (batch stopped) | v35 | OsmAnd, 42, no Skill | FAIL after 3 steps, valid recording | Recorder fix confirmed. The cold OsmAnd start showed its logo for several seconds; the model correctly chose Wait twice, and the v29 cycle stop treated two unchanged Waits as no progress | v36: unchanged Waits stop only after five in a row; other actions keep the v29 rule. Offline check: `test_waiting_on_loading_screen_is_bounded_separately` |
| 13 | `eval_batch_20261008T122658_094153Z` (3 runs) | v36 | OsmAnd, 42/43/44, no Skill | 0/3, all recordings valid | Seeds 42 (8 steps) and 43 (10 steps) ended in no-progress cycles. Seed 44 searched "Schaan, Liechtenstein" and `input text Liechtenstein` timed out twice at 10 s: OsmAnd searches on every typed character | v37: 60 s per typed word. The batch is superseded as baseline because one run ended on infrastructure |
| 14 | `eval_batch_20261008T123320_399123Z` (stopped) | v36 | Final batch, Contacts 42 | Runner error | Stopped by us to apply v37 before any OsmAnd run, so that all final runs share one version | None |
| 15 | `trial_OsmAndTrack_20261008T123559_848568Z` | v37 | OsmAnd, held-out seed 8 (Planken, Rotenboden), Skill | FAIL after 6 Waits | The cold OsmAnd start under software rendering showed its logo for over 40 s | v38: up to ten unchanged Waits |
| 16 | `trial_OsmAndTrack_20261008T123847_459399Z` | v38 | OsmAnd, held-out seed 8, Skill | Execution error at step 13 | Passed the splash after ten Waits and opened search, but `input text Planken,` timed out twice at 60 s: software rendering made OsmAnd too slow | Environment: headless host-GPU emulator (`-gpu host -no-window`). Typing "Planken" then took 2 s; a 3-minute probe produced 302 screenshots with none black |
| 17 | `trial_OsmAndTrack_20261008T125841_015970Z` | v38, headless host GPU | OsmAnd, held-out seed 8, Skill | FAIL, HTTP 400 at step 89 | Environment fixed: one Wait past the splash, fast typing. The model typed the task value "Planken, Liechtenstein" literally despite the Skill, found only the country and repeated a 4-action block 21 times; at 22,301 prompt tokens the provider answered "Prompt exceeds max length" | v39: history window (goal turn + latest 19 turns); stop when a 2-6 action block repeats three times (replayed offline: would stop this run before step 14 and trial 10's seed 42 before step 39, and leaves the passing Calendar/Contacts runs unchanged); the Skill lists each waypoint's search term derived from the task input |
| 18 | `trial_OsmAndTrack_20261008T131512_061545Z` | v39 | OsmAnd, held-out seed 8, Skill | Stopped after 11 steps (long-cycle stop worked) | Still typed "Planken, Liechtenstein": the system-prompt Skill was not followed | v40: each step's user message restates the search terms (D2 status bar) |
| 19 | `trial_OsmAndTrack_20261008T131754_294156Z` | v40 | OsmAnd, held-out seed 8, Skill | Stopped after 10 steps | Typed "Planken" (reminder followed), but on the empty result tapped SHOW ON MAP and zoomed | v41: the reminder states the empty-search rule |
| 20 | `trial_OsmAndTrack_20261008T132037_725440Z` | v41 | OsmAnd, held-out seed 8, Skill | Stopped at the third INCREASE SEARCH RADIUS | The model followed the rule (5 -> 10 -> 20 mi), but the label change was invisible at 64x128 (difference 0.0002), so three identical "ineffective" taps triggered the v29 stop. Recorded ineffective taps changed 0-8 full-resolution pixels; label changes 296-1373 | v42: more than 50 changed full-resolution pixels count as an effect. A GUI-tree alternative was rejected: one OsmAnd dump took 15 s |
## Changes and why they sit in that layer

- **Fresh XML retry (program layer).** The failure was a transient device
  state, not a model decision. The retry is bounded (three attempts, 1 s apart)
  and keeps the original guarantee that a stale XML file is never returned.
  Offline check: `test_fresh_xml_retries_transient_null_root`.
- **Black-frame guard (program layer).** An all-zero frame cannot come from a
  working display, because the status bar always renders. Treating it as an
  observation would turn an infrastructure fault into a fake model failure in
  the results. Offline check: `test_black_frame_is_infrastructure_error`.
- **Launch name resolution (program layer, mirrors upstream).** Open-AutoGLM
  resolves model Launch names through an alias table; ours was stricter than
  upstream. Repeating the allowed value in the correction prompt did not help
  (trial 4), so this is not an instruction-layer fix (D5 pp.41-42: a rule the
  model can be talked out of belongs in code). The rule never guesses between
  several apps and never accepts an unlisted Latin-script name. Offline check:
  `test_runner_tasks_have_rules_and_launch_names`.
- **Recorder early exit (program layer, v32).** Two runs lost their video
  (trial 4: host adb shell did not return after SIGINT; trial 7: the device
  recorder ended early). Neither reproduced in manual tests (four SIGINT timing
  tests, a 90-second screenshot-load probe). The recorder now polls each second;
  an early exit pulls the clip and starts the next one, and a stuck host shell is
  closed after the device clip is complete. Both cases write a `RECORDING NOTE`
  to the trajectory. GUI actions already wait while a clip rolls over, so at most
  about one second is unrecorded. Verified live by killing the device recorder
  mid-run: two valid clips, a logged note and no recorder error.
- **Launch timeout (program layer, v33).** Trial 9 found the actual cause of
  the recorder deaths: an expired 5-second `am start -W` made android_env
  restart the ADB server. Launching with a 30-second timeout removes the
  trigger; the v32 polling stays as a safety net. Offline check:
  `test_launch_waits_for_slow_cold_start`.
- **Keep the ADB server (program layer, v34).** Trial 10 showed that any slow
  command can trigger android_env's `adb kill-server` retry, not only launches.
  `android_compat.keep_adb_server()` keeps the retry but replaces the server
  restart with a 2-second pause. Offline check: `test_adb_retry_keeps_server`.
- **Recorder start-up check (program layer, v35).** See trial 11.

## How OsmAndTrack can actually be completed (manual exploration)

After trial 7 we operated the app by hand through ADB (no model) on the test
emulator, to learn what the model was missing. The resulting track passed the
**official** matcher `osmand._track_matches` for Oberplanken then Malbun
(saved points within 0.00003 degrees of the targets; tolerance 0.001).

1. OsmAnd opens on a default world view (West Africa). The search radius is
   centred on the map, so the first search ("Oberplanken") finds nothing until
   **INCREASE SEARCH RADIUS** is tapped several times (three here).
2. Results contain same-name distractors (aerialway stations, streets). Tapping
   the village row can open a street list *inside* that village; the row
   `SHOW (place) ON THE MAP` at the top selects the place itself.
3. First waypoint: on the place card choose **Actions > Plan a route**. This
   starts a route whose point 1 is the place (`points: 1`).
4. Each further waypoint: in Plan a route tap the **Search** (magnifier) button,
   clear the old query, type the name, select the place as above, then press
   **Back** until the Plan a route panel returns. The map stays centred on the
   place (the panel shows the distance from the previous point). Tap **Add**:
   it adds the centre-crosshair point and `points: N` increases.
5. When `points` equals the number of waypoints, tap **Done**. A message
   "GPX file saved to ..." confirms the saved track, which the verifier reads.

This is application knowledge (D5 pp.41-42: "a missing fact -> knowledge"),
not a model capability gap. It motivates the measured improvement in
[IMPROVEMENT_OSMAND.md](IMPROVEMENT_OSMAND.md).
