# Documented improvement: an OsmAnd Skill (before/after)

Course requirement (Syllabus p.1): "one documented improvement supported by
before-and-after results". This experiment changes **one variable** on the
hard task `OsmAndTrack`: whether the agent's prompt contains an app Skill.

## Problem found in the trajectories

Every OsmAnd run without the Skill failed in the same way (trials 7-9 in
[MEDIUM_HARD_TRIALS.md](MEDIUM_HARD_TRIALS.md)):

- The model opened **Menu > Plan a route > Create new route** and tapped
  **Add**, expecting a search dialog. In OsmAnd, Add places a point at the
  centre crosshair, which was in the Gulf of Guinea (the default world view).
  Repeated Adds at the same spot add nothing, so the cycle stop ended the run.
- When it did search, it typed "Balzers, Liechtenstein" (only the country is
  found), cleared and retyped (which resets the search radius) and saved a
  waypoint as a **Favorite** (which is not part of a track).

These are missing facts about the application, not perception or
instruction-following errors. Course D5 pp.41-42 places "a missing fact" in
the knowledge layer and a reusable procedure in instructions or Skills (D2
pp.30-33; D3 pp.26-27 SKILL.md). Fine-tuning is out of scope and unnecessary
when knowledge and instructions suffice (D5 p.42).

## The change

[`instructions/skills/osmand_track.md`](../instructions/skills/osmand_track.md)
(about 360 words) states the app facts and a five-step procedure. It was written
from a manual ADB exploration whose saved track passed the **official**
`osmand._track_matches` check, plus two facts read from the baseline
trajectory. It is loaded only for `OsmAndTrack`
(`config["task_skills"]`, `autoglm_agent.skill_text`). It names no evaluation
waypoint (its example is Vaduz, which is never a task waypoint).

What does not change: model, temperature, prompt contract, action adapter,
observation, step budget (90) and time budget (2700 s), task seeds and the
official verifier. Both conditions run the **same frozen v34 code** (identical
source hashes); the baseline passes `--disable-skills`, which only empties
`task_skills` in the batch's frozen configuration.

```powershell
# Before (no Skill)
.\.venv\Scripts\python.exe -X utf8 evaluate_tasks.py --tasks OsmAndTrack --seeds 42 43 44 --run-all-seeds --disable-skills
# After (with Skill), as part of the final evaluation
.\.venv\Scripts\python.exe -X utf8 evaluate_tasks.py --tasks ContactsAddContact SimpleCalendarAddOneEvent OsmAndTrack --seeds 42 43 44 --run-all-seeds
```

Task instances (seed: waypoints in order): 42: Bendern, Balzers, Oberplanken,
Nendeln; 43: Oberplanken, Malbun; 44: Schaan, Triesen, Bendern.

## Metrics

- **Outcome:** official verifier PASS/FAIL (the only success criterion).
- **Process milestones**, annotated by hand from each run's screenshots and
  replies, because a 0/3 outcome alone cannot show partial progress (D5 p.37):
  M1 searched for the first waypoint by name; M2 selected the place itself;
  M3 started Plan a route containing a waypoint; M4 number of correct route
  points added; M5 saved a track ("GPX file saved").
- Steps, model calls, duration, stop reason.

<!-- Results are added below after both batches finish. -->
