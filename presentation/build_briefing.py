"""Build the team briefing (Word) for teammates who did not follow the whole project.

usage: python build_briefing.py   -> Team_Briefing_AndroidWorld_Agent.docx next to this file
"""
from pathlib import Path
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Cm

HERE = Path(__file__).resolve().parent
NAVY, BLUE, GREY = RGBColor(0x07, 0x21, 0x40), RGBColor(0x00, 0x65, 0xBD), RGBColor(0x5E, 0x67, 0x73)
doc = Document()
for section in doc.sections:
    section.left_margin = section.right_margin = Cm(2.2)
    section.top_margin = section.bottom_margin = Cm(2.0)
base = doc.styles["Normal"]
base.font.name = "Arial"; base.font.size = Pt(10.5)
base.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
for name, size, color in (("Title", 24, NAVY), ("Heading 1", 17, NAVY), ("Heading 2", 13.5, BLUE), ("Heading 3", 11.5, NAVY)):
    st = doc.styles[name]; st.font.name = "Arial"; st.font.size = Pt(size); st.font.color.rgb = color; st.font.bold = True
    fonts = st.element.rPr.rFonts
    for theme_attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        fonts.attrib.pop(qn(theme_attr), None)          # the heading theme font would override Arial
    fonts.set(qn("w:eastAsia"), "Arial")


def h(text, level=1):
    doc.add_heading(text, level=level)


def p(text, bold_prefix=None, italic=False, color=None, size=None):
    para = doc.add_paragraph()
    if bold_prefix:
        r = para.add_run(bold_prefix); r.bold = True
    r = para.add_run(text); r.italic = italic
    if color: r.font.color.rgb = color
    if size: r.font.size = Pt(size)
    para.paragraph_format.space_after = Pt(6)
    return para


def bullets(items):
    for item in items:
        para = doc.add_paragraph(style="List Bullet")
        if isinstance(item, tuple):
            r = para.add_run(item[0]); r.bold = True
            para.add_run(item[1])
        else:
            para.add_run(item)
        para.paragraph_format.space_after = Pt(2)


def shade(cell, hex_fill):
    tc = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hex_fill)
    tc.append(sh)


def table(rows, widths=None, size=9.5):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = t.cell(r, c)
            cell.text = ""
            run = cell.paragraphs[0].add_run(str(value))
            run.font.size = Pt(size)
            if r == 0:
                run.bold = True; run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF); shade(cell, "072140")
            elif r % 2 == 0:
                shade(cell, "F2F5F9")
            if widths:
                cell.width = Cm(widths[c])
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def slide_section(number, title, says, data=None, terms=None, ask=None):
    h(f"Slide {number}: {title}", 2)
    p(says, bold_prefix="What it says. ")
    if data:
        p("", bold_prefix="The data, and where it comes from")
        bullets(data)
    if terms:
        p("", bold_prefix="Words on this slide")
        bullets(terms)
    if ask:
        p(ask, bold_prefix="If someone asks: ", italic=True)


# ── Cover ────────────────────────────────────────────────────────────────────────────────────────
doc.add_paragraph().paragraph_format.space_after = Pt(60)
title = doc.add_paragraph(); title.alignment = WD_ALIGN_PARAGRAPH.LEFT
r = title.add_run("Team briefing"); r.bold = True; r.font.size = Pt(30); r.font.color.rgb = NAVY
sub = doc.add_paragraph()
r = sub.add_run("One GUI agent for seven AndroidWorld tasks: how we got here, and what every slide means"); r.font.size = Pt(15); r.font.color.rgb = BLUE
p("Agentic AI in Modern Business, TUM School of Management. Group project and presentation.", color=GREY)
p("Team: Danh Phuong Le, Ssu-Cheng Chen, Hayati Ömer Koç, Jia Qi, Tin Nghia Nguyen.", color=GREY)
doc.add_paragraph().paragraph_format.space_after = Pt(30)
p("This document is for every team member, including those who did not follow every step. Part 1 tells the story of the project: "
  "how the agent started, the three lines of work it grew from, what failed on the way, and how we joined everything into one agent. "
  "Part 2 goes through the presentation slide by slide and explains every sentence and every number, so that anyone can present "
  "any slide and answer questions about it. Everything described here is the work of our whole group.")
p("All numbers come from our run records (the trajectory logs, the run summaries and the official verifier results). Where a number "
  "is an estimate or has a limit, we say so.", italic=True, color=GREY)
doc.add_page_break()

# ── Part 1 ───────────────────────────────────────────────────────────────────────────────────────
h("Part 1: How our agent came to be", 1)

h("1.1 The project in one minute", 2)
p("The course asks each group to build a GUI agent: a program that uses a phone the way a person does, by looking at the screen and "
  "deciding where to tap or what to type. The agent must be one class with one method, step(). We test it on AndroidWorld, a public "
  "benchmark from Google Research with 116 tasks on an Android emulator (a virtual phone on the computer). We must pick at least one "
  "task from each of the three difficulty rows on the course slide, run each task three times, record the screen of every run, keep "
  "logs, analyse at least one failure, and show one improvement with before-and-after results.")
