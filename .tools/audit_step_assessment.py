"""Audit completed assessment trials without model requests or device actions."""
import hashlib
import json
from pathlib import Path
import sys

import cv2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from autoglm_agent import api_settings
from probe_connection import save_json


def main():
    """Check original logs, dispatch counts, prompt snapshots and every video frame."""
    _, _, key = api_settings()
    names = ['trial_ClockTimerEntry_20261008T100055_458184Z',
        'trial_SystemCopyToClipboard_20261008T100628_570867Z',
        'trial_SystemCopyToClipboard_20261008T100911_808026Z',
        'trial_SystemCopyToClipboard_20261008T101351_637369Z']
    reviews = []
    # Audit each preserved version separately; never rewrite its original summary.
    for name in names:
        folder = ROOT/'runs'/name
        summary = json.loads((folder/'summary.json').read_text())
        review = {'run_id':name, 'summary':summary, 'json_errors':[],
            'credential_present':False, 'base64_in_readable_requests':False,
            'gui_dispatches_from_results':0, 'assessment_files':0, 'videos':[]}
        for path in folder.rglob('*'):
            if not path.is_file() or path.suffix not in {'.json','.jsonl','.txt','.py','.md','.xml'}:
                continue
            data = path.read_bytes()
            review['credential_present'] |= key.encode() in data
            if path.suffix == '.json':
                try:
                    value = json.loads(data)
                except ValueError:
                    review['json_errors'].append(str(path.relative_to(folder)))
                    continue
                if path.name == 'result.json':
                    review['gui_dispatches_from_results'] += bool(value.get('dispatch_returned'))
                if path.name == 'assessment.json':
                    review['assessment_files'] += 1
                if 'request' in path.name:
                    review['base64_in_readable_requests'] |= b'data:image/' in data
        review['source_hashes'] = {str(p.relative_to(folder/'source')):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (folder/'source').rglob('*') if p.is_file()}
        review['assessment_prompt_snapshotted'] = (folder/'source/instructions/assessment.md').is_file()
        # Full decode proves recordings are usable rather than merely nonempty.
        for path in sorted(folder.glob('video_*.mp4')):
            capture = cv2.VideoCapture(str(path))
            fps, frames = capture.get(cv2.CAP_PROP_FPS), 0
            while True:
                success, _ = capture.read()
                if not success:
                    break
                frames += 1
            capture.release()
            review['videos'].append({'file':path.name, 'frames_decoded':frames,
                'duration_seconds':frames/fps if fps else None})
        reviews.append(review)
    save_json(ROOT/'docs/evidence/step_assessment_audit.json', reviews)
    print(json.dumps({'trials':len(reviews), 'json_valid':all(not r['json_errors'] for r in reviews),
        'credentials_absent':all(not r['credential_present'] for r in reviews),
        'requests_without_base64':all(not r['base64_in_readable_requests'] for r in reviews),
        'videos_decode':all(r['videos'] and all(v['frames_decoded'] for v in r['videos']) for r in reviews),
        'dispatch_counts':[r['gui_dispatches_from_results'] for r in reviews]}, indent=2))


if __name__ == '__main__':
    main()
