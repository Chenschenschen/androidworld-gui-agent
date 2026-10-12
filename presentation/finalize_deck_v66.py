"""Turn the team's edited deck (AndroidWorld_GUI_Agent_Presentation_team_edit.pptx) into the final deck.

Markor + SMS now uses the v66 runs (Skill: Share > Plain Text); the other six tasks keep their v65 runs (same code).
Writes the speaker version (with notes) and the submission version (notes removed). The team's file is not changed.
usage: python finalize_deck_v66.py
"""
import copy
import hashlib
from pathlib import Path
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.shapes import MSO_SHAPE_TYPE

HERE = Path(__file__).resolve().parent
SRC = HERE / "AndroidWorld_GUI_Agent_Presentation_team_edit.pptx"   # the team's edited deck (seven demo slides), 12 October
OUT = HERE / "AndroidWorld_GUI_Agent_Presentation.pptx"
OUT_SUBMIT = HERE / "AndroidWorld_GUI_Agent_Presentation_submission.pptx"
IMG, VID = HERE / "images", HERE / "videos"
EVID = "https://github.com/Chenschenschen/androidworld-gui-agent/blob/team-agent/docs/evidence/markor_v66/runs"
MARKOR = [  # (seed, run_id, steps, verdict, clips, note) from runs/eval_batch_20261009T125038_033286Z
    (42, "trial_MarkorCreateNoteAndSms_20261009T125039_586151Z", 18, "FAIL", 1,
     "Note saved; Share > Plain Text sent its text to SMS Messenger; number confirmed. The model then said the SMS button "
     "was at the top right and tapped [940, 60] four times; the button was at the right of the message bar. No-progress stop."),
    (43, "trial_MarkorCreateNoteAndSms_20261009T125401_048355Z", 18, "PASS", 1,
     "New file, name and .txt, text, Save; More options > Share > Plain Text > SMS Messenger; number and checkmark; the text "
     "was already in the message field, so it only tapped SMS."),
    (44, "trial_MarkorCreateNoteAndSms_20261009T125719_921778Z", 18, "PASS", 2,
     "Same path as run 2: the note's text was shared with Share > Plain Text, not typed again; SMS sent in 18 steps."),
]

prs = Presentation(SRC)


def slide(n):
    return prs.slides[n - 1]


def replace_in(tf, old, new):
    for p in tf.paragraphs:
        for r in p.runs:
            if old in r.text:
                r.text = r.text.replace(old, new)
                return True
    for p in tf.paragraphs:  # text split over runs: keep the first run's formatting
        full = "".join(r.text for r in p.runs)
        if old in full:
            p.runs[0].text = full.replace(old, new)
            for r in p.runs[1:]:
                r.text = ""
            return True
    return False


def rep(n, old, new):
    for sh in slide(n).shapes:
        if sh.has_text_frame and replace_in(sh.text_frame, old, new):
            return
    raise AssertionError(f"slide {n}: {old!r} not found")


def note(n, old, new):
    assert replace_in(slide(n).notes_slide.notes_text_frame, old, new), f"notes {n}: {old!r} not found"


def set_note(n, text):
    slide(n).notes_slide.notes_text_frame.text = text


def table(n):
    return next(sh for sh in slide(n).shapes if sh.has_table).table


def cell_text(cell, text):
    tf = cell.text_frame
    p0 = tf.paragraphs[0]
    p0.runs[0].text = text
    for r in p0.runs[1:]:
        r.text = ""
    for p in tf.paragraphs[1:]:
        p._p.getparent().remove(p._p)


def copy_cell(tbl, src, dst):
    s, d = tbl.cell(*src)._tc, tbl.cell(*dst)._tc
    d.getparent().replace(d, copy.deepcopy(s))


def chart(n):
    return next(sh for sh in slide(n).shapes if sh.has_chart).chart


def set_chart(n, values_by_series):
    ch = chart(n)
    data = CategoryChartData()
    data.categories = list(ch.plots[0].categories)
    for s in ch.plots[0].series:
        data.add_series(s.name, values_by_series.get(s.name, list(s.values)))
    ch.replace_data(data)


