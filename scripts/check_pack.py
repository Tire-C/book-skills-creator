#!/usr/bin/env python3
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
required = ['README.md', 'source_index.md', 'skill_map.md', 'validation.md', 'router/SKILL.md']
missing = []
for item in required:
    if not (root / item).exists():
        missing.append(item)
for folder in ['atomic', 'combo', 'references']:
    if not (root / folder).exists():
        missing.append(folder + '/')
if missing:
    print('MISSING')
    for item in missing:
        print('-', item)
    raise SystemExit(1)
print('OK')