p("We chose seven tasks: two easy (Wi-Fi, Contacts), three medium (SMS, Files, Calendar) and two hard (Markor note plus SMS, and "
  "OsmAndTrack, the hardest task on the course list). Our final agent passed 18 of the 21 runs on one frozen version.")

h("1.2 Words you need first", 2)
table([
    ["Term", "Plain meaning"],
    ["AndroidWorld", "The benchmark: a set of phone tasks plus code that prepares each task and checks the result."],
    ["Task / seed", "A task is a template such as “Create a contact for {name}”. The seed is a number that fills in the details "
                    "(which name, which number). Same seed = same details."],
    ["Run", "One attempt at one task from start to finish, with its own screen recording and log."],
    ["Verifier", "AndroidWorld's official checker. After a run it reads the phone's data (for example the contacts database) and says "
                 "PASS or FAIL. The model's own “I am done” never counts."],
    ["Model", "The AI that looks at the screenshot and chooses the next action. Ours: AutoGLM-Phone-9B-Multilingual via the Z.ai API."],
    ["Agent / step()", "Our Python class around the model. Each step: take a screenshot, ask the model, check the answer, perform it on "
                       "the phone, record it."],
    ["Step budget", "The maximum number of steps we allow per run before we stop it."],
    ["Trajectory log", "The step-by-step record of a run: screenshots, the model's replies and what happened."],
    ["Frozen version", "A code version we lock (with a git tag) before an evaluation, so every run in the evaluation uses identical code."],
    ["Observation", "What the agent sees: a screenshot, and for some tasks also a text list of the buttons and labels on the screen."],
    ["GUI tree / accessibility tree", "That text list of screen elements. AndroidWorld can provide it through an “accessibility forwarder” "
                                      "(the same information a screen reader uses). UIAutomator is another, slower way to read it."],
    ["Grounding", "Turning “tap the Save button” into the right point on the screen. We use coordinates on a 0–1000 grid."],
    ["Skill", "App knowledge loaded only for one task, for example “in Markor, Share sends a file as MMS, so type the text into a new SMS”."],
    ["Check / refusal", "Our code inspects each model action before it reaches the phone and refuses clearly wrong ones, with a reason."],
    ["Failure classes (D1 p.50)", "grounding (tap lands on nothing), too_early (acting on a loading screen), lost_value (a value is lost or "
                                  "invented), wrong_app, false_done (model says done, verifier says FAIL). Others are labelled “other”."],
], widths=[4.2, 12.4])

h("1.3 Phase A: the first model, GELab-Zero 4B (unsuccessful)", 2)
p("The course slide suggests GELab-Zero, so we started there. The first runner (its own version series, v1 to v10, labelled "
  "“learning_…” in the logs) ran GELab-Zero 4B locally with Ollama on a laptop with an RTX 4070 GPU (8 GB of video memory).")
bullets([
    ("Too slow: ", "the model (about 9.9 GB in memory) did not fit completely on the 8 GB GPU, so part of it ran on the processor. One "
                   "screenshot request took 19–21 seconds (measured with 16 and 22 layers on the GPU)."),
    ("Weak results: ", "only 1 of 6 Contacts learning trials passed."),
    ("Format problems: ", "in a Wi-Fi run the model answered with a bare “COMPLETE” token that our parser could not accept, "
                          "and its message claimed Wi-Fi was on while the verifier scored 0."),
    ("Decision: ", "the course allows any model, so we switched to a hosted model. We report GELab as our first unsuccessful attempt."),
])

h("1.4 Phase B: AutoGLM through an API, warm-up tasks (AutoGLM v1–v29)", 2)
p("We moved to AutoGLM-Phone-9B-Multilingual, called through the Z.ai API. Version numbers restarted at v1 for this new agent. "
  "These versions built the shared base that all later work grew from (the main branch).")
bullets([
    "Wi-Fi and Camera passed 3 of 3 on v20; Contacts passed 3 of 3 on v14 and again on v28.",
    "Timer and Clipboard were never solved reliably (Timer 2/3 once on v16, Clipboard 1/2 on v20, later failures).",
    "Key lessons: tell the model the real state of a control (for example “Wi-Fi switch: OFF, checked=false”) instead of letting it "
    "guess; parse the model's reply strictly; follow the original Open-AutoGLM action format (v29).",
])

h("1.5 Phase C: three lines of work in parallel", 2)
p("From the shared base, the work continued in three places at the same time. All three are our group's work; they explored different "
  "tasks and ideas, and the final agent took the best lessons from each.")

