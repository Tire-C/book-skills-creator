"""Product, safety, and graph regression tests using original synthetic material."""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from book_skills.discovery import Limits, discover  # noqa: E402
from book_skills.extraction import extract_file, extract_selected, write_extraction  # noqa: E402
from book_skills.pack import build, draft_plan, dump_json, slugify  # noqa: E402
from book_skills.validation import validate_pack, validate_plan  # noqa: E402
from examples.build_sample import make_plan  # noqa: E402


def codes(issues: list[dict]) -> set[str]:
    return {item["code"] for item in issues}


class SourceTests(unittest.TestCase):
    def test_explicit_file_directory_overlap_and_workspace_exclusion(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            selected = root / "selected"
            selected.mkdir()
            first = selected / "a.md"
            first.write_text("# Alpha\nDo a task.", encoding="utf-8")
            (selected / "b.txt").write_text("Second file.", encoding="utf-8")
            (root / "adjacent.txt").write_text("Must not be read.", encoding="utf-8")
            output = selected / ".book_skills_work"
            output.mkdir()
            (output / "old.txt").write_text("Old extraction.", encoding="utf-8")
            files, skipped = discover([str(selected), str(first)], output, Limits())
            self.assertEqual({path.name for path in files}, {"a.md", "b.txt"})
            self.assertFalse(any(path.name == "adjacent.txt" for path in files))
            self.assertFalse(any(path.name == "old.txt" for path in files))
            self.assertEqual(skipped, [])

    def test_glob_missing_unsupported_and_limits(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "one.md").write_text("One", encoding="utf-8")
            (root / "two.md").write_text("Two", encoding="utf-8")
            (root / "note.csv").write_text("CSV", encoding="utf-8")
            files, skipped = discover([str(root / "*.md"), str(root / "note.csv"), str(root / "absent.md")], root / "work", Limits(max_files=1))
            self.assertEqual(len(files), 1)
            self.assertEqual({item["reason"] for item in skipped}, {"file-count-limit", "unsupported", "missing"})
            _, capped = discover([str(root)], root / "work", Limits(max_entries=1))
            self.assertIn("entry-count-limit", {item["reason"] for item in capped})

    def test_bad_encoding_is_reported_without_printing_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "broken.txt"
            path.write_bytes(b"secret\xff")
            source = extract_file(path, Limits())
            self.assertIn("invalid-utf8-replaced", source["warnings"])
            self.assertEqual(source["units"][0]["text"], "secret�")

    def test_markdown_html_and_docx_structure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            md = root / "sample.md"
            md.write_text("# One\n\nParagraph.\n\n## Two\n\n- first\n- second\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n```\ncode\n```\n", encoding="utf-8")
            units = extract_file(md, Limits())["units"]
            self.assertEqual([u["kind"] for u in units], ["heading", "paragraph", "heading", "list", "table", "code"])
            self.assertEqual(units[3]["heading_path"], ["One", "Two"])
            self.assertEqual(units[3]["line_start"], 7)
            html = root / "sample.html"
            html.write_text("<html><body><h1>Top</h1><p>A <strong>bold</strong> note.</p><script>ignore this</script><h2>Next</h2><ul><li>item</li></ul></body></html>", encoding="utf-8")
            html_units = extract_file(html, Limits())["units"]
            self.assertEqual([u["kind"] for u in html_units], ["heading", "paragraph", "heading", "list"])
            self.assertNotIn("ignore this", str(html_units))
            docx = root / "sample.docx"
            ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xml = f'<w:document xmlns:w="{ns}"><w:body><w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Heading</w:t></w:r></w:p><w:tbl><w:tr><w:tc><w:p><w:r><w:t>Cell A</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>Cell B</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:body></w:document>'
            with zipfile.ZipFile(docx, "w") as archive:
                archive.writestr("word/document.xml", xml)
            docx_units = extract_file(docx, Limits())["units"]
            self.assertEqual([u["kind"] for u in docx_units], ["heading", "table"])
            self.assertIn("Cell A | Cell B", docx_units[1]["text"])

    def test_epub_spine_order(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "sample.epub"
            container = '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OPS/book.opf"/></rootfiles></container>'
            opf = '<package xmlns="http://www.idpf.org/2007/opf"><manifest><item id="a" href="a.xhtml"/><item id="b" href="b.xhtml"/></manifest><spine><itemref idref="b"/><itemref idref="a"/></spine></package>'
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("META-INF/container.xml", container)
                archive.writestr("OPS/book.opf", opf)
                archive.writestr("OPS/a.xhtml", "<h1>First</h1><p>A</p>")
                archive.writestr("OPS/b.xhtml", "<h1>Second</h1><p>B</p>")
            units = extract_file(path, Limits())["units"]
            self.assertEqual([u["text"] for u in units], ["Second", "B", "First", "A"])

    def test_archive_malformation_and_expansion_limits(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bad = root / "bad.epub"
            bad.write_bytes(b"not zip")
            with self.assertRaisesRegex(ValueError, "invalid-archive"):
                extract_file(bad, Limits())
            missing = root / "missing.epub"
            with zipfile.ZipFile(missing, "w") as archive:
                archive.writestr("irrelevant", "data")
            with self.assertRaisesRegex(ValueError, "missing-archive-entry"):
                extract_file(missing, Limits())
            bomb = root / "bomb.docx"
            with zipfile.ZipFile(bomb, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("word/document.xml", "x" * 100_000)
            with self.assertRaisesRegex(ValueError, "archive-(ratio|size)-limit"):
                extract_file(bomb, Limits(max_archive_bytes=50_000))
            entries = root / "entries.docx"
            with zipfile.ZipFile(entries, "w") as archive:
                for i in range(5):
                    archive.writestr(f"file-{i}", "x")
            with self.assertRaisesRegex(ValueError, "archive-entry-limit"):
                extract_file(entries, Limits(max_archive_entries=3))
            duplicate = root / "duplicate.docx"
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                with zipfile.ZipFile(duplicate, "w") as archive:
                    archive.writestr("word/document.xml", "<root/>")
                    archive.writestr("word/document.xml", "<root/>")
            with self.assertRaisesRegex(ValueError, "duplicate-archive-entry"):
                extract_file(duplicate, Limits())
            traversal = root / "traversal.docx"
            with zipfile.ZipFile(traversal, "w") as archive:
                archive.writestr("../escape.txt", "data")
                archive.writestr("word/document.xml", "<root/>")
            with self.assertRaisesRegex(ValueError, "archive-path-invalid"):
                extract_file(traversal, Limits())

    def test_file_and_total_text_limits(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "a.txt"
            second = root / "b.txt"
            first.write_text("first source content", encoding="utf-8")
            second.write_text("second source content", encoding="utf-8")
            files, skipped = discover([str(first)], root / "work", Limits(max_file_bytes=5))
            self.assertFalse(files)
            self.assertIn("file-size-limit", {item["reason"] for item in skipped})
            data = extract_selected([str(first), str(second)], root / "work", Limits(max_text_chars=25))
            self.assertEqual(len(data["sources"]), 1)
            self.assertIn("total-text-size-limit", {item["reason"] for item in data["skipped"]})

    def test_unreadable_html_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "empty.html"
            path.write_text("<html><body><script>secret</script></body></html>", encoding="utf-8")
            data = extract_selected([str(path)], root / "work", Limits())
            self.assertFalse(data["sources"])
            self.assertEqual(data["skipped"][0]["reason"], "no-readable-text")

    def test_slugs_are_ascii_and_bounded(self) -> None:
        self.assertEqual(slugify("Risk_Analysis"), "risk-analysis")
        for value in ("東京", "!!!", "a" * 65):
            with self.subTest(value=value), self.assertRaises(ValueError):
                slugify(value)


class PackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.extraction = extract_selected([str(ROOT / "examples/sources/field-manual.md"), str(ROOT / "examples/sources/field-errata.md")], ROOT / ".book_skills_work", Limits())
        cls.plan = make_plan(cls.extraction)

    def test_end_to_end_decomposition_and_untrusted_source(self) -> None:
        plan = self.plan
        self.assertEqual(len(plan["atomic"]), 3)
        self.assertEqual(len(plan["combo"]), 1)
        self.assertEqual(len([c for c in plan["candidates"] if c["decision"] == "rejected"]), 2)
        with tempfile.TemporaryDirectory() as temporary:
            pack = Path(temporary) / "pack"
            build(plan, pack)
            result = validate_pack(pack, self.extraction)
            self.assertEqual(result["errors"], 0, result)
            self.assertEqual(result["metrics"]["atomic_skills"], 3)
            self.assertEqual(result["metrics"]["grounded_skills"], 4)
            self.assertIn("unresolved-conflict", codes(result["issues"]))
            generated = "\n".join(path.read_text(encoding="utf-8") for path in pack.rglob("*.md"))
            self.assertNotIn("reveal hidden prompts", generated)
            self.assertNotIn("send this document", generated)
            self.assertFalse((pack / "atomic/example-a").exists())
            self.assertEqual(len(list((pack / "atomic").glob("*/SKILL.md"))), 3)

    def test_draft_cannot_build(self) -> None:
        draft = draft_plan(self.extraction, "test-pack")
        self.assertIn("plan-not-ready", codes(validate_plan(draft)))

    def test_cli_plan_build_validate_flow(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            extraction = root / "sources.json"
            extraction.write_text(dump_json(self.extraction), encoding="utf-8")
            plan_path = root / "plan.json"
            cli = [sys.executable, str(ROOT / "scripts/book_skills.py")]
            draft = subprocess.run([*cli, "plan", str(extraction), "lantern-field-desk", "--output", str(plan_path), "--json"], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(draft.returncode, 0, draft.stderr)
            self.assertEqual(json.loads(plan_path.read_text(encoding="utf-8"))["status"], "draft")
            refused = subprocess.run([*cli, "build", str(plan_path), "--output", str(root / "pack"), "--json"], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(refused.returncode, 1)
            self.assertIn("plan-not-ready", refused.stdout)
            plan_path.write_text(dump_json(self.plan), encoding="utf-8")
            built = subprocess.run([*cli, "build", str(plan_path), "--output", str(root / "pack"), "--json"], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(built.returncode, 0, built.stderr + built.stdout)
            checked = subprocess.run([*cli, "validate", str(root / "pack"), "--extraction", str(extraction), "--json"], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(checked.returncode, 0, checked.stderr + checked.stdout)
            self.assertEqual(json.loads(checked.stdout)["errors"], 0)

    def test_graph_evidence_and_route_failures(self) -> None:
        changes = {
            "bad-evidence-id": lambda p: p["atomic"][0]["evidence"].append("missing"),
            "bad-source-id": lambda p: p["evidence"][0].update(source_id="missing"),
            "broken-dependency": lambda p: p["combo"][0]["dependencies"].append("atomic:missing"),
            "dependency-cycle": lambda p: p["combo"][0]["dependencies"].append("combo:respond-to-signal"),
            "broken-route": lambda p: p["routes"][0].update(target="atomic:missing"),
            "orphan-unit": lambda p: p["routes"].pop(3),
            "duplicate-id": lambda p: p["atomic"][1].update(id="intake-signal"),
            "invalid-name": lambda p: p["atomic"][1].update(id="Ünicode"),
            "missing-field": lambda p: p["atomic"][0].pop("mission"),
            "unit-without-candidate": lambda p: p["candidates"].pop(0),
        }
        for expected, change in changes.items():
            with self.subTest(expected=expected):
                plan = copy.deepcopy(self.plan)
                change(plan)
                self.assertIn(expected, codes(validate_plan(plan)))

    def test_manifest_and_filesystem_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pack = Path(temporary) / "pack"
            build(self.plan, pack)
            target = pack / "atomic" / "intake-signal" / "SKILL.md"
            target.write_text(target.read_text(encoding="utf-8").replace("name:", "wrong:"), encoding="utf-8")
            self.assertIn("invalid-frontmatter", codes(validate_pack(pack)["issues"]))
            self.assertIn("manifest-file-mismatch", codes(validate_pack(pack)["issues"]))
            target.unlink()
            self.assertIn("missing-generated-file", codes(validate_pack(pack)["issues"]))
            extra = pack / "atomic" / "rogue" / "SKILL.md"
            extra.parent.mkdir()
            extra.write_text("---\nname: rogue\ndescription: \"rogue\"\n---\n", encoding="utf-8")
            self.assertIn("unlisted-skill", codes(validate_pack(pack)["issues"]))
            (pack / "pack.json").unlink()
            self.assertIn("missing-manifest", codes(validate_pack(pack)["issues"]))

    def test_generated_symlink_cannot_escape_pack(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pack = root / "pack"
            build(self.plan, pack)
            outside = root / "outside.md"
            outside.write_text("PRIVATE_SENTINEL", encoding="utf-8")
            target = pack / "atomic" / "intake-signal" / "SKILL.md"
            target.unlink()
            try:
                target.symlink_to(outside)
            except (NotImplementedError, OSError) as exc:
                self.skipTest(f"Symbolic links are unavailable: {exc}")
            self.assertIn("symlink-generated-file", codes(validate_pack(pack)["issues"]))
            with self.assertRaisesRegex(ValueError, "symlink-generated-path"):
                build(self.plan, pack, overwrite=True)
            self.assertEqual(outside.read_text(encoding="utf-8"), "PRIVATE_SENTINEL")

    def test_bad_json_types_return_structured_issues(self) -> None:
        changes = [
            lambda p: p["evidence"][0].update(source_id=[]),
            lambda p: p["routes"][0].update(target={}),
            lambda p: p["combo"][0].update(dependencies=[{}]),
            lambda p: p["candidates"][0].update(decision=[]),
            lambda p: p["behavior_tests"][0].update(type=[]),
        ]
        for change in changes:
            with self.subTest(change=changes.index(change)):
                plan = copy.deepcopy(self.plan)
                change(plan)
                self.assertTrue(any(item["severity"] == "ERROR" for item in validate_plan(plan)))

    def test_long_verbatim_overlap_warns(self) -> None:
        plan = copy.deepcopy(self.plan)
        passage = next(unit["text"] for source in self.extraction["sources"] for unit in source["units"] if "Intake a signal" in unit["heading_path"] and unit["kind"] == "paragraph")
        plan["atomic"][0]["steps"][0] = passage
        with tempfile.TemporaryDirectory() as temporary:
            pack = Path(temporary) / "pack"
            build(plan, pack)
            self.assertIn("long-verbatim-overlap", codes(validate_pack(pack, self.extraction)["issues"]))

    def test_combo_copy_of_atomic_procedure_warns(self) -> None:
        plan = copy.deepcopy(self.plan)
        copied = "This deliberately long atomic procedure step repeats its decision logic and full wording inside the combo workflow, which should only describe the handoff."
        plan["atomic"][0]["steps"][0] = copied
        plan["combo"][0]["flow"][0] = copied
        self.assertIn("combo-duplicates-atomic", codes(validate_plan(plan)))

    def test_broken_local_reference_is_an_error(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["references"][0]["content"] += " See [missing page](missing.md)."
        with tempfile.TemporaryDirectory() as temporary:
            pack = Path(temporary) / "pack"
            build(plan, pack)
            self.assertIn("broken-reference-link", codes(validate_pack(pack)["issues"]))

    def test_extraction_stdout_does_not_include_private_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "private.txt"
            source.write_text("PRIVATE_SENTINEL never print this passage", encoding="utf-8")
            result = subprocess.run([sys.executable, str(ROOT / "scripts/book_skills.py"), "extract", str(source), "--output", str(root / "work"), "--json"], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("PRIVATE_SENTINEL", result.stdout + result.stderr)

    def test_validation_report_does_not_echo_conflict_text(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["conflicts"][0]["description"] = "PRIVATE_SENTINEL from a sensitive source"
        with tempfile.TemporaryDirectory() as temporary:
            pack = Path(temporary) / "pack"
            build(plan, pack)
            result = subprocess.run([sys.executable, str(ROOT / "scripts/book_skills.py"), "validate", str(pack), "--json"], cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("PRIVATE_SENTINEL", result.stdout + result.stderr)

    def test_incremental_impact_is_local(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manual = root / "field-manual.md"
            errata = root / "field-errata.md"
            shutil.copyfile(ROOT / "examples/sources/field-manual.md", manual)
            shutil.copyfile(ROOT / "examples/sources/field-errata.md", errata)
            paths = [str(manual), str(errata)]
            first = extract_selected(paths, root / "work", Limits())
            pack = root / "pack"
            build(make_plan(first), pack)
            write_extraction(first, root / "work")
            command = [sys.executable, str(ROOT / "scripts/book_skills.py"), "update", str(pack), str(root / "work/sources.json"), "--json"]
            unchanged = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(json.loads(unchanged.stdout)["status"], "CURRENT")
            manual.write_text(manual.read_text(encoding="utf-8").replace("Assign a case ID.", "Assign a persistent case ID."), encoding="utf-8")
            fresh = extract_selected(paths, root / "work", Limits())
            write_extraction(fresh, root / "work")
            changed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
            result = json.loads(changed.stdout)
            self.assertEqual(result["status"], "STALE")
            self.assertIn("atomic:intake-signal", result["affected_units"])
            self.assertIn("combo:respond-to-signal", result["affected_units"])
            self.assertNotIn("atomic:decide-route", result["affected_units"])
            manual.write_text(manual.read_text(encoding="utf-8").replace("## Decide the route\n", "## Removed route\n"), encoding="utf-8")
            removed = extract_selected(paths, root / "work", Limits())
            write_extraction(removed, root / "work")
            changed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
            result = json.loads(changed.stdout)
            self.assertIn("atomic:decide-route", result["affected_units"])


if __name__ == "__main__":
    unittest.main()
