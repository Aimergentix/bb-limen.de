"""Gemeinsame Quell-, Bild- und Ausgabeordner der Dokumentgeneratoren."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = ROOT / "dokumente"
SOURCES = DOCUMENTS / "vorlagen"
ASSETS = DOCUMENTS / "assets"
OUTPUT = DOCUMENTS / "handouts"