h("Line 1: branch Jia (AutoGLM v30–v62): Calendar and the hard OsmAnd task", 3)
bullets([
    ("Tasks added: ", "SimpleCalendarAddOneEvent (medium) and OsmAndTrack (hard)."),
    ("Test-setup problems fixed first: ", "the emulator returned black screenshots; the screen recorder died whenever the Android tools "
                                         "restarted their server; app starts took longer than the default 5 seconds; very long runs "
                                         "exceeded the provider's prompt length (fixed by keeping the goal plus the last 19 steps)."),
    ("Frozen evaluation v42: ", "Contacts 3/3, Calendar 3/3, OsmAnd 0/3 (seeds 42/43/44)."),
    ("OsmAnd Skill as text (v34–v42): ", "app knowledge written as instructions. Verifier 0/3 with and without it, but with the Skill the "
                                            "agent went further (searched by place name in 3/3 runs instead of 1/3)."),
    ("v43–v48: rules based on the model's words: ", "0 of 10 practice runs passed. The checks could only read what the model said "
                                                       "about the screen, and the model was often wrong."),
    ("v49–v58: the program reads the real screen: ", "OsmAnd's GUI tree through the accessibility forwarder (0.2 s per read), with "
                                                        "UIAutomator as a fallback for one screen the forwarder shows as empty. Still 0 passes, "
                                                        "but every run revealed a concrete bug."),
    ("v53 onward: Skill as code: ", "the program recognises each OsmAnd screen and tells the model the next step and where to tap; it "
                                   "refuses known traps. First PASS on v59 (practice), 3-waypoint PASS on v61."),
    ("v61 frozen comparison on the course slide's exact task (Ruggell then Bendern): ", "2/3 with the Skill, 0/3 without it. "
                                                                                       "This is our documented improvement."),
])

h("Line 2: branch hayati (its own numbering, v30–v57): SMS, Files and experiments", 3)
bullets([
    ("Tasks added: ", "SimpleSmsSend and FilesMoveFile."),
    ("SMS: ", "two seeds failed at first (a stale tap typed the number into the wrong field; the model translated the app name into "
              "Chinese). With real screen labels for the SMS app and an alias table for the app name, both passed (0/2 to 2/2)."),
    ("Files: ", "a missing label on folder cards and a failed screen read caused wrong taps; fixed with labels taken from the card's "
                "child text and one extra read. Three passes in a row on one version (v56)."),
    ("Experiments that did not work: ", "a step self-assessment (the model judges each step's effect, as in the AndroidWorld M3A agent), "
                                        "a wrapper around the unmodified upstream Open-AutoGLM agent (0/4), extra general guidance. "
                                        "Clipboard (about 15 attempts) and Timer stayed unsolved."),
    ("Research: ", "a comparison with top AndroidWorld leaderboard agents and their designs."),
    "Note: this branch numbers its versions separately, so its v49 is not the same code as v49 on branch Jia.",
])

h("Line 3: the integration package (amber_agent_integration_20261008): Markor and a second runner", 3)
bullets([
    ("Different setup: ", "the original Open-AutoGLM PhoneAgent with its own AndroidWorld runner, on a Mac, same AutoGLM model."),
    ("Results: ", "Wi-Fi 3/3, Contacts 3/4, SMS 5/8 (3 emulator crashes), Markor note plus SMS 6/11 (26 runs)."),
    ("Most valuable finding: ", "in Markor, “Share” attaches the note as a file, which turns the message into an MMS that shows "
                                "“Not sent”. The model still said done: a clear false_done. The fix is to type the text into a new, "
                                "plain SMS. It also found a Back/EXIT loop after a launch that did not bring the SMS app to the front."),
    ("What we did not take over: ", "this runner called the official verifier during a run and gave the result back to the model as a "
                                    "hint. That is like seeing the answer, so we did not use that idea, and runs that depended on it are "
                                    "not counted as results."),
])

h("1.6 Phase D: one team agent (branch team-agent, AutoGLM v63–v65)", 2)
p("The course asks for one agent, so we built the team agent on branch Jia's latest code (it already covered Wi-Fi, Contacts, Calendar "
  "and OsmAnd, had the most tests, and had the evaluation tooling). We did not merge whole code bases: the hayati branch changed the "
  "same core files in conflicting ways, and the integration package is a different program. Instead we added the three missing tasks "
  "ourselves and ported the lessons that the other lines had already learned.")
table([
    ["#", "Practice run (seeds outside the evaluation)", "Result", "What we learned / changed"],
    ["1", "Wi-Fi, seed 1 (v63)", "PASS, 5 steps", "Works as before"],
    ["2", "SMS, seed 1 (v63)", "PASS, 13 steps", "Opened the system Messages app first, then recovered"],
    ["3", "Files, seed 1 (v63)", "PASS, 17 steps", "Works with the official initialization"],
    ["4", "Markor + SMS, seed 1 (v63)", "FAIL", "Our focus check did not recognise Markor's custom editor; fixed (v64), Markor Skill added"],
    ["5", "Markor + SMS, seed 1 (v64)", "FAIL", "Model translated the SMS app name into Chinese; alias table added (v65), as the hayati line had"],
    ["6", "Markor + SMS, seed 1 (v65)", "PASS, 16 steps", "Skill followed: plain SMS, SMS button"],
    ["7", "OsmAnd, seed 8 (v65)", "PASS, 21 steps", "The Files task's setup had deleted OsmAnd's map; our runner now restores it"],
], widths=[0.8, 5.6, 2.6, 7.6])
p("A surprise on the way: AndroidWorld's official initialization of the Files task deletes every file in the phone's shared storage. "
  "That includes OsmAnd's offline map, which is not part of the app snapshot. So before every OsmAnd run the runner now checks that "
  "the map file exists and, if it does not, runs AndroidWorld's official OsmAnd setup again.")
