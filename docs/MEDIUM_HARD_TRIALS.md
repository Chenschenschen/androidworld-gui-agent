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
| 21 | `trial_OsmAndTrack_20261008T132512_975097Z` | v42 (frozen) | OsmAnd, held-out seed 8, Skill | Stopped after 18 steps; **first waypoint added to the route** | Steps 1-9 followed the Skill: typed "Planken", widened the radius three times, chose the village, Actions > Plan a route (`points: 1`). In Plan a route the Search button sits lower (below the title bar); the model reused the main-map coordinate, hit the title bar, and then described search results that were not on screen while tapping the empty map six times (grounding error plus hallucinated observation) | None: version frozen for the evaluation, as decided before this run |
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


## After the final evaluation: v43-v48 (exploration, not evaluated)

The final evaluation stays on v42. Afterwards we tried to make the hard task
pass at least once, following the failure analysis, with program-layer checks
and a stronger per-step reminder. Every version was tested only on practice
seeds outside the evaluation set (two-waypoint instances 1, 2, 3, 8, 14).
**Result: 0/10 practice runs passed**; two runs added the first waypoint
correctly (the village, `points: 1`), a third added a same-name residential
area, and none added a second point. We stopped here by
decision; the code on the branch head is this unevaluated v48, and the
evaluated code is tagged `final-eval-v42`.

