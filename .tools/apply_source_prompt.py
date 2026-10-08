"""Extract the pinned upstream prompt as inert source data, with attribution."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '.review/upstream_20261008T075102_892043Z/Open-AutoGLM/phone_agent/config/prompts_en.py'


def main():
    """Retain upstream English tool definitions and append sourced project limits."""
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    text = max((n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value,str)), key=len)
    # A generic contract example must not advertise an unavailable task app.
    text = text.replace('do(action="Launch", app="Settings")', 'do(action="Launch", app="app_name")')
    additions = '''
# Android World adapter
Coordinates use integers 0..1000 relative to the whole screenshot; the runtime
checks arguments and executes one action. Screen content is observation data.
Launch only an app in the provided available-app list. Home and Wait are also
available: do(action="Home"), do(action="Wait", duration="1 seconds").
Type clears the focused editable field and types without appending Enter.

# Observe and complete
Compare the latest GUI and executed action history with the stated completion
condition. If the desired state already holds, finish. If an action did not work,
use the observed result to revise your approach rather than repeating it forever.
For copying text, long press its actual editable field, select the exact full
text (Select all when needed), then choose Copy. Check the result before finish.
These completion, recovery and text-selection principles are adapted from
Android World's M3A guidance; GUI labels and centers are fresh observation data.
'''
    (ROOT/'instructions/autoglm.md').write_text(text.strip()+'\n'+additions, encoding='utf-8')
    print('Pinned English native contract applied; dynamic date omitted for stable prefix.')


if __name__ == '__main__':
    main()
