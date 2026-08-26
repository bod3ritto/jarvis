"""Wspólna konfiguracja testów — dodaje katalog projektu do ścieżki importu."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