p("Then we froze v65 (git tag team-agent-final-v65) and ran the final evaluation: six tasks with seeds 42, 43 and 44, and OsmAnd with "
  "seeds 31, 314 and 366, which produce exactly the route on the course slide. Both batches have the same source fingerprint.")

h("1.7 All the runs, from the first to the last", 2)
p("We counted every run that has a machine-readable record. Development runs on the three lines plus the final runs give about 300 "
  "recorded runs (exactly 301: 97 on the team-agent/Jia machine, 178 on the hayati branch, 26 in the integration package).")
table([
    ["Task", "Recorded runs", "PASS", "Comment"],
    ["SystemWifiTurnOn", "41", "28", "Solved early; 3/3 in the final"],
    ["CameraTakePhoto", "25", "9", "Warm-up only, not in the final seven"],
    ["ClockTimerEntry", "24", "4", "Never reliable; dropped"],
    ["SystemCopyToClipboard", "37", "4", "Never reliable; dropped"],
    ["ContactsAddContact", "42", "18", "2/3 in the final"],
    ["SimpleSmsSend", "21", "13", "3/3 in the final"],
    ["FilesMoveFile", "23", "12", "2/3 in the final"],
    ["SimpleCalendarAddOneEvent", "10", "7", "3/3 in the final"],
    ["MarkorCreateNoteAndSms", "17", "10", "3/3 in the final"],
    ["OsmAndTrack", "61", "8", "46 runs with 0 passes before the change; 2/3 in the final"],
    ["Total", "301", "113", ""],
], widths=[5.2, 3.0, 2.0, 6.4])
p("275 of these runs (the team-agent/Jia and hayati runs) have a summary with an end reason. They ended as follows: 96 passed, 60 setup "
  "or other errors, 47 stopped by the no-progress rule, 32 invalid model replies, 21 ran out of steps, and 19 were false completions "
  "(the model said done but the verifier said FAIL). The integration package's ledger has no end reasons, so it is not in this split.")

h("1.8 The final evaluation in detail (v65)", 2)
table([
    ["Task", "Run 1", "Run 2", "Run 3", "Passed"],
    ["SystemWifiTurnOn", "PASS (s42, 5 steps)", "PASS (s43, 5)", "PASS (s44, 5)", "3/3"],
    ["ContactsAddContact", "PASS (s42, 12)", "FAIL (s43, 11) other: navigation", "PASS (s44, 11)", "2/3"],
    ["SimpleSmsSend", "PASS (s42, 9)", "PASS (s43, 7)", "PASS (s44, 7)", "3/3"],
    ["FilesMoveFile", "PASS (s42, 17)", "FAIL (s43, 13) false_done", "PASS (s44, 13)", "2/3"],
    ["SimpleCalendarAddOneEvent", "PASS (s42, 20)", "PASS (s43, 21)", "PASS (s44, 16)", "3/3"],
    ["MarkorCreateNoteAndSms", "PASS (s42, 18)", "PASS (s43, 18)", "PASS (s44, 15)", "3/3"],
    ["OsmAndTrack", "PASS (s31, 22)", "PASS (s314, 23)", "FAIL (s366, 16) grounding", "2/3"],
], widths=[4.4, 3.2, 3.6, 3.6, 1.6], size=9)
p("Every run has a screen recording, a trajectory log and a summary. The three failures are analysed on slides 18 and 19.")

h("1.9 Ideas that did not work (and why that is useful)", 2)
bullets([
    "GELab-Zero 4B locally: too slow and wrong action format.",
    "A Skill only in the system prompt: the model ignored it; repeating it each step helped; turning it into code helped most.",
    "Checks based on the model's own description of the screen (v43–v48): the model's description was often wrong, so the checks missed.",
    "Asking the model to first search the country, then the village (OsmAnd): the model never completed that step; widening the search radius worked instead.",
    "Step self-assessment and the unmodified upstream agent: no gain on the hard warm-ups.",
    "Timer and Clipboard: never reliable, so we did not choose them for the final seven.",
    "Using verifier feedback during a run: it would have raised scores, but it is like seeing the answer, so we rejected it.",
])

h("1.10 Where to find everything", 2)
table([
    ["What", "Where"],
    ["Final agent code", "GitHub, branch team-agent, tag team-agent-final-v65 (autoglm_agent.py, run_task.py)"],
    ["Final results and failures", "docs/TEAM_FINAL_EVALUATION.md"],
    ["How the team agent was assembled", "docs/TEAM_AGENT.md"],
    ["OsmAnd improvement (before/after)", "docs/IMPROVEMENT_OSMAND.md"],
    ["Every learning run with cause and fix", "docs/MEDIUM_HARD_TRIALS.md"],
    ["Logs and summaries (exported)", "docs/evidence/ (team, extra, final, followup)"],
    ["Run log: one card per run (course log fields, note, recording, trajectory link)", "docs/RUN_LOG.md, and Run_Log_Final_Evaluation.docx in presentation/"],
    ["Presentation, script, Q&A", "presentation/ (PPTX with embedded demo videos, SCRIPT.md, QA.md)"],
    ["Screen recordings", "Not in git (too large). Zip archives next to the repository, for example team_agent_final_recordings_v65.zip"],
], widths=[5.6, 11.0])
doc.add_page_break()

