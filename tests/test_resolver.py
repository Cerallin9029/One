from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from instruction_lens.resolver import inspect


class ResolverTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.root = self.base / "repo"
        self.cwd = self.root / "app" / "src"
        self.cwd.mkdir(parents=True)
        (self.root / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")

    def write(self, directory, name, text):
        path = directory / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_root_to_cwd_order_excludes_siblings_and_ancestors(self):
        self.write(self.base, "AGENTS.md", "above root")
        self.write(self.root, "AGENTS.md", "root instructions")
        self.write(self.cwd.parent, "AGENTS.md", "app instructions")
        self.write(self.cwd, "AGENTS.md", "src instructions")
        sibling = self.root / "unrelated"
        sibling.mkdir()
        self.write(sibling, "AGENTS.md", "sibling instructions")
        report = inspect(self.cwd)
        self.assertEqual(report.root, str(self.root))
        self.assertEqual(
            report.combined_text, "root instructions\n\napp instructions\n\nsrc instructions"
        )

    def test_nearest_nested_repository_is_boundary(self):
        self.write(self.root, "AGENTS.md", "outer")
        (self.cwd.parent / ".git").mkdir()
        self.write(self.cwd.parent, "AGENTS.md", "inner")
        self.assertEqual(inspect(self.cwd).combined_text, "inner")

    def test_override_and_ordered_fallback(self):
        self.write(self.root, "AGENTS.md", "standard")
        override = self.write(self.root, "AGENTS.override.md", "override")
        self.write(self.cwd, "FIRST.md", "first fallback")
        self.write(self.cwd, "SECOND.md", "second fallback")
        report = inspect(self.cwd, fallback_filenames=("FIRST.md", "SECOND.md"))
        self.assertEqual(report.sources[0].path, str(override))
        self.assertEqual(report.combined_text, "override\n\nfirst fallback")
        self.assertEqual(len(report.sources[1].shadowed), 1)

    def test_empty_override_shadows_standard_without_spending_budget(self):
        self.write(self.root, "AGENTS.override.md", "  \n ")
        self.write(self.root, "AGENTS.md", "should stay hidden")
        self.write(self.cwd, "AGENTS.md", "abc")
        report = inspect(self.cwd, max_bytes=4)
        self.assertEqual(report.combined_text, "abc")
        self.assertEqual(report.consumed_bytes, 3)
        self.assertEqual(report.sources[0].status, "empty")
        self.assertTrue(report.has_warnings)

    def test_no_marker_means_cwd_only(self):
        (self.root / ".git").unlink()
        self.write(self.root, "AGENTS.md", "parent")
        self.write(self.cwd, "AGENTS.md", "local")
        report = inspect(self.cwd)
        self.assertEqual(report.root, str(self.cwd))
        self.assertEqual(report.combined_text, "local")

    def test_empty_markers_disable_parent_search(self):
        self.write(self.root, "AGENTS.md", "parent")
        self.assertEqual(inspect(self.cwd, root_markers=()).sources, [])

    def test_custom_marker_and_explicit_root(self):
        self.write(self.cwd.parent, "workspace.toml", "")
        self.write(self.root, "AGENTS.md", "outer")
        self.write(self.cwd.parent, "AGENTS.md", "inner")
        self.assertEqual(inspect(self.cwd, root_markers=("workspace.toml",)).combined_text, "inner")
        self.assertEqual(inspect(self.cwd, root=self.root).combined_text, "outer\n\ninner")

    def test_byte_budget_and_later_file_skipped(self):
        self.write(self.root, "AGENTS.md", "abcde")
        self.write(self.cwd.parent, "AGENTS.md", "XYZ")
        self.write(self.cwd, "AGENTS.md", "ignored")
        report = inspect(self.cwd, max_bytes=7)
        self.assertEqual(report.combined_text, "abcde\n\nXY")
        self.assertEqual(report.consumed_bytes, 7)
        self.assertEqual(
            [s.status for s in report.sources], ["loaded", "truncated", "skipped-budget"]
        )

    def test_utf8_truncation_is_bytes_and_lossy_decoded(self):
        self.write(self.root, "AGENTS.md", "你好")
        report = inspect(self.cwd, max_bytes=4)
        self.assertEqual(report.combined_text, "你\ufffd")
        self.assertEqual(report.consumed_bytes, 4)

    def test_invalid_utf8_is_replaced(self):
        (self.cwd / "AGENTS.md").write_bytes(b"hello\xff")
        self.assertEqual(inspect(self.cwd).combined_text, "hello\ufffd")

    def test_exact_and_zero_budget(self):
        self.write(self.cwd, "AGENTS.md", "1234")
        self.assertEqual(inspect(self.cwd, max_bytes=4).sources[0].status, "loaded")
        zero = inspect(self.cwd, max_bytes=0)
        self.assertEqual(zero.consumed_bytes, 0)
        self.assertEqual(zero.sources[0].status, "skipped-budget")
        self.assertEqual(zero.combined_text, "")

    def test_control_separators_are_content_in_rust_whitespace_rules(self):
        for character in ("\x1c", "\x1d", "\x1e", "\x1f"):
            with self.subTest(character=repr(character)):
                self.write(self.root, "AGENTS.md", character)
                self.write(self.cwd, "AGENTS.md", "XYZ")
                report = inspect(self.cwd, max_bytes=2)
                self.assertEqual(report.combined_text, f"{character}\n\nX")
                self.assertEqual(report.sources[0].status, "loaded")
                self.assertEqual(report.consumed_bytes, 2)

    def test_unicode_whitespace_still_does_not_spend_budget(self):
        self.write(self.root, "AGENTS.md", "\u3000\u00a0")
        self.write(self.cwd, "AGENTS.md", "XYZ")
        report = inspect(self.cwd, max_bytes=5)
        self.assertEqual(report.combined_text, "XYZ")
        self.assertEqual(report.sources[0].status, "empty")
        self.assertEqual(report.consumed_bytes, 3)

    def test_large_file_is_read_across_bounded_chunks(self):
        content = "x" * 70000
        self.write(self.cwd, "AGENTS.md", content)
        report = inspect(self.cwd, max_bytes=65537)
        self.assertEqual(len(report.combined_text), 65537)
        self.assertEqual(report.sources[0].status, "truncated")

    def test_untrusted_mode_never_reads_project_documents(self):
        self.write(self.cwd, "AGENTS.md", "project text")
        with patch.object(Path, "open", side_effect=AssertionError("unexpected read")):
            report = inspect(self.cwd, trusted=False)
        self.assertEqual(report.sources, [])
        self.assertEqual(report.searched_directories, [])

    def test_json_hides_instruction_body_unless_requested(self):
        self.write(self.cwd, "AGENTS.md", "PRIVATE_MARKER_FOR_TEST")
        report = inspect(self.cwd)
        self.assertNotIn("PRIVATE_MARKER_FOR_TEST", json.dumps(report.to_dict()))
        self.assertIn("PRIVATE_MARKER_FOR_TEST", json.dumps(report.to_dict(show_text=True)))

    def test_directory_named_agents_is_not_selected(self):
        (self.cwd / "AGENTS.override.md").mkdir()
        self.write(self.cwd, "AGENTS.md", "normal")
        self.assertEqual(inspect(self.cwd).combined_text, "normal")

    def test_invalid_input_rejected(self):
        for name in ("../outside.md", "", ".", "..", "bad\0name"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                inspect(self.cwd, fallback_filenames=(name,))
        with self.assertRaises(ValueError):
            inspect(self.cwd, max_bytes=-1)
        (self.base / "unrelated").mkdir()
        with self.assertRaises(ValueError):
            inspect(self.cwd, root=self.base / "unrelated")
        with self.assertRaises(ValueError):
            inspect(self.root / ".git")

    def test_symlink_outside_root_is_reported(self):
        outside = self.write(self.base, "outside.md", "external")
        try:
            (self.cwd / "AGENTS.md").symlink_to(outside)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        report = inspect(self.cwd)
        self.assertEqual(report.combined_text, "external")
        self.assertTrue(report.sources[0].outside_root)

    def test_read_errors_do_not_fall_back_silently(self):
        self.write(self.cwd, "AGENTS.override.md", "blocked")
        self.write(self.cwd, "AGENTS.md", "fallback")
        with patch.object(Path, "open", side_effect=PermissionError("denied")):
            with self.assertRaises(PermissionError):
                inspect(self.cwd)

    def test_shadowed_metadata_error_is_a_warning_after_valid_selection(self):
        self.write(self.cwd, "AGENTS.override.md", "override")
        standard = self.write(self.cwd, "AGENTS.md", "standard")
        original = Path.stat

        def probe(path, *args, **kwargs):
            if path == standard:
                raise PermissionError(13, "permission denied", str(path))
            return original(path, *args, **kwargs)

        with patch.object(Path, "stat", probe):
            report = inspect(self.cwd)
        self.assertEqual(report.combined_text, "override")
        self.assertEqual(len(report.sources[0].probe_errors), 1)
        self.assertTrue(report.has_warnings)

    def test_preferred_metadata_error_does_not_choose_standard(self):
        override = self.write(self.cwd, "AGENTS.override.md", "override")
        self.write(self.cwd, "AGENTS.md", "standard")
        original = Path.stat

        def probe(path, *args, **kwargs):
            if path == override:
                raise PermissionError(13, "permission denied", str(path))
            return original(path, *args, **kwargs)

        with patch.object(Path, "stat", probe):
            with self.assertRaises(PermissionError):
                inspect(self.cwd)

    def test_shadowed_symlink_loop_does_not_prevent_loading_override(self):
        self.write(self.cwd, "AGENTS.override.md", "override")
        loop = self.cwd / "AGENTS.md"
        try:
            loop.symlink_to(loop)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        report = inspect(self.cwd)
        self.assertEqual(report.combined_text, "override")
        self.assertEqual(len(report.sources[0].probe_errors), 1)
        self.assertTrue(report.has_warnings)

    def cli(self, *args):
        # Use the installed module so packaging and CLI behavior are tested together.
        return subprocess.run(
            [sys.executable, "-m", "instruction_lens", str(self.cwd), *args],
            capture_output=True,
            text=True,
            check=False,
            cwd=self.base,
        )

    def test_cli_warning_exit_and_default_body_privacy(self):
        self.write(self.cwd, "AGENTS.md", "PRIVATE_MARKER_FOR_TEST")
        result = self.cli("--max-bytes", "3", "--fail-on-warning", "--json")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertNotIn("PRIVATE_MARKER_FOR_TEST", result.stdout)
        self.assertEqual(json.loads(result.stdout)["sources"][0]["status"], "truncated")

    def test_cli_errors_are_structured_and_have_exit_2(self):
        result = self.cli("--max-bytes", "-1", "--json")
        self.assertEqual(result.returncode, 2)
        self.assertIn("error", json.loads(result.stdout))

    def test_cli_oversized_budget_loads_small_file_without_overflow(self):
        self.write(self.cwd, "AGENTS.md", "small file")
        result = self.cli("--max-bytes", "9223372036854775808", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["consumed_bytes"], 10)
        self.assertEqual(report["sources"][0]["status"], "loaded")

    def test_cli_text_view_escapes_terminal_controls(self):
        self.write(self.cwd, "AGENTS.md", "hello\x1b[31m")
        result = self.cli("--show-text")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("\x1b", result.stdout)
        self.assertIn("\\u001b", result.stdout)


if __name__ == "__main__":
    unittest.main()
