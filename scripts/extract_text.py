#!/usr/bin/env python3
"""Extract selected text, Markdown, and DOCX sources into a local workspace."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree


SUPPORTED_EXTENSIONS = {".txt", ".md", ".markdown", ".docx"}
DEFAULT_OUTPUT = Path(".book_skills_work")
SEPARATOR_WIDTH = 72
WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def is_within(path: Path, directory: Path) -> bool:
    """Return whether path is inside directory without requiring either to exist."""
    try:
        path.resolve().relative_to(directory.resolve())
    except ValueError:
        return False
    return True


def iter_selected_files(path: Path, output_dir: Path) -> Iterable[Path]:
    """Yield files from an explicitly selected file or directory."""
    if path.is_symlink():
        return
    if path.is_file():
        if not is_within(path, output_dir):
            yield path
        return
    if path.is_dir():
        for item in sorted(path.rglob("*"), key=lambda candidate: candidate.as_posix().casefold()):
            if item.is_symlink() or is_within(item, output_dir):
                continue
            if item.is_file():
                yield item


def read_plain_text(path: Path) -> tuple[str, str]:
    """Read UTF-8 text, using replacement characters as a safe final fallback."""
    data = path.read_bytes()
    try:
        return data.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace"), "utf-8-replacement"


def extract_docx_text(path: Path) -> str:
    """Extract paragraphs from the main DOCX document XML."""
    try:
        with zipfile.ZipFile(path) as archive:
            document_xml = archive.read("word/document.xml")
    except KeyError as exc:
        raise ValueError("missing-document-xml") from exc
    except (zipfile.BadZipFile, RuntimeError) as exc:
        raise ValueError("invalid-docx-archive") from exc

    try:
        root = ElementTree.fromstring(document_xml)
    except ElementTree.ParseError as exc:
        raise ValueError("invalid-document-xml") from exc

    paragraphs = []
    paragraph_tag = f"{{{WORD_NAMESPACE}}}p"
    text_tag = f"{{{WORD_NAMESPACE}}}t"
    tab_tag = f"{{{WORD_NAMESPACE}}}tab"
    break_tags = {
        f"{{{WORD_NAMESPACE}}}br",
        f"{{{WORD_NAMESPACE}}}cr",
    }

    for paragraph in root.iter(paragraph_tag):
        fragments = []
        for element in paragraph.iter():
            if element.tag == text_tag and element.text:
                fragments.append(element.text)
            elif element.tag == tab_tag:
                fragments.append("\t")
            elif element.tag in break_tags:
                fragments.append("\n")
        paragraphs.append("".join(fragments))

    return "\n".join(paragraphs)


def read_source(path: Path) -> tuple[str, str]:
    """Read a supported source and return its text and decoding method."""
    if path.suffix.lower() == ".docx":
        return extract_docx_text(path), "docx-xml"
    return read_plain_text(path)


def source_label(path: Path) -> str:
    """Return a stable, non-resolved path label for output metadata."""
    try:
        return path.relative_to(Path.cwd()).as_posix()
    except ValueError:
        return path.as_posix()


def collect_sources(
    raw_paths: list[str], output_dir: Path
) -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    """Collect and decode supported files from only the user-selected inputs."""
    supported: list[dict[str, object]] = []
    skipped: list[dict[str, str]] = []
    seen: set[Path] = set()

    for raw_path in raw_paths:
        selected = Path(raw_path).expanduser()
        if not selected.exists():
            skipped.append({"path": selected.as_posix(), "reason": "missing"})
            continue
        if selected.is_symlink():
            skipped.append({"path": selected.as_posix(), "reason": "symlink"})
            continue

        found_file = False
        for item in iter_selected_files(selected, output_dir):
            found_file = True
            identity = item.resolve()
            if identity in seen:
                continue
            seen.add(identity)

            if item.suffix.lower() not in SUPPORTED_EXTENSIONS:
                skipped.append({"path": source_label(item), "reason": "unsupported"})
                continue

            try:
                raw_size = item.stat().st_size
                text, encoding = read_source(item)
            except (OSError, ValueError) as exc:
                reason = str(exc) if isinstance(exc, ValueError) else exc.__class__.__name__
                skipped.append(
                    {
                        "path": source_label(item),
                        "reason": f"read-error: {reason}",
                    }
                )
                continue

            supported.append(
                {
                    "path": source_label(item),
                    "format": item.suffix.lower().lstrip("."),
                    "bytes": raw_size,
                    "characters": len(text),
                    "encoding": encoding,
                    "text": text,
                }
            )

        if selected.is_dir() and not found_file:
            skipped.append({"path": selected.as_posix(), "reason": "no-files"})

    supported.sort(key=lambda item: str(item["path"]).casefold())
    skipped.sort(key=lambda item: (item["path"].casefold(), item["reason"]))
    return supported, skipped


def build_full_text(sources: list[dict[str, object]]) -> str:
    """Combine sources with visible file boundaries."""
    sections = []
    rule = "=" * SEPARATOR_WIDTH
    for source in sources:
        text = str(source["text"]).rstrip()
        sections.append(f"{rule}\nSOURCE: {source['path']}\n{rule}\n\n{text}\n")
    return "\n".join(sections)


def build_metadata(
    sources: list[dict[str, object]], skipped: list[dict[str, str]]
) -> dict[str, object]:
    """Build extraction metadata without embedding source contents."""
    total_characters = sum(int(source["characters"]) for source in sources)
    estimated_words = sum(
        len(re.findall(r"\S+", str(source["text"]))) for source in sources
    )
    source_metadata = [
        {key: value for key, value in source.items() if key != "text"}
        for source in sources
    ]
    return {
        "total_sources": len(sources) + len(skipped),
        "supported_sources": len(sources),
        "skipped_sources": len(skipped),
        "total_bytes": sum(int(source["bytes"]) for source in sources),
        "total_characters": total_characters,
        "estimated_words": estimated_words,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": source_metadata,
        "skipped": skipped,
    }


def write_outputs(
    output_dir: Path, full_text: str, metadata: dict[str, object]
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "full_text.txt").write_text(full_text, encoding="utf-8")
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def print_summary(output_dir: Path, metadata: dict[str, object]) -> None:
    print("Extraction complete")
    print(f"Supported sources: {metadata['supported_sources']}")
    print(f"Skipped sources: {metadata['skipped_sources']}")
    print(f"Bytes read: {metadata['total_bytes']}")
    print(f"Characters extracted: {metadata['total_characters']}")
    print(f"Estimated words: {metadata['estimated_words']}")
    print(f"Output directory: {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract selected TXT, Markdown, and DOCX sources into a local workspace."
    )
    parser.add_argument("paths", nargs="+", help="Explicit source file(s) or folder(s)")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Workspace directory (default: .book_skills_work)",
    )
    args = parser.parse_args()

    output_dir = args.output.expanduser()
    sources, skipped = collect_sources(args.paths, output_dir)
    if not sources:
        print("No readable TXT, Markdown, or DOCX sources were found.")
        print(f"Skipped sources: {len(skipped)}")
        raise SystemExit(1)

    full_text = build_full_text(sources)
    metadata = build_metadata(sources, skipped)
    try:
        write_outputs(output_dir, full_text, metadata)
    except OSError as exc:
        parser.exit(2, f"error: could not write extraction workspace: {exc}\n")
    print_summary(output_dir, metadata)


if __name__ == "__main__":
    main()
