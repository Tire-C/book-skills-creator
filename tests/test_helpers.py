from __future__ import annotations

import ast
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"


def run_script(script_name: str, *arguments: Path | str) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(SCRIPTS_DIR / script_name),
        *(str(argument) for argument in arguments),
    ]
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def write_valid_pack(root: Path) -> None:
    for filename in ("README.md", "source_index.md", "skill_map.md", "validation.md"):
        (root / filename).write_text(f"# {filename}\n", encoding="utf-8")

    for folder in ("atomic", "combo", "references"):
        (root / folder).mkdir(parents=True, exist_ok=True)

    router = root / "router" / "SKILL.md"
    router.parent.mkdir(parents=True, exist_ok=True)
    router.write_text(
        "---\n"
        "name: test-router\n"
        'description: "Route test requests."\n'
        "---\n\n"
        "# Test router\n",
        encoding="utf-8",
    )


def write_docx(path: Path, paragraphs: list[list[tuple[str, str]]]) -> None:
    """Create a minimal synthetic DOCX containing text, tabs, and line breaks."""
    namespace = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    paragraph_xml = []
    for paragraph in paragraphs:
        runs = []
        for kind, value in paragraph:
            if kind == "text":
                runs.append(f"<w:r><w:t>{value}</w:t></w:r>")
            elif kind == "tab":
                runs.append("<w:r><w:tab/></w:r>")
            elif kind == "break":
                runs.append("<w:r><w:br/></w:r>")
        paragraph_xml.append(f"<w:p>{''.join(runs)}</w:p>")

    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{namespace}"><w:body>'
        f"{''.join(paragraph_xml)}"
        "</w:body></w:document>"
    )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document_xml)


