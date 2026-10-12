# Presentation script

Slides 1 to 32 are presented; slides 33 to 35 are an appendix for questions. About 3416 spoken words, roughly 25 minutes at 135 words per minute, plus 8.0 minutes of video if every clip is played to the end.

The speaker notes in AndroidWorld_GUI_Agent_Presentation.pptx contain the same text; AndroidWorld_GUI_Agent_Presentation_submission.pptx is the same deck without notes.

## Slide 1: Title

Hello everyone, and thank you for having us.
Our project is a GUI agent for Android. A GUI agent uses a phone the way a person does: it looks at the screen and decides where to tap or what to type.
In the next 25 minutes we will show how we built one agent, how we tested it on seven AndroidWorld tasks, where it failed, and how we improved it.

## Slide 2: One agent, seven tasks: 17 of 21 runs passed the official check

Here is the short version.
We built one agent and gave it seven tasks from AndroidWorld, from easy to the hardest one on the course list. Each task ran three times on frozen, git-tagged code, and every run was screen-recorded.
17 of the 21 runs passed. Pass means the official AndroidWorld checker looked at the phone's data and confirmed the task was done. The model's own "I am done" does not count.
Behind this result there is a lot of work: about 300 recorded runs across the project and 66 versions of the agent.
And it was cheap: the model cost for all 21 final runs was about 0.066 euro.

## Slide 3: A phone assistant that uses apps the way a person does

Our use case is a phone assistant for everyday tasks.
You tell it in plain words what you want, for example "Send this message to this number", and it opens the right app and does the steps on the screen.
This is useful because it works with normal apps. It needs no special interface from the app maker. It only needs the screen, like a person.
In business this helps with three things: helping people who find phones hard to use, saving time on repeated phone tasks, and testing apps automatically.

## Slide 4: Seven tasks from all three difficulty rows of the course list

The course asks for at least three tasks, at least one from each difficulty row. We chose seven, so we could see patterns, not just single cases.
Two warm-up tasks: turn on Wi-Fi and add a contact.
Three real-work tasks: send an SMS, move a file, and add a calendar event with date, time and length.
Two multi-app tasks: write a note in Markor and send it by SMS, which uses two apps, and OsmAndTrack, the hardest task on the list, with a reference of 60 steps.
For the six template tasks AndroidWorld fills in random names and numbers. For OsmAnd we used exactly the route on the course slide: Ruggell, then Bendern.

## Slide 5: Why AutoGLM-Phone-9B, and what we tried first

Next, the model. The course says any model is fine, as long as we name it. Ours is AutoGLM-Phone-9B-Multilingual, which we use through the Z.ai API.
We did not start with it. Our first versions used GELab-Zero 4B, the model on the course slide, running locally with Ollama on a laptop GPU with 8 gigabytes of memory. The model did not fit completely on the GPU, so one screenshot request took about 20 seconds. Only one of six Contacts trials passed, and in a Wi-Fi run the model answered in a format our parser could not accept, and even said Wi-Fi was on when it was not. That was our first unsuccessful attempt.
AutoGLM is trained for phone screens and has a clear action format. Our median time per model call was 1.75 seconds, and the price is 0.045 euro per million tokens.
On the AndroidWorld leaderboard a 9B AutoGLM-Mobile entry is listed at 80.2 percent. That entry may not be the exact hosted version we use, so we only say it is one of the top-ranked model families.

## Slide 6: One class, one step(): observe, decide, check, act, record

This is how the agent works. It is one Python class with one method, step, as the course asks.
Each step does five things.
First, observe: take a screenshot of the phone. For Wi-Fi and OsmAnd it also gets text labels of the screen, and we report this for every run.
Second, decide: send the task, the recent history and the screenshot to the model. The model answers with one action, for example tap at this point, or type this text.
Third, check: our code checks the action before anything happens on the phone. Is the format valid? Is the point on the screen? Is a text field really focused before we type?
Fourth, act: run the action on the emulator.
Fifth, record: save the screenshot, the model's answer and the result in the trajectory log, while the screen recorder runs.
This repeats until the model says finish or the step budget ends. Then the official checker decides pass or fail. All seven tasks use this same class.

