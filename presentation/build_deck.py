"""Build the group presentation as an editable PowerPoint file with embedded videos and speaker notes.

usage: python build_deck.py   (writes AndroidWorld_GUI_Agent_Presentation.pptx and SCRIPT.md next to this file)
Numbers come from presentation/data/facts.json (computed from the run records) and docs/TEAM_FINAL_EVALUATION.md.
"""
import json
from pathlib import Path
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from deck_lib import *

HERE = Path(__file__).resolve().parent
IMG, VID = HERE / "images", HERE / "videos"
F = json.loads((HERE / "data" / "facts.json").read_text(encoding="utf-8"))
prs = new_deck()
BLANK = prs.slide_layouts[6]
SLIDES = []          # (title, script) for SCRIPT.md


def slide(kicker, title, script):
    s = prs.slides.add_slide(BLANK)
    number = len(prs.slides)
    if kicker is not None:
        header(s, kicker, title, number, None)
    notes(s, script)
    SLIDES.append((title, script))
    return s


# 1 ─ Title ───────────────────────────────────────────────────────────────────────────────────────
s = slide(None, "Title", """
Hello everyone, and thank you for having us.
Our project is a GUI agent for Android. A GUI agent uses a phone the way a person does: it looks at the screen and decides where to tap or what to type.
In the next 25 minutes we will show how we built one agent, how we tested it on seven AndroidWorld tasks, where it failed, and how we improved it.
""")
# Left: navy panel with course, project title and team. Right: three real screens from our runs as phones.
SOFT = RGBColor(0xB9, 0xC4, 0xD6)
rect(s, 0, 0, W, H, fill=RGBColor(0xEE, 0xF3, 0xF8))
rect(s, 0, 0, 7.9, H, fill=NAVY)
rect(s, 0, 0, 7.9, 0.08, fill=BLUE)
text(s, 0.75, 0.7, 6.8, 0.35, "AGENTIC AI IN MODERN BUSINESS  \u00b7  PRESENTATION", size=13, bold=True, color=LIGHT)
text(s, 0.75, 1.02, 6.8, 0.35, "TUM School of Management", size=13, color=SOFT)
text(s, 0.75, 1.6, 7.0, 1.3, "One GUI agent for seven\nAndroidWorld tasks", size=34, bold=True, color=WHITE, spacing=1.0)
text(s, 0.75, 3.05, 6.6, 0.85, "An agent that looks at the phone screen and decides where to tap, "
     "evaluated with the official AndroidWorld verifier.", size=16, color=SOFT, spacing=1.15)
rect(s, 0.75, 4.15, 1.1, 0.06, fill=BLUE)
text(s, 0.75, 4.65, 3.8, 0.3, "TEAM MEMBERS", size=11, bold=True, color=LIGHT)
members = [("Danh Phuong Le", "03824340"), ("Ssu-Cheng Chen", "03827578"), ("Hayati \u00d6mer Ko\u00e7", "03801613"),
           ("Jia Qi", "03812325"), ("Tin Nghia Nguyen", "03826855")]
text(s, 0.75, 4.98, 2.5, 1.9, "\n".join(m for m, _ in members), size=13, color=WHITE, spacing=1.28)
text(s, 3.2, 4.98, 1.4, 1.9, "\n".join(i for _, i in members), size=13, color=SOFT, spacing=1.28)
text(s, 5.05, 4.65, 2.6, 0.3, "LECTURERS", size=11, bold=True, color=LIGHT)
text(s, 5.05, 4.98, 2.6, 1.2, "Haoyuan Jiang\nXuerui Zhang\nZhenyu Wang", size=13, color=WHITE, spacing=1.28)


def phone(path, x, y, h, angle=0, crop=0.08):
    pic = s.shapes.add_picture(str(path), Inches(x), Inches(y), height=Inches(h))
    pic.crop_top = crop                                   # hide AndroidWorld's debug overlay above the app
    pic.height = int(pic.height * (1 - crop))
    pic.auto_shape_type = MSO_SHAPE.ROUNDED_RECTANGLE
    pic.line.color.rgb = RGBColor(0x1B, 0x1F, 0x2A)
    pic.line.width = Pt(6)
    pic.rotation = angle
    return pic


phone(IMG / "traj_6.png", 8.1, 1.45, 4.9, -8)
phone(IMG / "traj_3.png", 10.5, 1.45, 4.9, 8)
phone(IMG / "osmand_pass_4.png", 9.15, 0.85, 5.75)
text(s, 7.9, 6.75, 5.43, 0.35, "Real screens from our evaluation runs", size=11, color=GREY, align=PP_ALIGN.CENTER)

# 2 ─ At a glance ─────────────────────────────────────────────────────────────────────────────────
s = slide("At a glance", "One agent, seven tasks: 18 of 21 runs passed the official check", f"""
Here is the short version.
We built one agent and gave it seven tasks from AndroidWorld, from easy to the hardest one on the course list. Each task ran three times on one frozen version, and every run was screen-recorded.
18 of the 21 runs passed. Pass means the official AndroidWorld checker looked at the phone's data and confirmed the task was done. The model's own "I am done" does not count.
Behind this result there is a lot of work: about {F['project_runs']} recorded runs across the project and {F['versions']} versions of the agent.
And it was cheap: the model cost for all 21 final runs was about {F['final_cost_eur']} euro.
""")
for i, (value, label) in enumerate([("18 / 21", "runs passed the official\nAndroidWorld verifier"),
                                     ("7 tasks", "covering easy, medium\nand hard (D1 task list)"),
                                     (f"~{F['project_runs']}", "recorded runs across\nthe whole project"),
                                     (f"{F['versions']}", "agent versions, each\nchange tested and logged")]):
    x = 0.7 + i * 3.02
    rect(s, x, 1.6, 2.85, 2.05, fill=PALE_BLUE if i == 0 else PALE)
    rect(s, x, 1.6, 2.85, 0.07, fill=BLUE)
    big_number(s, x + 0.2, 1.85, 2.55, value, label, value_size=44 if i == 0 else 38)