# 2 - at a glance
rep(2, "18 of 21 runs passed", "17 of 21 runs passed")
rep(2, "18 / 21", "17 / 21")
rep(2, "65", "66")
rep(2, "One frozen version for all 21 runs", "Frozen, git-tagged code for all runs")
rep(2, "About 0.065 €", "About 0.066 €")
rep(2, "1.77 s median", "1.75 s median")
note(2, "Each task ran three times on one frozen version", "Each task ran three times on frozen, git-tagged code")
note(2, "18 of the 21 runs passed", "17 of the 21 runs passed")
note(2, "65 versions", "66 versions")
note(2, "about 0.065 euro", "about 0.066 euro")

# 5 - model
t = table(5)
cell_text(t.cell(3, 1), "1.75 s median (297 calls)")
cell_text(t.cell(6, 1), "17 / 21 in the final evaluation")
note(5, "1.77 seconds", "1.75 seconds")

# 7 - Markor Skill
rep(7, "Fact: Share attaches the file and makes a failing MMS", "Fact: Share > File makes a failing MMS")
rep(7, "Procedure: name + extension, Save, launch SMS, plain text, SMS button",
    "Procedure: name + extension, Save, Share > Plain Text, SMS Messenger, number, SMS")
note(7, "For Markor it is text: use a plain SMS, never Markor's Share menu, because that sends an MMS that fails.",
     "For Markor it is text: share the note with Share, Plain Text. Share, File would attach the file and turn the message into an MMS that fails.")

# 8 - safety net (the truncated reply was in a v65 Markor run)
t = table(8)
assert t.cell(4, 0).text == "Truncated reply"
t._tbl.remove(t._tbl.tr_lst[4])
big = [sh for sh in slide(8).shapes if sh.has_text_frame and sh.text_frame.text.strip() == "8" and sh.top < 6 * 914400]
assert len(big) == 1   # the big number, not the page number in the footer
replace_in(big[0].text_frame, "8", "7")
rep(8, "(7 of 21 runs had one or more)", "(6 of 21 runs had one or more)")
rep(8, "Six of the seven runs with a refusal still passed.", "Five of the six runs with a refusal still passed.")
note(8, "stopped 8 actions", "stopped 7 actions")

# 9 - reproduce
rep(9, "git checkout team-agent-final-v65", "git checkout team-agent-final-v66")

# 11 - how we tested
rep(11, "How we tested: one frozen version, three runs per task", "How we tested: frozen code, three runs per task")
rep(11, "Git tag team-agent-final-v65", "Final agent: tag team-agent-final-v66")
rep(11, "Same source fingerprint in both batches", "Six tasks run on v65: same code")
rep(11, "No changes during the batch", "Markor re-run on v66 after a Skill fix")
note(11, "First, we froze the code. The final version has a git tag, and both evaluation batches have the same source fingerprint, so all 21 runs come from exactly the same agent.",
     "First, we froze the code with a git tag before every batch, and nothing changed during a batch. The final agent is version 66. "
     "Six tasks were run with version 65; version 66 only changed the Markor Skill, which these tasks never load, so they ran the same code. "
     "Markor was run again with version 66 after we fixed its Skill.")

# 12 - results grid
rep(12, "18 of 21 runs passed", "17 of 21 runs passed")
t = table(12)
assert t.cell(6, 1).text == "MarkorCreateNoteAndSms" and t.cell(2, 3).text.startswith("FAIL")
copy_cell(t, (2, 3), (6, 2))
replace_in(t.cell(6, 2).text_frame, "s43", "s42")
replace_in(t.cell(6, 2).text_frame, "other: navigation", "grounding")
cell_text(t.cell(6, 5), "2/3")
rep(12, "One frozen version (tag team-agent-final-v65).", "Tag team-agent-final-v66 (six tasks run on v65, same code).")
note(12, "Wi-Fi, SMS, Calendar and Markor passed all three runs.", "Wi-Fi, SMS and Calendar passed all three runs.")
note(12, "Contacts, Files and OsmAnd passed two of three.", "Contacts, Files, Markor and OsmAnd passed two of three.")
note(12, "passed five of six", "passed four of six")
note(12, "The three failures are all different. One is a false finish, one is a missed tap, and one is a navigation problem.",
     "There are four failures: one false finish, two missed taps, and one navigation problem.")

# 14 - run log: Markor rows from v66
rep(14, "Model AutoGLM-Phone-9B (Z.ai), version v65, grounding by coordinates. Rows written by the runner during each run; click a run to open its log.",
    "Model AutoGLM-Phone-9B (Z.ai), grounding by coordinates; Markor rows v66, OsmAnd v65 (same code). Click a run to open its log.")
