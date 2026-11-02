"""Setzt die beiden Markdown-Handouts als einseitige A4-PDFs.

Aufruf: python3 tools/generate_pdfs.py
Benötigt ReportLab sowie die lokal installierten Schriften Noto Serif/Sans.
Die Markdown-Dateien bleiben die Textquelle; die Website wird nicht verändert.
"""
from __future__ import annotations

from html import escape, unescape
from io import BytesIO
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable, Image, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "dokumente"
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 13 * mm
WIDTH = PAGE_WIDTH - 2 * MARGIN
GAP = 5 * mm


def palette():
    """Die bestehenden Markenfarben aus dem hellen PALETTE-Block beziehen."""
    css = (ROOT / "src/style.css").read_text(encoding="utf-8")
    block = css.split(":root {", 1)[1].split("}", 1)[0]
    return {
        name: colors.HexColor(value)
        for name, value in re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", block)
    }


PALETTE = palette()


def register_fonts():
    font_dir = Path("/usr/share/fonts/truetype/noto")
    for family, source in (("Text", "NotoSerif"), ("Label", "NotoSans")):
        for suffix, file_suffix in (("", "Regular"), ("-Bold", "Bold"),
                                    ("-Italic", "Italic"), ("-BoldItalic", "BoldItalic")):
            pdfmetrics.registerFont(TTFont(family + suffix, str(font_dir / f"{source}-{file_suffix}.ttf")))
        pdfmetrics.registerFontFamily(
            family, normal=family, bold=family + "-Bold",
            italic=family + "-Italic", boldItalic=family + "-BoldItalic",
        )


def inline(text):
    text = escape(unescape(text.strip()))
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    return text


def style(size=8.1, leading=None, font="Text", color="body", **kwargs):
    kwargs.setdefault("spaceAfter", 3.2)
    return ParagraphStyle(
        "handout", fontName=font, fontSize=size, leading=leading or size * 1.36,
        textColor=PALETTE[color], alignment=TA_LEFT,
        allowWidows=0, allowOrphans=0, **kwargs,
    )


def para(text, **kwargs):
    return Paragraph(inline(text), style(**kwargs))


def sections(path):
    """Nur die redaktionellen Kapitel, ohne Bearbeitungshinweis und Trenner."""
    source = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"^### (.+)$", source, re.M))
    return {
        match[1]: re.sub(r"(?m)^---\s*$", "", source[match.end():matches[i+1].start() if i+1 < len(matches) else len(source)]).strip()
        for i, match in enumerate(matches)
    }


def blocks(text, size=8.1, font="Text"):
    result = []
    buffer = []

    def flush():
        if buffer:
            result.append(para(" ".join(buffer), size=size, font=font))
            buffer.clear()

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line == "&nbsp;":
            flush()
        elif line.startswith("#### "):
            flush()
            result.append(para(line[5:], size=size + 1.2, font="Label-Bold", color="ink"))
        elif line.startswith(("* ", "- ")):
            flush()
            nested = len(raw) - len(raw.lstrip()) >= 2
            result.append(Paragraph(
                inline(line[2:]), style(size=size, font=font, leftIndent=7 if nested else 0,
                                       bulletIndent=0, spaceAfter=2.5),
                bulletText="·" if nested else None,
            ))
        elif line.startswith("> "):
            flush()
            result.append(para(line[2:], size=size, font=font))
        else:
            buffer.append(line)
            if raw.endswith("  "):
                flush()
    flush()
    return result


class Leaf(Flowable):
    """Dezente Vektorzeichnung nach dem vorhandenen Blattmotiv der Website."""
    def __init__(self):
        super().__init__()
        self.width, self.height = 26, 32

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(PALETTE["accent"])
        c.setLineWidth(0.8)
        p = c.beginPath()
        p.moveTo(13, 30)
        p.curveTo(28, 18, 25, 5, 13, 3)
        p.curveTo(1, 4, -1, 16, 13, 30)
        c.drawPath(p)
        c.line(13, 1, 13, 27)
        for y in (10, 17):
            c.line(13, y, 7, y+4)
            c.line(13, y, 19, y+4)
        c.restoreState()


