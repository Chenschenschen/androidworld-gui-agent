---
name: markor-note-then-sms
description: Save a Markor note, then share its text from the note (Share > Plain Text) as a plain SMS with Simple SMS Messenger. Loaded only for MarkorCreateNoteAndSms.
---
# Markor note, then share its content by SMS

Lessons from a teammate's runs of this task (Open-AutoGLM runner, 8 October 2026) and from checking the share path on our emulator (9 October 2026):

Facts about these app versions:
- "Share the entire content of the note via SMS" is done from the note itself: in Markor's editor, More options (three dots, top right) > Share > Plain Text hands the note's text to another app. Never choose Share > File: it attaches the file, which turns the message into an MMS that shows "Not sent".
- Markor's new-file dialog has a Name field and a separate extension field (.txt or .md). Together they must give the requested file name exactly.
- Android's share sheet may not show Simple SMS Messenger in its first row. Swipe up to see all apps and tap "SMS Messenger". "Messages" is a different app.
- After the share, Simple SMS Messenger opens "New conversation". After the number is confirmed with the checkmark, the message field already holds the note's text and the send button reads SMS.

Procedure:
1. Launch Markor. Tap the + button. Replace the Name text with the file name without its extension, set the extension field to the requested extension, and tap OK.
2. Type the exact text into the editor and tap Save.
3. Tap More options (three dots, top right), then Share, then Plain Text.
4. In the share sheet, swipe up if needed and tap SMS Messenger (not Messages).
5. Type the number into "Add Contact or Number…" and tap the checkmark on its right.
6. Do not type the text again: the message field already holds the note's text. Check that it shows exactly the requested text and no attachment, then tap the send button labelled SMS.
7. Finish only when a sent message with the exact text is shown without a "Not sent" warning.
