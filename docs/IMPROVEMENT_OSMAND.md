# Documented improvement: an OsmAnd Skill (before/after)

Course requirement (Syllabus p.1): "one documented improvement supported by
before-and-after results". This experiment changes **one variable** on the
hard task `OsmAndTrack`: whether the agent receives an app Skill.

## Result in one table

Same frozen v42 code (identical source hashes), same model, sampling, budgets,
task seeds and official verifier. The two batch configurations differ only in
`task_skills`.

| OsmAndTrack, seeds 42/43/44 | Before: no Skill | After: Skill |
| --- | --- | --- |
| Official verifier PASS | 0/3 | 0/3 |
| M1 searched the first waypoint by name | 1/3 (full "Bendern, Liechtenstein") | **3/3** (place name only) |
| M2 selected the place itself | 0/3 | **1/3** (seed 42 chose a same-name guidepost) |
| M3 started Plan a route containing a searched point | 0/3 | **1/3** (the guidepost) |
| M4 route points within the verifier tolerance (of 9 required) | 0 | 0 |
| M5 saved a track | 0/3 | 0/3 |
| Mean executed steps before the no-progress stop | 9.0 | 17.7 |
| Mean duration | 83.2 s | 174.7 s |
| Prompt tokens per run | 23-47k | 69-136k |

Batches: before [`eval_batch_20261008T132945_347728Z`](evidence/final/eval_batch_20261008T132945_347728Z/RESULTS.md),
after [`eval_batch_20261008T133403_527980Z`](evidence/final/eval_batch_20261008T133403_527980Z/RESULTS.md)
(OsmAnd rows of the final evaluation).

**Honest reading.** The Skill did not make the hard task succeed: both
conditions score 0/3 on the only success criterion. It did move the agent
through the first stages of the correct procedure (search by place name in all
three runs, a route started in one), which no run reached without it. Three runs per condition is a small sample, so the milestone
differences show a direction, not a measured effect size. Milestones were
annotated by hand from screenshots and replies (definitions below) because an
outcome-only score cannot show partial progress (D5 p.37).

## Problem found in the trajectories

Every OsmAnd run without the Skill failed in one of two ways (trials 7-13 in
[MEDIUM_HARD_TRIALS.md](MEDIUM_HARD_TRIALS.md) and the baseline batch):

- **Wrong feature.** Menu > Plan a route > Create new route, then repeated
  **Add**, expecting a search dialog. In OsmAnd, Add places a point at the
  centre crosshair, which was in the Gulf of Guinea (the default world view).
- **Wrong search syntax.** Typing the task's waypoint text
  ("Bendern, Liechtenstein") finds only the country; clearing and retyping
  resets the search radius; a place-card "Add" saves a Favorite, which is not
  part of a track.

These are missing facts about one application, not general perception or
instruction-following errors. Course D5 pp.41-42 place "a missing fact" in the
knowledge layer and a reusable procedure in instructions or Skills (D2 Skills;
D3 pp.26-27 SKILL.md). Fine-tuning is out of scope and, per D5 p.42, not the
first step when knowledge and instructions can be improved.

## The change (the Skill)

1. [`instructions/skills/osmand_track.md`](../instructions/skills/osmand_track.md):
   app facts and a five-step procedure, written from a manual ADB exploration
   whose saved track passed the **official** `osmand._track_matches` check,
   plus facts read from baseline trajectories. Loaded into the system prompt
   only for `OsmAndTrack` (`config["task_skills"]`, `autoglm_agent.skill_text`).
2. Search terms derived from the task input: the name before the comma of each
   given waypoint, listed in the Skill text.
3. One reminder line in every step's user message with those terms and the
   empty-search rule (`autoglm_agent.skill_reminder`, a D2 status line).

Parts 2 and 3 were added after held-out trials showed the system-prompt Skill
alone was not followed (the model kept typing the full task value; trials 17-20).
All Skill development used held-out task seed 8 (Planken, Rotenboden) and the
manual exploration; the Skill names no evaluation waypoint (its example is
Vaduz, which is never a task waypoint). One limitation: the manual exploration
used the waypoints of evaluation seed 43 (Oberplanken, Malbun) to learn the
app's procedure; no instance-specific coordinates or taps were written into
the Skill.

What does not change between conditions: model, temperature, prompt contract,
action adapter, observation, history window, no-progress rules, step budget
(90) and time budget (2700 s), task seeds and the official verifier.