# ── Part 2 ───────────────────────────────────────────────────────────────────────────────────────
h("Part 2: Every slide explained", 1)
p("For each slide: what it says, where its numbers come from, the words a newcomer may not know, and a likely question. The spoken "
  "script for each slide is in the slide notes and in SCRIPT.md. We present slides 1 to 26 (about 22 minutes of speaking plus 2 minutes of video). Slides 27 to 29 are an appendix after the Thank-you slide: they stay in the file and we only open them if a question needs them.")

slide_section(1, "Cover", "Course, project title, the one-sentence idea of the project, team and lecturers. The three phones show real "
              "screens from our evaluation runs: the OsmAnd route Ruggell to Bendern in the middle, a Markor note and a sent SMS behind it.",
              ask="Which model? Say it right away: AutoGLM-Phone-9B-Multilingual, through the Z.ai API.")

slide_section(2, "At a glance", "The whole result on one slide: one agent, seven tasks, 18 of 21 runs passed the official check.",
              data=[("18 / 21: ", "the final evaluation, one frozen version (v65), three runs per task, judged by the AndroidWorld verifier."),
                    ("7 tasks: ", "two easy, three medium, two hard, from the course's task list (D1 slide 7)."),
                    ("~300 recorded runs: ", "301 runs with records across the whole project (see Part 1, section 1.7)."),
                    ("65 versions: ", "the AutoGLM agent's versions v1 to v65 on the line that became the final agent; every change is written "
                                      "down with its reason. (The early GELab runner had its own v1–v10.)"),
                    ("About 0.065 €: ", "1.45 million tokens for the 21 final runs at 0.045 € per million tokens."),
                    ("1.77 s: ", "median time of one model call in the final runs (296 calls).")],
              terms=[("Frozen: ", "the code was locked with a git tag before the runs."),
                     ("Extra inputs disclosed: ", "two tasks received screen labels in addition to the screenshot, and we say so (slides 6, 13–14 and appendix slide 27).")],
              ask="Is 18/21 the success rate of the agent? It is the result of 21 runs; with three runs per task it is a small sample.")

slide_section(3, "Use case", "Who would use such an agent and why: it works with normal apps and needs only the screen, like a person.",
              data=["The three phones show one real run (Markor note, then the same text as an SMS)."],
              terms=[("No special app interface: ", "the agent does not need an API from the app maker; it taps the normal screen.")])

slide_section(4, "The seven tasks", "Our seven tasks grouped by the course's difficulty rows, with what the agent is told and the "
              "reference number of steps.",
              data=[("Reference steps: ", "the number AndroidWorld lists for each task (course slide D1 p.7): 3, 5, 6, 10, 17, 9, 60."),
                    ("OsmAnd: ", "we use the course slide's exact instance, Ruggell then Bendern.")],
              terms=[("Template task: ", "the slide shows {placeholders}; AndroidWorld fills them from the seed.")],
              ask="Why seven and not three? More tasks show patterns of failure, not single cases.")

slide_section(5, "Model choice", "Why AutoGLM-Phone-9B, and our first attempt with GELab-Zero.",
              data=[("1.77 s median: ", "296 model calls in the final evaluation."),
                    ("19–21 s per screenshot request: ", "measured for GELab-Zero 4B on an RTX 4070 laptop (8 GB GPU), with 22 and 16 layers on the GPU."),
                    ("Contacts 1 PASS in 6 trials: ", "the GELab learning trials."),
                    ("€0.045 per million tokens: ", "the price we pay for the Z.ai API."),
                    ("80.2%: ", "an AutoGLM-Mobile 9B entry on the AndroidWorld community leaderboard. It may not be the exact hosted model we "
                                "call, so the footnote says so and we only say “one of the top-ranked model families”.")],
              terms=[("Ollama: ", "a tool to run models locally."), ("Partial offload: ", "part of the model on the GPU, the rest on the slower processor."),
                     ("Native do(...) / finish(...): ", "AutoGLM's own action format, for example do(action=\"Tap\", element=[500, 335]).")],
              ask="Why not the course model? We started with it; it was too slow on our hardware and its answers did not parse. The course allows any model.")

slide_section(6, "Agent design: the loop", "The agent is one class with one step() method. Each step: observe, decide, check, act, record. "
              "The loop ends when the model says finish or the step budget ends; then the verifier decides.",
              terms=[("Check: ", "our code validates the model's action before the phone sees it (slide 8)."),
                     ("Record: ", "screenshots, model replies and results go to the trajectory log; a screen recorder runs all the time.")],
              ask="Where is step()? In AutoGLMAgent in autoglm_agent.py.")

