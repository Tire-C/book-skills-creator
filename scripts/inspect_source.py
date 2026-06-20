#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

SUPPORTED = {
    '.pdf', '.epub', '.docx', '.txt', '.md', '.markdown',
    '.html', '.htm', '.rtf', '.mobi', '.azw', '.azw3'
}


def iter_sources(path: Path):
    if path.is_file():
        yield path
    elif path.is_dir():
        for item in sorted(path.rglob('*')):
            if item.is_file():
                yield item


def main() -> None:
    parser = argparse.ArgumentParser(description='Inspect selected sources before pack creation.')
    parser.add_argument('paths', nargs='+')
    args = parser.parse_args()

    found = []
    skipped = []

    for raw in args.paths:
        path = Path(raw).expanduser()
        if not path.exists():
            skipped.append((str(path), 'missing'))
            continue
        for item in iter_sources(path):
            ext = item.suffix.lower()
            if ext in SUPPORTED:
                found.append(item)
            else:
                skipped.append((str(item), 'unsupported'))

    print('SUPPORTED')
    for item in found:
        size_kb = item.stat().st_size / 1024
        print(f'- {item} | {item.suffix.lower()} | {size_kb:.1f} KB')

    print('\nSKIPPED')
    for item, reason in skipped:
        print(f'- {item} | {reason}')

    print('\nCOUNT')
    print(len(found))

    if not found:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