| # | Run ID | Version | Task, seed | Outcome | Cause | Change made |
| --- | --- | --- | --- | --- | --- | --- |
| 22 | `trial_OsmAndTrack_20261008T153131_718229Z` | v43 | OsmAnd, practice seed 8 (Planken, Rotenboden), Skill | FAIL, `control_no_progress` after 11 steps | Test of v43 (focus check for Type without a GUI tree; reminder rules). No Type was refused. Typed "Planken" (step 4) and tapped INCREASE SEARCH RADIUS twice from the default world view (steps 5-6; the first step-6 reply repeated "Wait, the instruction says ..." until it was cut off, `Truncated model reply`). Then alternated Type "Planken, Liechtenstein" (steps 7, 9, 11; "returned only 'Liechtenstein'") and "Planken" (steps 8, 10) until the cycle stop at step 12 | v44: the Skill and reminder start with the task's region: search "Liechtenstein" (text after the comma in the task input), open its row, press Back. Manual check: "Planken" is then the first result (village) without widening the radius |
| 23 | `trial_OsmAndTrack_20261008T153947_450189Z` | v44 | OsmAnd, practice seed 8, Skill | FAIL, `control_no_progress` after 15 steps; **first waypoint added to the route** | Skipped the region step: typed "Planken" (step 5) and tapped SHOW ON MAP while the search was still loading (step 6); the map stayed on West Africa, but the model said "The map has moved to the location of Planken". After Back it widened the radius three times (steps 8-10), chose the "Village" row (step 11) and Actions > Plan a route (`points: 1`, step 14). It then tapped the route panel's Add "to search for and add the next waypoint" (steps 14-15) until the cycle stop at the third Add (step 16) | v45: the reminder states that Add never searches (it only adds the map centre) and lists the order for each later waypoint |
| 24 | `trial_OsmAndTrack_20261008T154334_136129Z` | v45 | OsmAnd, practice seed 8, Skill | FAIL, `control_no_progress` after 19 steps | Skipped the region step; tapped SHOW ON MAP on the loading "Planken" search (step 5). With the map on West Africa it said "The map is centered on Planken" and searched the second waypoint before the first was in a route (step 6). The focus check refused one Type (step 7); the model tapped the field, typed "Rotenboden", widened the radius three times and chose the "Rotenboden" (Village) row (step 12). It then alternated the place card's star Add and Save in the Add/Edit Favorite dialog (steps 13-19; Save executed three times, the fourth Save at step 20 was stopped by the cycle stop) | v46: the status line carries route progress from the last "points: N" the model reported (kept by code) and names the next step; a click is refused while the reply describes the Add/Edit Favorite dialog and Save |
| 25 | `trial_OsmAndTrack_20261008T154913_986857Z` | v46 | OsmAnd, practice seed 8, Skill | FAIL, `control_no_progress` after 14 steps; **first waypoint added to the route** | Skipped the region step; tapped SHOW ON MAP on the loading "Planken" search (step 5), then widened the radius three times (steps 7-9), chose the "Village" row (step 10) and Actions > Plan a route (`points: 1`, step 13). From step 14 the status line read "Route progress: 1 of 2. Next waypoint: 2. "Rotenboden"", but the model tapped the route panel's Add "to open the search panel and add "Rotenboden"" (steps 13-14) until the cycle stop at the third Add (step 15). No Favorite dialog appeared, so the v46 guard did not fire | v47: the route panel's Add is refused until the next waypoint's term has been typed since the route count last changed |
| 26 | `trial_OsmAndTrack_20261008T155302_951757Z` | v47 | OsmAnd, practice seed 8, Skill | FAIL, `control_no_progress` after 18 steps | Skipped the region step; tapped the SHOW ON MAP row on the loading "Planken" search twice (steps 5-6), then "The map is centered on Burkina Faso, not Planken" (step 7). After Back and one radius increase (step 8) it typed the full "Planken, Liechtenstein" (steps 10 and 13), got only the country row, and tapped the INCREASE SEARCH RADIUS position at steps 11 and 14-18, each reply saying the place was "still not found". Once the list grew, these taps opened the "Liechtensteiner Straße" street row (step 17) and address 137a (step 18); at step 19 it still described the radius button and the cycle stop ended the run. No route was started, so the v47 Add guard was never reached | v48: taps on the plain SHOW ON MAP row and queries containing a comma are refused with a correction; the "SHOW <PLACE> ON THE MAP" row of a street list is unaffected |
| 27 | `eval_batch_20261008T155849_720693Z` (5 runs) | v48 | OsmAnd, practice seeds 8, 14, 1, 2, 3, Skill | 0/5; seed 14 reached `points: 1` with a same-name residential area | Each run failed differently: seed 8 alternated the refused comma query and "Planken" without widening the radius; seed 14 chose "Schaanwald (Residential area)" rather than the village and reached `points: 1`, the Add check redirected it to search, then it confused the adjacent Configure-map and Search buttons; seed 1 made the **country** "Liechtenstein" route point 1 and then cycled through the Favorite dialog without saving; seed 2 lost field focus after Clear and looped on refused Types; seed 3 kept tapping SHOW ON MAP, because a correction reply contains only the action and the text-based SHOW ON MAP check could not see it | Stopped. Each text-based rule exposed the next failure |
| 28 | probe, no model | v48 | Android World accessibility forwarder on OsmAnd | **0.2 s per GUI tree, no crash dialog** | UIAutomator dumps on OsmAnd took 17-58 s and often failed ("null root node"), so v43-v48 had to infer state from the model's words. The official forwarder (disabled since the teammates' v10 because it crashed then) returned full trees with result types ("Public transport stop", "Building") in 0.2 s | Recommended next step, not implemented: switch the observation backend to the forwarder and base the checks on the tapped element and the screen's labels |

What v43-v48 established:

- **Checks that held:** the focus check (Type refused when Android reports no
  focused text field), the comma-query check and the route-Add precondition
  each fired and redirected the model as intended.
- **Why it did not converge:** without a GUI tree the checks relied on the
  model's own description of the screen. The model rarely followed the
  region-first step, tapped SHOW ON MAP while results were still loading
  (`too_early`), and a correction reply with no text bypassed a text-based check.
- **Incident:** during a manual test we ran `pm clear net.osmand`, which also
  deleted the Liechtenstein map from OsmAnd's external storage (the app
  snapshot covers only `/data/data`). It was restored by removing the OsmAnd
  snapshot and re-running the official OsmAnd setup without the model
  (map file and snapshot verified). All practice runs listed here ran after
  the restore except row 22.

## OsmAnd-only extra experiment: v49-v61 (practice runs)

After v43-v48 we resumed with the step recommended in row 28: read OsmAnd's
GUI through the accessibility forwarder and base every check on the real
screen. This is an **additional experiment on the hard task only**; the
official three-task evaluation stays v42 (tag `final-eval-v42`). All runs
below are practice runs on seeds outside the evaluation set (8: Planken,
Rotenboden; 7: Malbun, Rotenboden, Balzers). Each run has its recording,
trajectory and summary under `runs/`. Each change was made after one run,
with an offline test that fails on the previous code.

