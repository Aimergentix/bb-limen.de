"""Baut die aktuellen Markdown-Handouts als PDF, HTML und EML.

Aufruf: .venv-documents/bin/python tools/build_documents.py
Die Ausgabe liegt neben den Quellen; bestehende Ausgaben werden ersetzt.
"""

from io import BytesIO
from pathlib import Path
import argparse
import re

import generate_emails as emails
import generate_pdfs as pdfs


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
                        help="Markdown-Quellen; Standard: die zwei aktuellen Handouts.")
    args = parser.parse_args()
    sources = args.sources or [pdfs.OUT_DIR / f"bb-limen-{name}.md"
                               for name in ("stammdaten", "vorstellung")]
    pdfs.register_fonts()
    for path in sources:
        source = path.read_text(encoding="utf-8")
        title = "BB Limen · " + path.stem.removeprefix("bb-limen-").capitalize()
        buffer = BytesIO()
        document = pdfs.SimpleDocTemplate(
            buffer, pagesize=pdfs.A4, rightMargin=pdfs.MARGIN,
            leftMargin=pdfs.MARGIN, topMargin=12 * pdfs.mm,
            bottomMargin=14 * pdfs.mm, title=title, pageCompression=1)
        # Der vorhandene Footer verhindert versehentlich mehrseitige Einseiter.
        document.build(pdf_story(source), onFirstPage=pdfs.footer, onLaterPages=pdfs.footer)
        html = emails.document_html(
            '<tr><td style="padding:28px;">' + emails.markdown(source) + '</td></tr>', title)
        plain = emails.PlainText()
        plain.feed(html)
        message = emails.EmailMessage(policy=emails.SMTP)
        message["Subject"] = title
        message["X-Unsent"] = "1"
        message.set_content(plain.text())
        message.add_alternative(html, subtype="html")
        path.with_suffix(".pdf").write_bytes(buffer.getvalue())
        path.with_suffix(".html").write_text(html, encoding="utf-8")
        path.with_suffix(".eml").write_bytes(message.as_bytes())
        print(f"Erzeugt: {path.with_suffix('.pdf')} / .html / .eml")


if __name__ == "__main__":
    main()
