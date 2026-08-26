"""
utils/logger.py — Centralna konfiguracja logowania dla JARVIS.

Kolorowe logi w konsoli (colorlog) + zapis do pliku logs/jarvis.log.
colorlog jest opcjonalny — bez niego logi są zwykłe, ale wszystko działa.

Użycie w dowolnym module:

    from utils.logger import get_logger
    logger = get_logger(__name__)
"""
import logging
import logging.handlers

try:
    import colorlog

    HAS_COLORLOG = True
except ImportError:  # kolory są miłym dodatkiem, nie wymogiem
    HAS_COLORLOG = False

import config

_configured = False

CONSOLE_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def _build_console_handler() -> logging.Handler:
    """Handler konsolowy — kolorowy jeśli colorlog dostępny, inaczej zwykły."""
    if HAS_COLORLOG:
        handler = colorlog.StreamHandler()
        handler.setFormatter(
            colorlog.ColoredFormatter(
                f"%(log_color)s{CONSOLE_FORMAT}",
                datefmt="%H:%M:%S",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold_red",
                },
            )
        )
        return handler

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(CONSOLE_FORMAT, datefmt="%H:%M:%S"))
    return handler


def setup_logging() -> None:
    """Konfiguruje root logger. Wywoływane raz, automatycznie przy pierwszym get_logger()."""
    global _configured
    if _configured:
        return

    level = getattr(logging, config.LOG_LEVEL, logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)

    root.addHandler(_build_console_handler())

    # Plik — rotacja przy przekroczeniu LOG_MAX_SIZE
    file_handler = logging.handlers.RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.LOG_MAX_SIZE,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(CONSOLE_FORMAT))
    root.addHandler(file_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Zwraca skonfigurowany logger dla danego modułu (np. get_logger(__name__))."""
    setup_logging()
    return logging.getLogger(name)