card(s, 0.7, 4.0, 3.8, 2.55, "Rigorous", ["One frozen version for all 21 runs", "Every run screen-recorded", "Official checker decides success"], body_size=16, title_size=18)
card(s, 4.75, 4.0, 3.8, 2.55, "Cheap and fast", [f"About {F['final_cost_eur']} € model cost for 21 runs", f"{F['median_call_s']} s median per model call", "Hosted model, laptop without GPU"], body_size=16, title_size=18)
card(s, 8.8, 4.0, 3.8, 2.55, "Honest", ["Failures kept, analysed, not rerun", "Fixes tested on other task seeds", "Extra inputs disclosed per task"], accent=ORANGE, body_size=16, title_size=18)

# 3 ─ Use case ────────────────────────────────────────────────────────────────────────────────────
s = slide("Use case", "A phone assistant that uses apps the way a person does", """
Our use case is a phone assistant for everyday tasks.
You tell it in plain words what you want, for example "Send this message to this number", and it opens the right app and does the steps on the screen.
This is useful because it works with normal apps. It needs no special interface from the app maker. It only needs the screen, like a person.
In business this helps with three things: helping people who find phones hard to use, saving time on repeated phone tasks, and testing apps automatically.
""")
card(s, 0.7, 1.65, 3.9, 1.55, "Who it helps", "People who find phones hard to use, busy users with repeated tasks, teams that test apps.")
card(s, 0.7, 3.4, 3.9, 1.55, "What it needs", "Only the screen: no special app interface. It reads, taps, types and swipes like a person.")
card(s, 0.7, 5.15, 3.9, 1.55, "What it is told", "One sentence in plain English, for example: “Create a note named … and share its content via SMS.”")
if (IMG / "traj_1.png").exists():
    for i, name in enumerate(["traj_1.png", "traj_3.png", "traj_6.png"]):
        picture(s, IMG / name, 5.0 + i * 2.65, 1.65, h=5.05, phone=True)
    text(s, 5.0, 6.72, 7.6, 0.3, "One of our runs: a note in Markor, then the same text sent as an SMS", size=11, color=GREY)

# 4 ─ Tasks ───────────────────────────────────────────────────────────────────────────────────────
s = slide("Tasks", "Seven tasks from all three difficulty rows of the course list", """
The course asks for at least three tasks, at least one from each difficulty row. We chose seven, so we could see patterns, not just single cases.
Two warm-up tasks: turn on Wi-Fi and add a contact.
Three real-work tasks: send an SMS, move a file, and add a calendar event with date, time and length.
Two multi-app tasks: write a note in Markor and send it by SMS, which uses two apps, and OsmAndTrack, the hardest task on the list, with a reference of 60 steps.
For the six template tasks AndroidWorld fills in random names and numbers. For OsmAnd we used exactly the route on the course slide: Ruggell, then Bendern.
""")
rows = [["Row", "Task", "What the agent is told (short)", "Reference steps"],
        ["Warm-up", "SystemWifiTurnOn", "Turn Wi-Fi on", "3"],
        ["Warm-up", "ContactsAddContact", "Create a contact with a name and number", "5"],
        ["Real work", "SimpleSmsSend", "Send a message to a number with Simple SMS Messenger", "6"],
        ["Real work", "FilesMoveFile", "Move a file from one folder to another", "10"],
        ["Real work", "SimpleCalendarAddOneEvent", "Create an event on a date and hour, with title and length", "17"],
        ["Multi-app", "MarkorCreateNoteAndSms", "Create a note, then share its text with a number via SMS", "9"],
        ["Multi-app", "OsmAndTrack", "Save a track: Ruggell, then Bendern (the slide's instance)", "60"]]
fills = {}
for r in range(1, 8):
    tone = PALE_BLUE if r <= 2 else (PALE if r <= 5 else PALE_ORANGE)
    for c in range(4):
        fills[(r, c)] = tone
table(s, 0.7, 1.7, 11.9, 4.4, rows, col_widths=[1.5, 3.0, 5.9, 1.5], size=14, fills=fills, align_center_from=3)
text(s, 0.7, 6.3, 11.9, 0.6, "Reference steps: the number of steps AndroidWorld lists for each task (course slide D1 p.7).", size=12, color=GREY)

# 5 ─ Model choice ────────────────────────────────────────────────────────────────────────────────
s = slide("Model", "Why AutoGLM-Phone-9B, and what we tried first", f"""
Next, the model. The course says any model is fine, as long as we name it. Ours is AutoGLM-Phone-9B-Multilingual, which we use through the Z.ai API.
We did not start with it. Our first versions used GELab-Zero 4B, the model on the course slide, running locally with Ollama on a laptop GPU with 8 gigabytes of memory. The model did not fit completely on the GPU, so one screenshot request took about 20 seconds. Only one of six Contacts trials passed, and in a Wi-Fi run the model answered in a format our parser could not accept, and even said Wi-Fi was on when it was not. That was our first unsuccessful attempt.
AutoGLM is trained for phone screens and has a clear action format. Our median time per model call was {F['median_call_s']} seconds, and the price is 0.045 euro per million tokens.
On the AndroidWorld leaderboard a 9B AutoGLM-Mobile entry is listed at 80.2 percent. That entry may not be the exact hosted version we use, so we only say it is one of the top-ranked model families.
""")
rows = [["", "AutoGLM-Phone-9B (Z.ai API)", "GELab-Zero 4B (local, Ollama)"],
        ["Built for", "Phone GUI control", "Phone GUI control"],
        ["Where it runs", "Hosted API", "Laptop GPU (8 GB), partial offload"],
        ["Speed per model call", f"{F['median_call_s']} s median ({F['calls_final']} calls)", "19–21 s per screenshot request"],
        ["Action format", "Native do(...) / finish(...), parsed reliably", "Bare tokens our parser rejected"],
        ["Cost", "€0.045 per million tokens", "Free, but slow"],
        ["Our results", "18 / 21 in the final evaluation", "Contacts: 1 PASS in 6 trials"],
        ["Leaderboard", "AutoGLM-Mobile (9B) 80.2% on AndroidWorld*", "—"]]
table(s, 0.7, 1.7, 8.1, 4.45, rows, col_widths=[2.1, 3.2, 2.8], size=13, bold_first_col=True)
card(s, 9.1, 1.7, 3.55, 4.4, "Our first attempt (v1–v10)", [
    "Started with GELab-Zero, the model on the course slide",
    "Model larger than the 8 GB GPU: ~20 s per screenshot request",
    "Contacts: 1 of 6 trials passed",
    "Wi-Fi: invalid action format, false “Wi-Fi is on”",
    "Switched to the hosted AutoGLM model"], accent=ORANGE, body_size=13)
