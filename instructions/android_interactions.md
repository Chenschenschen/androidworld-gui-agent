# General Android interaction guidance v1

Keep your visible explanation brief and grounded in the supplied observation:
identify the remaining goal, the relevant visible control, the actual effect of
the previous action, and the intended effect of ONE next action. If evidence is
uncertain, say so. Preserve the native answer format; do not output a script or
a second action. The goal and its completion condition remain authoritative.

Choose the easiest available route using the supplied app capabilities. Prefer
Launch for an available app instead of searching the app drawer. Stay in an app
that already provides the required control. A background verifier service is
not an interactive app. Never invent controls or capabilities.

Ground each action in the CURRENT screenshot. When fresh GUI labels identify
the intended control, use its supplied centre and properties. Check the actual
label: a nearby clear button, suggestion or menu is not an editable field or a
Copy command. Earlier coordinates may no longer be valid.

Before Type, focus the actual editable field. A keyboard alone does not prove
the intended field is focused. Type replaces that field's contents without
Enter; preserve the requested value exactly and inspect the visible result.
Numeric keypads may be buttons rather than editable fields; observe how a tap
changes the value instead of assuming independent fields or keyboard support.

Text selection normally starts with a long press INSIDE the editable text.
The first selection may cover only one word. Inspect its highlighted range;
use the visible Select all command when the whole value is required. Copy is a
command in the text-selection toolbar, possibly inside its overflow. A cleared
field or an old clipboard suggestion is not evidence of a successful copy.

After an action, use the actual observed result, not the previous explanation,
to judge progress. A focus change can be useful despite little image change.
If loading is visible, use a bounded Wait and inspect again. If a target was
missed, locate it afresh. Scroll only to reveal relevant hidden content; Back
only when the current screen is the wrong route. Do not blindly swipe, go back,
relaunch, or repeat a toggle/capture/save operation because you are uncertain.
If history shows the same failed approach or a menu cycle, choose a different
evidence-supported approach. If none exists, explain the limitation rather
than claiming success. The harness bounds repeated ineffective actions.

Before every action, check the visible completion condition. A filled unsaved
form is not a saved record, and a closed menu alone is not the requested result.
Finish when the required state is supported by the current GUI and executed
history. Do not repeat a completed operation to demonstrate completion.

Adapted from pinned Android World M3A GUIDANCE, AutoGLM's native Type/Launch
contract, and the course D3/D4 observation-feedback/recovery principles.
These are reusable interaction rules, not per-task app routes or coordinates.
