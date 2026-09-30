"""Shared, explicit source selection and limits."""

from __future__ import annotations

import glob
import itertools
import os
import stat
from dataclasses import dataclass
from pathlib import Path


BUILTIN = {".txt", ".md", ".markdown", ".docx", ".html", ".htm", ".epub"}
OPTIONAL = {".pdf"}
RECOGNIZED = BUILTIN | OPTIONAL | {".rtf", ".mobi", ".azw", ".azw3"}


@dataclass(frozen=True)
class Limits:
    max_files: int = 500
    max_entries: int = 5000
    max_file_bytes: int = 50 * 1024 * 1024
    max_total_bytes: int = 250 * 1024 * 1024
    max_depth: int = 20
    max_archive_entries: int = 2000
    max_archive_bytes: int = 150 * 1024 * 1024
    max_archive_ratio: int = 200
    max_text_chars: int = 20_000_000

    def __post_init__(self) -> None:
        if any(value <= 0 for value in vars(self).values()):
            raise ValueError("all source limits must be positive")


def within(path: Path, directory: Path) -> bool:
    try:
        path.resolve().relative_to(directory.resolve())
        return True
    except ValueError:
        return False


def label(path: Path) -> str:
    try:
        return path.absolute().relative_to(Path.cwd()).as_posix()
    except ValueError:
        return path.absolute().as_posix()


def is_link(path: Path) -> bool:
    """Catch symlinks and Windows junction/reparse directories."""
    if path.is_symlink():
        return True
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except OSError:
        return False
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def has_symlink_ancestor(path: Path) -> bool:
    absolute = path.absolute()
    return any(is_link(parent) for parent in (absolute, *absolute.parents))


def walk_files(selected: Path, output: Path, limits: Limits, skipped: list[dict[str, str]]):
    """Walk a selected tree in a stable order without following directory links."""
    for directory, dirnames, filenames in os.walk(selected, topdown=True, followlinks=False):
        current = Path(directory)
        depth = len(current.relative_to(selected).parts)
        kept = []
        for name in sorted(dirnames, key=str.casefold):
            child = current / name
            if within(child, output):
                continue
            if is_link(child):
                skipped.append({"path": label(child), "reason": "symlink"})
            elif depth + 1 > limits.max_depth:
                skipped.append({"path": label(child), "reason": "depth-limit"})
            else:
                kept.append(name)
        dirnames[:] = kept
        for name in sorted(filenames, key=str.casefold):
            yield current / name


def discover(raw_paths: list[str], output: Path, limits: Limits) -> tuple[list[Path], list[dict[str, str]]]:
    """Expand only named paths; never follow symlinks or include the output workspace."""
    found: list[Path] = []
    skipped: list[dict[str, str]] = []
    seen: set[Path] = set()
    total = 0
    inspected = 0
    for raw in raw_paths:
        expanded = Path(raw).expanduser()
        if glob.has_magic(str(expanded)):
            expanded_matches = list(itertools.islice(glob.iglob(str(expanded), recursive=True), limits.max_entries + 1))
            if len(expanded_matches) > limits.max_entries:
                skipped.append({"path": raw, "reason": "glob-entry-limit"})
            matches = sorted((Path(p) for p in expanded_matches[:limits.max_entries]), key=lambda p: str(p).casefold())
        else:
            matches = [expanded]
        if not matches:
            skipped.append({"path": raw, "reason": "missing"})
        for selected in matches:
            if not selected.exists() and not selected.is_symlink():
                skipped.append({"path": label(selected), "reason": "missing"})
                continue
            if has_symlink_ancestor(selected):
                skipped.append({"path": label(selected), "reason": "symlink"})
                continue
            if selected.is_file():
                candidates = [selected]
            elif selected.is_dir():
                candidates = walk_files(selected, output, limits, skipped)
            else:
                skipped.append({"path": label(selected), "reason": "not-file"})
                continue
            for item in candidates:
                inspected += 1
                if inspected > limits.max_entries:
                    skipped.append({"path": label(selected), "reason": "entry-count-limit"})
                    break
                if within(item, output):
                    continue
                if is_link(item):
                    skipped.append({"path": label(item), "reason": "symlink"})
                    continue
                if not item.is_file():
                    continue
                if selected.is_dir() and len(item.relative_to(selected).parts) > limits.max_depth:
                    skipped.append({"path": label(item), "reason": "depth-limit"})
                    continue
                identity = item.resolve()
                if identity in seen:
                    continue
                seen.add(identity)
                if item.suffix.lower() not in RECOGNIZED:
                    skipped.append({"path": label(item), "reason": "unsupported"})
                    continue
                size = item.stat().st_size
                if size > limits.max_file_bytes:
                    skipped.append({"path": label(item), "reason": "file-size-limit"})
                    continue
                if len(found) >= limits.max_files:
                    skipped.append({"path": label(item), "reason": "file-count-limit"})
                    continue
                if total + size > limits.max_total_bytes:
                    skipped.append({"path": label(item), "reason": "total-size-limit"})
                    continue
                total += size
                found.append(item)
            if selected.is_dir() and not any(within(path, selected) for path in found) and not any(item["path"] == label(selected) and item["reason"] == "entry-count-limit" for item in skipped):
                skipped.append({"path": label(selected), "reason": "no-readable-files"})
    found.sort(key=lambda p: label(p).casefold())
    skipped.sort(key=lambda item: (item["path"].casefold(), item["reason"]))
    return found, skipped
