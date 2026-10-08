"""Audit original general-guidance trials without changing their summaries."""

from pathlib import Path
import hashlib
import json
import sys
import cv2

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from autoglm_agent import api_settings

TRIALS = ['trial_SystemCopyToClipboard_20261008T120006_301144Z',
          'trial_SystemCopyToClipboard_20261008T120410_422924Z',
          'trial_SystemCopyToClipboard_20261008T121139_680477Z',
          'trial_SystemCopyToClipboard_20261008T121918_952583Z',
          'trial_SystemCopyToClipboard_20261008T122528_654658Z',
          'trial_SystemCopyToClipboard_20261008T123647_174079Z',
          'trial_SystemCopyToClipboard_20261008T124033_256747Z']


def audit_video(path):
    """Decode every frame and preserve measured duration and completeness."""
    capture = cv2.VideoCapture(str(path))
    expected, fps = int(capture.get(cv2.CAP_PROP_FRAME_COUNT)), capture.get(cv2.CAP_PROP_FPS)
    decoded = 0
    # Metadata alone cannot establish that the recorded frames are readable.
    while capture.read()[0]:
        decoded += 1
    capture.release()
    return {'path':str(path.relative_to(PROJECT)),'frames':decoded,'expected_frames':expected,
            'fully_decoded':decoded == expected and decoded > 0,'seconds':decoded/fps if fps else None}


def main():
    """Check JSON, credential/image redaction, actual guide flags and video readability."""
    _, _, key = api_settings()
    rows = []
    # Each immutable run is examined separately; invalid originals stay invalid.
    for trial_id in TRIALS:
        folder = PROJECT/'runs'/trial_id
        summary = json.loads((folder/'summary.json').read_text(encoding='utf-8'))
        config = json.loads((folder/'config.json').read_text(encoding='utf-8'))
        count, requests = 0, []
        for path in folder.rglob('*.json'):
            raw = path.read_text(encoding='utf-8')
            data = json.loads(raw)
            if key in raw or 'data:image/' in raw:
                raise ValueError('Readable JSON contains unredacted credential/image data')
            count += 1
            if path.name.startswith('request_'):
                messages = data['messages']
                system = messages[0]['content']
                requests.append({'path':str(path.relative_to(folder)),
                    'has_general_guidance':'General Android interaction guidance' in system,
                    'has_task_recipe':'TASK PROCEDURE' in system,
                    'has_editor_capability':'QuickNote tab opens an existing editable note' in system})
        rows.append({'run_id':trial_id,'original_summary':summary,'json_files':count,
            'task_guidance':config.get('task_guidance'),'interaction_guidance':config.get('interaction_guidance'),
            'requests':requests,'videos':[audit_video(path) for path in folder.glob('*video_*.mp4')],
            'interaction_sha256':hashlib.sha256((folder/'source/instructions/android_interactions.md').read_bytes()).hexdigest()})
    output = PROJECT/'docs/evidence/general_guidance_audit.json'
    output.write_text(json.dumps({'trials':rows,'original_summaries_unchanged':True},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'audit':str(output),'trials':len(rows),'json_files':sum(r['json_files'] for r in rows)}))


if __name__ == '__main__':
    main()
