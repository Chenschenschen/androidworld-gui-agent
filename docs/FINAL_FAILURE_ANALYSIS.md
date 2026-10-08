# Failure analysis: the hard task in the final evaluation

Course requirement: "an analysis of at least one failure" (Syllabus p.1), and a
failure revealed by the evaluation in the presentation. This document analyses
one run step by step, then classifies the other final-evaluation failures and
the infrastructure faults found on the way. Failure classes follow D1 p.50
(`grounding`, `too_early`, `lost_value`, `wrong_app`, `false_done`); a failure
that fits none of them is labelled "other" with a description, not forced
into a class. Fix layers follow D4 p.27 and D5 pp.41-42.

## Deep dive: OsmAndTrack, seed 42, with the Skill

Run `trial_OsmAndTrack_20261008T134852_193100Z` (v42, final batch). Goal:
"Save a track with waypoints Bendern, Liechtenstein, Balzers, Liechtenstein,
Oberplanken, Liechtenstein, Nendeln, Liechtenstein in the OsmAnd maps app in
the same order as listed." Official verifier: FAIL. Stop: bounded no-progress
rule after 17 executed steps (budget 90). Trajectory, task and summary:
[evidence/final/runs/trial_OsmAndTrack_20261008T134852_193100Z](evidence/final/runs/trial_OsmAndTrack_20261008T134852_193100Z/trajectory.txt).

| Steps | What the model saw and did | Assessment |
| --- | --- | --- |
| 1-3 | Launched OsmAnd, waited one step on the splash screen, opened Search | Correct (Skill step 1) |
| 4 | Typed `Bendern` (the search term from the Skill, not the full task text) | Correct; the baseline typed "Bendern, Liechtenstein" |
| 5-6 | On "Could not find anything" tapped SHOW ON MAP, then went back | Against the Skill's empty-search rule; recovered |
| 7-9 | INCREASE SEARCH RADIUS three times (5 -> 10 -> 20 mi), until results appeared | Correct; v42's full-resolution effect check let these legitimate repeats run |
| 10 | Reply: *"The last entry 'Bendern' ... is the correct one (Guidepost). I will tap this row"* ([screen](evidence/final/runs/trial_OsmAndTrack_20261008T134852_193100Z/step_010/observation_0/screen.png)) | **Wrong object.** A same-name signpost, although the Skill says to choose the village/hamlet/town, not a street, station or shop |
| 11-12 | Place card > Actions > Plan a route: `points: 1` ([screen](evidence/final/runs/trial_OsmAndTrack_20261008T134852_193100Z/step_013/observation_0/screen.png)) | Correct procedure, wrong point: about 300 m from the Bendern village node (0.25 mi scale bar), beyond the verifier's 0.001 degree tolerance (about 110 m) |
| 13 | Tapped Search *inside* Plan a route at the lower position | Correct (in held-out trial 21 the model had reused the main-map position) |
| 14 | Saw the old "Bendern" results ([screen](evidence/final/runs/trial_OsmAndTrack_20261008T134852_193100Z/step_014/observation_0/screen.png)); said it would clear the field, but tapped the back arrow | Grounding slip: the back arrow (top left), not Clear (top right) |
| 15 | `Type "Balzers"` | **The text went nowhere.** The search page was empty and its field unfocused (no keyboard); the Python check "is an editable field focused?" needs a GUI tree, which OsmAnd does not supply in this configuration, so it could not reject the action |
| 16-17 | Reply: *"The search results are empty for 'Balzers'. I need to increase the search radius"*, tapping where that button had been ([screen](evidence/final/runs/trial_OsmAndTrack_20261008T134852_193100Z/step_016/observation_0/screen.png): the page shows only a history entry "Guidepost Bendern" and no query) | **Hallucinated observation.** The model described the state it expected, not the screenshot; both taps hit empty space (0 changed pixels) |
| 18 | Third identical tap without effect: stopped (`control_no_progress`) | The harness bounded the failure after 17 steps instead of 90 |

### Causes, by layer