```powershell
# Before (no Skill)
.\.venv\Scripts\python.exe -X utf8 evaluate_tasks.py --tasks OsmAndTrack --seeds 42 43 44 --run-all-seeds --disable-skills
# After (with Skill), as part of the final evaluation
.\.venv\Scripts\python.exe -X utf8 evaluate_tasks.py --tasks ContactsAddContact SimpleCalendarAddOneEvent OsmAndTrack --seeds 42 43 44 --run-all-seeds
```

Task instances (seed: waypoints in order): 42: Bendern, Balzers, Oberplanken,
Nendeln; 43: Oberplanken, Malbun; 44: Schaan, Triesen, Bendern.

## Per-run milestones

| Seed | Before (no Skill) | After (Skill) |
| --- | --- | --- |
| 42 | Typed "Bendern, Liechtenstein", got only the country/SHOW ON MAP, moved on to "Balzers, Liechtenstein", retyped until the cycle stop (12 steps). M1 only | Typed "Bendern", widened the radius three times, but chose "Bendern (Guidepost)", a same-name signpost, against the Skill's rule; Actions > Plan a route made it route point 1 (`points: 1`), about 300 m from the village node (estimated from the 0.25 mi scale bar; tolerance about 110 m). Then "Balzers" never reached the unfocused search field (17 steps). M1, M3 |
| 43 | Menu > Plan a route > Create new route, then Add three times on the empty world view until the cycle stop (8 steps). None | Typed "Oberplanken", widened the radius three times, chose the hamlet, then tapped the place card's Add and saved a Favorite three times (14 steps). M1-M2 |
| 44 | Same as seed 43 before (7 steps). None | Typed "Schaan", widened the radius once, then alternated searches for Triesen and Bendern (22 steps). M1 |

Milestone definitions: M1 the first waypoint's name was typed into OsmAnd
search; M2 the place itself (village/hamlet result) was opened; M3 Plan a route
showed `points: 1` or more with a point taken from search; M4 number of route
points within the verifier's 0.001 degree tolerance of a waypoint, in order;
M5 "GPX file saved" shown.

## What would come next

The remaining failures sit in different layers (D4 p.27, D5 pp.41-42):
a same-name distractor chosen against the Skill (the guidepost), an unfocused
field that silently swallowed typed text (program layer: check the
typed text appears before continuing), a Skill fact the model ignored (the
Favorite trap; instruction layer, or a program rule that blocks the Favorite
dialog for this task), and the model describing results that were not on screen
(model/perception; not fixable by instructions alone). See
[FINAL_FAILURE_ANALYSIS.md](FINAL_FAILURE_ANALYSIS.md).

## Follow-up after the evaluation (v43-v48, not evaluated)

We then implemented the program-layer fixes named above and more: a focus
check for Type that needs no GUI tree, refusing Favorite saves, comma queries,
SHOW ON MAP taps and a route Add before the next search, a code-kept route
progress line and a region-first step. On ten practice runs (seeds outside the
evaluation set) none passed; two added the first waypoint correctly and none a
second. The checks worked when they fired, but without a GUI tree they relied
on the model's own description of the screen. A probe then showed that Android
World's accessibility forwarder returns OsmAnd's GUI tree in 0.2 s, which would
let the checks use the real screen; this is the recommended next step. Details:
[MEDIUM_HARD_TRIALS.md](MEDIUM_HARD_TRIALS.md), rows 22-28.

## Additional experiment: v61 on the slide instance

