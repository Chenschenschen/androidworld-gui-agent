"""Save pinned primary GitHub sources for an auditable protocol review."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def fetch(url):
    """Read a public source with a bounded timeout; never use project credentials."""
    request = urllib.request.Request(url, headers={'User-Agent':'course-agent-source-review'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def main():
    """Pin each repository revision and preserve reviewed source files unchanged."""
    out = ROOT / '.review' / datetime.now(timezone.utc).strftime('upstream_%Y%m%dT%H%M%S_%fZ')
    out.mkdir()
    repositories = {
        'zai-org/Open-AutoGLM': ['LICENSE','phone_agent/config/prompts_en.py','phone_agent/model/client.py','phone_agent/agent.py','phone_agent/actions/handler.py','phone_agent/adb/input.py'],
        'google-research/android_world': ['LICENSE','android_world/agents/m3a.py','android_world/agents/t3a.py','android_world/agents/base_agent.py','android_world/env/actuation.py','android_world/task_evals/single/clock.py'],
    }
    records = []
    # These downloads are independent evidence files, never executed from GitHub.
    for repo, files in repositories.items():
        sha = json.loads(fetch('https://api.github.com/repos/'+repo+'/commits/main'))['sha']
        for name in files:
            url = 'https://raw.githubusercontent.com/'+repo+'/'+sha+'/'+name
            data = fetch(url)
            path = out / repo.split('/')[1] / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            records.append({'repository':repo,'commit':sha,'file':name,'url':url,'sha256':hashlib.sha256(data).hexdigest()})
    (out/'manifest.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    print(json.dumps({'evidence':str(out),'sources':len(records)}), flush=True)


if __name__ == '__main__':
    main()