def columns(cells, widths=None, padding=0, background=None):
    if widths is None:
        widths = [(WIDTH - GAP * (len(cells)-1)) / len(cells)] * len(cells)
    row, actual = [], []
    for i, (cell, width) in enumerate(zip(cells, widths)):
        if i:
            row.append("")
            actual.append(GAP)
        row.append(cell)
        actual.append(width)
    table = Table([row], colWidths=actual, hAlign="LEFT")
    commands = [("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), padding),
                ("RIGHTPADDING", (0, 0), (-1, -1), padding),
                ("TOPPADDING", (0, 0), (-1, -1), padding),
                ("BOTTOMPADDING", (0, 0), (-1, -1), padding)]
    if background:
        for i in range(len(cells)):
            commands.append(("BACKGROUND", (i*2, 0), (i*2, 0), PALETTE[background]))
    table.setStyle(TableStyle(commands))
    return table


def heading(text, small=False):
    return para(text, font="Label-Bold", color="ink", size=8.1 if small else 9,
                spaceBefore=6, spaceAfter=5)


def masthead(subtitle, contact=None):
    left = [para("BB LIMEN", font="Text", color="ink", size=25, leading=28, spaceAfter=2),
            para(subtitle, font="Label", color="ink", size=8.3)]
    if contact:
        right = blocks(contact, size=7.3, font="Label")
        top = columns([left, right, Leaf()], [WIDTH*.50, WIDTH*.37-GAP, WIDTH*.13-GAP])
    else:
        top = columns([left, Leaf()], [WIDTH-40-GAP, 40])
    return [top, Spacer(1, 6), Rule(), Spacer(1, 8)]


class Rule(Flowable):
    def __init__(self):
        super().__init__()
        self.width, self.height = WIDTH, 1

    def draw(self):
        self.canv.setStrokeColor(PALETTE["accent"])
        self.canv.setLineWidth(.65)
        self.canv.line(0, 0, self.width, 0)


def profiles(text, portraits=False):
    parts = re.split(r"(?m)^#### (.+)\n", text)
    cards = []
    for name, body in zip(parts[1::2], parts[2::2]):
        content = [para(name, font="Text", color="ink", size=13.5, spaceAfter=5)]
        if portraits:
            file = "aranda_bw.png" if "Aranda" in name else "mika_bw.png"
            photo = Image(str(OUT_DIR / "assets" / file), width=37, height=37)
            content = [columns([content, photo], [(WIDTH-GAP)/2-16-45-GAP, 45])]
        content += blocks(body, size=8, font="Label")
        cards.append(content)
    return columns(cards, padding=8, background="surface")


def portrait_story(data):
    header = data["Kopfzeile"].splitlines()
    story = masthead(unescape(header[1].replace("**", "").strip()))
    story += [para(header[2], size=7.35, font="Label", spaceAfter=8)]
    motto, intro = data["Unser Leitsatz"].split("\n", 1)
    story += [para(motto, size=16, leading=19.5, font="Text", color="ink", spaceAfter=5)]
    story += blocks(intro, size=8.2)
    story += [Spacer(1, 5), profiles(data["Die betreuenden Personen"], portraits=True)]
    key = next(key for key in data if key.startswith("Typische Aufgabenbereiche"))
    story.append(heading(key))
    groups = re.split(r"\n(?=\* \*\*)", data[key])
    note = ""
    if "\n*(Hinweis:" in groups[-1]:
        groups[-1], note = groups[-1].split("\n*(Hinweis:", 1)
        note = "*(Hinweis:" + note
    story.append(columns([blocks(group, size=7.9) for group in groups]))
    if note:
        story += [para(note, size=7.1, color="muted", spaceAfter=1)]
    story.append(heading("Zusammenarbeit mit den Beteiligten in der Praxis"))
    cooperation = re.split(r"\n(?=\* \*\*)", data["Zusammenarbeit mit den Beteiligten in der Praxis"])
    story.append(columns([blocks(group, size=7.9) for group in cooperation]))
    story += [Spacer(1, 6), Rule(), Spacer(1, 6)]
    contact = re.split(r"\n(?=\* \*\*)", data["Kontaktdaten BB Limen"])
    story.append(columns([blocks(group, size=7.6, font="Label") for group in contact]))
    return story


def service_story(data):
    sender = data["Absender / Bürokopf"].splitlines()
    story = masthead(sender[1].strip(), "\n\n".join(sender[2:]))
    story += blocks(data["Empfänger"], size=7.7, font="Label")
    subject = data["Betreff"].splitlines()
    story += [Spacer(1, 5), para(subject[0], size=7.7, font="Label", color="muted", spaceAfter=4),
              para(subject[1], size=14.5, leading=18, color="ink", spaceAfter=8)]
    story += blocks(data["Anschreiben an die Service-Einheit"], size=8.1)
    key = next(key for key in data if key.startswith("1. "))
    address, notice = data[key].split("**Wichtiger Hinweis", 1)
    story += [heading(key), columns([
        blocks(address, size=9, font="Label"),
        blocks("**Wichtiger Hinweis" + notice, size=7.65),
    ], padding=8, background="surface")]
    key = next(key for key in data if key.startswith("2. "))
    story += [heading(key), *blocks(data[key], size=7.8)]
    key = next(key for key in data if key.startswith("3. "))
    story += [heading(key), profiles(data[key])]
    key = next(key for key in data if key.startswith("4. "))
    story += [heading(key), *blocks(data[key], size=7.8)]
    key = next(key for key in data if key.startswith("5. "))
    form, thanks = data[key].split("```text", 1)[1].split("```", 1)
    story += [heading(key), Rule(), Spacer(1, 5)]
    for line in form.strip().splitlines():
        if line.strip():
            story.append(para(line, size=8, font="Label", spaceAfter=7))
    story += blocks(thanks, size=7.5)
    return story


def footer(canvas, document):
    if document.page != 1:
        raise ValueError("Der Text überschreitet eine A4-Seite; bitte den Satz prüfen.")
    canvas.saveState()
    canvas.setTitle(document.title)
    canvas.setAuthor("BB Limen · Büro für rechtliche Betreuung")
    canvas.setFont("Label", 6.5)
    canvas.setFillColor(PALETTE["muted"])
    canvas.drawString(MARGIN, 8 * mm, "BB LIMEN · Büro für rechtliche Betreuung")
    canvas.drawRightString(PAGE_WIDTH-MARGIN, 8 * mm, f"{document.page:02d}")
    canvas.restoreState()


def main():
    register_fonts()
    jobs = [
        ("BB-Limen-Vorstellung-Einseiter", portrait_story, "Kurzporträt & Vorstellung"),
        ("BB-Limen-Stammdaten-Serviceeinheiten-Amtsgerichte", service_story, "Stammdatenmitteilung an die Betreuungsgerichte"),
    ]
    for name, make_story, title in jobs:
        output = OUT_DIR / f"{name}.pdf"
        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer, pagesize=A4, rightMargin=MARGIN, leftMargin=MARGIN,
            topMargin=11*mm, bottomMargin=14*mm, title=title, pageCompression=1,
        )
        document.build(make_story(sections(OUT_DIR / f"{name}.md")),
                       onFirstPage=footer, onLaterPages=footer)
        output.write_bytes(buffer.getvalue())
        print(f"Erzeugt: {output}")


if __name__ == "__main__":
    main()
