from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from site_support import REPO


class BuildTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="bb-limen-build-test-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        for name in ("src", "public", "tools"):
            shutil.copytree(REPO / name, self.work / name, ignore=shutil.ignore_patterns("__pycache__"))
        self.assertEqual(self.run_build().returncode, 0)

    def run_build(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["sh", str(self.work / "tools/build.sh"), *args],
                              cwd="/tmp", text=True, capture_output=True, check=False)

    def snapshot(self, directory: str) -> dict[str, bytes]:
        base = self.work / directory
        return {str(path.relative_to(base)): path.read_bytes()
                for path in base.rglob("*") if path.is_file()}

    def change_page(self, old: str, new: str) -> None:
        path = self.work / "src/pages/index.html"
        path.write_text(path.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")

    def change_catalog(self, change) -> None:
        path = self.work / "src/seiten.json"
        catalog = json.loads(path.read_text())
        change(catalog)
        path.write_text(json.dumps(catalog))

    def assert_build_fails_without_writes(self) -> None:
        before = {name: self.snapshot(name) for name in ("src", "public", "dist")}
        result = self.run_build()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("FEHLER:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        for name in before:
            self.assertEqual(before[name], self.snapshot(name))

    def test_build_is_repeatable_and_preserves_sources(self) -> None:
        before = {name: self.snapshot(name) for name in ("src", "public", "dist")}
        self.assertEqual(self.run_build().returncode, 0)
        for name in before:
            self.assertEqual(before[name], self.snapshot(name))
        self.assertEqual(self.run_build("--check").returncode, 0)

    def test_missing_partial_preserves_last_good_output(self) -> None:
        (self.work / "src/partials/rail.html").unlink()
        self.assert_build_fails_without_writes()

    def test_missing_include_preserves_last_good_output(self) -> None:
        self.change_page("<!-- @include rail -->", "")
        self.assert_build_fails_without_writes()

    def test_duplicate_include_is_rejected(self) -> None:
        self.change_page("<!-- @include rail -->", "<!-- @include rail -->\n<!-- @include rail -->")
        self.assert_build_fails_without_writes()

    def test_same_line_include_is_rejected(self) -> None:
        self.change_page("<!-- @include rail -->", "Text <!-- @include rail -->")
        self.assert_build_fails_without_writes()

    def test_wrong_order_is_rejected(self) -> None:
        self.change_page("<!-- @include skip -->", "<!-- @include rail -->")
        self.assert_build_fails_without_writes()

    def test_nested_include_is_rejected(self) -> None:
        (self.work / "src/partials/rail.html").write_text("<!-- @include foot -->\n")
        self.assert_build_fails_without_writes()

    def test_old_generated_blocks_are_rejected(self) -> None:
        self.change_page("<!-- @include rail -->", "<!-- #rail -->\nalt\n<!-- /#rail -->")
        self.assert_build_fails_without_writes()

    def test_unknown_navigation_target_is_rejected(self) -> None:
        self.change_page("<!-- @include rail -->", "<!-- @include rail -->\n%%CUR-unbekannt%%")
        self.assert_build_fails_without_writes()

    def test_unregistered_page_is_rejected(self) -> None:
        shutil.copy2(self.work / "src/pages/index.html", self.work / "src/pages/neu.html")
        self.assert_build_fails_without_writes()

    def test_missing_page_is_rejected(self) -> None:
        (self.work / "src/pages/vorsorge.html").unlink()
        self.assert_build_fails_without_writes()

    def test_empty_catalog_is_rejected(self) -> None:
        self.change_catalog(lambda data: data.update(pages=[]))
        self.assert_build_fails_without_writes()

    def test_duplicate_catalog_page_is_rejected(self) -> None:
        self.change_catalog(lambda data: data["pages"].append(data["pages"][0]))
        self.assert_build_fails_without_writes()

    def test_invalid_catalog_values_are_rejected(self) -> None:
        original = (self.work / "src/seiten.json").read_bytes()
        for field, value in (("file", "../index.html"), ("language", "unbekannt"),
                             ("language", []), ("sitemap", "ja"), ("lastmod", "2026-02-30")):
            with self.subTest(field=field):
                (self.work / "src/seiten.json").write_bytes(original)
                self.change_catalog(lambda data: data["pages"][0].update({field: value}))
                self.assert_build_fails_without_writes()

    def test_unlisted_public_file_is_rejected(self) -> None:
        (self.work / "public/notiz.txt").write_text("privat")
        self.assert_build_fails_without_writes()

    def test_public_symlink_is_rejected(self) -> None:
        file = self.work / "public/robots.txt"
        file.unlink()
        file.symlink_to(self.work / "src/seiten.json")
        self.assert_build_fails_without_writes()

    def test_empty_public_file_is_rejected(self) -> None:
        (self.work / "public/favicon.ico").write_bytes(b"")
        self.assert_build_fails_without_writes()

    def test_check_detects_drift_without_repairing(self) -> None:
        (self.work / "dist/index.html").write_text("manuell")
        before = self.snapshot("dist")
        self.assertNotEqual(self.run_build("--check").returncode, 0)
        self.assertEqual(before, self.snapshot("dist"))

    def test_stale_output_is_removed_on_next_build(self) -> None:
        (self.work / "dist/alt.html").write_text("alt")
        self.assertNotEqual(self.run_build("--check").returncode, 0)
        self.assertEqual(self.run_build().returncode, 0)
        self.assertFalse((self.work / "dist/alt.html").exists())

    def test_existing_foreign_output_directory_is_preserved(self) -> None:
        before = self.snapshot("src")
        self.assertNotEqual(self.run_build("--output", str(self.work / "src")).returncode, 0)
        self.assertEqual(before, self.snapshot("src"))

    def test_new_output_inside_source_tree_is_rejected(self) -> None:
        output = self.work / "src/ausgabe"
        self.assertNotEqual(self.run_build("--output", str(output)).returncode, 0)
        self.assertFalse(output.exists())

    def test_output_symlink_is_rejected(self) -> None:
        shutil.rmtree(self.work / "dist")
        (self.work / "dist").symlink_to(self.work / "public", target_is_directory=True)
        before = self.snapshot("public")
        self.assertNotEqual(self.run_build().returncode, 0)
        self.assertEqual(before, self.snapshot("public"))


if __name__ == "__main__":
    unittest.main()
