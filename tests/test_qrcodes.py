"""Technische QR-Integration: Datenfluss und Erhalt der Ausgabe bei Fehlern."""
from contextlib import redirect_stderr
from io import StringIO
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import build
from generate_qrcodes import verify_bytes


class QRBuildTests(unittest.TestCase):
    def test_changed_contact_is_encoded_without_manually_updated_images(self):
        # Nur generierten Inhalt vergleichen, keine Erwartung an Büroangaben (R-REDAKTION-3).
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("src", "public"):
                shutil.copytree(build.ROOT / name, root / name)
            path = root / "src/bureauangaben.json"
            office = json.loads(path.read_text(encoding="utf-8"))
            office["email"] = "qr-build-test@example.org"
            path.write_text(json.dumps(office, ensure_ascii=False), encoding="utf-8")
            files = build.render(root)
            for name, payload in files.items():
                if name.endswith(".vcf"):
                    png = files[f"qrcodes/{Path(name).stem}.png"]
                    verify_bytes(png, payload, name)
            self.assertIn(office["email"].encode(), files["bb-limen.vcf"])

    def test_failed_decode_preserves_previous_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            output.mkdir()
            sentinel = output / "previous-output"
            sentinel.write_bytes(b"unchanged")
            with patch.object(sys, "argv", ["build.py", "--output", str(output)]), \
                 patch("generate_qrcodes.verify_bytes", side_effect=ValueError("Decodierfehler")), \
                 patch.object(build, "write_output") as writer, \
                 redirect_stderr(StringIO()) as errors:
                self.assertEqual(build.main(), 1)
                writer.assert_not_called()
            self.assertIn("Decodierfehler", errors.getvalue())
            self.assertEqual(sentinel.read_bytes(), b"unchanged")

    def test_invalid_png_is_rejected(self):
        with self.assertRaises(RuntimeError):
            verify_bytes(b"invalid PNG", b"BEGIN:VCARD\r\n", "synthetic")
