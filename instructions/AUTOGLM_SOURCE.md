# Prompt attribution

autoglm.md adapts zai-org/Open-AutoGLM's English SYSTEM_PROMPT, Apache2.0.
The license is preserved in LICENSE_AutoGLM.txt; the pinned source, commit and
hashes are recorded in [the pinned manifest](../docs/sources/pinned_upstream.json).

Changes: omit dynamic date for a stable prefix, use app_name in the generic
Launch example, document normalized checked coordinates and existing Home/Wait,
and append Android World's M3A completion/recovery/text-selection principles.
assessment.md separately paraphrases M3A SUMMARY_PROMPT_TEMPLATE at the pinned
Android World commit. It compares the actual before/after screens, GUI properties,
goal and previous reply, returning a short read-only outcome summary. Native
action generation remains unchanged; the summary is feedback for the next
decision, never an executable action or official verifier feedback.
v32 reuses native capability context in the summary request, matching M3A's
shared PROMPT_PREFIX structure. v33 renders the existing Launch example's
placeholder as a real allowed app value after a recorded literal app_name
reply. This supplies a legal example argument, not an automatic app choice.
v34 disables assessment by default after the unsuccessful experiment; exact
tested prompt/source snapshots remain in the original trial folders.
Task completion criteria are short visible goals in autoglm_agent.py, not fixed
action replays. Exact executed native replies and original observations remain
in each run. See ../docs/COURSE_AND_UPSTREAM_REVIEW.md for the course/source map.