slide_section(7, "Context and Skills", "What goes into each model request, and the two Skills.",
              data=[("Every request: ", "action rules, a completion rule (what done looks like), the last 20 steps, the newest screenshot, a short status."),
                    ("Markor Skill (text): ", "built from the Markor failure analysis: never use Markor's Share menu; type the text into a new plain SMS."),
                    ("OsmAnd Skill (code): ", "recognises the screen from the GUI tree and states the next step and its tap centre.")],
              terms=[("Completion rule: ", "one sentence per task, for example “the saved contact view shows the exact name and number; a filled form is not enough”.")],
              ask="Is the OsmAnd Skill a script? It suggests, the model decides and acts, and it sometimes ignored the suggestion. It only works for OsmAnd.")

slide_section(8, "Safety net", "Actions are checked before they reach the phone. Refused actions are not executed; the model gets the reason "
              "and one correction in the same step.",
              data=[("8 refusals in the final runs, in 7 of 21 runs: ", "3 typing with no focused text field, 2 malformed replies, 1 unsupported "
                     "action, 1 truncated reply, 1 OsmAnd favourite button."),
                    ("6 of the 7 runs with a refusal still passed.", "")],
              terms=[("Malformed reply: ", "the model did not give exactly one action."), ("Favourite button: ", "on an OsmAnd place card it saves a favourite, not a route point.")])

slide_section(9, "Implementation", "The four parts of the system and how they talk to each other, plus how we run, test and reproduce it.",
              data=[("AutoGLM model: ", "runs on Z.ai's servers; we call it over HTTPS (model name autoglm-phone-multilingual). The API key is in a local .env file and never in git."),
                    ("Agent: ", "the AutoGLMAgent class in autoglm_agent.py. Its step() builds the request (prompt, Skills, task settings), checks the answer and executes one action."),
                    ("Runner: ", "run_task.py sets up the task from its seed, starts the screen recorder, calls step() until the run ends, asks the verifier and writes the logs."),
                    ("Phone: ", "an Android emulator (Pixel 6, Android 13) without a window. AndroidWorld talks to it over adb to read the screen and to tap and type, and it provides the task setup and the verifier."),
                    ("Batch evaluation: ", "evaluate_tasks.py runs tasks × seeds, writes a fingerprint of the source files into every run, and stops if the code changes during a batch."),
                    ("Reproduce: ", "check out the tag team-agent-final-v65 and run evaluate_tasks.py with the seven tasks and seeds 42 43 44 (OsmAnd 31 314 366) and --run-all-seeds. Python 3.11 on a Windows laptop, no GPU needed.")],
              terms=[("adb: ", "Android Debug Bridge, the standard tool a computer uses to control an Android phone or emulator."),
                     ("Headless: ", "the emulator runs without showing a window; the recorder still films its screen."),
                     ("Source fingerprint: ", "hashes of the agent's files; equal fingerprints prove two runs used the same code.")],
              ask="Where is the loop? The runner calls step() again and again; each call does observe, decide, check, act, record (slide 6).")

slide_section(10, "One run step by step", "Markor with seed 44 (15 steps, PASS): six screenshots and, under each, a sentence from the model's own reasoning in the log.",
              data=["Steps 2, 4, 8, 10, 14 and 15 of run trial_MarkorCreateNoteAndSms_20261008T222633_440045Z."],
              ask="Did the model really write these sentences? Yes, they are verbatim from its replies in the trajectory log.")

slide_section(11, "How we tested", "One frozen version, three runs per task, the official verifier, and one log row per run in the course's format.",
              data=[("Tag team-agent-final-v65: ", "both batches recorded the same source fingerprint (hashes of the agent's files)."),
                    ("Seeds 42, 43, 44 for six tasks; 31, 314, 366 for OsmAnd: ", "these three OsmAnd seeds all produce the slide's route."),
                    ("Step budgets: ", "about 2 to 4 times the reference steps (Wi-Fi 12, Contacts 16, SMS 20, Files 25, Calendar 35, Markor 40, OsmAnd 90)."),
                    ("Three boxes: ", "what we keep for every one of the 21 runs: a summary row in the course's log fields (D1 p.49), written by the runner during the run; "
                                      "the trajectory log (every screenshot, model reply, check and result); and the screen recording. The full log follows on slides 13 and 14.")],
              ask="Why not rerun failures? Rerunning the same code until it passes only measures luck.")

slide_section(12, "Results", "All 21 runs: blue PASS, orange FAIL with its failure class.",
              data=["Wi-Fi, SMS, Calendar, Markor 3/3; Contacts, Files, OsmAnd 2/3. Hard tasks together 5/6.",
                    "The “s” number in each cell is the task seed."])

