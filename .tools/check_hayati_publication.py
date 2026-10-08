"""Check the hayati publication set without exposing credentials or editing runs."""
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
VIDEO = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v', '.wmv', '.mpeg', '.mpg', '.3gp', '.3g2', '.flv', '.ts'}


def main():
    """Audit prospective tracked files and retained original evidence hashes."""
    listed = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT)
    names = sorted(set(listed.decode('utf-8').rstrip('\0').split('\0')))
    keys = []
    for line in (ROOT / '.env').read_text(encoding='utf-8-sig').splitlines():
        name, separator, value = line.partition('=')
        if separator and 'KEY' in name and not name.lstrip().startswith('#'):
            value = value.strip().strip('\"\'')
            if value:
                keys.append(value.encode())
    secret_pattern = re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\r?\n[A-Za-z0-9+/=]{25,}|github_pat_[A-Za-z0-9_]{30,}|ghp_[A-Za-z0-9]{30,}|Bearer [A-Za-z0-9_.-]{25,}')
    total = 0
    runs = 0
    for name in names:
        file = ROOT / name
        assert file.is_file() and not file.is_symlink(), name
        assert file.name != '.env' and file.suffix.lower() not in VIDEO, name
        data = file.read_bytes()
        assert len(data) < 100 * 1024 * 1024, 'File exceeds GitHub limit: ' + name
        assert not any(key in data for key in keys), 'Local API credential found in ' + name
        suspicious = any(prefix in data for prefix in (b'-----BEGIN ', b'github_pat_', b'ghp_', b'Bearer '))
        assert not (suspicious and secret_pattern.search(data)), 'Possible credential found in ' + name
        if file.suffix.lower() == '.zip':
            with ZipFile(io.BytesIO(data)) as archive:
                for member in archive.infolist():
                    assert Path(member.filename).suffix.lower() not in VIDEO, 'Video inside archive: ' + name
                    content = archive.read(member)
                    assert not any(key in content for key in keys), 'Credential inside archive: ' + name
                    suspicious = any(prefix in content for prefix in (b'-----BEGIN ', b'github_pat_', b'ghp_', b'Bearer '))
                    assert not (suspicious and secret_pattern.search(content)), 'Possible credential inside archive: ' + name
        total += len(data)
        runs += name.startswith('runs/')
    # Original exported evidence must retain its previously recorded SHA256.
    manifest = json.loads((ROOT / 'docs/evidence/export_manifest.json').read_text(encoding='utf-8'))
    for item in manifest:
        assert hashlib.sha256((ROOT / item['export']).read_bytes()).hexdigest() == item['sha256'], item['export']
    print(json.dumps({'branch': subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT).decode().strip(), 'files': len(names), 'run_files': runs, 'nonvideo_mib': round(total / 1024 / 1024, 2), 'videos_in_publication': 0, 'local_api_keys_in_publication': 0, 'preserved_export_hashes': len(manifest)}, indent=2))


if __name__ == '__main__':
    main()
