"""Build presentation videos from the 21 final runs: per-run joins, a 7x3 sped-up wall, two featured clips, posters.

usage: python make_videos.py <project> <out_dir>
"""
import json, math, subprocess, sys
from pathlib import Path

project, out = Path(sys.argv[1]), Path(sys.argv[2])
(out / "parts").mkdir(parents=True, exist_ok=True)
FONT = "C\\:/Windows/Fonts/arialbd.ttf"
ORDER = ["SystemWifiTurnOn", "ContactsAddContact", "SimpleSmsSend", "FilesMoveFile",
         "SimpleCalendarAddOneEvent", "MarkorCreateNoteAndSms", "OsmAndTrack"]
SHORT = {"SystemWifiTurnOn": "Wi-Fi", "ContactsAddContact": "Contacts", "SimpleSmsSend": "SMS", "FilesMoveFile": "Files",
         "SimpleCalendarAddOneEvent": "Calendar", "MarkorCreateNoteAndSms": "Markor+SMS", "OsmAndTrack": "OsmAnd"}
WALL_SECONDS, TILE_W, TILE_H = 45, 180, 400

def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)

def duration(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).decode())

runs = []
for batch in ("eval_batch_20261008T215129_132839Z", "eval_batch_20261008T223002_941777Z"):
    runs += [r for r in json.loads((project / "runs" / batch / "results.json").read_text(encoding="utf-8"))
             if r["task"] != "MarkorCreateNoteAndSms"]
# Markor + SMS: final runs come from v66 (Skill shares the note with Share > Plain Text)
runs += json.loads((project / "runs" / "eval_batch_20261009T125038_033286Z" / "results.json").read_text(encoding="utf-8"))
grid = {}
for r in runs:
    folder = project / "runs" / r["run_id"]
    clips = sorted(folder.glob("video_*.mp4"))
    listing = out / "parts" / f"{r['run_id']}.txt"
    listing.write_text("".join(f"file '{c.as_posix()}'\n" for c in clips), encoding="utf-8")
    full = out / "parts" / f"{r['run_id']}.mp4"
    if not full.exists():
        ff("-f", "concat", "-safe", "0", "-i", str(listing), "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-an", str(full))
    grid.setdefault(r["task"], []).append((r, full, duration(full)))

# One tile per run: sped up to end within WALL_SECONDS, labelled, frozen on its last frame afterwards.
tiles = []
for row in range(3):
    for task in ORDER:
        r, full, seconds = grid[task][row]
        speed = max(1, math.ceil(seconds / (WALL_SECONDS - 2)))  # every tile must reach its end
        verdict = r["verifier"]
        colour = "0x2E7D32" if verdict == "PASS" else "0xC0392B"
        tile = out / "parts" / f"tile_{task}_{row}.mp4"
        label = (f"drawbox=x=0:y=0:w=iw:h=58:color=0x1B1F2A@0.85:t=fill,"
                 f"drawtext=fontfile='{FONT}':text='{SHORT[task]}  s{r['task_seed']}':fontcolor=white:fontsize=17:x=8:y=7,"
                 f"drawtext=fontfile='{FONT}':text='{verdict}  x{speed}':fontcolor=white:fontsize=15:x=8:y=33:box=1:boxcolor={colour}@1:boxborderw=3")
        ff("-i", str(full), "-vf", f"setpts=PTS/{speed},scale={TILE_W}:{TILE_H},{label},tpad=stop_mode=clone:stop_duration={WALL_SECONDS},fps=15",
           "-t", str(WALL_SECONDS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "28", "-an", str(tile))
        tiles.append(tile)
inputs = sum((["-i", str(t)] for t in tiles), [])
layout = "|".join(f"{c * TILE_W}_{r * TILE_H}" for r in range(3) for c in range(7))
ff(*inputs, "-filter_complex", f"xstack=inputs=21:layout={layout}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "27",
   "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out / "wall_21_runs.mp4"))
ff("-ss", str(WALL_SECONDS - 1), "-i", str(out / "wall_21_runs.mp4"), "-frames:v", "1", str(out / "wall_21_runs_poster.png"))

# Featured clips at a fixed speed with a caption bar.
def featured(task, row, speed, caption, name):
    r, full, seconds = grid[task][row]
    text = caption.replace(":", "\\:")
    ff("-i", str(full), "-vf", f"setpts=PTS/{speed},drawbox=x=0:y=0:w=iw:h=86:color=0x1B1F2A@0.85:t=fill,"
       f"drawtext=fontfile='{FONT}':text='{text}':fontcolor=white:fontsize=26:x=16:y=14,"
       f"drawtext=fontfile='{FONT}':text='{r['verifier']}  |  x{speed} speed':fontcolor=white:fontsize=22:x=16:y=50,fps=25",
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(out / f"{name}.mp4"))
    mid = seconds / speed / 2
    ff("-ss", f"{mid:.1f}", "-i", str(out / f"{name}.mp4"), "-frames:v", "1", str(out / f"{name}_poster.png"))
    return seconds / speed

print("featured success", featured("FilesMoveFile", 0, 3, "Files move, seed 42", "featured_files_pass"))
print("featured failure", featured("FilesMoveFile", 1, 3, "Files move, seed 43", "featured_files_fail"))
print("featured Markor pass", featured("MarkorCreateNoteAndSms", 1, 4, "Markor + SMS (shares the note), seed 43", "featured_markor_v66_pass"))
print("featured Markor fail", featured("MarkorCreateNoteAndSms", 0, 4, "Markor + SMS (shares the note), seed 42", "featured_markor_v66_fail"))
print("wall", duration(out / "wall_21_runs.mp4"), "s")