slide_section(13, "Run log (1/2): one row per run", "The course's run log (D1 p.49: “Friday's presentation is this table, sorted”), one row per run, sorted by task. This part has the five single-app tasks.",
              data=[("Columns: ", "task, run (1 to 3), seed, observation, steps used / step budget, verifier result, failure class, number of video clips, and a short note."),
                    ("Same for every run: ", "model AutoGLM-Phone-9B (Z.ai), version v65, grounding by coordinates. To save space they are in the grey line above the table."),
                    ("Links: ", "each run number (“1 of 3”) opens that run's readable trajectory log on GitHub."),
                    ("Clips: ", "Android's screen recorder stops after 180 seconds, so the runner starts a new clip; longer runs have 2 to 4 clips."),
                    ("Orange rows: ", "the two failures here, Contacts s43 (other: navigation) and Files s43 (false_done)."),
                    ("Source: ", "the rows come from each run's summary.json, written by the runner while the run happened.")],
              terms=[("Chinese app name: ", "the model sometimes wrote the app name in Chinese; with one allowed app the runner can still resolve it.")],
              ask="Where are the videos? Not in git because of their size. Every clip is in team_agent_final_recordings_v65.zip, in a folder named after the run ID. docs/RUN_LOG.md lists each run with its clips and log link.")

slide_section(14, "Run log (2/2): the two multi-app tasks", "The same table for Markor + SMS and OsmAnd, with longer notes because these runs have more going on.",
              data=["Markor: all three runs followed the Skill (save the note, then send the same text as a plain SMS); run 1 needed the alias table for a Chinese app name; run 2 had one truncated reply that was retried.",
                    "OsmAnd run 1: the runner first restored the map, because the Files runs had cleared shared storage. Runs 1 and 2 passed in 22 and 23 steps of 90.",
                    "OsmAnd run 3 (FAIL, grounding): Ruggell became route point 1, then the model tapped Clear at [941, 57] instead of [941, 83] three times. Analysed on slide 19."],
              terms=[("Alias table: ", "a small list in our code that maps other names of an app (for example Chinese ones) to the real app.")])

slide_section(15, "Demo: all 21 runs", "One video with all 21 final runs at once. Columns are tasks, rows are runs.",
              data=["Each clip is sped up so that all end within 45 seconds; the label shows the speed (x2 = twice as fast) and PASS/FAIL.",
                    "Each clip stops on its final screen. Orange labels mark the three failures."],
              terms=[("Embedded video: ", "the video is inside the PowerPoint file; click it to play.")])

slide_section(16, "Demo: one success, one failure", "Markor seed 44 at 4x speed (PASS) and Files seed 43 at 3x speed (FAIL).",
              data=["Watch the file names in the Files grid: they are cut off, and the agent picks a look-alike file."])

slide_section(17, "How 275 project runs ended", "End reasons of all runs with a machine-readable summary, from the first tests to the final.",
              data=["PASS 96; setup or other errors 60; no-progress stops 47; invalid replies 32; step budget used up 21; said done but verifier FAIL 19.",
                    "Setup errors are the largest failure group: emulator, recorder or a crashed service, not the model.",
                    "The card lists the five failure classes from D1 p.50, and the final evaluation's classes: false_done 1, grounding 1, other 1."],
              terms=[("No-progress stop: ", "our rule stops a run when the same action repeats and the screen does not change."),
                     ("Invalid reply: ", "two broken answers in one step end the run.")])

slide_section(18, "Deep dive: Files, seed 43", "Our main failure analysis. Task: move documentary.mp4 from Alarms to Movies.",
              data=["Step 5: the Files grid shows cut-off names (“documentary_20…”). The model picked that file and wrote "
                    "“…matches the required file documentary.mp4 (assuming it is named differently here)”, inventing the full name.",
                    "Steps 6–11: correct moving steps, but on the wrong file. Steps 12–13: waited for “Moving 1 item” and finished.",
                    "Verifier: FAIL, because documentary.mp4 never moved. Class: false_done; root cause: a look-alike chosen from a truncated name.",
                    "Fix layers: instruction (use list view or search the exact name) and program (check the full name before Move)."],
              terms=[("Distractor files: ", "AndroidWorld adds files with similar names to make the task realistic.")])

slide_section(19, "Two more failures, and why runs differ", "Contacts seed 43 and OsmAnd seed 366, plus a table showing that the same task can pass on one run and fail on another.",
              data=["Contacts s43: two swipes moved the form past the Phone field; four more swipes changed only the blinking cursor, and our own "
                    "change check counted that as a change, so the model was told its swipe worked. Class: other (navigation).",
                    "OsmAnd s366: our code said “Tap Clear at [941, 83]”; the model tapped [941, 57], the top edge of the button, three times. Class: grounding.",
                    "Table: OsmAnd was 2/3 in two separate frozen evaluations (v61, v65) but a different run failed each time; Contacts seed 43 passed in v42 and failed in v65."],
              ask="Did the agent get worse? Not necessarily: each run starts fresh, and long tasks give more chances for one small error.")

slide_section(20, "Test-setup problems", "Problems that were not the model's fault, and their fixes.",
              data=["Black screenshots (emulator graphics mode), recorder stopped (Android tools restarted their server), app start timeouts (5 s too short).",
                    "“keeps stopping” dialog: AndroidWorld's accessibility service crashed in 11 of 25 OsmAnd runs from v49 on; the model closes it and the empty screen read is repeated.",
                    "OsmAnd map missing: the Files task's initialization deletes shared storage; the runner now restores the map."],
              terms=[("Harness: ", "everything around the model: emulator, recorder, runner, verifier.")])