| Cause | Course class | Layer where it belongs (D4 p.27, D5 pp.41-42) | Status |
| --- | --- | --- | --- |
| Same-name distractor chosen although the Skill states the rule | other: wrong object (knowledge given, not applied) | Instruction layer did not hold; a program check could reject a non-settlement result for this task | Not fixed |
| Back arrow instead of Clear (step 14) | `grounding` | Perception/pointing; the model's own decision | Not fixed |
| Typing into an unfocused field passed silently (step 15) | `grounding` (action landed on nothing) | **Program layer**: Python could verify that the typed text appears (or tap the field first) before reporting success; the existing focus check depends on a GUI tree that is too slow for OsmAnd (one dump took 15 s) | Not fixed; documented |
| Results described that were not on screen (steps 16-17) | other: hallucinated observation | Model/perception; D1 p.37 "the most dangerous ... because it is silent" applies to observations too. Instructions do not reliably fix it | Bounded by the no-progress stop |

What worked: the Skill's facts changed the first nine steps from the baseline
behaviour (Add on an empty route, or full-text search) to the correct search
procedure; the v42 effect check allowed the legitimate radius repeats; the v39
cycle stop ended an unproductive run early; no false completion occurred.

## The other final-evaluation failures

| Run | What happened | Class |
| --- | --- | --- |
| OsmAnd seed 43, Skill (`..._135208_398127Z`) | Typed "Oberplanken", widened the radius three times, opened the hamlet, then tapped the place card's **Add** (a Favorite) and saved it three times ([screen](evidence/final/runs/trial_OsmAndTrack_20261008T135208_398127Z/step_009/observation_0/screen.png)). The Skill states this exact fact | other: wrong feature (knowledge given, not applied) |
| OsmAnd seed 44, Skill (`..._135454_519070Z`) | Typed "Schaan", widened the radius once, then alternated searches for the second and third waypoints, each with one radius increase | other: search strategy (did not finish the first waypoint) |
| OsmAnd seeds 42-44, no Skill (baseline batch) | Plan a route > Add on the empty world view ([screen](evidence/final/runs/trial_OsmAndTrack_20261008T133145_104938Z/step_007/observation_0/screen.png)), or full-text search finding only the country | other: missing app knowledge |

Contacts (3/3) and Calendar (3/3) had no failures in the final batch. Earlier
Calendar learning trials failed only through infrastructure (below).

**Observation about the taxonomy.** For the easy and medium tasks the five GUI
classes were sufficient during development (for example `false_done` and
`lost_value` in the teammates' warm-up analysis). For a 60-step task in a
complex app, most failures were about *what* to do (wrong feature, wrong
object, weak plan), not *where* to tap. We report them as such.

## Infrastructure faults found before the final batch

These are not model failures, but each would have produced a wrong or invalid
result if left in place. Full evidence: [MEDIUM_HARD_TRIALS.md](MEDIUM_HARD_TRIALS.md).

| Symptom | Root cause found | Fix |
| --- | --- | --- |
| Model "waited for loading" on a black screen | Host-GPU emulator returned all-black frames (`glReadPixels` 0x506) | Headless host-GPU emulator; all-black frames stop the run as `rendering_infrastructure_error` |
| Recorder died after app launches | android_env ran `adb kill-server` before retrying a timed-out command | Keep the server on retries; 30 s launch timeout |
| Empty clip at start | Encoder failed to configure after the PID was visible | Confirm the recorder survives start-up |
| Run stopped on a splash screen | Two unchanged Waits counted as no progress | Bound Waits separately (ten) |
| Typing one word took over 60 s | Software rendering made OsmAnd's per-character search too slow | Headless host GPU (2 s) |
| HTTP 400 "Prompt exceeds max length" | Full history after 88 steps (22k tokens) | Goal turn plus latest 19 turns |
| Legitimate repeated taps stopped | "5 mi" -> "10 mi" invisible at 64x128 | Count clear full-resolution pixel changes |
| Launch name rejected | Model translated the app name into Chinese | Resolve non-Latin names when one app is allowed |

## After the evaluation

Six follow-up versions (v43-v48) turned the fix layers above into checks and
were tested on ten practice runs: 0/10 passed, and new failure modes appeared
each time (for example making the country itself route point 1, confusing two
adjacent buttons, or tapping SHOW ON MAP while results were still loading,
which is `too_early`). The common cause is observation: OsmAnd gave no usable
GUI tree to our UIAutomator path, so the program could not check the screen
itself. Android World's accessibility forwarder does provide it in 0.2 s; see
[MEDIUM_HARD_TRIALS.md](MEDIUM_HARD_TRIALS.md), rows 22-28.
