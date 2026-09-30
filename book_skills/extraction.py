"""Structured local extraction. Source text stays in the ignored workspace."""

from __future__ import annotations

import hashlib
import json
import posixpath
import re
import shutil
import subprocess
import threading
import zipfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree as ET

from .discovery import BUILTIN, Limits, discover, label


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
OCF = "{urn:oasis:names:tc:opendocument:xmlns:container}"
OPF = "{http://www.idpf.org/2007/opf}"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_text(path: Path, limits: Limits) -> tuple[str, str, list[str]]:
    data = path.read_bytes()
    if len(data) > limits.max_file_bytes:
        raise ValueError("file-size-limit")
    try:
        return data.decode("utf-8-sig"), "utf-8", []
    except UnicodeDecodeError:
        return data.decode("utf-8", "replace"), "utf-8-replacement", ["invalid-utf8-replaced"]


def checked_archive(path: Path, limits: Limits) -> zipfile.ZipFile:
    archive: zipfile.ZipFile | None = None
    try:
        archive = zipfile.ZipFile(path)
        entries = archive.infolist()
        if len({entry.filename for entry in entries}) != len(entries):
            raise ValueError("duplicate-archive-entry")
        if len(entries) > limits.max_archive_entries:
            raise ValueError("archive-entry-limit")
        if sum(entry.file_size for entry in entries) > limits.max_archive_bytes:
            raise ValueError("archive-size-limit")
        for entry in entries:
            parts = entry.filename.replace("\\", "/").split("/")
            if entry.filename.startswith("/") or ".." in parts:
                raise ValueError("archive-path-invalid")
            if entry.file_size > limits.max_archive_bytes or (entry.file_size > 4096 and entry.file_size / max(entry.compress_size, 1) > limits.max_archive_ratio):
                raise ValueError("archive-ratio-limit")
        return archive
    except (zipfile.BadZipFile, OSError) as exc:
        if archive is not None:
            archive.close()
        raise ValueError("invalid-archive") from exc
    except ValueError:
        if archive is not None:
            archive.close()
        raise


def archive_read(archive: zipfile.ZipFile, name: str, limits: Limits) -> bytes:
    try:
        info = archive.getinfo(name)
        if info.file_size > limits.max_archive_bytes:
            raise ValueError("archive-size-limit")
        with archive.open(info) as stream:
            data = stream.read(info.file_size + 1)
        if len(data) != info.file_size:
            raise ValueError("archive-entry-size-mismatch")
        return data
    except KeyError as exc:
        raise ValueError("missing-archive-entry") from exc
    except (RuntimeError, zipfile.BadZipFile) as exc:
        raise ValueError("invalid-archive-entry") from exc


def blocks_text(text: str) -> list[dict]:
    blocks = []
    for match in re.finditer(r"\S(?:.*\S)?(?:\n(?!\s*\n)\S(?:.*\S)?)*", text):
        value = match.group().strip()
        if value:
            blocks.append({"kind": "paragraph", "text": value, "line_start": text.count("\n", 0, match.start()) + 1, "line_end": text.count("\n", 0, match.end()) + 1})
    return blocks


def blocks_markdown(text: str) -> list[dict]:
    lines = text.splitlines()
    blocks: list[dict] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        start = i + 1
        if re.match(r"^\s*(```|~~~)", line):
            fence = re.match(r"^\s*(```|~~~)", line).group(1)
            part = [line]
            i += 1
            while i < len(lines):
                part.append(lines[i])
                i += 1
                if lines[i - 1].lstrip().startswith(fence):
                    break
            kind = "code"
        elif re.match(r"^#{1,6}\s+", line):
            part = [line]
            i += 1
            kind = "heading"
        elif re.match(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)", line):
            part = []
            while i < len(lines) and re.match(r"^\s*(?:[-*+]\s+|\d+[.)]\s+|\s{2,}\S)", lines[i]):
                part.append(lines[i]); i += 1
            kind = "list"
        elif "|" in line and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            part = []
            while i < len(lines) and lines[i].strip() and "|" in lines[i]:
                part.append(lines[i]); i += 1
            kind = "table"
        else:
            part = []
            while i < len(lines) and lines[i].strip() and not re.match(r"^#{1,6}\s+|^\s*(```|~~~)", lines[i]):
                part.append(lines[i]); i += 1
            kind = "paragraph"
        blocks.append({"kind": kind, "text": "\n".join(part), "line_start": start, "line_end": i})
    return blocks


class StructuralHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blocks: list[dict] = []
        self.active: str | None = None
        self.depth = 0
        self.hidden = 0
        self.buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "nav"}:
            self.hidden += 1
        if self.hidden:
            return
        if self.active is None and tag in {"p", "li", "pre", "blockquote", "h1", "h2", "h3", "h4", "h5", "h6", "tr"}:
            self.active, self.depth, self.buffer = tag, 1, []
        elif self.active:
            if tag not in {"br", "img", "hr", "meta", "link", "input"}:
                self.depth += 1
            if tag in {"br", "td", "th"}:
                self.buffer.append("\n" if tag == "br" else " | ")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "nav"} and self.hidden:
            self.hidden -= 1
            return
        if self.hidden or not self.active:
            return
        if tag not in {"br", "img", "hr", "meta", "link", "input"}:
            self.depth -= 1
        if tag == self.active or self.depth <= 0:
            value = " ".join("".join(self.buffer).split())
            if value:
                kind = "heading" if re.fullmatch(r"h[1-6]", self.active) else ("table" if self.active == "tr" else "list" if self.active == "li" else "code" if self.active == "pre" else "paragraph")
                self.blocks.append({"kind": kind, "text": value, "level": int(self.active[1]) if kind == "heading" else None})
            self.active, self.depth, self.buffer = None, 0, []

    def handle_data(self, data: str) -> None:
        if not self.hidden and self.active:
            self.buffer.append(data)


def blocks_html(text: str) -> list[dict]:
    parser = StructuralHTML()
    parser.feed(text)
    return parser.blocks


def paragraph_text(element: ET.Element) -> str:
    parts = []
    for node in element.iter():
        if node.tag == W + "t" and node.text:
            parts.append(node.text)
        elif node.tag == W + "tab":
            parts.append("\t")
        elif node.tag in {W + "br", W + "cr"}:
            parts.append("\n")
    return "".join(parts)


def blocks_docx(path: Path, limits: Limits) -> list[dict]:
    with checked_archive(path, limits) as archive:
        try:
            root = ET.fromstring(archive_read(archive, "word/document.xml", limits))
        except ET.ParseError as exc:
            raise ValueError("invalid-document-xml") from exc
    body = root.find(W + "body")
    if body is None:
        raise ValueError("missing-document-body")
    blocks = []
    for node in body:
        if node.tag == W + "p":
            value = paragraph_text(node)
            if not value.strip():
                continue
            style = node.find("./" + W + "pPr/" + W + "pStyle")
            name = style.get(W + "val", "") if style is not None else ""
            heading = re.fullmatch(r"Heading([1-6])", name, re.IGNORECASE)
            blocks.append({"kind": "heading" if heading else "paragraph", "text": value, "level": int(heading.group(1)) if heading else None})
        elif node.tag == W + "tbl":
            rows = []
            for row in node.findall(W + "tr"):
                cells = [" ".join(paragraph_text(p) for p in cell.iter(W + "p")) for cell in row.findall(W + "tc")]
                rows.append(" | ".join(cells))
            if rows:
                blocks.append({"kind": "table", "text": "\n".join(rows)})
    return blocks


def blocks_epub(path: Path, limits: Limits) -> list[dict]:
    with checked_archive(path, limits) as archive:
        try:
            container = ET.fromstring(archive_read(archive, "META-INF/container.xml", limits))
            rootfile = container.find(".//" + OCF + "rootfile")
            if rootfile is None or not rootfile.get("full-path"):
                raise ValueError("missing-epub-package")
            opf_path = rootfile.get("full-path")
            if opf_path.startswith("/") or ".." in opf_path.split("/"):
                raise ValueError("archive-path-invalid")
            package = ET.fromstring(archive_read(archive, opf_path, limits))
        except ET.ParseError as exc:
            raise ValueError("invalid-epub-xml") from exc
        manifest = {item.get("id"): item.get("href") for item in package.findall(".//" + OPF + "manifest/" + OPF + "item")}
        spine = [item.get("idref") for item in package.findall(".//" + OPF + "spine/" + OPF + "itemref")]
        if not spine:
            raise ValueError("missing-epub-spine")
        blocks = []
        for idref in spine:
            href = manifest.get(idref)
            if not href:
                raise ValueError("missing-epub-spine-item")
            chapter_path = unquote(href.split("#")[0].split("?", 1)[0]).replace("\\", "/")
            name = posixpath.normpath(posixpath.join(posixpath.dirname(opf_path), chapter_path))
            if name.startswith(("../", "/")) or name == "..":
                raise ValueError("archive-path-invalid")
            chapter = archive_read(archive, name, limits).decode("utf-8-sig", "replace")
            blocks.extend(blocks_html(chapter))
        return blocks