slide_section(21, "The hardest task: from zero passes to two of three", "All OsmAnd runs grouped by version phase, with how many passed.",
              data=["v30–v42 (Skill as text): 26 runs, 0 passed. v43–v48 (rules on the model's words): 10, 0. v49–v58 (reads the screen): 10, 0.",
                    "v59–v62 (Skill as code): 11 runs, 5 passed. v63–v65 (final agent): 4 runs, 3 passed.",
                    "So 46 runs without a pass, then 8 passes in the next 15. Fixes were tested on practice seeds, never on the evaluation seeds."])

slide_section(22, "Before and after", "The documented improvement: same frozen code (v61), same seeds, same model; only the Skill on or off.",
              data=["Verifier PASS 0/3 → 2/3; searched the place name only 0/3 → 3/3; route started with a searched place 0/3 → 2/3; saved a track 0/3 → 2/3; mean steps 23.3 → 18.7.",
                    "Chart: text Skill only (v42, other seeds) 0; no Skill (v61) 0; Skill as code (v61) 2; final agent (v65) 2.",
                    "Without the Skill the model typed “Ruggell, Liechtenstein” (finds only the country) and two runs used navigation, which never saves a track."],
              ask="Is it fair? Only one setting changed, and both batches have the same source fingerprint. Three runs per side is still small.")

slide_section(23, "Lessons built into the final agent", "Each failure we saw, its cause, the change, and the final result.",
              data=["Markor “Not sent” → Markor Skill → Markor 3/3.",
                    "Markor typing refused (custom editor) → focus check fixed → Markor 3/3.",
                    "SMS app name in Chinese → alias table → Markor 3/3.",
                    "OsmAnd map missing → map check plus official setup → OsmAnd 2/3.",
                    "OsmAnd 0/3 → Skill as code plus GUI tree → OsmAnd 2/3.",
                    "38 automatic offline tests; each fix has a test that fails on the old code and passes on the new code."])

slide_section(24, "Our work in numbers", "Six numbers behind the result.",
              data=["~300 recorded runs; 65 agent versions; 1,453 steps and 1,642 model calls in the runs of this agent's line on our machine; "
                    "38 offline tests; 0.48 € model cost of all those local runs."])

slide_section(25, "Findings and limitations", "What we learned and what is still limited.",
              data=["Findings: trust the harness first; the verifier decides; where knowledge lives matters (prompt < reminder each step < code); "
                    "long tasks fail by small errors; checks catch traps (8 in the final runs).",
                    "Limitations: three runs per task; one model, one laptop, one emulator; the OsmAnd Skill only works for OsmAnd; two tasks used "
                    "extra screen labels; fixes after the freeze are not evaluated."])

slide_section(26, "Thank you", "Repository, branch and tag, model and benchmark. The questions and short answers we prepared are in QA.md.")

slide_section(27, "Appendix: actions and observation", "The seven actions the model may use, with real examples, and what the agent sees in each task.",
              data=[("Wi-Fi: ", "screenshot plus text labels from the Settings app (UIAutomator)."),
                    ("OsmAnd: ", "screenshot plus the accessibility tree, plus the coded Skill."),
                    ("Other five tasks: ", "screenshot only (Markor also gets a text Skill).")],
              terms=[("0–1000 grid: ", "the model gives positions as if the screen were 1000 by 1000, whatever its real size."),
                     ("Accessibility tree: ", "the list of on-screen elements a screen reader uses; AndroidWorld provides it.")],
              ask="Is the tree cheating? No; AndroidWorld provides it and the course's own example log lists it as an observation type. It changes "
                  "what we measure, so we report it per task.")

slide_section(28, "Appendix: steps versus the reference", "Mean steps of passing runs compared with the course's reference steps and our step budget.",
              data=["Ours: Wi-Fi 5, Contacts 11.5, SMS 7.7, Files 15, Calendar 19, Markor 17, OsmAnd 22.5.",
                    "Reference: 3, 5, 6, 10, 17, 9, 60. Budget: 12, 16, 20, 25, 35, 40, 90.",
                    "Markor uses about twice the reference because the agent types the text twice (note and SMS) instead of sharing it; OsmAnd uses far fewer than the reference because the Skill leads the shortest path."])

slide_section(29, "Appendix: speed and cost", "Mean run time per task and the cost of the final evaluation.",
              data=["Mean run time (s): Wi-Fi 71, Contacts 95, SMS 71, Files 109, Calendar 153, Markor 261, OsmAnd 537. Times include app start, "
                    "setup and recording; one OsmAnd run also included restoring the map.",
                    "1.45 M tokens (1,423,741 prompt + 23,737 completion) × 0.045 € per million = about 0.065 €.",
                    "All runs on our machine together: 10.8 M tokens, about 0.48 €."])

out = HERE / "Team_Briefing_AndroidWorld_Agent.docx"
doc.save(out)
print("saved", out)