## Slide 7: Context and Skills: what goes into each model request

What does the model receive at each step?
A system prompt with the action rules and a short completion rule, for example: the contact must be saved, a filled form is not enough.
The last 20 steps of history, the newest screenshot, and a short status text.
For two tasks we add a Skill. A Skill is app knowledge, loaded only for its task, as in the course's Skills idea.
For Markor it is text: share the note with Share, Plain Text. Share, File would attach the file and turn the message into an MMS that fails.
For OsmAnd the Skill is code. It reads the screen and tells the model the next step and where to tap. The model still decides and acts, and it did not always follow the advice.
So nothing is a fixed list of taps. The model makes every decision.

## Slide 8: A safety net: actions are checked before they reach the phone

Our check step catches bad actions before they happen.
The general checks work for every task: an action must have the right format, a point must be on the screen, and typing is only allowed when a text field is focused. Otherwise the text would go nowhere.
Task checks protect against known traps. For OsmAnd, the star button on a place card saves a favourite, not a route point, so we refuse it.
When we refuse an action, the model gets one correction in the same step, with the reason.
In the 21 final runs these checks stopped 7 actions. Without them, some of these passing runs would have failed.

## Slide 9: Implementation: four parts and how they talk

How is it implemented? Four parts work together.
The Android emulator runs a Pixel 6 phone with Android 13, without a window. AndroidWorld sets up each task from its seed and, at the end, its official verifier checks the result.
Our runner, run_task.py, prepares the task, starts the screen recorder, calls the agent step by step, then asks the verifier and writes the logs.
The agent, the AutoGLMAgent class in autoglm_agent.py, builds each request and checks each answer. The model itself runs behind the Z.ai API.
Around this, evaluate_tasks.py runs whole batches and stops if the code changes during a batch, and 38 offline tests protect every fix. One command reproduces the whole evaluation.

## Slide 10: One run, step by step: the OsmAnd track Ruggell to Bendern

Here is one full run from the final evaluation: the hardest task, OsmAnd, with seed 314. It passed in 23 steps.
The model searched for Ruggell. The first search found nothing nearby, so it increased the search radius three times, scrolled the results, and picked the row labelled Village.
From the place menu it chose Plan a route, so Ruggell became the first point of the route.
Then it searched for Bendern, picked the village, went back to the route panel and tapped Add. The panel showed two points. It tapped Done, which saves the track, and called finish.
On the way it closed a crash dialog, and our check refused one Type because no text field was focused.
The official checker then read the saved track and confirmed both points in the right order. Under each picture is a sentence from the model's own reasoning, taken from the log.

## Slide 11: How we tested: frozen code, three runs per task

How did we test?
First, we froze the code with a git tag before every batch, and nothing changed during a batch. The final agent is version 66. Six tasks were run with version 65; version 66 only changed the Markor Skill, which these tasks never load, so they ran the same code. Markor was run again with version 66 after we fixed its Skill.
Each task ran three times with fixed task seeds, 42, 43 and 44. For OsmAnd we used 31, 314 and 366, because these three seeds produce exactly the route on the course slide.
Success is decided only by the official AndroidWorld verifier, which reads the phone's data.
Every run keeps three records: a summary row with the fields from the course, written by our runner while the run happens; a step-by-step trajectory log; and a screen recording. You will see all 21 rows right after the results.
We did not rerun failures. A rerun of the same code only measures luck.

## Slide 12: 17 of 21 runs passed; every task passed at least twice

