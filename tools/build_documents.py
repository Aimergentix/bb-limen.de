"""Baut die aktuellen Markdown-Handouts als PDF, HTML und EML.

Aufruf: .venv-documents/bin/python tools/build_documents.py
Quellen: dokumente/vorlagen/; Ausgabe: dokumente/handouts/.
"""

from io import BytesIO
from pathlib import Path
import argparse
import base64
from html import escape
import mimetypes
import re

from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Spacer

import generate_emails as emails
import generate_pdfs as pdfs
from document_paths import OUTPUT, SOURCES


IMAGE = re.compile(r"(?m)^!\[([^\]\n]*)\]\(([^)\n]+)\)[ \t]*$")
# Alt-Texte mit diesem Präfix sind QR-Codes (quadratisch), keine runden Porträts.
QR_ALT = "QR-Code"
QR_MM = 20   # Kantenlänge des QR-Code im PDF
QR_PX = 112  # Kantenlänge des QR-Code in HTML und E-Mail


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
        yield source[start:match.start()], None, False
        path = (directory / match[2]).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Bild nicht gefunden: {path}")
        yield match[1], path, match[1].startswith(QR_ALT)
        start = match.end()
    yield source[start:], None, False


def illustrated_pdf_story(source, directory):
    story = []
    row = []  # Aufeinanderfolgende Bilder (Porträt, QR-Code) landen nebeneinander.

    def flush_row():
        if row:
            story.append(pdfs.columns(row) if len(row) > 1 else row[0])
            story.append(Spacer(1, 4 * mm))
            row.clear()

    parts = list(source_parts(source, directory))
    index = 0
    while index < len(parts):
        text, image, is_qr = parts[index]
        if image is None:
            # Folgt dem Text direkt ein QR-Code, steht der Code daneben statt darunter.
            if index + 1 < len(parts) and parts[index + 1][1] is not None and parts[index + 1][2]:
                qr_path = parts[index + 1][1]
                width = QR_MM * mm
                story.append(pdfs.columns(
                    [pdf_story(text), pdfs.Image(str(qr_path), width=width, height=width)],
                    [pdfs.WIDTH - width - pdfs.GAP, width]))
                story.append(Spacer(1, 4 * mm))
                index += 2
                continue
            flush_row()
            story.extend(pdf_story(text))
        elif is_qr:
            row.append(pdfs.Image(str(image), width=QR_MM * mm, height=QR_MM * mm))
        else:
            row.append(Portrait(image))
        index += 1
    flush_row()
    return story


def illustrated_html(source, directory, title, embedded=False):
    content, images = [], []
    for text, image, is_qr in source_parts(source, directory):
        if image is None:
            content.append(emails.markdown(text))
            continue
        mime = mimetypes.guess_type(image.name)[0]
        if mime not in ("image/png", "image/jpeg", "image/webp"):
            raise ValueError(f"Nicht unterstütztes Bildformat: {image}")
        data = image.read_bytes()
        cid = f"{'qr' if is_qr else 'portrait'}-{len(images)}@bb-limen.de"
        url = f"cid:{cid}" if embedded else f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"
        if is_qr:
            content.append(
                f'<p style="margin:0 0 16px;"><img src="{url}" '
                f'alt="{escape(text, quote=True)}" width="{QR_PX}" height="{QR_PX}" '
                f'style="display:block;width:{QR_PX}px;height:{QR_PX}px;"></p>')
        else:
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
                        help="Markdown-Quellen; Standard: kleingeschriebene .md-Dateien direkt in dokumente/vorlagen/.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT,
                        help="Ausgabeordner für PDF, HTML und EML (Standard: dokumente/handouts/).")
    args = parser.parse_args()
    sources = args.sources or sorted(path for path in SOURCES.glob("*.md")
                                    if path.name == path.name.lower())
    if not sources:
        parser.error(f"Keine Markdown-Vorlagen gefunden: {SOURCES}")
    stems = [path.stem for path in sources]
    if len(stems) != len(set(stems)):
        parser.error("Vorlagen mit gleichem Dateinamen würden dieselbe Ausgabe überschreiben")
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
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
        output = output_dir / path.stem
        output.with_suffix(".pdf").write_bytes(buffer.getvalue())
        output.with_suffix(".html").write_text(html, encoding="utf-8")
        output.with_suffix(".eml").write_bytes(message.as_bytes())
        print(f"Erzeugt: {output.with_suffix('.pdf')} / .html / .eml")


if __name__ == "__main__":
    main()