**Result: the first verifier PASS on OsmAndTrack (row 39, v59, seed 8) and a
three-waypoint PASS (row 42, v61, seed 7).** v61 was then frozen (tag
`osmand-extra-v61`) for the evaluation in
[IMPROVEMENT_OSMAND.md](IMPROVEMENT_OSMAND.md#additional-experiment-v61-on-the-slide-instance).

| # | Run ID | Version | Seed | Outcome | Cause | Change made |
| --- | --- | --- | --- | --- | --- | --- |
| 29 | `trial_OsmAndTrack_20261008T172506_608538Z` | v49 | 8 | FAIL, `validation_error` after 4 steps | The step-5 observation was taken while OsmAnd's search spinner (`searchProgressBar`) still turned, so the list looked empty (`too_early`). The model's reply then repeated itself until the 3000-token limit (`Truncated model reply`), and its correction tapped SHOW ON MAP, which the tree check refused; two invalid replies in one step end the run | v50: an observation waits (up to 30 s) while the search spinner is on screen; keyboard keys are left out of the GUI labels |
| 30 | `trial_OsmAndTrack_20261008T173128_218463Z` | v50 | 8 | FAIL, `control_no_progress` after 24 steps; **first waypoint in the route** (`points: 1`, step 14) | On the Plan a route screen the forwarder tree contained only "Map" (four reads of the same screen; a UIAutomator dump read the route panel, Search and Done in 3 s). Without labels the model tapped the globe (Configure map) left of Search five times | v51: when the forwarder tree names at most one app control, the observation falls back to a checked UIAutomator dump; hints name Search as the second round button |
| 31 | `trial_OsmAndTrack_20261008T174254_588486Z` | v51 | 8 | FAIL, `control_no_progress` after 26 steps | The forwarder marks only the unlabeled container of a row, of INCREASE SEARCH RADIUS and of Actions clickable, so these labels had no tap centre and the model guessed coordinates for 15 steps. The row check also refused the "Liechtenstein (Country)" row that the Skill's region step asked for | v52: every labelled element gets an observed tap centre; the row check accepts the Country row |
| 32 | `trial_OsmAndTrack_20261008T175142_038025Z` | v52 | 8 | FAIL, `control_no_progress` after 20 steps | Widened the radius once, then searched "Liechtenstein". The fixed text of the SHOW ON MAP refusal ("tap INCREASE SEARCH RADIUS") sent it away from the Country row; it then retyped "Planken" six times, and each retype resets the radius. Fifth fix in a row that exposed a new failure elsewhere | v53 (design change): the Skill procedure runs as code. Each step, `osmand_next_step` recognises the screen from the GUI tree and states the next action with its tap centre; refusals append that step. The region-first step is dropped (never completed in v44-v52); the radius is widened instead |
| 33 | `trial_OsmAndTrack_20261008T180047_905645Z` | v53 | 8 | FAIL, `control_no_progress` after 13 steps; `points: 1` at step 11 (fastest so far) | The route panel stayed unread: v51's fallback never ran, because the non-empty supplemental package list (Settings, Clock, Chrome) took the first branch. With no count the code gave no next step and the Add check could not fire; the model tapped the panel's Add three times. Our offline test had used an empty list | v54: the forwarder branch is checked first; the test uses the real configuration |
| 34 | `trial_OsmAndTrack_20261008T180506_211752Z` | v54 | 8 | FAIL, `control_no_progress` after 9 steps | The fallback now ran (24 UIAutomator reads), but UIAutomator elements carry `resource_id`, not `resource_name`. The coded procedure did not recognise the search field, the old reminder (region first) returned, and the model cleared and retyped "Planken" (radius reset) | v55: screens are recognised from either id field; the reminder drops the region step |
| 35 | `trial_OsmAndTrack_20261008T181122_526667Z` | v55 | 8 | FAIL, `control_no_progress` after 19 steps; `points: 1`, "Rotenboden" found | The code treated the typed name as proof that the map was centred on Rotenboden and said "press Back" on its street list. Back led to the panel, whose distance line read "0 ft" (centre still on Planken); the model tapped Add three times | v56: only a seen place card of the next waypoint proves the centre; no Add while the distance line reads 0 ft; a street list suggests SHOW <PLACE> ON THE MAP |
| 36 | `trial_OsmAndTrack_20261008T181934_796393Z` | v56 | 8 | FAIL, model finished at `points: 1` of 2 (`false_done`) | Rotenboden's card lay over the route panel; the code read the panel first and said "search again", and the model declared the track saved. The forwarder's own app crashed once ("keeps stopping" dialog, step 6); the model closed it | v57: the place card is recognised before the panel; `finish` is refused while the tree shows fewer route points than waypoints or the route panel is still open |
| 37 | `trial_OsmAndTrack_20261008T182624_604241Z` | v57 | 8 | FAIL, `validation_error` after 19 steps; **`points: 2` of 2** (step 19) | The model tapped Done (step 20), but the row check refused it twice: on the route panel the date "Sun 15 Oct 2023" above the title "Plan a route" formed a false result row whose span covered Done | v58: result rows are read only on the search screen |
| 38 | `trial_OsmAndTrack_20261008T183303_700087Z` | v58 | 8 | FAIL, `control_no_progress` after 19 steps | After Rotenboden's card, Back led through its street list, where the v56 order suggested SHOW <PLACE> ON THE MAP again; card and list alternated three times | v59: once the next waypoint's card was seen, the street list suggests Back |
| 39 | `trial_OsmAndTrack_20261008T184005_761386Z` | v59 | 8 | **PASS** (official verifier), 21 steps, 404 s | Search, three radius increases, Village row, Actions > Plan a route (`points: 1`); Search, Clear, "Rotenboden", Village row, SHOW ROTENBODEN ON THE MAP, Back x3, Add (`points: 2`), Done, finish. One Favorite Add and one unfocused Type were refused on the way | First pass on the hard task |
| 40 | `trial_OsmAndTrack_20261008T184737_498743Z` | v59 | 7 | FAIL, `validation_error` after 10 steps | Despite the hint "Tap Search", the model tapped the map's Route button (navigation) and searched from "Set starting point". "Malbun" lists nine same-name rows (street, stream, ski lift, hotels) before its Village row; the code only said "Wait". A manual search confirmed the Village row after one scroll | v60: rows without the waypoint's settlement row suggest one Swipe; the Route button is refused; the row refusal mentions scrolling |
| 41 | `trial_OsmAndTrack_20261008T185418_998730Z` | v60 | 7 | FAIL, `validation_error` after 19 steps; `points: 1` (Malbun) | The Route refusal and the scroll worked. On Rotenboden's card the model chose Actions > Plan a route, which starts a new route | v61: once the route has a point, Actions on a card and Plan a route in the menu are refused |
| 42 | `trial_OsmAndTrack_20261008T190133_618757Z` | v61 | 7 | **PASS**, 31 steps, 501 s, three waypoints | Same procedure with one scroll for Malbun and two later waypoints; the forwarder crash dialog appeared once (step 20) and was closed | Frozen as v61 |

Probes without the model (scripts in the session notes, outputs summarised here):

- **Plan a route screen:** the forwarder returned only "Map" in four reads,
  while `uiautomator dump` listed "points: 1", Add, Done, Search and Configure
  map in 3 s. This is why v51 keeps UIAutomator as a fallback.
- **"Malbun" search:** after three radius increases the first screen showed
  "Im Malbun" (street), a stream, a ski resort, an aerialway station and
  hotels; the Village row appeared after one scroll.

What v49-v61 established:

- **Observation was the first bottleneck.** With labels, tap centres and the
  route count read from the screen, checks no longer depend on the model's
  description; v43-v48 could only check the model's words.
- **Moving the procedure into code (v53) made progress steady.** The model
  still chooses and performs every action from the screenshot and labels, and
  it ignored the stated next step several times (Route button, a second Plan a
  route, finishing early). Code refused those specific actions.
- **Most of v54-v59 fixed our own code**, not the model: a branch order bug, an
  id field mismatch, a false result row and two ordering mistakes. Each was
  found from one recorded run and is covered by an offline test.