Here are all 21 runs. Blue is pass, orange is fail.
Wi-Fi, SMS and Calendar passed all three runs.
Contacts, Files, Markor and OsmAnd passed two of three.
Both multi-app tasks together passed four of six, including OsmAndTrack, the hardest task on the list.
There are four failures: one false finish, two missed taps, and one navigation problem. We will look at each of them in a moment.
Please keep in mind that three runs is a small sample. Three of three does not mean the task always works.

## Slide 13: Run log (1/2): one row per run

Here is the full log, one row per run, sorted by task, as the course asks.
Each row has the course's fields: task, run, the observation, steps against the budget, the verifier result, the failure class, the recording and a short note. The model, version and grounding are the same for every run, so they are in the line above the table.
Our runner writes these rows while each run happens, so nothing is filled in from memory. Each run number links to its full step-by-step log on GitHub.
The notes show small things the checks handled, for example the SMS runs where the model wrote the app name in Chinese and our runner still understood it.

## Slide 14: Run log (2/2): the two multi-app tasks

The second part shows the two hard tasks, with longer notes.
All three Markor runs saved the note and then shared its text with Markor's Share, Plain Text; none typed the text again. Run 1 failed on the very last tap: it looked for the SMS button at the top right instead of next to the message.
The first OsmAnd run had to restore the map first, because the Files task had cleared the phone's storage. The other failure here, OsmAnd run 3, reached the first route point and then missed the Clear button. We come back to it in the failure analysis.

## Slide 15: All 21 evaluation runs at once (sped up)

Now the demo. This video shows all 21 evaluation runs at the same time.
Each column is one task, each row is one run. The label says the task, the seed, pass or fail, and how much the video is sped up. Each clip ends on the final screen.
You can see the difference in length: Wi-Fi is sped up only two times, OsmAnd about ten times or more.
Look at the orange labels: Contacts seed 43, Files seed 43 and OsmAnd seed 366. These are the three failures we explain next.

## Slide 16: Warm-up: SystemWifiTurnOn

First the warm-up tasks, sped up so you can follow. Wi-Fi, seed 42: the agent opens Settings, Network and internet, then Internet, switches Wi-Fi on, and finishes on its own when it sees the switch on. Five steps.

## Slide 17: Warm-up: ContactsAddContact

Contacts. On the left, seed 42: it types the name, scrolls once to the phone field, types the number and saves. On the right, seed 43: two swipes go past the phone field, and four more swipes only move the blinking cursor, so our no-progress rule stops the run.

## Slide 18: Real work: SimpleSmsSend

Now the real-work tasks. SMS, seed 42: a new conversation, the number, the message, and send. Nine steps.

## Slide 19: Real work: FilesMoveFile

Here are two runs of the same task, Files, at a speed you can follow. Both are three times faster.
On the left, seed 42. The folder holds look-alike files whose names are cut off. The agent scrolls until it sees the full name, sci_fi_book.mp3, selects exactly that file and moves it to Audiobooks. The file disappears from Recordings, and the agent goes to Audiobooks to check before it says done. The checker says pass.
On the right, seed 43. Everything looks right: it opens the folder, selects a file, and moves it to Movies. But watch the file name in the grid. The name is cut off, and the agent picks a file that only looks like the right one. Then it says it is done. The checker says fail.
Same app, same kind of screen, one different choice. This brings us to the failure analysis.

## Slide 20: Real work: SimpleCalendarAddOneEvent

Calendar, seed 44: the title and the description, then the date, the start hour and the length, and save. Sixteen steps, with no refused action.

## Slide 21: Multi-app and memory: MarkorCreateNoteAndSms

Markor plus SMS, four times faster. On the left, seed 43: the agent creates the note and saves it. Then it uses Markor's own Share, Plain Text, picks SMS Messenger and enters the number. The message box already holds the note's text, so it only taps SMS. Pass. On the right, seed 42: the same path works until the very last tap. The model says the SMS button is at the top right and taps there four times, but the button is next to the message. The run stops: fail, a grounding error.

## Slide 22: Multi-app and memory: OsmAndTrack

