"""Erzeugt HTML-E-Mails und unadressierte EML-Entwürfe aus den Handouts.

Aufruf: python3 tools/generate_emails.py (gemeinsamer Dokument-Build).
Texte: dokumente/vorlagen/*.md; Farben: heller PALETTE-Block in src/style.css.
"""
from email.message import EmailMessage
from email.policy import SMTP
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
import re

from document_paths import OUTPUT

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "src/style.css").read_text(encoding="utf-8")
PALETTE = dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})", CSS.split(":root {", 1)[1].split("}", 1)[0]))
SANS = "Arial, Helvetica, sans-serif"
SERIF = "Georgia, 'Times New Roman', serif"
LINK = f"color:{PALETTE['link-ink']};text-decoration:underline;overflow-wrap:anywhere;word-break:break-word;"


def inline(source):
    """Nur unterstütztes Markdown ausgeben; Quell-HTML immer maskieren."""
    source = unescape(source.strip())
    pattern = r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+`|https?://[^\s<>]+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|\+49(?:[ \t]+\d+)+)"
    output = []
    for token in re.split(pattern, source):
        if token.startswith("**") and token.endswith("**"):
            output.append(f"<strong>{inline(token[2:-2])}</strong>")
        elif token.startswith("*") and token.endswith("*"):
            output.append(f"<em>{inline(token[1:-1])}</em>")
        elif token.startswith("`") and token.endswith("`"):
            output.append(inline(token[1:-1]))
        elif token.startswith("https://") or token.startswith("http://"):
            output.append(f'<a href="{escape(token, quote=True)}" style="{LINK}">{escape(token)}</a>')
        elif re.fullmatch(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", token):
            output.append(f'<a href="mailto:{escape(token, quote=True)}" style="{LINK}">{escape(token)}</a>')
        elif token.startswith("+49"):
            number = re.sub(r"\s+", "", token)
            output.append(f'<a href="tel:{number}" style="{LINK}">{escape(token)}</a>')
        else:
            output.append(escape(token))
    return "".join(output)


def paragraph(text):
    return f'<p style="margin:0 0 12px;font:15px/1.65 {SANS};color:{PALETTE["body"]};">{text}</p>'


def heading(text, level=2):
    size = 20 if level == 2 else 21
    family = SANS if level == 2 else SERIF
    return f'<h{level} style="margin:0 0 14px;font-family:{family};font-size:{size}px;line-height:1.35;font-weight:{"bold" if level == 2 else "normal"};color:{PALETTE["ink"]};">{inline(text)}</h{level}>'


def markdown(source):
    """Absätze, Listen, Unterüberschriften, Adressblöcke und Textfelder setzen."""
    lines = source.splitlines()
    output, pending, lists = [], [], []
    index = 0

    def flush():
        if pending:
            output.append(paragraph("<br>".join(inline(line) for line in pending)))
            pending.clear()

    def close_lists(minimum=-1):
        while lists and lists[-1] >= minimum:
            output.append("</li></ul>")
            lists.pop()

    while index < len(lines):
        raw = lines[index]
        line = raw.strip()
        index += 1
        if line.startswith("```"):
            flush()
            close_lists()
            code = []
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code.append(lines[index])
                index += 1
            index += 1
            output.append(f'<pre style="margin:0 0 14px;padding:14px;border:1px solid {PALETTE["line"]};font:14px/1.8 {SANS};color:{PALETTE["body"]};white-space:pre-wrap;word-wrap:break-word;">{escape(chr(10).join(code))}</pre>')
        elif not line or line == "&nbsp;" or line == "---":
            flush()
        elif re.match(r"^#{1,6} ", line):
            flush()
            close_lists()
            match = re.match(r"^(#{1,6}) (.+)$", line)
            output.append(heading(match[2], min(len(match[1]), 3)))
        elif line.startswith("> "):
            flush()
            close_lists()
            quote = [line[2:]]
            while index < len(lines) and lines[index].strip().startswith("> "):
                quote.append(lines[index].strip()[2:])
                index += 1
            output.append(f'<blockquote style="margin:0 0 16px;padding:12px 16px;border-left:3px solid {PALETTE["accent"]};background-color:{PALETTE["surface"]};">{paragraph("<br>".join(inline(part) for part in quote))}</blockquote>')
        elif re.match(r"[*-]\s+", line):
            flush()
            indent = len(raw) - len(raw.lstrip())
            close_lists(indent + 1)
            if not lists or indent > lists[-1]:
                output.append(f'<ul style="margin:0 0 12px;padding-left:22px;font:15px/1.65 {SANS};color:{PALETTE["body"]};"><li style="margin:0 0 6px;">')
                lists.append(indent)
            else:
                output.append('</li><li style="margin:0 0 6px;">')
            output.append(inline(re.sub(r"^[*-]\s+", "", line)))
        else:
            if raw[:1].isspace() and lists:
                output.append("<br>" + inline(line))
            else:
                close_lists()
                pending.append(line)
    flush()
    close_lists()
    return "\n".join(output)


