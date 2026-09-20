from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = (
    "index.html",
    "buero.html",
    "leistungen.html",
    "vorsorge.html",
    "fachkreise.html",
    "leichte-sprache.html",
    "impressum.html",
    "datenschutz.html",
    "404.html",
)


class BuildTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="bb-limen-build-test-")
        self.work = Path(self.temp.name)
        (self.work / "tools").mkdir()
        shutil.copy2(ROOT / "tools" / "build.sh", self.work / "tools" / "build.sh")
        (self.work / "tools" / "build.sh").chmod(0o755)
        shutil.copytree(ROOT / "partials", self.work / "partials")
        for page in PAGES:
            shutil.copy2(ROOT / page, self.work / page)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_build(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["tools/build.sh"],
            cwd=self.work,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def snapshot(self) -> dict[str, bytes]:
        return {page: (self.work / page).read_bytes() for page in PAGES}

    def assert_failed_without_page_changes(self, before: dict[str, bytes]) -> None:
        result = self.run_build()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertEqual(before, self.snapshot())

    def test_valid_build_is_idempotent(self) -> None:
        before = self.snapshot()
        result = self.run_build()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, self.snapshot())

    def test_missing_partial_changes_no_page(self) -> None:
        before = self.snapshot()
        (self.work / "partials" / "rail.html").unlink()
        self.assert_failed_without_page_changes(before)

    def test_missing_end_marker_changes_no_page(self) -> None:
        before = self.snapshot()
        page = self.work / "datenschutz.html"
        page.write_text(page.read_text(encoding="utf-8").replace("<!-- /#rail -->", "", 1), encoding="utf-8")
        before["datenschutz.html"] = page.read_bytes()
        self.assert_failed_without_page_changes(before)

    def test_missing_start_marker_changes_no_page(self) -> None:
        before = self.snapshot()
        page = self.work / "index.html"
        page.write_text(page.read_text(encoding="utf-8").replace("<!-- #skip -->", "", 1), encoding="utf-8")
        before["index.html"] = page.read_bytes()
        self.assert_failed_without_page_changes(before)

    def test_same_line_markers_are_rejected_without_page_changes(self) -> None:
        before = self.snapshot()
        page = self.work / "index.html"
        page.write_text(
            page.read_text(encoding="utf-8").replace(
                "<!-- #skip -->", "<!-- #skip --><!-- /#skip -->", 1
            ),
            encoding="utf-8",
        )
        before["index.html"] = page.read_bytes()
        self.assert_failed_without_page_changes(before)

    def test_nested_markers_are_rejected_without_page_changes(self) -> None:
        before = self.snapshot()
        page = self.work / "index.html"
        page.write_text(
            page.read_text(encoding="utf-8").replace(
                "<!-- #rail -->", "<!-- #rail -->\n<!-- #rail -->", 1
            ),
            encoding="utf-8",
        )
        before["index.html"] = page.read_bytes()
        self.assert_failed_without_page_changes(before)


if __name__ == "__main__":
    unittest.main()
