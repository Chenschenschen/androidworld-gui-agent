"""Read saved artifacts, decode videos and check private-key exclusion; no device actions."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import cv2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from autoglm_agent import api_settings
from probe_connection import save_json


def review_run(folder, expected, key, output):
    """Check one run's original trace, requests, switch transition and video decoding."""
    summary = json.loads((folder / 'summary.json').read_text())
    result = {'run_id':folder.name, 'summary':summary, 'missing':[], 'json_errors':[], 'credential_present':False,
              'source_matches_batch':True, 'calls':0, 'gui_actions':[], 'model_finish':[], 'switch_transitions':[], 'videos':[], 'incomplete_steps':[]}
    # Inspect original files; report only credential presence, never its value.
    for path in folder.rglob('*'):
        if path.is_file() and path.suffix in {'.json','.jsonl','.txt','.py','.md','.xml'}:
            data = path.read_bytes()
            result['credential_present'] |= key.encode() in data
            if path.suffix == '.json':
                try:
                    json.loads(data)
                except Exception:
                    result['json_errors'].append(str(path.relative_to(folder)))
    for name, digest in expected.items():
        path = folder / 'source' / name
        result['source_matches_batch'] &= path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == digest
    # Every completed step should retain its decision, reply and observed result.
    for step in sorted(folder.glob('step_*')):
        if int(step.name.split('_')[-1]) <= summary['steps']:
            for name in ('action.json','execution_start.json','result.json','after.png','after_tree.json'):
                if not (step / name).exists():
                    result['missing'].append(str((step / name).relative_to(folder)))
        else:
            result['incomplete_steps'].append({'step':step.name, 'execution_started':(step / 'execution_start.json').exists(),
                'note':'Expected interrupted/failed step; inspect saved request, error and stop reason.'})
        for observed in step.glob('observation_*'):
            for response in observed.glob('response_*.json'):
                result['calls'] += 1
                data = json.loads(response.read_text())
                assert data['model'] == 'autoglm-phone-multilingual'
        if (step / 'action.json').exists():
            action = json.loads((step / 'action.json').read_text())
            (result['model_finish'] if action['native']['command'] == 'finish' else result['gui_actions']).append({'step':step.name, **action['native']})
            before = step / action['observation_id'] / 'tree.json'
            after = step / 'after_tree.json'
            if before.exists() and after.exists():
                flags = [[{'label':(e.get('metadata') or {}).get('observed_label'), 'checked':e['is_checked']} for e in json.loads(p.read_text()) if e['is_checkable']] for p in (before,after)]
                if any(flags):
                    result['switch_transitions'].append({'step':step.name,'before':flags[0],'after':flags[1]})
    # Decode all frames, not only a container header, and retain the final frame.
    for video in folder.glob('video_*.mp4'):
        capture = cv2.VideoCapture(str(video))
        frames, last = 0, None
        while True:
            okay, frame = capture.read()
            if not okay:
                break
            frames, last = frames + 1, frame
        fps = capture.get(cv2.CAP_PROP_FPS)
        capture.release()
        if last is not None:
            cv2.imwrite(str(output / f'{folder.name}_{video.stem}_final.png'), last)
        result['videos'].append({'file':video.name,'frames_decoded':frames,'fps':fps,'duration_seconds':frames/fps if fps else None})
    return result


def main():
    """Create a new audit folder for a completed frozen evaluation batch."""
    batch = Path(sys.argv[1]).resolve()
    output = batch / datetime.now(timezone.utc).strftime('audit_%Y%m%dT%H%M%S_%fZ')
    output.mkdir()
    expected = json.loads((batch / 'batch.json').read_text())['source_hashes']
    records = json.loads((batch / 'results.json').read_text())
    _, _, key = api_settings()
    reviews = [review_run(ROOT / 'runs' / record['run_id'], expected, key, output) for record in records]
    save_json(output / 'artifact_review.json', reviews)
    print(json.dumps({'audit':str(output),'runs':len(reviews),'missing':sum(len(r['missing']) for r in reviews),
        'json_errors':sum(len(r['json_errors']) for r in reviews),'credential_present':any(r['credential_present'] for r in reviews),
        'sources_match':all(r['source_matches_batch'] for r in reviews),'videos_decode':all(r['videos'] and all(v['frames_decoded'] for v in r['videos']) for r in reviews)}, indent=2))


if __name__ == '__main__':
    main()