def sections(source):
    matches = list(re.finditer(r"^### (.+)$", source, re.M))
    return [(match[1], re.sub(r"(?m)^---\s*$", "", source[match.end():matches[i+1].start() if i+1 < len(matches) else len(source)]).strip()) for i, match in enumerate(matches)]


def content_rows(source):
    rows = []
    for index, (name, body) in enumerate(sections(source)):
        if index == 0:
            lines = body.splitlines()
            content = f'<p style="margin:0 0 6px;font:32px/1.2 {SERIF};color:{PALETTE["ink"]};">{inline(lines[0])}</p>'
            content += paragraph(inline(lines[1]))
            if len(lines) > 2:
                content += markdown("\n".join(lines[2:]))
            border = f'border-bottom:2px solid {PALETTE["accent"]};'
        else:
            border = f'border-bottom:1px solid {PALETTE["line"]};'
            if name == "Unser Leitsatz":
                motto, body = body.split("\n", 1)
                content = f'<h1 style="margin:0 0 14px;font:26px/1.35 {SERIF};color:{PALETTE["ink"]};">{inline(motto)}</h1>' + markdown(body)
            elif name == "Betreff":
                lines = body.splitlines()
                content = paragraph(inline(lines[0]))
                content += f'<h1 style="margin:0;font:25px/1.35 {SERIF};color:{PALETTE["ink"]};">{inline(" ".join(lines[1:]))}</h1>'
            elif name in ("Empfänger", "Anschreiben an die Service-Einheit"):
                content = markdown(body)
            else:
                content = heading(name) + markdown(body)
        rows.append(f'<tr><td style="padding:24px 28px;{border}">{content}</td></tr>')
    return "\n".join(rows)


def document_html(content, title):
    return f'''<!DOCTYPE html>
<html lang="de" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{escape(title)}</title>
</head>
<body style="margin:0;padding:0;background-color:{PALETTE['surface']};color:{PALETTE['body']};-webkit-text-size-adjust:100%;">
<table role="presentation" width="100%" border="0" cellpadding="0" cellspacing="0" bgcolor="{PALETTE['surface']}" style="width:100%;border-collapse:collapse;">
<tr><td align="center" style="padding:20px 8px;">
<!--[if mso]><table role="presentation" width="680" border="0" cellpadding="0" cellspacing="0"><tr><td><![endif]-->
<table role="presentation" width="100%" border="0" cellpadding="0" cellspacing="0" bgcolor="{PALETTE['paper']}" style="width:100%;max-width:680px;table-layout:fixed;border-collapse:collapse;background-color:{PALETTE['paper']};overflow-wrap:anywhere;word-wrap:break-word;">
{content}
</table>
<!--[if mso]></td></tr></table><![endif]-->
</td></tr></table>
</body>
</html>
'''


def render(source, title):
    return document_html(content_rows(source), title)


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.in_body = False

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self.in_body = True
        if self.in_body and tag == "li":
            self.parts.append("\n• ")
        if self.in_body and tag == "br":
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if self.in_body and tag in ("p", "h1", "h2", "h3", "pre", "tr", "ul"):
            self.parts.append("\n\n")
        if tag == "body":
            self.in_body = False

    def handle_data(self, data):
        if self.in_body:
            self.parts.append(data)

    def text(self):
        return re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", "".join(self.parts)).strip() + "\n"


def write_email(output_name, title, html):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / f"{output_name}.html").write_text(html, encoding="utf-8")
    plain = PlainText()
    plain.feed(html)
    message = EmailMessage(policy=SMTP)
    message["Subject"] = title
    message["X-Unsent"] = "1"
    message.set_content(plain.text())
    message.add_alternative(html, subtype="html")
    (OUTPUT / f"{output_name}.eml").write_bytes(message.as_bytes())
    print(f"Erzeugt: {OUTPUT / output_name}.html und .eml")


def main():
    # Gemeinsamer Einstieg verhindert abweichende Quell- und Ausgabepfade.
    from build_documents import main as build_documents
    build_documents()


if __name__ == "__main__":
    main()