def blocks_pdf(path: Path, limits: Limits) -> list[dict]:
    command = shutil.which("pdftotext")
    if not command:
        raise ValueError("pdftotext-unavailable")
    try:
        process = subprocess.Popen([command, "-layout", str(path), "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except OSError as exc:
        raise ValueError("pdftotext-failed") from exc
    timer = threading.Timer(60, process.kill)
    timer.daemon = True
    timer.start()
    try:
        assert process.stdout is not None
        data = process.stdout.read(limits.max_text_chars * 4 + 1)
        if len(data) > limits.max_text_chars * 4:
            process.kill()
            process.wait()
            raise ValueError("text-size-limit")
        process.wait()
    finally:
        timer.cancel()
        if process.stdout is not None:
            process.stdout.close()
    if process.returncode:
        raise ValueError("pdftotext-failed")
    text = data.decode("utf-8", "replace")
    if len(text) > limits.max_text_chars:
        raise ValueError("text-size-limit")
    if not text.strip():
        raise ValueError("pdf-no-readable-text")
    return blocks_text(text)


def normalize_units(source_id: str, blocks: list[dict], limits: Limits) -> list[dict]:
    headings: list[str] = []
    counters: dict[str, int] = {}
    units = []
    total = 0
    for order, block in enumerate(blocks, 1):
        content = block["text"].strip()
        total += len(content)
        if total > limits.max_text_chars:
            raise ValueError("text-size-limit")
        kind = block["kind"]
        if kind == "heading":
            level = block.get("level") or (len(re.match(r"^#+", content).group()) if content.startswith("#") else 1)
            heading = re.sub(r"^#{1,6}\s+", "", content)
            headings = headings[:level - 1] + [heading]
        key = json.dumps([headings, kind], ensure_ascii=False)
        counters[key] = counters.get(key, 0) + 1
        unit_id = source_id + "-" + digest((key + str(counters[key])).encode())[:12]
        units.append({"id": unit_id, "kind": kind, "heading_path": list(headings), "order": order,
                      "line_start": block.get("line_start"), "line_end": block.get("line_end"),
                      "characters": len(content), "words": len(content.split()), "sha256": digest(content.encode()), "text": content})
    return units


def extract_file(path: Path, limits: Limits) -> dict:
    original = path.read_bytes()
    if len(original) > limits.max_file_bytes:
        raise ValueError("file-size-limit")
    fmt = path.suffix.lower()
    source_id = "src-" + digest(label(path).encode())[:16]
    warnings: list[str] = []
    if fmt in {".txt", ".md", ".markdown", ".html", ".htm"}:
        content, encoding, warnings = read_text(path, limits)
        method = "markdown-blocks" if fmt in {".md", ".markdown"} else "html-blocks" if fmt in {".html", ".htm"} else "plain-text-blocks"
        if fmt in {".html", ".htm"}:
            warnings.append("nonstructural-html-may-be-omitted")
        blocks = blocks_markdown(content) if fmt in {".md", ".markdown"} else blocks_html(content) if fmt in {".html", ".htm"} else blocks_text(content)
    elif fmt == ".docx":
        method, encoding, blocks = "docx-xml", "docx-xml", blocks_docx(path, limits)
        warnings.append("main-document-only")
    elif fmt == ".epub":
        method, encoding, blocks = "epub-spine", "utf-8-replacement", blocks_epub(path, limits)
        warnings.append("media-and-layout-omitted")
    elif fmt == ".pdf":
        method, encoding, blocks = "pdftotext", "utf-8-replacement", blocks_pdf(path, limits)
        warnings.append("reading-order-uncertain")
    else:
        raise ValueError("extractor-unavailable")
    units = normalize_units(source_id, blocks, limits)
    if path.read_bytes() != original:
        raise ValueError("source-changed-during-extraction")
    if not units:
        warnings.append("no-readable-text")
    return {"id": source_id, "path": label(path), "format": fmt.lstrip("."), "bytes": len(original),
            "sha256": digest(original), "method": method, "extractor_version": "2.0",
            "encoding": encoding,
            "quality": "unreadable" if not units else "partial" if warnings else "complete",
            "extracted_at": datetime.now(timezone.utc).isoformat(), "extracted_sha256": digest("\n".join(u["text"] for u in units).encode()),
            "warnings": warnings, "units": units}


def extract_selected(paths: list[str], output: Path, limits: Limits) -> dict:
    files, skipped = discover(paths, output, limits)
    sources = []
    total_characters = 0
    for path in files:
        try:
            source = extract_file(path, limits)
            if not source["units"]:
                skipped.append({"path": label(path), "reason": "no-readable-text"})
                continue
            size = sum(unit["characters"] for unit in source["units"])
            if total_characters + size > limits.max_text_chars:
                raise ValueError("total-text-size-limit")
            total_characters += size
            sources.append(source)
        except (ValueError, OSError, RuntimeError, zipfile.BadZipFile) as exc:
            skipped.append({"path": label(path), "reason": str(exc) if isinstance(exc, ValueError) else "read-error"})
    return {"schema_version": "2.0", "sources": sources, "skipped": skipped}


def public_metadata(data: dict) -> dict:
    sources = [{key: value for key, value in source.items() if key != "units"} | {"characters": sum(u["characters"] for u in source["units"]), "unit_count": len(source["units"])} for source in data["sources"]]
    return {"schema_version": "2.0", "total_sources": len(sources) + len(data["skipped"]), "supported_sources": len(sources),
            "skipped_sources": len(data["skipped"]), "total_bytes": sum(s["bytes"] for s in sources),
            "total_characters": sum(s["characters"] for s in sources),
            "estimated_words": sum(u["words"] for s in data["sources"] for u in s["units"]),
            "sources": sources, "skipped": data["skipped"]}


def write_extraction(data: dict, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "sources.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output / "metadata.json").write_text(json.dumps(public_metadata(data), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sections = ["=" * 72 + "\nSOURCE: " + s["path"] + "\n" + "=" * 72 + "\n\n" + "\n".join(u["text"] for u in s["units"]) for s in data["sources"]]
    (output / "full_text.txt").write_text("\n\n".join(sections) + "\n", encoding="utf-8")
