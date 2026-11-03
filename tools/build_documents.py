"""Baut die aktuellen Markdown-Handouts als PDF, HTML und EML.

Aufruf: .venv-documents/bin/python tools/build_documents.py
Die Ausgabe liegt neben den Quellen; bestehende Ausgaben werden ersetzt.
"""

from io import BytesIO
from pathlib import Path
import argparse
import base64
from html import escape
import mimetypes
import re

from reportlab.lib.utils import ImageReader

import generate_emails as emails
import generate_pdfs as pdfs


IMAGE = re.compile(r"(?m)^!\[([^\]\n]*)\]\(([^)\n]+)\)[ \t]*$")


class Portrait(pdfs.Flowable):
    """Ein kleines Porträt mittig zuschneiden und kreisförmig setzen."""

    def __init__(self, path):
        super().__init__()
        self.image = ImageReader(str(path))
        self.width = self.height = 18 * pdfs.mm
        self.spaceAfter = 8
        self.hAlign = "LEFT"

    def draw(self):
        canvas = self.canv
        size = self.width
        width, height = self.image.getSize()
        scale = size / min(width, height)
        canvas.saveState()
        circle = canvas.beginPath()
        circle.circle(size / 2, size / 2, size / 2)
        canvas.clipPath(circle, stroke=0)
        canvas.drawImage(self.image, (size - width * scale) / 2,
                         (size - height * scale) / 2,
                         width=width * scale, height=height * scale, mask="auto")
        canvas.restoreState()


def source_parts(source, directory):
    """Lokale Markdown-Bildblöcke unabhängig vom Textsatz auflösen."""
    start = 0
    for match in IMAGE.finditer(source):
        yield source[start:match.start()], None
        path = (directory / match[2]).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Porträt nicht gefunden: {path}")
        yield match[1], path
        start = match.end()
    yield source[start:], None


def illustrated_pdf_story(source, directory):
    story = []
    for text, image in source_parts(source, directory):
        story.extend([Portrait(image)] if image else pdf_story(text))
    return story


def illustrated_html(source, directory, title, embedded=False):
    content, images = [], []
    for text, image in source_parts(source, directory):
        if image is None:
            content.append(emails.markdown(text))
            continue
        mime = mimetypes.guess_type(image.name)[0]
        if mime not in ("image/png", "image/jpeg", "image/webp"):
            raise ValueError(f"Nicht unterstütztes Porträtformat: {image}")
        data = image.read_bytes()
        cid = f"portrait-{len(images)}@bb-limen.de"
        url = f"cid:{cid}" if embedded else f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"
        content.append(
            f'<p style="margin:0 0 16px;"><img src="{url}" '
            f'alt="{escape(text, quote=True)}" width="72" height="72" '
            'style="display:block;width:72px;height:72px;object-fit:cover;border-radius:50%;"></p>')
        images.append((cid, mime, data))
    html = emails.document_html(
        '<tr><td style="padding:28px;">' + "\n".join(content) + '</td></tr>', title)
    return html, images


def flow(source):
    story = []
    parts = re.split(r"(?m)^(#{1,2}) (.+)\n", source)
    story += pdfs.blocks(parts[0], size=9, font="Label")
    for level, title, body in zip(parts[1::3], parts[2::3], parts[3::3]):
        story.append(pdfs.para(title, font="Text" if level == "#" else "Label-Bold",
                               color="ink", size=18 if level == "#" else 13,
                               leading=23 if level == "#" else 17, spaceAfter=8))
        story += pdfs.blocks(body, size=9, font="Label")
    return story


def pdf_story(source):
    # Nur Markdown-Trenner entfernen; redaktionellen Text vollständig setzen.
    source = re.sub(r"(?m)^---\s*$", "", source)
    parts = re.split(r"(?m)^### (.+)\n", source)
    story = flow(parts[0])
    for title, body in zip(parts[1::2], parts[2::2]):
        story.append(pdfs.heading(title))
        if re.search(r"(?m)^#### ", body):
            # Einleitung vor den Personenkarten ebenfalls erhalten.
            intro = re.split(r"(?m)^#### ", body, maxsplit=1)[0]
            story += pdfs.blocks(intro, size=9, font="Label")
            story.append(pdfs.profiles(body))
        else:
            story += pdfs.blocks(body, size=9, font="Label")
    return story


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="*", type=Path,
                        help="Markdown-Quellen; Standard: alle .md-Dateien direkt in dokumente/.")
    args = parser.parse_args()
    sources = args.sources or sorted(pdfs.OUT_DIR.glob("*.md"))
    pdfs.register_fonts()
    for path in sources:
        source = path.read_text(encoding="utf-8")
        # Leere Markdown-Überschriften enthalten keinen redaktionellen Text.
        source = re.sub(r"(?m)^#{1,6}[ \t]*$", "", source)
        names = re.findall(r"(?m)^\*\*Name:\*\*[ \t]*([^\n]+)$", source)
        title = (f"BB Limen · {names[0].strip()} · Vorstellung" if len(names) == 1 else
                 "BB Limen · " + path.stem.removeprefix("bb-limen-").capitalize())
        buffer = BytesIO()
        document = pdfs.SimpleDocTemplate(
            buffer, pagesize=pdfs.A4, rightMargin=pdfs.MARGIN,
            leftMargin=pdfs.MARGIN, topMargin=12 * pdfs.mm,
            bottomMargin=14 * pdfs.mm, title=title, pageCompression=1)
        # Der vorhandene Footer verhindert versehentlich mehrseitige Einseiter.
        document.build(illustrated_pdf_story(source, path.parent),
                       onFirstPage=pdfs.footer, onLaterPages=pdfs.footer)
        html, _ = illustrated_html(source, path.parent, title)
        email_html, images = illustrated_html(source, path.parent, title, embedded=True)
        plain = emails.PlainText()
        plain.feed(html)
        message = emails.EmailMessage(policy=emails.SMTP)
        message["Subject"] = title
        message["X-Unsent"] = "1"
        message.set_content(plain.text())
        message.add_alternative(email_html, subtype="html")
        for cid, mime, data in images:
            message.get_payload()[-1].add_related(
                data, maintype="image", subtype=mime.split("/", 1)[1],
                cid=f"<{cid}>", disposition="inline")
        path.with_suffix(".pdf").write_bytes(buffer.getvalue())
        path.with_suffix(".html").write_text(html, encoding="utf-8")
        path.with_suffix(".eml").write_bytes(message.as_bytes())
        print(f"Erzeugt: {path.with_suffix('.pdf')} / .html / .eml")


if __name__ == "__main__":
    main()
