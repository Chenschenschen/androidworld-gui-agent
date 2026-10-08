---
name: markor-note-then-sms
description: Save a Markor note, then send its text as a plain SMS with Simple SMS Messenger. Loaded only for MarkorCreateNoteAndSms.
---
# Markor note, then a plain SMS

Lessons from a teammate's runs of this task (Open-AutoGLM runner, 8 October 2026):

Facts about these app versions:
- "Share its entire content via SMS" means sending the note's text as a new SMS. Markor's own Share menu attaches the file, which turns the message into an MMS that shows "Not sent".
- Markor's new-file dialog has a Name field and a separate extension field (.txt or .md). Together they must give the requested file name exactly.
- Simple SMS Messenger starts a message from "Start a conversation" (or +): type the number, tap the checkmark, then type in "Type a message...". The send button reads SMS for a plain message and MMS when something is attached.

Procedure:
1. Launch Markor. Tap the + button. Replace the Name text with the file name without its extension, set the extension field to the requested extension, and tap OK.
2. Type the exact text into the editor and tap Save.
3. Launch Simple SMS Messenger. If Markor is still shown, press Home and Launch again; never repeat Back or EXIT inside Markor.
4. Tap Start a conversation (or +), type the number, tap the checkmark.
5. Tap "Type a message...", type the exact note text (no attachment preview may be visible), and tap the send button labelled SMS.
6. Finish only when a sent message with the exact text is shown without a "Not sent" warning.
