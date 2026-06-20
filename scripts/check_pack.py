#!/usr/bin/env python3
import sys
from pathlib import Path

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
required = ['README.md', 'source_index.md', 'skill_map.md', 'validation.md', 'router/SKILL.md']
missing = []
invalid = []

for item in required:
    if not (root / item).exists():
        missing.append(item)

for folder in ['atomic', 'combo', 'references']:
    if not (root / folder).exists():
        missing.append(folder + '/')

for skill_file in root.glob('**/SKILL.md'):
    text = skill_file.read_text(encoding='utf-8').strip()
    if not text:
        invalid.append(str(skill_file))
    elif 'name:' not in text or 'description:' not in text:
        invalid.append(str(skill_file))

if missing or invalid:
    if missing:
        print('MISSING')
        for item in missing:
            print('-', item)
    if invalid:
        print('INVALID_SKILL_FILES')
        for item in invalid:
            print('-', item)
    raise SystemExit(1)

print('OK')
