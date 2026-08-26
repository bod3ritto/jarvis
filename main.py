"""
main.py — Punkt wejścia aplikacji JARVIS.

Uruchom:
    python main.py
"""
import sys

from PyQt6.QtWidgets import QApplication

from gui.main_window import JarvisWindow
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    logger.info("🚀 Uruchamianie JARVIS...")

    app = QApplication(sys.argv)
    window = JarvisWindow()
    window.show()

    logger.info("✅ JARVIS gotowy!")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