t = table(14)
copy_cell(t, (6, 5), (1, 5))   # FAIL style
copy_cell(t, (6, 6), (1, 6))   # failure-class style
for row, (seed, rid, steps, verdict, clips, text) in enumerate(MARKOR, start=1):
    assert t.cell(row, 0).text == "MarkorCreateNoteAndSms" and t.cell(row, 2).text == str(seed)
    link = t.cell(row, 1).text_frame.paragraphs[0].runs[0]
    link.hyperlink.address = f"{EVID}/{rid}/trajectory.txt"
    cell_text(t.cell(row, 4), f"{steps} / 40")
    cell_text(t.cell(row, 5), verdict)
    if verdict == "PASS":
        cell_text(t.cell(row, 6), "—")
    cell_text(t.cell(row, 7), str(clips))
    cell_text(t.cell(row, 8), text)
note(14, "All three Markor runs followed the Skill: save the note, then send its text as a plain SMS. One run needed the alias table, because the model named the SMS app in Chinese.",
     "All three Markor runs saved the note and then shared its text with Markor's Share, Plain Text; none typed the text again. "
     "Run 1 failed on the very last tap: it looked for the SMS button at the top right instead of next to the message.")
note(14, "The only failure here, OsmAnd run 3,", "The other failure here, OsmAnd run 3,")