text(s, 0.7, 6.25, 11.9, 0.7, "* Community leaderboard entry (google-research/android_world); the listed checkpoint may differ from the hosted model we call.", size=11, color=GREY)

# 6 ─ Architecture ────────────────────────────────────────────────────────────────────────────────
s = slide("Agent design", "One class, one step(): observe, decide, check, act, record", """
This is how the agent works. It is one Python class with one method, step, as the course asks.
Each step does five things.
First, observe: take a screenshot of the phone.
Second, decide: send the task, the recent history and the screenshot to the model. The model answers with one action, for example tap at this point, or type this text.
Third, check: our code checks the action before anything happens on the phone. Is the format valid? Is the point on the screen? Is a text field really focused before we type?
Fourth, act: run the action on the emulator.
Fifth, record: save the screenshot, the model's answer and the result in the trajectory log, while the screen recorder runs.
This repeats until the model says finish or the step budget ends. Then the official checker decides pass or fail. All seven tasks use this same class.
""")
steps = [("1  Observe", "Screenshot\n(+ GUI labels for\nsome tasks)"), ("2  Decide", "AutoGLM picks\none action"),
         ("3  Check", "Format, screen point,\nfocus, task rules"), ("4  Act", "Tap, type, swipe,\nlaunch, back"),
         ("5  Record", "Trajectory log\n+ screen video")]
