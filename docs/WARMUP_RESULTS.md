# Recorded warm-up results, 8 October 2026

Success below means model finish **and** official Android World PASS, with valid
initialization/video and no runtime error. Original failed runs are preserved.
Three seeds are a small sample. Different versions are not a frozen 15/15 batch.

| Task | Version and seeds | Clean result | Evidence |
| --- | --- | --- | --- |
| Wi-Fi | v20,42/43/44 | 3/3 (100%), five steps each | [Frozen results](evidence/batches/easy_batch_20261008T064328_366877Z/RESULTS.md) |
| Camera | v20,42/43/44 | 3/3 (100%), four steps each | [Same frozen results](evidence/batches/easy_batch_20261008T064328_366877Z/RESULTS.md) |
| Contacts | v28,42/43/44; identical frozen source hashes | 3/3 (100%), eleven steps each | [Bounded result](evidence/batches/easy_batch_20261008T081652_065024Z/RESULTS.md), [repeats](evidence/batches/easy_batch_20261008T082214_015428Z/RESULTS.md) |
| Timer | v28,42 | 0/1 (0%), twelve steps; no finish | [Bounded result](evidence/batches/easy_batch_20261008T081652_065024Z/RESULTS.md) |
| Clipboard | v27,43;v28 saved-screen probe | 0/1 live (0%); probe still false-finished | [Live result](evidence/batches/easy_batch_20261008T081108_236581Z/RESULTS.md), [unexecuted probe](evidence/clipboard_probe.json) |

Earlier Contacts v14 also passed 3/3. Earlier Timer v16 passed 2/3 and Clipboard
v20 passed 1/2. These remain distinct historical measurements; they cannot be
combined selectively to claim current three-repeat success.

## What was corrected

The original Wi-Fi stopping error needed correctly labeled **actual checked GUI
state**, not more toggles. Camera's duplicate finish response needed a safe
parser correction, not another shutter press. Both earned recorded 3/3 gates.

Following the user's correction, all 174 D1–D4 pages and the supplied examples
were reviewed again, together with 12 pinned primary GitHub source files. The
implementation now uses the upstream native English action contract, short
visible completion goals, ordered conversation, latest image and factual GUI
results. Experimental Clock keypad Type and accumulated task recipes were
withdrawn. Details and source/slide mapping:
[COURSE_AND_UPSTREAM_REVIEW.md](COURSE_AND_UPSTREAM_REVIEW.md).

Trajectory evidence exposed and repaired bounded recorder readiness, weak Launch
validation errors, Clipper incorrectly advertised as a GUI app, and real XML
EditText controls incorrectly rejected when editability was missing. Native Type
preserves exact text without Enter. The existing checked GUI supplement now
includes Chrome. The scheduler stops at the first failed clean trial by default.
Every failed trial is diagnosed and recorded before another run.

The current v29 adds a bounded stop for repeated actions in an unchanged short
cycle, following D4 pp.26–27. Sixteen offline adapter checks pass. This limits
wasted actions but does not correct Timer's digit error or Clipboard's false
finish. v29 has no live success claim; successful live gates are v20/v28 above.
[Saved-evidence verification](evidence/offline_verification.json) confirms
the Contacts source equality and would block the recorded Timer cycle before
step 12, using no model calls or device actions.

## What remains unresolved

Timer's correctly grounded step5 chooses7 after observed buffer20, omitting a
required0 from200701. It then appends digits to a full wrong entry. The reviewed
native contract and factual selected-control feedback did not solve sequencing.
Clipboard correctly typed the email but treated Clear input as Copy, then
false-finished on an existing suggestion. A saved-screen factual-feedback probe
still false-finished. Neither task was repeated unchanged after this diagnosis;
neither has three clean current repeats. No forced completion, next-digit
controller, direct clipboard write or per-step verifier feedback was added.

The original logs and videos remain in the local run archive. The public
[approved evidence export](evidence/README.md) describes exactly what is shipped,
including the selected original screenshots and diagnostic trajectories. Completed
artifact audits found matching frozen sources, valid JSON, no logged credential,
no missing completed-step evidence and decodable recordings. Recording-invalid
attempts are labeled separately; recovering their clip does not make them valid.

## Run independently

From the project directory:

```powershell
.\.venv\Scripts\python.exe -X utf8 run_task.py --task ContactsAddContact --seed 42
```

Each evaluation already invokes this independent Python entry point. The
run.ps1 -CheckOnly check also passed from C:/Users/koc, without a model request.
See [RUNNING_TASKS.md](RUNNING_TASKS.md) for emulator/.env setup and each task.
Ollama is stopped; hosted inference requires no local language-model weights.

Markor, SimpleCalendarAddOneEvent and the jointly selected harder task remain
the agreed course scope. These warm-ups do not satisfy the full easy/medium/hard
evaluation and presentation requirement.
