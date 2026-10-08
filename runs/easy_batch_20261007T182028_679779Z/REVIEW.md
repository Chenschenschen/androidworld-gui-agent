# Interrupted diagnostic batch

This batch stopped after two Wi-Fi trials when a capture mismatch was found.
The original runner summaries/RESULTS.md are preserved, but these runs are
**excluded from the requested three-case capability evaluation**.

In `trial_SystemWifiTurnOn_20261007T182029_359660Z`, step 2, `before.png` shows
Settings while `tree.json` contains the launcher package and its Settings icon.
The model's tap is grounded in an obsolete tree. The seed-43 trial repeats this
pattern. Official FAIL remains the observed task outcome; classification is
an observation infrastructure error rather than clean model failure evidence.

The batch's source-hash check deliberately stopped further trials after the
active run completed. No GUI intervention was used to complete either task.
The replacement batch is `easy_batch_20261007T182934_895562Z`, using the official
UIAutomator tree backend for Wi-Fi. The preceding capture probe confirmed that
the Settings tree matches the foreground app and Wi-Fi remains off.

The a11y forwarder documents its networking dependency. Its recovery code can
enable Wi-Fi; the repaired Wi-Fi loader does not construct that wrapper.
This is an observation-method repair, not a change to the official verifier.
