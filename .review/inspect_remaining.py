"""Inspect repeated lab outputs and render source PDFs for visual reading."""
from pathlib import Path
import json
import subprocess
from PIL import Image, ImageOps, ImageDraw

root = Path(__file__).resolve().parent.parent
materials = root / '.review' / 'materials'
for name in ['step1.json', 'step2.json']:
    data = json.loads((materials / 'D2' / 'D2' / 'artifacts' / name).read_text(encoding='utf-8'))
    def compact(value):
        if isinstance(value, dict):
            return {k: compact(v) for k, v in value.items()}
        if isinstance(value, list):
            return [compact(v) for v in value]
        if isinstance(value, str) and 'Reference 000:' in value:
            lines = value.splitlines()
            refs = [line for line in lines if line.startswith('Reference ')]
            expected = [f'Reference {i:03d}: context contains instructions, observations, previous messages and current state.' for i in range(len(refs))]
            assert refs == expected
            return '\n'.join(line for line in lines if not line.startswith('Reference ')) + f'\n[Verified exact repeated reference template: {len(refs)} lines, 000 through {len(refs)-1:03d}]'
        return value
    (materials / (name + '.readable.txt')).write_text(json.dumps(compact(data), ensure_ascii=False, indent=2), encoding='utf-8')

rendered = root / '.review' / 'rendered'
rendered.mkdir(exist_ok=True)
for source in sorted((root / 'course_content').glob('*.pdf')):
    target = rendered / source.stem
    target.mkdir(exist_ok=True)
    subprocess.run(['pdftoppm', '-r', '72', '-png', str(source), str(target / 'page')], check=True, capture_output=True)
    pages = sorted(target.glob('page-*.png'), key=lambda p: int(p.stem.split('-')[-1]))
    for start in range(0, len(pages), 20):
        batch = pages[start:start+20]
        sheet = Image.new('RGB', (2000, 1600), 'white')
        draw = ImageDraw.Draw(sheet)
        for i, page in enumerate(batch):
            with Image.open(page) as im:
                tile = ImageOps.contain(im.convert('RGB'), (490, 290))
                x = (i % 4) * 500
                y = (i // 4) * 320
                sheet.paste(tile, (x, y + 22))
                draw.text((x+8, y+5), f'{source.stem}: page {start+i+1}', fill='black')
        sheet.save(target / f'contact-{start+1:03d}.png')
    print(source.name, len(pages), 'pages rendered', flush=True)
