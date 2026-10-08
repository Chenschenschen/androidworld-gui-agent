"""Compare GPU layer counts on identical saved requests; execute no phone actions."""

import base64
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import subprocess
import sys
import threading
import time
import urllib.request

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
from probe_connection import save_json


def gpu_memory():
    """Read current dedicated NVIDIA memory use and capacity in MiB."""
    raw = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.used,memory.total',
        '--format=csv,noheader,nounits'], text=True)
    used, total = map(int, raw.strip().split(','))
    return {'used_mib': used, 'total_mib': total, 'percent': round(100 * used / total, 1)}


def monitor_memory(stop, samples):
    """Sample memory during inference, so final residency does not hide the peak."""
    # Sampling continues only until this one bounded API request finishes.
    while not stop.is_set():
        samples.append(gpu_memory())
        stop.wait(2)


def ask(payload, folder):
    """Run one saved request, keeping loading/tokens/timing and actual GPU residency."""
    folder.mkdir()
    logged = json.loads(json.dumps(payload))
    # Images remain on disk; never put base64 into a readable request artifact.
    for message in logged.get('messages', []):
        if 'images' in message:
            message['images'] = ['Frozen image from original step_008/model_input.png']
    save_json(folder / 'request.json', logged)
    samples, stop = [], threading.Event()
    monitor = threading.Thread(target=monitor_memory, args=(stop, samples))
    monitor.start()
    started = time.monotonic()
    try:
        request = urllib.request.Request('http://localhost:11434/api/chat',
            data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.load(response)
    finally:
        stop.set()
        monitor.join(timeout=5)
    result['wall_seconds'] = time.monotonic() - started
    save_json(folder / 'response.json', result)
    with urllib.request.urlopen('http://localhost:11434/api/ps', timeout=10) as response:
        residency = json.load(response)
    save_json(folder / 'residency.json', residency)
    save_json(folder / 'gpu_memory.json', samples)
    row = {'folder': folder.name, 'num_gpu': payload['options']['num_gpu'],
        'wall_seconds': result['wall_seconds'],
        'load_seconds': result.get('load_duration', 0) / 1e9,
        'prompt_seconds': result.get('prompt_eval_duration', 0) / 1e9,
        'generation_seconds': result.get('eval_duration', 0) / 1e9,
        'output_tokens': result.get('eval_count'),
        'peak_memory_percent': max(s['percent'] for s in samples),
        'peak_memory_mib': max(s['used_mib'] for s in samples),
        'reply': result['message']['content'], 'executed': False}
    print(json.dumps(row), flush=True)
    return row


def main():
    """Measure two warm tree repeats and one image request at 16 then 22 layers."""
    if Path(sys.prefix).resolve() != (PROJECT / '.venv').resolve():
        raise RuntimeError('Use project .venv Python')
    source = PROJECT / 'runs/trial_ContactsAddContact_20261007T165206_708350Z'
    output = PROJECT / 'runs' / datetime.now(timezone.utc).strftime('gpu_offload_%Y%m%dT%H%M%S_%fZ')
    output.mkdir()
    print('Evidence:', output, flush=True)
    tree = json.loads((source / 'step_004/tree/request_0.json').read_text())
    picture = json.loads((source / 'step_008/screenshot/request_0.json').read_text())
    picture['messages'][1]['images'] = [base64.b64encode(
        (source / 'step_008/model_input.png').read_bytes()).decode('ascii')]
    records = []
    # Change only GPU layer count; warm-up is recorded but excluded from comparison.
    for layers in (16, 22):
        warm = json.loads(json.dumps(tree))
        warm['options']['num_gpu'] = layers
        records.append({**ask(warm, output / f'gpu{layers}_warmup'), 'warmup': True})
        if records[-1]['peak_memory_percent'] > 85:
            raise RuntimeError('Memory headroom exceeded; do not retain this setting')
        # Identical saved inputs isolate placement/timing from GUI/task changes.
        for label, template in [('tree_1', tree), ('tree_2', tree), ('image_1', picture)]:
            payload = json.loads(json.dumps(template))
            payload['options']['num_gpu'] = layers
            records.append({**ask(payload, output / f'gpu{layers}_{label}'), 'warmup': False})
            save_json(output / 'progress.json', records)
    summary = {'kind': 'saved_request_gpu_probe', 'executed_phone_actions': False,
        'original_run': source.name, 'records': records,
        'limits': 'Two cached tree repeats and one image per setting; small diagnostic, not task quality or general speed evidence.'}
    summary['warm_tree_median_seconds'] = {str(layers): statistics.median(
        r['wall_seconds'] for r in records if r['num_gpu'] == layers and 'tree_' in r['folder'])
        for layers in (16, 22)}
    save_json(output / 'summary.json', summary)
    print(json.dumps(summary['warm_tree_median_seconds']), flush=True)


if __name__ == '__main__':
    main()
