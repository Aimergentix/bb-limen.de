"""Technischer Datenfluss lokaler Signaturen, ohne redaktionelle Erwartungen."""
from html.parser import HTMLParser
import base64
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import build
import generate_signatures as signatures
from generate_qrcodes import verify_bytes


class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))
        if tag not in {"meta", "img", "br"}:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            raise ValueError(f"Ungültige HTML-Verschachtelung: {tag}")


class SignatureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("src", "public"):
            shutil.copytree(build.ROOT / name, self.root / name)

    def test_changed_contact_reaches_html_vcard_and_qr(self):
        path = self.root / "src/betreuende.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        person = data["personen"][0]
        person["email"] = 'signature-flow@example.org'
        person["vorname"] = 'Test & <Vorname>'
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        files = signatures.render(self.root)
        slug = person["kennung"]
        page = files[f"dokumente/signaturen/{slug}.html"].decode()
        parser = Elements()
        parser.feed(page)
        self.assertFalse(parser.stack)
        self.assertTrue(any(tag == "a" and attrs.get("href") == "mailto:" + person["email"]
                            for tag, attrs in parser.elements))
        image = next(attrs for tag, attrs in parser.elements if tag == "img")
        self.assertTrue(image["src"].startswith('data:image/png;base64,'))
        png = base64.b64decode(image["src"].split(',', 1)[1], validate=True)
        card = files[f"dokumente/signaturen/{slug}.vcf"]
        verify_bytes(png, card, slug)
        self.assertIn(person["email"].encode(), card)
        self.assertNotIn('<Vorname>', page)
        self.assertFalse((self.root / 'dokumente').exists())

    def test_installed_html_is_independent_and_updated_by_build(self):
        with tempfile.TemporaryDirectory() as destination:
            target = Path(destination)
            (self.root / '.signature-output.json').write_text(
                json.dumps({'directory': str(target)}), encoding='utf-8')
            files = signatures.render(self.root)
            signatures.write_output(files, self.root)
            for name, content in files.items():
                if name.endswith('.html'):
                    installed = target / Path(name).name
                    self.assertEqual(installed.read_bytes(), content)
                    self.assertNotIn(b'file://', content)
                    self.assertNotIn(str(self.root).encode(), content)
                    installed.write_bytes(b'previous export')
            signatures.write_output(files, self.root)
            for name, content in files.items():
                if name.endswith('.html'):
                    self.assertEqual((target / Path(name).name).read_bytes(), content)

    def test_office_fallback_is_used(self):
        path = self.root / 'src/betreuende.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        for person in data['personen']:
            person['email'] = None
            person['telefon'] = None
            person['anschrift'] = None
        path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        office = build.load_office(self.root)
        files = signatures.render(self.root)
        for name, content in files.items():
            if name.endswith('.html'):
                page = content.decode()
                self.assertIn('mailto:' + office['email'], page)
                self.assertIn('tel:' + office['telefon']['e164'], page)

    def test_check_build_does_not_write_local_signatures(self):
        output = self.root / 'site'
        website = build.render(self.root)
        with patch.object(build, 'ROOT', self.root), \
             patch.object(build, 'render', return_value=website), \
             patch.object(sys, 'argv', ['build.py', '--output', str(output)]), \
             patch.object(signatures, 'write_output') as writer:
            self.assertEqual(build.main(), 0)
            writer.assert_not_called()
        self.assertFalse((self.root / 'signature.html').exists())
        self.assertFalse((self.root / 'dokumente').exists())

    def test_default_build_refreshes_signatures(self):
        website = build.render(self.root)
        with patch.object(build, 'ROOT', self.root), \
             patch.object(build, 'render', return_value=website), \
             patch.object(sys, 'argv', ['build.py']):
            self.assertEqual(build.main(), 0)
        for person in build.load_people(self.root):
            path = self.root / 'dokumente/signaturen' / (person['kennung'] + '.html')
            self.assertTrue(path.is_file())
