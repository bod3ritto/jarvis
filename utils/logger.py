"""
utils/logger.py — Centralna konfiguracja logowania dla JARVIS.

Kolorowe logi w konsoli (colorlog) + zapis do pliku logs/jarvis.log.
Użycie w dowolnym module:

    from utils.logger import get_logger
    logger = get_logger(__name__)
"""
import logging
import logging.handlers

import colorlog

import config

_configured = False


def setup_logging() -> None:
    """Konfiguruje root logger. Wywoływane raz, automatycznie przy pierwszym get_logger()."""
    global _configured
    if _configured:
        return

    level = getattr(logging, config.LOG_LEVEL, logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)

    # Konsola — kolorowe logi
    console_handler = colorlog.StreamHandler()
    console_handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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
    root.addHandler(console_handler)

    # Plik — rotacja przy przekroczeniu LOG_MAX_SIZE
    file_handler = logging.handlers.RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.LOG_MAX_SIZE,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    root.addHandler(file_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Zwraca skonfigurowany logger dla danego modułu (np. get_logger(__name__))."""
    setup_logging()
    return logging.getLogger(name)