# 15 - video wall: same layout, new Markor column (v66)
for sh in slide(15).shapes:
    if sh.shape_type == MSO_SHAPE_TYPE.MEDIA:
        part = slide(15).part
        for rel in part.rels.values():
            if rel.reltype.endswith("/video") or rel.reltype.endswith("/media"):
                rel.target_part._blob = (VID / "wall_21_runs.mp4").read_bytes()
        blip = sh._element.xpath(".//a:blip")[0]
        part.related_part(blip.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"))._blob = (VID / "wall_21_runs_poster.png").read_bytes()

# 16-22 - demo slides: correct notes (they carried a copy of the old Files notes)
set_note(16, "First the warm-up tasks, sped up so you can follow. Wi-Fi, seed 42: the agent opens Settings, Network and internet, then Internet, "
             "switches Wi-Fi on, and finishes on its own when it sees the switch on. Five steps.")
set_note(17, "Contacts. On the left, seed 42: it types the name, scrolls once to the phone field, types the number and saves. "
             "On the right, seed 43: two swipes go past the phone field, and four more swipes only move the blinking cursor, so our no-progress rule stops the run.")
set_note(18, "Now the real-work tasks. SMS, seed 42: a new conversation, the number, the message, and send. Nine steps.")
set_note(20, "Calendar, seed 44: the title and the description, then the date, the start hour and the length, and save. Sixteen steps, with no refused action.")
set_note(21, "Markor plus SMS, four times faster. On the left, seed 43: the agent creates the note and saves it. Then it uses Markor's own Share, Plain Text, "
             "picks SMS Messenger and enters the number. The message box already holds the note's text, so it only taps SMS. Pass. "
             "On the right, seed 42: the same path works until the very last tap. The model says the SMS button is at the top right and taps there four times, "
             "but the button is next to the message. The run stops: fail, a grounding error.")
set_note(22, "Finally OsmAnd, the hardest task. On the left, seed 314, the run you saw step by step: Ruggell, Plan a route, Bendern, Done, in 23 steps, "
             "and it closed a crash dialog on the way. On the right, seed 366: Ruggell became the first point, but then the model tapped just above "
             "the Clear button three times, and the run stopped.")

# 21 - Markor demo: v66 clips and cards
s21 = slide(21)
places = {sh.name: sh for sh in s21.shapes if sh.name.startswith("Clip placeholder")}
for name, clip in [("Clip placeholder left", "featured_markor_v66_pass"), ("Clip placeholder right", "featured_markor_v66_fail")]:
    ph = places[name]
    s21.shapes.add_movie(str(VID / f"{clip}.mp4"), ph.left, ph.top, ph.width, ph.height,
                         poster_frame_image=str(VID / f"{clip}_poster.png"), mime_type="video/mp4")
    ph._element.getparent().remove(ph._element)
rep(21, "Seed ?", "Seed 43")
rep(21, "? steps, PASS", "18 steps, PASS")
rep(21, "Saved the note, then sent it as an SMS", "Shared the note (Share > Plain Text), then sent the SMS")
rep(21, "Seed ?", "Seed 42")
rep(21, "… steps, FAIL", "18 steps, FAIL")
rep(21, "Wrote the same message instead of copy-pasting", "Shared the note, then tapped the top edge instead of SMS")

# 23 - outcomes of all project runs (now 284 with a summary)
rep(23, "How 275 project runs ended", "How 284 project runs ended")
set_chart(23, {"Runs": [65, 21, 32, 19, 48, 99]})
rep(23, "Final evaluation: false_done 1, grounding 1, other 1", "Final evaluation: false_done 1, grounding 2, other 1")
note(23, "all 275 runs", "all 284 runs")
note(23, "96 runs passed", "99 runs passed")
note(23, "60 runs ended", "65 runs ended")

# 25 - other failures
note(25, "The other two failures.", "Two more failures. The fourth one, Markor seed 42, you saw in its demo: it missed the SMS button.")

# 29 - lessons
t = table(29)
assert t.cell(1, 0).text.startswith("Markor")
cell_text(t.cell(1, 1), "Share > File attaches the note: MMS")
cell_text(t.cell(1, 2), "Skill: Share > Plain Text, then SMS")
for r in (1, 2, 3):
    cell_text(t.cell(r, 3), "Markor 2 / 3")
note(29, "We turned that into the Markor Skill, and the final runs passed three of three.",
     "We turned that into the Markor Skill: share the note as plain text. The final runs passed two of three; the failure was a missed tap at the very end.")

# 30 - work in numbers (now including the v66 runs)
rep(30, "65", "66")
rep(30, "1,453", "1,531")
rep(30, "1,642", "1,722")
rep(30, "€0.48", "€0.51")
note(30, "65 versions", "66 versions")
note(30, "1453 executed steps", "1531 executed steps")

# 31 - findings
rep(31, "8 actions stopped", "7 actions stopped")

# 34, 35 - appendix
set_chart(34, {"Our agent (mean of passing runs)": [5.0, 11.5, 7.7, 15.0, 19.0, 18.0, 22.5]})
note(34, "Markor needs about twice the reference, because the agent types the text twice, once in the note and once in the SMS, instead of sharing it.",
     "Markor needs about twice the reference: the note's name and extension take several steps, and sharing goes through a menu, the share sheet and the number.")
rep(35, "about 0.065 €", "about 0.066 €")
set_chart(35, {"Mean run time (s)": [71.0, 95.0, 71.0, 109.0, 153.0, 202.0, 537.0]})
rep(35, "1.45 M", "1.47 M")
rep(35, "€0.065", "€0.066")
rep(35, "1.77 s", "1.75 s")
note(35, "Markor took about four minutes", "Markor took about three and a half minutes")
note(35, "1.45 million", "1.47 million")
note(35, "about 0.065 euro", "about 0.066 euro")
note(35, "0.48 euro", "0.51 euro")
note(35, "1.77 seconds", "1.75 seconds")

# cover, use case, thank you: Markor phone screens now from the v66 run (seed 43)
swap = {"traj_1.png": "markor_v66_editor.png", "traj_3.png": "markor_v66_share_menu.png", "traj_6.png": "markor_v66_sent.png",
        "traj_2.png": "markor_v66_new_file.png", "traj_5.png": "markor_v66_composer.png"}
by_hash = {hashlib.sha1((IMG / old).read_bytes()).hexdigest(): (IMG / new).read_bytes() for old, new in swap.items()}
swapped = 0
for s in prs.slides:
    for sh in s.shapes:
        if sh.shape_type == MSO_SHAPE_TYPE.PICTURE and sh.image.sha1 in by_hash:
            blip = sh._element.xpath(".//a:blip")[0]
            s.part.related_part(blip.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed"))._blob = by_hash[sh.image.sha1]
            swapped += 1
assert swapped == 5, swapped   # 5 image parts; traj_3 and traj_6 are shared by the cover and slide 3
rep(3, "One of our runs: a note created in Markor, then sent as an SMS", "One of our runs: a note in Markor, shared as an SMS")

prs.save(OUT)
for s in prs.slides:
    if s.has_notes_slide:
        s.notes_slide.notes_text_frame.text = ""
prs.save(OUT_SUBMIT)
print("saved", OUT.name, "and", OUT_SUBMIT.name)
