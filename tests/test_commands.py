"""
tests/test_commands.py — Testy jednostkowe parsera komend (bez mikrofonu/TTS).

Uruchom:
    pytest tests/test_commands.py -v
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Umożliwia import modułów z katalogu głównego projektu przy uruchamianiu przez pytest
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from commands.command_parser import CommandParser
from commands.command_executor import CommandExecutor


@pytest.fixture(scope="module")
def parser():
    return CommandParser()


@pytest.mark.parametrize(
    "text,expected_command",
    [
        ("dżarwis, pomiń reklamę", "youtube_skip_ad"),
        ("wycisz mikrofon", "discord_mute"),
        ("włącz mikrofon", "discord_unmute"),
        ("przełącz na kanał gaming", "discord_switch_channel"),
        ("jaka jest godzina", "system_time"),
        ("pokaż ekran kowalskiego", "discord_view_screen"),
    ],
)
def test_parse_known_commands(parser, text, expected_command):
    command, confidence, params = parser.parse(text)
    assert command == expected_command
    assert confidence > 0


def test_parse_unknown_command_returns_none(parser):
    command, confidence, params = parser.parse("dżarwis, opowiedz mi żart o kotach")
    assert command is None
    assert confidence == 0


def test_strip_activation_keyword(parser):
    assert parser.strip_activation_keyword("dżarwis, pauza") == "pauza"
    assert parser.strip_activation_keyword("jarvis pauza") == "pauza"
    assert parser.strip_activation_keyword("pauza") == "pauza"


def test_extract_channel_name_parameter(parser):
    _, _, params = parser.parse("przełącz na kanał ogólny")
    assert params.get("channel_name") == "ogólny"


def test_executor_calls_handler_and_speaks():
    fake_tts = MagicMock()
    executor = CommandExecutor(tts=fake_tts)

    result = executor.execute("system_time", {})

    assert result is True
    fake_tts.speak.assert_called_once()


def test_executor_unknown_command_returns_false():
    fake_tts = MagicMock()
    executor = CommandExecutor(tts=fake_tts)

    result = executor.execute("nonexistent_command", {})

    assert result is False
