# Read-only step assessment

Compare the BEFORE and AFTER screenshots, their observed GUI properties, and
the action that was actually dispatched. Give a short summary of the latest
step for use in the next action decision. Include the intended effect, whether
it worked as expected, and any observed mismatch. Be critical: the previous
action and its explanation may be wrong. If it failed, explain the evidence
and what should or should not be done next. Preserve exact values that matter.

Use one line, preferably fewer than 50 words. Return only the summary, with no
operation code. This request assesses an already executed step; it does not
operate the device. Distinguish visible evidence from uncertainty.

Adapted from Android World's M3A SUMMARY_PROMPT_TEMPLATE, Apache License 2.0;
source attribution and changes are in instructions/AUTOGLM_SOURCE.md.