After v43-v48 we continued on the hard task only (rows 29-42 of
[MEDIUM_HARD_TRIALS.md](MEDIUM_HARD_TRIALS.md#osmand-only-extra-experiment-v49-v61-practice-runs)).
This experiment is **additional**: the official three-task evaluation above
stays v42. Two things changed between v42 and v61:

1. **Observation (kept in both conditions below).** OsmAnd's GUI tree comes
   from Android World's accessibility forwarder, with a checked UIAutomator
   dump when the forwarder shows a near-empty screen (OsmAnd's Plan a route
   screen); every labelled element gets a tap centre; an observation waits
   while OsmAnd's search spinner turns.
2. **The Skill, now partly program (switched off in the "before" condition).**
   Besides the Skill text, the code recognises the OsmAnd screen from the tree
   and states the next step of the procedure with its tap centre
   (`osmand_next_step`), and refuses actions the screen shows to be wrong:
   the place card's Favorite Add, the plain SHOW ON MAP row, a non-settlement
   result row, the navigation Route button, a second Plan a route, the route
   panel's Add before the next place was opened, and `finish` before Done saved
   the track. The model still chooses and performs every action.

**Task: exactly the course slide's instance**, "Save a track with waypoints
Ruggell, Liechtenstein and Bendern, Liechtenstein" (the slide shortens Android
World's "... in the OsmAnd maps app in the same order as listed"). Android
World draws the waypoints from the seed; seeds 31, 314 and 366 all produce
this list, so the three runs repeat the slide task. None of these seeds, and
no Ruggell-Bendern instance, was run before v61 was frozen (tag
`osmand-extra-v61`); practice used seeds 8 and 7.

Same frozen v61 code (identical source hashes in both batches), model,
sampling, budgets, seeds and official verifier; the batches differ only in
`task_skills` (`--disable-skills`).

| OsmAndTrack, slide instance, seeds 31/314/366 | Before: no Skill | After: Skill (program + text) |
| --- | --- | --- |
| **Official verifier PASS** | **0/3** | **2/3** |
| M1 searched the first waypoint by name | 3/3, all as the full "Ruggell, Liechtenstein" (finds only the country) | 3/3, place name only |
| M2 selected the place itself | 0/3 | 2/3 |
| M3 started Plan a route containing a searched point | 0/3 (two runs used navigation, one tapped points on the map) | 2/3 |
| M4 route points within the verifier tolerance (of 6 required) | 0 | 4 |
| M5 saved a track | 0/3 | 2/3 |
| Mean executed steps | 23.3 (stopped by the no-progress rule) | 18.7 |
| Mean duration | 457 s | 336 s |
| Prompt tokens per run | 89-353k | 80-220k |
| Actions refused by the OsmAnd checks | 0 (checks off) | 3 (SHOW ON MAP twice, the Favorite Add once); the general focus check also refused 2 Types |

Batches: after [`eval_batch_20261008T191026_753929Z`](evidence/extra/eval_batch_20261008T191026_753929Z/RESULTS.md),
before [`eval_batch_20261008T192739_139270Z`](evidence/extra/eval_batch_20261008T192739_139270Z/RESULTS.md).

| Seed | Before: no Skill | After: Skill |
| --- | --- | --- |
| 31 | Tapped the map's Route button (navigation), set start and destination by typing "Ruggell, Liechtenstein" and "Bendern, Liechtenstein", which both resolve to the country, then cycled through navigation settings looking for a save button (20 steps). M1 | Typed "Ruggell", widened the radius three times, scrolled. The forwarder crashed; with no GUI tree for one step the model swiped past the visible village row and later kept swiping at the end of the list (11 steps). M1. Analysed in [FINAL_FAILURE_ANALYSIS.md](FINAL_FAILURE_ANALYSIS.md#additional-experiment-the-one-failure-of-v61-on-the-slide-task) |
| 314 | Navigation again: start and destination both "Country Liechtenstein", then added and removed intermediate points until the cycle stop (35 steps). M1 | **PASS** in 22 steps: Ruggell village (one scroll), Actions > Plan a route, Search "Bendern", SHOW BENDERN ON THE MAP, Back x3, Add, Done, finish. The Favorite Add and one unfocused Type were refused |
| 366 | Menu > Plan a route > Create new route; two taps meant for Search landed on the map and added two points on the default world view (steps 8-9); typed "Ruggell, Liechtenstein", tapped SHOW ON MAP (country), then Add four times (15 steps). M1 | **PASS** in 23 steps, same procedure; SHOW ON MAP and one unfocused Type were refused, and the forwarder's crash dialog appeared once and the model closed it |

**Honest reading.**

- This is the first time the hard task passed in this project, and the
  difference is large on the only success criterion (0/3 to 2/3), but three
  runs per condition remain a small sample.
- The improvement is mostly **program knowledge**: the procedure was written
  from a manual exploration of this OsmAnd version and is OsmAnd-specific. A
  new app would need its own procedure. In D5 pp.41-42 terms the Skill moved
  from the instruction layer (v42: text, 0/3) into the program layer.
- The model was still needed for every decision, and it disagreed with the
  stated step several times (tapping Route, a second Plan a route, finishing
  early, "the row is not there"). The checks caught the first three; the last
  one, without a GUI tree, caused the failed run.
- Most of the 13 versions (v49-v61) fixed our own code, not the model (a
  branch order bug, an id field mismatch, a false result row, step ordering).
  Each fix came from one recorded run and has an offline test.

After the evaluation we changed two rules for the seed-31 failure (v62:
re-read an empty forwarder tree once; widen the radius before scrolling at the
end of the list). They are not part of the comparison above. One check run of
v62 on seed 31 (`trial_OsmAndTrack_20261008T195225_073828Z`) passed in 22
steps, but the forwarder did not crash in it and the village row appeared after
one scroll, so neither new rule was exercised; it shows no regression, not that
the fix works.
