# Named successful recordings

Local copies are in `runs/presentation`. Original run folders and summaries are
preserved; copied summaries retain their original run IDs for provenance.

Use the named *_complete.mp4 files for Files playback. Android screenrecord
rolls over after roughly three minutes, so *_video_001.mp4 may stop before MOVE
and *_video_002.mp4 continues. These are parts, not missing task endings. All
four Files complete files preserve the summed original frame counts (335,570,
303,574 respectively), including their post-move state. Original clips remain.
The derived complete files concatenate recorded parts without re-encoding;
they do not fill recorder rollover pauses with invented frames.
The presentation index.json now lists complete_video for each Files success.

| Named folder and matching MP4 | Original run | Result |
| --- | --- | --- |
|SMS_01_seed42_PASS_v45|trial_SimpleSmsSend_20261008T130636_231233Z|Official PASS, model finish at10|
|SMS_02_seed43_PASS_v49|trial_SimpleSmsSend_20261008T132854_166582Z|Official PASS, model finish at7|
|SMS_03_seed44_PASS_v49|trial_SimpleSmsSend_20261008T133321_726192Z|Official PASS, model finish at7|
|FILES_01_easy_to_medium_PASS_v52|trial_FilesMoveFile_20261008T141450_696380Z|Official PASS, model finish at12; two clips|
|FILES_V53_01_easy_to_medium_PASS|trial_FilesMoveFile_20261008T153825_684536Z|Official PASS, model finish at20; two clips|
|FILES_V53_02_medium_to_easy_PASS|trial_FilesMoveFile_20261008T154346_710337Z|Official PASS, model finish at12; two clips|
|FILES_V54_03_easy_to_medium_PASS|trial_FilesMoveFile_20261008T155433_701814Z|Official PASS, model finish at19; two clips|

Each folder contains the full trajectory, source/settings, screenshots, summary
and video. Matching named MP4s are directly in `runs/presentation` for presenting.
Use the latest two SMS recordings to show the same repaired version; the first
recording uses an earlier version. See SIMPLE_SMS_TRIAL.md for all failures.
The Files folder has two correspondingly named MP4s. All 228 files match the
original; both clips decoded fully (320 and 15 frames). This initial Files PASS
alone does not establish a successful three-move linked sequence.
The fresh v53 forward archive has348 identical copied files and clips decoded
at332/238 frames. A manual file return before this sequence is recorded in FILES_MOVE_TRIAL.md.
The v53 reverse archive has221 identical files and clips decoded at298/5 frames.
The final v54 archive has348 identical files and clips decoded at348/226 frames.
Present FILES_V53_01, FILES_V53_02 and FILES_V54_03 for the requested linked
forward/back/forward sequence. The third needed one failed v53 attempt and a
bounded XML-read repair; these three successes use two versions, not a frozen
3/3 first-attempt gate. All earlier failures remain in the original runs archive.