Finally OsmAnd, the hardest task. On the left, seed 314, the run you saw step by step: Ruggell, Plan a route, Bendern, Done, in 23 steps, and it closed a crash dialog on the way. On the right, seed 366: Ruggell became the first point, but then the model tapped just above the Clear button three times, and the run stopped.

## Slide 23: How 284 project runs ended: the setup failed most often

Before we look at single failures, here is the bigger picture: all 284 runs in our project that have a machine-readable summary, from the first tests to the final evaluation.
99 runs passed. Among the rest, the largest group is not the model at all: 65 runs ended with setup or other errors, for example the emulator, the recorder or a crashed service.
Next come no-progress stops: the agent repeated an action and nothing changed, so our rule stopped the run early instead of wasting the budget. Then invalid replies, and runs that used up the step budget.
The most dangerous group is false completion: the model says done, but the checker says fail. We saw 19 of these. The course calls this false_done, and our completion rules and checks are there to reduce it.

## Slide 24: Deep dive: a false finish caused by a look-alike file

Our main failure analysis: Files, seed 43. The task: move documentary dot mp4 from Alarms to Movies.
AndroidWorld puts distractor files with similar names in the same folder. In the grid view, the names are cut off.
At step 5 the agent saw "documentary underscore 20..." and picked it. In its reasoning it even wrote "assuming it is named differently here". So it guessed, and it invented the full name.
Then it did the move perfectly, waited for "Moving 1 item", and finished with the message that the file was moved. The verifier failed it, because the real file never moved.
Class: false_done. The root cause is choosing a look-alike from a truncated name.
Where to fix it: in the instructions, switch to list view or search for the exact name. And in the program, a check before Move that the selected name is exactly the requested one. That is the course's idea of a check step before declaring done.

## Slide 25: Two more failures, and why runs of one task differ

Two more failures. The fourth one, Markor seed 42, you saw in its demo: it missed the SMS button.
Contacts, seed 43: the agent swiped to find the phone field, but two swipes went past it to the end of the form. Then it kept swiping in the same direction. Our own feedback did not help: the blinking text cursor counted as a screen change, so the agent was told its swipe had worked. We classify this as other, a navigation problem.
OsmAnd, seed 366: our code said "tap Clear at 941, 83". The model tapped at 941, 57, the very top edge of the button, three times, and nothing happened. That is grounding: the tap lands on nothing.
An important pattern: the same task can pass on one run and fail on another. OsmAnd was two of three in two separate frozen evaluations, but different runs failed, for different reasons. Long tasks have many steps, and each step is a chance for a small error.

## Slide 26: Not every failure is the model: test-setup problems

Not every failure is the model's fault. We found several problems in the test setup itself, and we fixed them before trusting any result.
On our laptop the emulator first returned black screenshots, so the model was waiting on a black screen. The screen recorder died when the Android tools restarted their server. A cold app start took longer than the default five seconds.
Two problems were special. AndroidWorld's accessibility service crashed in 11 of 25 OsmAnd runs with it; the model learned to close the dialog. And the official initialization of the Files task deletes every file in shared storage, including OsmAnd's offline map. So before each OsmAnd run our runner now checks the map and restores it.
Our lesson: trust the test harness first, then judge the model.

## Slide 27: The hardest task: from zero passes to two of three

Now the improvement. We focused on OsmAndTrack, the hardest task. It needs about 20 correct steps in a map app.
This chart shows all our OsmAnd runs, grouped by version, and how many passed.
For a long time nothing passed: 46 runs with zero passes. With the Skill only as text, and later with rules based on the model's own words, the agent never saved a correct track.
Two changes made the difference. First, we gave the program eyes: the accessibility tree, so the code can read the real screen. Second, we turned the Skill into code: it recognises the screen and gives the next step and where to tap.
After that, 8 of the next 15 runs passed, and both frozen evaluations reached two of three.

## Slide 28: Before and after: only the Skill changed

