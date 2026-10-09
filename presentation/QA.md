# Q&A preparation

Short answers in simple English. Numbers match the slides and the run records. Appendix slides 27–29 (after the Thank-you slide) back up some answers.

## About the model

**Q1. Which model did you use, and why?**
AutoGLM-Phone-9B-Multilingual, through the Z.ai API. It is trained to control phone screens, it has a clear action format that we can parse reliably, and it is fast and cheap: 1.77 seconds per call at the median, and 0.045 euro per million tokens. All 21 final runs cost about 0.065 euro.

**Q2. The course slide suggests GELab-Zero. Why did you not use it?**
We started with it. Our first ten versions ran GELab-Zero 4B locally with Ollama on a laptop GPU with 8 GB of memory. The model did not fit completely, so one screenshot request took about 20 seconds. Only 1 of 6 Contacts trials passed, and in a Wi-Fi run the model used an action format our parser could not accept and claimed Wi-Fi was on when it was not. The course allows any model, so we switched, and we report this as an unsuccessful attempt.

**Q3. You say AutoGLM is "top-ranked". What is the evidence?**
The AndroidWorld leaderboard lists a 9B AutoGLM-Mobile entry at 80.2 percent. It is a community entry and may not be the exact hosted version we call, so we only say "one of the top-ranked model families", not "the best".

**Q4. Would a bigger or better model solve your failures?**
Partly. Two of our three final failures are perception or grounding errors: the model misread a cut-off file name and tapped just outside a button. A stronger vision model may help there. But it would not know app facts, like Markor's Share menu making a failing MMS. That needs knowledge, not size.

## About the method

**Q5. Is giving the agent the accessibility tree cheating?**
No, but it changes what we measure, so we report it per task. AndroidWorld provides this tree itself, it is what a screen reader sees, and it contains no answer. The course example log on slide 49 even lists "accessibility tree" as an observation type. Five of our seven tasks used only the screenshot. Wi-Fi had Settings labels, and OsmAnd had the tree plus a coded Skill. (Appendix slide 27 shows this per task.)

**Q6. Is the OsmAnd Skill just a hard-coded solution?**
It is app knowledge in code, and we say that openly. It reads the screen and suggests the next step and where to tap. But it never taps by itself: the model decides every action, and in our runs it ignored the suggestion several times, for example by tapping the navigation button. Without the Skill, the same model passed 0 of 3. With it, 2 of 3. It only works for OsmAnd.

**Q7. Did the agent ever see the verifier result during a run?**
No. The official verifier runs only after the run ends. One earlier experiment in our project fed the verifier result back to the model during a run. We decided that this is like seeing the answer, so we did not use that idea or those results.

**Q8. When your checks refuse an action, are you not helping the model too much?**
The checks only stop actions that are clearly invalid on the real screen: a broken reply, typing with no focused text field, or a known trap button. The model still has to find the right action itself. In the final runs only 8 actions were refused, and the runs still had to pass the official verifier.

**Q9. In Markor + SMS, did the agent share the note, or type the text again?**
In the evaluated version (v65) it typed the same text again in Simple SMS Messenger. The official checker looks at two things: the note file with the right name and text, and a sent SMS with exactly that text to the right number. It does not check how the text got into the SMS. Markor's file share attaches the file, so the message becomes an MMS that shows "Not sent", and the checker gives only half the score. After the freeze we changed only the Markor Skill to Markor's own Share > Plain Text, which hands the note's text to the SMS app, and evaluated it separately with the same three seeds: all three runs shared the note and none typed the text again; two passed, and one missed the SMS send button (a grounding error). Details: docs/MARKOR_SHARE_V66.md.

## About the results

**Q10. Is three runs per task enough?**
It is the course requirement, and it is a small sample. That is why we do not claim success rates like "100 percent". We say "3 of 3 runs" and we look at the reasons for each failure, which is more useful than the number alone.

**Q11. Why did you not rerun the failed runs?**
The version was frozen. Rerunning the same code until it passes only measures luck. We kept all failures and analysed them instead.

**Q12. Why does OsmAnd use seeds 31, 314 and 366 and the other tasks 42, 43 and 44?**
A seed only chooses the task's parameters. The course slide shows OsmAnd with one fixed route, Ruggell then Bendern, and these three seeds produce exactly that route. The other tasks are shown as templates, so any seed is valid; we used 42, 43 and 44 for all of them.

**Q13. Contacts passed 3 of 3 in an earlier evaluation and 2 of 3 now. Did the agent get worse?**
Not necessarily. The same seed passed before and failed now, and each run starts fresh with no memory. Long tasks have many steps, and a small error at one step is enough. OsmAnd shows the same thing: 2 of 3 in two evaluations, but a different run failed each time.

**Q14. Is the improvement fair? How do you know the Skill caused it?**
We ran the same frozen code, the same seeds and the same model, and changed only one setting: the Skill on or off. Both batches have the same source fingerprint. Without the Skill 0 of 3, with it 2 of 3. Three runs per side is still a small sample.

## About cost and next steps

**Q15. How much did it cost?**
About 0.065 euro for the 21 final runs, 1.45 million tokens. All runs of this agent on our machine together cost about 0.48 euro. (Appendix slide 29 has run time and cost per task.)

**Q16. What would you do next?**
More seeds per task for a better estimate. A check that the selected item is exactly the requested one, which would fix the Files false finish. Snapping a tap that lands just outside a button to that button, which would fix the OsmAnd miss. And a more general way to build Skills, so that a new app does not need hand-written steps.