class InspectSourceTests(unittest.TestCase):
    def test_explicit_directory_reports_supported_and_unsupported_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_dir = Path(temporary)
            (source_dir / "sample.txt").write_text("Plain text fixture.", encoding="utf-8")
            (source_dir / "sample.md").write_text("# Markdown fixture\n", encoding="utf-8")
            write_docx(source_dir / "sample.docx", [[("text", "DOCX fixture.")]])
            (source_dir / "ignored.csv").write_text("a,b\n1,2\n", encoding="utf-8")

            result = run_script("inspect_source.py", source_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("sample.txt", result.stdout)
            self.assertIn("sample.md", result.stdout)
            self.assertIn("sample.docx", result.stdout)
            self.assertIn("ignored.csv | unsupported", result.stdout)
            self.assertRegex(result.stdout, r"COUNT\s+3\s*$")

    def test_returns_one_when_no_supported_source_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source_dir = Path(temporary)
            (source_dir / "ignored.csv").write_text("a,b\n1,2\n", encoding="utf-8")

            result = run_script("inspect_source.py", source_dir)

            self.assertEqual(result.returncode, 1)
            self.assertRegex(result.stdout, r"COUNT\s+0\s*$")


class ExtractTextTests(unittest.TestCase):
    def test_extracts_explicit_directory_and_deduplicates_overlapping_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_dir = root / "sources"
            output_dir = root / ".book_skills_work"
            source_dir.mkdir()
            text_file = source_dir / "sample.txt"
            markdown_file = source_dir / "sample.md"
            markdown_long_file = source_dir / "appendix.markdown"
            docx_file = source_dir / "sample.docx"
            text_file.write_text("Plain text fixture.", encoding="utf-8")
            markdown_file.write_text("# Markdown fixture\n\nSecond source.", encoding="utf-8")
            markdown_long_file.write_text(
                "# Markdown extension fixture\n", encoding="utf-8"
            )
            write_docx(
                docx_file,
                [
                    [("text", "DOCX first paragraph.")],
                    [
                        ("text", "Second"),
                        ("tab", ""),
                        ("text", "paragraph"),
                        ("break", ""),
                        ("text", "continued."),
                    ],
                ],
            )
            (source_dir / "ignored.csv").write_text("a,b\n1,2\n", encoding="utf-8")

            result = run_script(
                "extract_text.py",
                source_dir,
                text_file,
                "--output",
                output_dir,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("Plain text fixture.", result.stdout)
            self.assertNotIn("DOCX first paragraph.", result.stdout)
            self.assertTrue((output_dir / "full_text.txt").is_file())
            self.assertTrue((output_dir / "metadata.json").is_file())

            full_text = (output_dir / "full_text.txt").read_text(encoding="utf-8")
            metadata = json.loads(
                (output_dir / "metadata.json").read_text(encoding="utf-8")
            )

            self.assertEqual(full_text.count("SOURCE:"), 4)
            self.assertIn(
                "DOCX first paragraph.\nSecond\tparagraph\ncontinued.", full_text
            )
            self.assertEqual(metadata["supported_sources"], 4)
            self.assertEqual(metadata["skipped_sources"], 1)
            self.assertEqual(metadata["total_sources"], 5)
            self.assertGreater(metadata["total_bytes"], 0)
            self.assertGreater(metadata["total_characters"], 0)
            self.assertGreater(metadata["estimated_words"], 0)
            self.assertEqual(metadata["skipped"][0]["reason"], "unsupported")
            formats = {source["format"] for source in metadata["sources"]}
            self.assertEqual(formats, {"txt", "md", "markdown", "docx"})
            docx_metadata = next(
                source for source in metadata["sources"] if source["format"] == "docx"
            )
            self.assertEqual(docx_metadata["encoding"], "docx-xml")

    def test_invalid_docx_is_skipped_without_creating_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            invalid_docx = root / "invalid.docx"
            output_dir = root / ".book_skills_work"
            invalid_docx.write_bytes(b"not a zip archive")

            result = run_script(
                "extract_text.py", invalid_docx, "--output", output_dir
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("No readable TXT, Markdown, or DOCX sources", result.stdout)
            self.assertNotIn("not a zip archive", result.stdout)
            self.assertFalse(output_dir.exists())

    def test_docx_without_main_document_xml_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            incomplete_docx = root / "incomplete.docx"
            output_dir = root / ".book_skills_work"
            with zipfile.ZipFile(incomplete_docx, "w") as archive:
                archive.writestr("[Content_Types].xml", "<Types/>")

            result = run_script(
                "extract_text.py", incomplete_docx, "--output", output_dir
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("No readable TXT, Markdown, or DOCX sources", result.stdout)
            self.assertFalse(output_dir.exists())

    def test_docx_with_invalid_main_xml_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            malformed_docx = root / "malformed.docx"
            output_dir = root / ".book_skills_work"
            with zipfile.ZipFile(malformed_docx, "w") as archive:
                archive.writestr("word/document.xml", "<w:document>")

            result = run_script(
                "extract_text.py", malformed_docx, "--output", output_dir
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("No readable TXT, Markdown, or DOCX sources", result.stdout)
            self.assertFalse(output_dir.exists())

    def test_returns_one_and_writes_nothing_without_supported_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_dir = root / "sources"
            output_dir = root / ".book_skills_work"
            source_dir.mkdir()
            (source_dir / "ignored.csv").write_text("a,b\n1,2\n", encoding="utf-8")

            result = run_script(
                "extract_text.py", source_dir, "--output", output_dir
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("No readable TXT, Markdown, or DOCX sources", result.stdout)
            self.assertFalse(output_dir.exists())

    def test_symlink_input_is_skipped_when_supported_by_the_platform(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target.txt"
            link = root / "linked.txt"
            output_dir = root / ".book_skills_work"
            target.write_text("Symlink target fixture.", encoding="utf-8")

            try:
                link.symlink_to(target)
            except (NotImplementedError, OSError) as exc:
                self.skipTest(f"Symbolic links are unavailable: {exc}")

            result = run_script("extract_text.py", link, "--output", output_dir)

            self.assertEqual(result.returncode, 1)
            self.assertFalse(output_dir.exists())


class CheckPackTests(unittest.TestCase):
    def test_valid_pack_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack = Path(temporary) / "valid-pack"
            pack.mkdir()
            write_valid_pack(pack)

            result = run_script("check_pack.py", pack)

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stdout.strip(), "OK")

    def test_missing_pack_files_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack = Path(temporary) / "incomplete-pack"
            pack.mkdir()

            result = run_script("check_pack.py", pack)

            self.assertEqual(result.returncode, 1)
            self.assertIn("MISSING", result.stdout)
            self.assertIn("router/SKILL.md", result.stdout)

    def test_invalid_skill_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack = Path(temporary) / "invalid-pack"
            pack.mkdir()
            write_valid_pack(pack)
            (pack / "atomic" / "broken" / "SKILL.md").parent.mkdir(parents=True)
            (pack / "atomic" / "broken" / "SKILL.md").write_text(
                "# Missing metadata\n", encoding="utf-8"
            )

            result = run_script("check_pack.py", pack)

            self.assertEqual(result.returncode, 1)
            self.assertIn("INVALID_SKILL_FILES", result.stdout)
            self.assertIn("broken", result.stdout)


class RepositoryQualityTests(unittest.TestCase):
    def test_all_python_files_parse(self) -> None:
        python_files = sorted(SCRIPTS_DIR.glob("*.py")) + sorted(
            (REPO_ROOT / "tests").glob("*.py")
        )
        self.assertTrue(python_files)
        for path in python_files:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_extraction_workspace_is_ignored_and_untracked(self) -> None:
        git = shutil.which("git")
        if git is None:
            self.skipTest("Git is unavailable")

        ignored = subprocess.run(
            [git, "check-ignore", ".book_skills_work/full_text.txt"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        tracked = subprocess.run(
            [git, "ls-files", ".book_skills_work"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(ignored.returncode, 0, ignored.stderr)
        self.assertEqual(tracked.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