for i, (t, b) in enumerate(steps):
    x = 0.7 + i * 2.45
    rect(s, x, 1.9, 2.05, 2.0, fill=PALE_BLUE if i != 2 else PALE_ORANGE, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
    text(s, x + 0.1, 2.1, 1.85, 0.4, t, size=16, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    text(s, x + 0.08, 2.5, 1.89, 1.35, b, size=14, color=INK, align=PP_ALIGN.CENTER)
    if i < 4:
        arrow(s, x + 2.08, 2.87, x + 2.42, 2.87, color=BLUE)
text(s, 0.7, 4.3, 11.9, 0.45, "repeat until the model says finish, or the step budget ends  →  official AndroidWorld verifier: PASS / FAIL",
     size=15, bold=True, color=BLUE, align=PP_ALIGN.CENTER, fill=PALE)
card(s, 0.7, 5.05, 5.8, 1.75, "step() in AutoGLMAgent (autoglm_agent.py)", "Reads the screen and the task, chooses one action, checks it, executes it, and reports whether the model said it is done.")
card(s, 6.8, 5.05, 5.8, 1.75, "Same agent for all seven tasks", "Task-specific knowledge is loaded as data (completion rule, optional Skill). The model still decides every action.")

# 7 ─ Actions and observation ─────────────────────────────────────────────────────────────────────
s = slide("Agent design", "What the agent can do, and what it sees in each task", """
The model can use seven actions: tap, type, swipe, launch an app, go back, wait, and finish. Taps use coordinates on a grid from 0 to 1000.
What the agent sees is the screenshot. For two tasks it also gets text labels of the screen elements. For Wi-Fi these come from the Settings app. For OsmAnd they come from AndroidWorld's accessibility tree, the same information a screen reader uses.
We show this openly because it changes what we measure: five tasks were solved from the screenshot alone, two had extra help. The course example log on slide 49 also lists "accessibility tree" as an observation type, so this is allowed, but it must be reported.
""")
rows = [["Action", "Example"], ["Tap", "do(action=\"Tap\", element=[500, 335])"], ["Type", "do(action=\"Type\", text=\"Ruggell\")"],
        ["Swipe", "do(action=\"Swipe\", start=[500,560], end=[500,260])"], ["Launch", "do(action=\"Launch\", app=\"markor\")"],
        ["Back / Wait", "do(action=\"Back\")"], ["Finish", "finish(message=\"Track saved\")"]]
table(s, 0.7, 1.7, 5.6, 4.0, rows, col_widths=[1.4, 4.2], size=12, bold_first_col=True)
rows = [["Task", "Observation"], ["Wi-Fi", "Screenshot + Settings labels"], ["Contacts", "Screenshot only"], ["SMS", "Screenshot only"],
        ["Files", "Screenshot only"], ["Calendar", "Screenshot only"], ["Markor + SMS", "Screenshot only (+ text Skill)"],
        ["OsmAnd", "Screenshot + accessibility tree (+ coded Skill)"]]
fills = {(1, 1): PALE_BLUE, (7, 1): PALE_ORANGE}
table(s, 6.6, 1.7, 6.0, 4.0, rows, col_widths=[1.8, 4.2], size=12, bold_first_col=True, fills=fills)
text(s, 0.7, 5.95, 11.9, 0.9, "Grounding: coordinates on a 0–1000 grid. Where labels are given, the step text also lists each label's tap centre.",
     size=13, color=GREY)

# 8 ─ Context and Skills ──────────────────────────────────────────────────────────────────────────
s = slide("Agent design", "Context and Skills: what goes into each model request", """
What does the model receive at each step?
A system prompt with the action rules and a short completion rule, for example: the contact must be saved, a filled form is not enough.
The last 20 steps of history, the newest screenshot, and a short status text.
For two tasks we add a Skill. A Skill is app knowledge, loaded only for its task, as in the course's Skills idea.
For Markor it is text: use a plain SMS, never Markor's Share menu, because that sends an MMS that fails.
For OsmAnd the Skill is code. It reads the screen and tells the model the next step and where to tap. The model still decides and acts, and it did not always follow the advice.
So nothing is a fixed list of taps. The model makes every decision.
""")
card(s, 0.7, 1.7, 3.85, 3.95, "Every request", ["System prompt: action rules", "Completion rule: what “done” looks like", "Last 20 steps of history", "Newest screenshot", "Status: step number, last result"], body_size=15, title_size=18)
card(s, 4.75, 1.7, 3.85, 3.95, "Markor Skill (text)", ["Loaded only for this task", "Fact: Share attaches the file and makes a failing MMS", "Procedure: name + extension, Save, launch SMS, plain text, SMS button", "Repeated each step as a reminder"], body_size=15, title_size=18)
card(s, 8.8, 1.7, 3.85, 3.95, "OsmAnd Skill (code)", ["Recognises the screen from the GUI tree", "States the next step and its tap centre", "Refuses actions the screen shows to be wrong", "Model still chooses every action"], accent=ORANGE, body_size=15, title_size=18)
text(s, 0.7, 5.9, 11.95, 0.75, "No fixed list of taps: Skills add app knowledge, the model makes every decision.", size=17, bold=True, color=BLUE, align=PP_ALIGN.CENTER, fill=PALE, anchor=MSO_ANCHOR.MIDDLE)

# 9 ─ Safety net ──────────────────────────────────────────────────────────────────────────────────
s = slide("Agent design", "A safety net: actions are checked before they reach the phone", f"""
Our check step catches bad actions before they happen.
The general checks work for every task: an action must have the right format, a point must be on the screen, and typing is only allowed when a text field is focused. Otherwise the text would go nowhere.
Task checks protect against known traps. For OsmAnd, the star button on a place card saves a favourite, not a route point, so we refuse it.
When we refuse an action, the model gets one correction in the same step, with the reason.
In the 21 final runs these checks stopped {F['refusals_total']} actions. Without them, some of these passing runs would have failed.
""")
rows = [["Check", "Why", "Final runs"]] + [[a, b, str(c)] for a, b, c in F["refusal_rows"]]
table(s, 0.7, 1.7, 7.3, 0.45 * len(rows), rows, col_widths=[2.6, 3.6, 1.1], size=13, bold_first_col=True, align_center_from=2)
card(s, 8.3, 1.7, 4.35, 2.95, "How a refusal works", ["The action is not executed", "The model gets the reason in the same step", "One correction per step; a second invalid reply ends the run", "All refusals are logged"], body_size=14, title_size=17)
big_number(s, 0.7, 4.95, 3.5, f"{F['refusals_total']}", "actions stopped in the final runs\n(7 of 21 runs had one or more)", value_size=40)
text(s, 4.4, 5.05, 8.25, 1.5, "Without these checks, the agent would have typed into nothing, saved a favourite instead of a route point, or acted on a broken reply. Six of the seven runs with a refusal still passed.", size=15, color=INK)

# 10 ─ Trajectory ─────────────────────────────────────────────────────────────────────────────────
traj = [m for m in F.get("traj", [])]
s = slide("Trajectory", "One run, step by step: a Markor note sent as an SMS", """
Here is one full run from the final evaluation, Markor with seed 44. It passed in 15 steps.
The model opened Markor and tapped plus. In the new file dialog it typed the name and set the extension.
It typed the note text and saved it. Then it launched Simple SMS Messenger, started a new conversation, entered the number, typed the same text and pressed the SMS button.
At the end it saw the sent message and called finish. The checker then confirmed both parts: the note exists with the right text, and the SMS was sent to the right number.
Under each picture you see a sentence from the model's own reasoning, taken from the log.
""")
for i, m in enumerate(traj[:6]):
    x = 0.55 + i * 2.08
    picture(s, IMG / m["file"], x + 0.08, 1.55, h=3.7, phone=True)
    rect(s, x - 0.04, 5.15, 1.96, 1.8, fill=PALE)
    text(s, x + 0.04, 5.2, 1.8, 0.3, f"Step {m['step']}", size=13, bold=True, color=BLUE)
    text(s, x + 0.04, 5.5, 1.82, 1.45, "“" + m["model_quote"] + "”", size=10.5, color=INK, spacing=1.05)

# 11 ─ Evaluation method ──────────────────────────────────────────────────────────────────────────
s = slide("Evaluation", "How we tested: one frozen version, three runs per task", """
How did we test?
First, we froze the code. The final version has a git tag, and both evaluation batches have the same source fingerprint, so all 21 runs come from exactly the same agent.
Each task ran three times with fixed task seeds, 42, 43 and 44. For OsmAnd we used 31, 314 and 366, because these three seeds produce exactly the route on the course slide.
Success is decided only by the official AndroidWorld verifier, which reads the phone's data.
Every run has a screen recording, a step-by-step log, and one summary row with the fields from the course: task, run, model, observation, grounding, steps, verifier, failure class, recording and a note.
We did not rerun failures. A rerun of the same code only measures luck.
""")
card(s, 0.7, 1.7, 3.9, 2.35, "Frozen", ["Git tag team-agent-final-v65", "Same source fingerprint in both batches", "No changes during the batch"], body_size=15, title_size=17)
card(s, 4.75, 1.7, 3.9, 2.35, "Three runs per task", ["Seeds 42, 43, 44", "OsmAnd: 31, 314, 366 = the slide's route", "Failures kept, never rerun"], body_size=15, title_size=17)
card(s, 8.8, 1.7, 3.85, 2.35, "Judged independently", ["Official AndroidWorld verifier", "The model's “finish” never counts", "Step budget about 2–4× reference"], body_size=15, title_size=17)
rows = [["task", "run", "model", "observation", "grounding", "steps", "verifier", "failure class", "recording"],
        ["FilesMoveFile", "2 of 3", "autoglm-phone", "screenshot", "coordinates", "13 / 25", "FAIL", "false_done", "video_001.mp4"]]
table(s, 0.7, 4.4, 11.95, 0.85, rows, col_widths=[1.55, 0.85, 1.75, 1.35, 1.35, 0.95, 1.0, 1.4, 1.75], size=13, align_center_from=1)
text(s, 0.7, 5.35, 11.95, 1.2, "One row per run, as on the course slide (D1 p.49). All 21 rows, the logs and the recordings are kept in the repository and the recording archive.",
     size=13, color=GREY)

# 12 ─ Results ────────────────────────────────────────────────────────────────────────────────────
s = slide("Results", "18 of 21 runs passed; every task passed at least twice", """
Here are all 21 runs. Blue is pass, orange is fail.
Wi-Fi, SMS, Calendar and Markor passed all three runs.
Contacts, Files and OsmAnd passed two of three.
Both multi-app tasks together passed five of six, including OsmAndTrack, the hardest task on the list.
The three failures are all different. One is a false finish, one is a missed tap, and one is a navigation problem. We will look at each of them in a moment.
Please keep in mind that three runs is a small sample. Three of three does not mean the task always works.
""")
order = F["result_rows"]
rows = [["Row", "Task", "Run 1", "Run 2", "Run 3", "Passed"]]
fills = {}
for r, item in enumerate(order, start=1):
    cells = []
    for c, run in enumerate(item["runs"]):
        cells.append(f"PASS  s{run['seed']}" if run["pass"] else f"FAIL  s{run['seed']}\n{run['class']}")
        fills[(r, c + 2)] = BLUE if run["pass"] else ORANGE
    rows.append([item["row"], item["task"], *cells, f"{sum(x['pass'] for x in item['runs'])}/3"])
table(s, 0.7, 1.65, 11.95, 4.95, rows, col_widths=[1.3, 3.3, 2.1, 2.1, 2.1, 1.05], size=13, fills=fills, align_center_from=2, bold_first_col=False)
text(s, 0.7, 6.65, 11.95, 0.35, "s = task seed. Official AndroidWorld verifier. One frozen version (tag team-agent-final-v65).", size=11, color=GREY)

# 13 ─ Efficiency ─────────────────────────────────────────────────────────────────────────────────
s = slide("Results", "Steps used versus the course's reference steps", """
This chart compares the steps our agent used in passing runs with the reference steps from the course list.
On simple tasks the agent needs a few more steps than the reference, for example because it checks the result or opens a menu first.
Markor needs about twice the reference, because the agent types the text twice, once in the note and once in the SMS, instead of sharing it.
On OsmAnd it is the other way round: the reference is 60 steps, and our agent needed only about 22, because the coded Skill leads it along the shortest path.
The light bar is the step budget, the maximum we allow before we stop a run.
""")
cats = [x["short"] for x in F["steps_rows"]]
bar_chart(s, 0.7, 1.6, 11.95, 5.3, cats, [("Our agent (mean of passing runs)", [x["ours"] for x in F["steps_rows"]]),
                                            ("Reference steps (course list)", [x["ref"] for x in F["steps_rows"]]),
                                            ("Step budget", [x["budget"] for x in F["steps_rows"]])],
          colors=[BLUE, NAVY, LINE], gap=70, overlap=-10)

# 14 ─ Speed and cost ─────────────────────────────────────────────────────────────────────────────
s = slide("Results", f"Speed and cost: about {F['final_cost_eur']} € for all 21 runs", f"""
How long and how expensive was it?
Simple tasks finished in about one to two minutes. Markor took about four minutes and OsmAnd about nine, including app start and setup time.
All 21 runs together used about {F['final_tokens_m']} million tokens. At 0.045 euro per million tokens, that is about {F['final_cost_eur']} euro.
Even the whole project, all local development runs together, cost only about {F['project_cost_eur']} euro in model calls.
The model answers fast, {F['median_call_s']} seconds per call at the median. Most of the time per step is the phone: waiting for screens to load, typing, and saving logs and video.
""")
cats = [x["short"] for x in F["cost_rows"]]
bar_chart(s, 0.7, 1.6, 7.6, 5.3, cats, [("Mean run time (s)", [x["seconds"] for x in F["cost_rows"]])], colors=[BLUE], legend=False, gap=80, font_size=11)
big_number(s, 8.75, 1.75, 3.9, f"{F['final_tokens_m']} M", "tokens for all 21 final runs", value_size=36)
big_number(s, 8.75, 3.35, 3.9, f"€{F['final_cost_eur']}", "model cost of the final evaluation\n(€0.045 per million tokens)", value_size=36)
big_number(s, 8.75, 4.95, 3.9, f"{F['median_call_s']} s", "median time per model call", value_size=36)

# 15 ─ Demo wall ──────────────────────────────────────────────────────────────────────────────────
s = slide("Demo", "All 21 evaluation runs at once (sped up)", """
Now the demo. This video shows all 21 evaluation runs at the same time.
Each column is one task, each row is one run. The label says the task, the seed, pass or fail, and how much the video is sped up. Each clip ends on the final screen.
You can see the difference in length: Wi-Fi is sped up only two times, OsmAnd about ten times or more.
Look at the orange labels: Contacts seed 43, Files seed 43 and OsmAnd seed 366. These are the three failures we explain next.
""")
movie(s, VID / "wall_21_runs.mp4", VID / "wall_21_runs_poster.png", 0.7, 1.5, 5.45 * 1260 / 1200, 5.45)
card(s, 6.85, 1.5, 5.8, 5.45, "How to read it", [
    "Columns: Wi-Fi, Contacts, SMS, Files, Calendar, Markor + SMS, OsmAnd",
    "Rows: run 1, 2, 3 (seeds 42 / 43 / 44; OsmAnd 31 / 314 / 366)",
    "Label: verdict and speed-up (x2 = twice as fast)",
    "Each clip stops on its final screen"], body_size=17, title_size=20)

# 16 ─ Featured demos ─────────────────────────────────────────────────────────────────────────────
s = slide("Demo", "One success and one failure, step by step", """
Here are two runs at a speed you can follow.
On the left, Markor with seed 44, four times faster. Watch how it creates the note, saves it, switches to the SMS app, and sends a plain SMS.
On the right, Files with seed 43, three times faster. Everything looks right: it opens the folder, selects a file, and moves it to Movies. But watch the file name in the grid. The name is cut off, and the agent picks a file that only looks like the right one. Then it says it is done. The checker says fail.
This brings us to the failure analysis.
""")
movie(s, VID / "featured_markor_pass.mp4", VID / "featured_markor_pass_poster.png", 1.3, 1.55, 2.45, 5.45)
movie(s, VID / "featured_files_fail.mp4", VID / "featured_files_fail_poster.png", 6.95, 1.55, 2.45, 5.45)
card(s, 3.95, 1.55, 2.75, 3.6, "Success", ["Markor + SMS, seed 44", "15 steps, PASS", "Note saved, then a plain SMS with the same text", "x4 speed"], accent=BLUE, title_size=20, body_size=15)
card(s, 9.6, 1.55, 3.05, 3.6, "Failure", ["Files, seed 43", "13 steps, FAIL", "Moved a look-alike file, then said done", "x3 speed"], accent=ORANGE, title_size=20, body_size=15)

# 17 ─ Where failures come from ───────────────────────────────────────────────────────────────────
s = slide("Failure analysis", "How 275 project runs ended: the setup failed most often", f"""
Before we look at single failures, here is the bigger picture: all {F['local_runs']} runs in our project that have a machine-readable summary, from the first tests to the final evaluation.
{F['outcome_rows'][5][1]} runs passed. Among the rest, the largest group is not the model at all: {F['outcome_rows'][0][1]} runs ended with setup or other errors, for example the emulator, the recorder or a crashed service.
Next come no-progress stops: the agent repeated an action and nothing changed, so our rule stopped the run early instead of wasting the budget. Then invalid replies, and runs that used up the step budget.
The most dangerous group is false completion: the model says done, but the checker says fail. We saw {F['false_done']} of these. The course calls this false_done, and our completion rules and checks are there to reduce it.
""")
cats = [x[0] for x in F["outcome_rows"]]
chart = bar_chart(s, 0.7, 1.6, 7.4, 5.3, cats, [("Runs", [x[1] for x in F["outcome_rows"]])], colors=[BLUE], legend=False, horizontal=True, gap=55)
color_points(chart, [BLUE if c == "PASS" else ORANGE if c.startswith("Said done") else MUTED for c in cats])
card(s, 8.45, 1.7, 4.2, 4.9, "The five failure classes (D1 p.50)", [
    [("grounding", {"bold": True}), (": the tap lands on nothing", {})],
    [("too_early", {"bold": True}), (": acting on a loading screen", {})],
    [("lost_value", {"bold": True}), (": a value is lost or invented", {})],
    [("wrong_app", {"bold": True}), (": the wrong app is used", {})],
    [("false_done", {"bold": True}), (": says done, verifier fails", {})],
    "Final evaluation: false_done 1, grounding 1, other 1"], body_size=15)

# 18 ─ Deep dive ──────────────────────────────────────────────────────────────────────────────────
s = slide("Failure analysis", "Deep dive: a false finish caused by a look-alike file", """
Our main failure analysis: Files, seed 43. The task: move documentary dot mp4 from Alarms to Movies.
AndroidWorld puts distractor files with similar names in the same folder. In the grid view, the names are cut off.
At step 5 the agent saw "documentary underscore 20..." and picked it. In its reasoning it even wrote "assuming it is named differently here". So it guessed, and it invented the full name.
Then it did the move perfectly, waited for "Moving 1 item", and finished with the message that the file was moved. The verifier failed it, because the real file never moved.
Class: false_done. The root cause is choosing a look-alike from a truncated name.
Where to fix it: in the instructions, switch to list view or search for the exact name. And in the program, a check before Move that the selected name is exactly the requested one. That is the course's idea of a check step before declaring done.
""")
picture(s, IMG / "files43_step5.png", 0.7, 1.6, h=5.3, phone=True)
picture(s, IMG / "files43_final.png", 3.25, 1.6, h=5.3, phone=True)
rows = [["Steps", "What happened", "Assessment"],
        ["1–4", "Opened Files, the storage root, then Alarms", "Correct"],
        ["5", "Grid with cut-off names; long-pressed “documentary_20…”", "Wrong object"],
        ["6–11", "More options > Move to > Movies > MOVE", "Correct steps, wrong file"],
        ["12–13", "Waited for “Moving 1 item”, then finish", "false_done"]]
table(s, 5.95, 1.6, 6.7, 2.5, rows, col_widths=[0.9, 4.1, 1.7], size=12, fills={(4, 2): ORANGE})
text(s, 5.95, 4.25, 6.7, 0.75, [[("Model: ", {"bold": True, "color": NAVY}), ("“" + F["files_quote"] + "”", {"italic": True})]], size=13)
card(s, 5.95, 5.1, 3.25, 1.75, "Class", "false_done (D1 p.50); root cause: a look-alike chosen from a truncated name", accent=ORANGE, body_size=13)
card(s, 9.4, 5.1, 3.25, 1.75, "Fix layer", "Instruction: list view or exact search. Program: check the full name before Move", body_size=13)

# 19 ─ Other failures and variance ────────────────────────────────────────────────────────────────
s = slide("Failure analysis", "Two more failures, and why runs of one task differ", """
The other two failures.
Contacts, seed 43: the agent swiped to find the phone field, but two swipes went past it to the end of the form. Then it kept swiping in the same direction. Our own feedback did not help: the blinking text cursor counted as a screen change, so the agent was told its swipe had worked. We classify this as other, a navigation problem.
OsmAnd, seed 366: our code said "tap Clear at 941, 83". The model tapped at 941, 57, the very top edge of the button, three times, and nothing happened. That is grounding: the tap lands on nothing.
An important pattern: the same task can pass on one run and fail on another. OsmAnd was two of three in two separate frozen evaluations, but different runs failed, for different reasons. Long tasks have many steps, and each step is a chance for a small error.
""")
picture(s, IMG / "contacts43_step9.png", 0.7, 1.6, h=4.3, phone=True)
picture(s, IMG / "osmand366_step15.png", 2.75, 1.6, h=4.3, phone=True)
text(s, 0.7, 5.95, 4.0, 0.9, "Left: Contacts s43, Phone field cut off at the top.  Right: OsmAnd s366, Clear button at the top right.", size=11, color=GREY)
card(s, 5.0, 1.6, 3.7, 2.45, "Contacts s43: other", "Two swipes went past the Phone field; four more changed only the blinking cursor, which our check counted as a change.", accent=ORANGE, body_size=14)
card(s, 8.95, 1.6, 3.7, 2.45, "OsmAnd s366: grounding", "Code: “Tap Clear at [941, 83]”. Model tapped [941, 57], the top edge of the button, three times: no effect.", accent=ORANGE, body_size=14)
rows = [["Same task, two frozen evaluations", "Run 1", "Run 2", "Run 3"],
        ["OsmAnd v61 (Skill experiment)", "FAIL", "PASS", "PASS"],
        ["OsmAnd v65 (final)", "PASS", "PASS", "FAIL"],
        ["Contacts v42 (earlier)", "PASS", "PASS", "PASS"],
        ["Contacts v65 (final)", "PASS", "FAIL", "PASS"]]
fills = {(1, 1): ORANGE, (1, 2): BLUE, (1, 3): BLUE, (2, 1): BLUE, (2, 2): BLUE, (2, 3): ORANGE,
         (3, 1): BLUE, (3, 2): BLUE, (3, 3): BLUE, (4, 1): BLUE, (4, 2): ORANGE, (4, 3): BLUE}
table(s, 5.0, 4.3, 7.65, 2.2, rows, col_widths=[3.45, 1.4, 1.4, 1.4], size=12, fills=fills, align_center_from=1)

# 20 ─ Infrastructure ─────────────────────────────────────────────────────────────────────────────
s = slide("Failure analysis", "Not every failure is the model: test-setup problems", f"""
Not every failure is the model's fault. We found several problems in the test setup itself, and we fixed them before trusting any result.
On our laptop the emulator first returned black screenshots, so the model was waiting on a black screen. The screen recorder died when the Android tools restarted their server. A cold app start took longer than the default five seconds.
Two problems were special. AndroidWorld's accessibility service crashed in {F['crash_runs']} of {F['crash_total']} OsmAnd runs with it; the model learned to close the dialog. And the official initialization of the Files task deletes every file in shared storage, including OsmAnd's offline map. So before each OsmAnd run our runner now checks the map and restores it.
Our lesson: trust the test harness first, then judge the model.
""")
rows = [["Symptom", "Root cause", "Fix"],
        ["Model “waited” on a black screen", "Emulator GPU mode returned all-black frames", "Headless host-GPU emulator; black frames stop the run"],
        ["Screen recording stopped", "Android tools restarted their server on a timeout", "Keep the server; longer app-start timeout"],
        ["App start timed out", "Cold start longer than 5 s", "30 s launch timeout"],
        ["“keeps stopping” dialog", f"Accessibility service crash ({F['crash_runs']} of {F['crash_total']} OsmAnd runs)", "Model closes it; empty tree read again"],
        ["OsmAnd map missing", "Files task initialization deletes shared storage", "Check the map before OsmAnd; rerun official setup"]]
table(s, 0.7, 1.65, 8.6, 4.6, rows, col_widths=[2.6, 3.0, 3.0], size=12, bold_first_col=True)
if (IMG / "forwarder_crash.png").exists():
    picture(s, IMG / "forwarder_crash.png", 9.7, 1.65, h=4.6, phone=True)
text(s, 0.7, 6.4, 11.9, 0.5, "Trust the harness before judging the model: without these fixes, setup faults would look like agent failures.", size=14, bold=True, color=BLUE)

# 21 ─ Improvement journey ────────────────────────────────────────────────────────────────────────
s = slide("Improvement", "The hardest task: from zero passes to two of three", """
Now the improvement. We focused on OsmAndTrack, the hardest task. It needs about 20 correct steps in a map app.
This chart shows all our OsmAnd runs, grouped by version, and how many passed.
For a long time nothing passed: 46 runs with zero passes. With the Skill only as text, and later with rules based on the model's own words, the agent never saved a correct track.
Two changes made the difference. First, we gave the program eyes: the accessibility tree, so the code can read the real screen. Second, we turned the Skill into code: it recognises the screen and gives the next step and where to tap.
After that, 8 of the next 15 runs passed, and both frozen evaluations reached two of three.
""")
cats = [x["phase"] for x in F["osmand_phases"]]
bar_chart(s, 0.7, 1.6, 8.0, 5.3, cats, [("Runs", [x["runs"] for x in F["osmand_phases"]]), ("Passed", [x["passed"] for x in F["osmand_phases"]])],
          colors=[LINE, BLUE], gap=60, overlap=-5)
card(s, 9.0, 1.7, 3.65, 4.9, "What changed", [
    "Skill as text: the model often ignored it",
    "Rules on the model’s words: bypassed",
    [("Program reads the screen", {"bold": True}), (" (accessibility tree)", {})],
    [("Skill as code", {"bold": True}), (": next step + tap centre", {})],
    "Each fix tested on practice seeds, never on the evaluation seeds"], body_size=14)

# 22 ─ Before and after ───────────────────────────────────────────────────────────────────────────
s = slide("Improvement", "Before and after: only the Skill changed", """
This is our documented improvement with before and after results.
We ran the slide's exact OsmAnd task three times with the Skill and three times without it. Same frozen code, same seeds, same model. Only the Skill was switched on or off.
Without the Skill: zero of three. The model typed "Ruggell, Liechtenstein", which only finds the country, and two runs used navigation, which never saves a track.
With the Skill: two of three passed.
The chart on the right shows the milestones. Without the Skill the agent never reached the first real milestone.
To be fair, this is app knowledge in code, and it only works for OsmAnd. A new app would need its own procedure.
""")
rows = [["OsmAnd, seeds 31 / 314 / 366", "No Skill", "Skill"],
        ["Official verifier PASS", "0 / 3", "2 / 3"],
        ["Searched the place name only", "0 / 3", "3 / 3"],
        ["Route started with a searched place", "0 / 3", "2 / 3"],
        ["Saved a track", "0 / 3", "2 / 3"],
        ["Mean steps", "23.3", "18.7"]]
table(s, 0.7, 1.7, 6.2, 3.3, rows, col_widths=[3.6, 1.3, 1.3], size=14, bold_first_col=True, fills={(1, 1): ORANGE, (1, 2): BLUE}, align_center_from=1)
text(s, 0.7, 5.2, 6.2, 1.6, "Frozen v61 (tag osmand-extra-v61); identical source hashes in both batches; only task_skills differs. Three runs per side is a small sample.",
     size=12, color=GREY)
bar_chart(s, 7.2, 1.6, 5.45, 5.3, ["Text Skill only\n(v42, other seeds)", "No Skill\n(v61)", "Skill as code\n(v61)", "Final agent\n(v65)"],
          [("Passed of 3", [0, 0, 2, 2])], colors=[BLUE], legend=False, axis_max=3, major_unit=1, gap=70)

# 23 ─ Lessons carried into the final agent ───────────────────────────────────────────────────────
s = slide("Improvement", "Every failure taught us something we built into the final agent", """
The improvement was not only OsmAnd. While building the final agent, each failure led to one small, tested change.
For Markor, an earlier analysis found that sharing the file from Markor sends an MMS that fails. We turned that into the Markor Skill, and the final runs passed three of three.
Markor's editor uses a custom text box, so our focus check refused typing. We fixed the check.
The model sometimes translated the SMS app name into Chinese. With two apps in one task we could not guess which one it meant, so we added an alias table.
And the Files task deleted OsmAnd's map, so we added the map check.
Each fix came from one recorded failure and has an automatic test.
""")
rows = [["Failure we saw", "Cause", "Change", "Final result"],
        ["Markor: message “Not sent”", "Markor’s Share menu makes an MMS", "Markor Skill: plain SMS, SMS button", "Markor 3 / 3"],
        ["Markor: typing refused", "Custom editor not seen as a text field", "Focus check accepts the editor", "Markor 3 / 3"],
        ["SMS app name in Chinese", "Two apps allowed, name unclear", "Alias table for known translations", "Markor 3 / 3"],
        ["OsmAnd map missing", "Files initialization clears storage", "Map check + official setup", "OsmAnd 2 / 3"],
        ["OsmAnd 0 / 3", "Long procedure, model loses its place", "Skill as code + GUI tree", "OsmAnd 2 / 3"]]
table(s, 0.7, 1.7, 11.95, 4.1, rows, col_widths=[2.9, 3.2, 3.6, 2.25], size=13, bold_first_col=True)
text(s, 0.7, 6.0, 11.95, 0.8, f"Every change has an automatic offline test ({F['tests']} tests in total) that fails on the old code and passes on the new code.", size=14, color=BLUE, bold=True)

# 24 ─ Effort ─────────────────────────────────────────────────────────────────────────────────────
s = slide("Our work in numbers", "Behind the final result", f"""
A few numbers show the work behind the result.
About {F['project_runs']} recorded runs across the project, {F['versions']} versions of the agent, {F['tests']} automatic tests, and {F['local_steps']} executed steps in this agent's runs alone.
Every version change has a written reason, and every run has its log. This is what lets us explain the failures today, instead of guessing.
""")
nums = [(f"~{F['project_runs']}", "recorded runs across the project"), (f"{F['versions']}", "agent versions with a written reason"),
        (f"{F['local_steps']:,}", "steps executed in this agent's runs"), (f"{F['local_calls']:,}", "model calls in this agent's runs"),
        (f"{F['tests']}", "automatic offline tests"), (f"€{F['project_cost_eur']}", "model cost of all local runs")]
for i, (v, l) in enumerate(nums):
    x = 0.7 + (i % 3) * 4.05
    y = 1.8 + (i // 3) * 2.45
    rect(s, x, y, 3.8, 2.1, fill=PALE)
    rect(s, x, y, 3.8, 0.07, fill=NAVY)
    big_number(s, x + 0.25, y + 0.35, 3.4, v, l, value_size=40)

# 25 ─ Findings and limitations ───────────────────────────────────────────────────────────────────
s = slide("Findings", "What we learned, and what is still limited", """
To finish, what did we learn?
One: trust the test setup before you judge the model. Black screens and lost videos looked like agent failures at first.
Two: the official checker must decide, not the model. False completions are real, and they are the most dangerous failure.
Three: where knowledge lives matters. A Skill in the system prompt was ignored. Repeated each step it was followed. As code it worked best.
Four: long tasks fail by small errors adding up. A missed tap or a wrong guess at any step is enough.
Our limitations: three runs per task is a small sample; we used one model; the OsmAnd Skill only works for OsmAnd; and two tasks used extra screen labels, which we report in the results.
""")
card(s, 0.7, 1.7, 6.9, 5.0, "Findings", body_size=19, title_size=21, body=[
    [("Trust the harness first", {"bold": True}), (": setup faults looked like agent failures", {})],
    [("The verifier decides", {"bold": True}), (": false completions are real and dangerous", {})],
    [("Where knowledge lives matters", {"bold": True}), (": prompt < reminder each step < code", {})],
    [("Long tasks fail by small errors", {"bold": True}), (": one missed tap is enough", {})],
    [("Checks catch traps", {"bold": True}), (f": {F['refusals_total']} actions stopped in the final runs", {})]])
card(s, 7.85, 1.7, 4.8, 5.0, "Limitations", accent=ORANGE, body_size=19, title_size=21, body=[
    "Three runs per task: small sample",
    "One model, one laptop, one emulator",
    "OsmAnd Skill works only for OsmAnd",
    "Two tasks used extra screen labels",
    "Fixes after the freeze are not evaluated"])

# 26 ─ Thank you ──────────────────────────────────────────────────────────────────────────────────
s = slide(None, "Thank you", """
Thank you for listening. We are happy to take your questions.
""")
# Same split layout as the cover, so the talk opens and closes with one look.
rect(s, 0, 0, W, H, fill=RGBColor(0xEE, 0xF3, 0xF8))
rect(s, 0, 0, 7.9, H, fill=NAVY)
rect(s, 0, 0, 7.9, 0.08, fill=BLUE)
text(s, 0.75, 0.7, 6.8, 0.35, "AGENTIC AI IN MODERN BUSINESS  ·  PRESENTATION", size=13, bold=True, color=LIGHT)
text(s, 0.75, 1.85, 6.9, 1.1, "Thank you", size=54, bold=True, color=WHITE)
text(s, 0.75, 3.0, 6.9, 0.5, "Questions are welcome", size=22, color=SOFT)
rect(s, 0.75, 3.85, 1.1, 0.06, fill=BLUE)
text(s, 0.75, 4.2, 6.9, 0.9, "github.com/Chenschenschen/androidworld-gui-agent\nbranch team-agent  ·  tag team-agent-final-v65",
     size=15, color=RGBColor(0xF0, 0x9A, 0x5B), spacing=1.2)
text(s, 0.75, 5.3, 6.9, 0.9, "Model: AutoGLM-Phone-9B-Multilingual (Z.ai)\nBenchmark: AndroidWorld (Google Research)", size=14,
     color=SOFT, spacing=1.2)
phone(IMG / "traj_2.png", 8.1, 1.45, 4.9, -8)
phone(IMG / "traj_5.png", 10.5, 1.45, 4.9, 8)
phone(IMG / "osmand_pass_3.png", 9.15, 0.85, 5.75)

import sys
out = HERE / (sys.argv[1] if len(sys.argv) > 1 else "AndroidWorld_GUI_Agent_Presentation.pptx")
prs.save(out)
words = sum(len(t.split()) for _, t in SLIDES)
lines = [f"# Presentation script\n\nAbout {words} words, roughly {words / 135:.0f} minutes at 135 words per minute, plus about 2 minutes of video.\n"]
for i, (title, script) in enumerate(SLIDES, start=1):
    lines.append(f"## Slide {i}: {title}\n\n{script.strip()}\n")
(HERE / "SCRIPT.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
print("saved", out, len(prs.slides), "slides,", words, "script words")
