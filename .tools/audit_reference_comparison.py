"""Audit immutable comparison artifacts and fully decode their local videos."""

import json
from pathlib import Path
import sys
import cv2

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT))
from autoglm_agent import api_settings

RUNS = [
    'trial_ClockTimerEntry_20261008T110331_988395Z',
    'trial_ClockTimerEntry_20261008T110453_899546Z',
    'trial_ClockTimerEntry_20261008T110722_819990Z',
    'trial_SystemCopyToClipboard_20261008T111031_420458Z',
    'trial_SystemCopyToClipboard_20261008T111249_290736Z',
    'trial_SystemCopyToClipboard_20261008T111502_200837Z',
    'trial_SystemCopyToClipboard_20261008T112059_418312Z',
]


def audit_run(name, key):
    """Validate JSON, readable request privacy and full video decoding per run."""
    folder = PROJECT / 'runs' / name
    summary = json.loads((folder/'summary.json').read_text())
    row = {field:summary.get(field) for field in ('task','version','agent_done','verifier',
        'evaluation_valid','clean_agent_success','steps','steps_attempted',
        'model_calls_attempted','gui_actions_dispatched','duration_seconds',
        'agent_phase_seconds','stop_reason','error_class','video_errors')}
    row.update(run_id=name, json_files=0, credential_found=False, request_contains_image_data=False,videos=[])
    for path in folder.rglob('*.json'):
        text = path.read_text(encoding='utf-8')
        json.loads(text)
        row['json_files'] += 1
        row['credential_found'] |= key in text
        if 'request' in path.name:
            row['request_contains_image_data'] |= 'data:image/' in text
    # Decode every frame; duration metadata alone does not prove a readable clip.
    for path in folder.glob('*.mp4'):
        video = cv2.VideoCapture(str(path))
        frames = 0
        fps = video.get(cv2.CAP_PROP_FPS)
        expected = video.get(cv2.CAP_PROP_FRAME_COUNT)
        while video.isOpened():
            ok,_ = video.read()
            if not ok:
                break
            frames += 1
        video.release()
        row['videos'].append({'file':path.name,'frames_decoded':frames,
            'frames_reported':expected,'fps':fps,'seconds':frames/fps if fps else None,
            'complete_decode':frames>0 and frames==int(expected)})
    return row


if __name__ == '__main__':
    key = api_settings()[2]
    rows = [audit_run(name,key) for name in RUNS]
    target = PROJECT/'docs/evidence/upstream_reference_audit.json'
    target.write_text(json.dumps(rows,indent=2)+chr(10))
    print(json.dumps(rows,indent=2))
