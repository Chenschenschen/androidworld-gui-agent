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