This is our documented improvement with before and after results.
We ran the slide's exact OsmAnd task three times with the Skill and three times without it. Same frozen code, same seeds, same model. Only the Skill was switched on or off.
Without the Skill: zero of three. The model typed "Ruggell, Liechtenstein", which only finds the country, and two runs used navigation, which never saves a track.
With the Skill: two of three passed.
The chart on the right shows the milestones. Without the Skill the agent never reached the first real milestone.
To be fair, this is app knowledge in code, and it only works for OsmAnd. A new app would need its own procedure.

## Slide 29: Every failure taught us something we built into the final agent

The improvement was not only OsmAnd. While building the final agent, each failure led to one small, tested change.
For Markor, an earlier analysis found that sharing the file from Markor sends an MMS that fails. We turned that into the Markor Skill: share the note as plain text. The final runs passed two of three; the failure was a missed tap at the very end.
Markor's editor uses a custom text box, so our focus check refused typing. We fixed the check.
The model sometimes translated the SMS app name into Chinese. With two apps in one task we could not guess which one it meant, so we added an alias table.
And the Files task deleted OsmAnd's map, so we added the map check.
Each fix came from one recorded failure and has an automatic test.

## Slide 30: Behind the final result

A few numbers show the work behind the result.
About 300 recorded runs across the project, 66 versions of the agent, 38 automatic tests, and 1531 executed steps in this agent's runs alone.
Every version change has a written reason, and every run has its log. This is what lets us explain the failures today, instead of guessing.

## Slide 31: What we learned, and what is still limited

To finish, what did we learn?
One: trust the test setup before you judge the model. Black screens and lost videos looked like agent failures at first.
Two: the official checker must decide, not the model. False completions are real, and they are the most dangerous failure.
Three: where knowledge lives matters. A Skill in the system prompt was ignored. Repeated each step it was followed. As code it worked best.
Four: long tasks fail by small errors adding up. A missed tap or a wrong guess at any step is enough.
Our limitations: three runs per task is a small sample; we used one model; the OsmAnd Skill only works for OsmAnd; and two tasks used extra screen labels, which we report in the results.

## Slide 32: Thank you

Thank you for listening. We are happy to take your questions.

## Appendix slide 33 (not presented; for questions): What the agent can do, and what it sees in each task

The model can use seven actions: tap, type, swipe, launch an app, go back, wait, and finish. Taps use coordinates on a grid from 0 to 1000.
What the agent sees is the screenshot. For two tasks it also gets text labels of the screen elements. For Wi-Fi these come from the Settings app. For OsmAnd they come from AndroidWorld's accessibility tree, the same information a screen reader uses.
We show this openly because it changes what we measure: five tasks were solved from the screenshot alone, two had extra help. The course example log on slide 49 also lists "accessibility tree" as an observation type, so this is allowed, but it must be reported.

## Appendix slide 34 (not presented; for questions): Steps used versus the course's reference steps

This chart compares the steps our agent used in passing runs with the reference steps from the course list.
On simple tasks the agent needs a few more steps than the reference, for example because it checks the result or opens a menu first.
Markor needs about twice the reference: the note's name and extension take several steps, and sharing goes through a menu, the share sheet and the number.
On OsmAnd it is the other way round: the reference is 60 steps, and our agent needed only about 22, because the coded Skill leads it along the shortest path.
The light bar is the step budget, the maximum we allow before we stop a run.

## Appendix slide 35 (not presented; for questions): Speed and cost: about 0.066 € for all 21 runs

How long and how expensive was it?
Simple tasks finished in about one to two minutes. Markor took about three and a half minutes and OsmAnd about nine, including app start and setup time.
All 21 runs together used about 1.47 million tokens. At 0.045 euro per million tokens, that is about 0.066 euro.
Even the whole project, all local development runs together, cost only about 0.51 euro in model calls.
The model answers fast, 1.75 seconds per call at the median. Most of the time per step is the phone: waiting for screens to load, typing, and saving logs and video.
