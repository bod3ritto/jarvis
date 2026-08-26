"""
tests/test_commands.py — Testy parsera i executora.

Nie wymagają mikrofonu, przeglądarki ani Discorda — wszystkie zależności
sprzętowe są zamockowane, a moduły automatyzacji importują się leniwie.

    pytest tests/test_commands.py -v
"""
from unittest.mock import MagicMock

import pytest

from commands.command_parser import MATCH_THRESHOLD, CommandParser
from commands.command_executor import CommandExecutor


@pytest.fixture(scope="module")
def parser():
    return CommandParser()


@pytest.fixture
def executor():
    """Executor z atrapą TTS — nic nie jest wypowiadane na głos."""
    return CommandExecutor(tts=MagicMock())


# ---------------------------------------------------------------- parsowanie

@pytest.mark.parametrize(
    "text,expected",
    [
        # YouTube
        ("dżarwis, pomiń reklamę", "youtube_skip_ad"),
        ("odtwórz", "youtube_play"),
        ("wznów", "youtube_play"),
        ("pauza", "youtube_pause"),
        ("zatrzymaj", "youtube_pause"),
        ("stop", "youtube_pause"),
        ("następne wideo", "youtube_next"),
        ("poprzednie wideo", "youtube_previous"),
        ("pełny ekran", "youtube_fullscreen"),
        # Discord
        ("wycisz mikrofon", "discord_mute"),
        ("włącz mikrofon", "discord_unmute"),
        ("wycisz dźwięk", "discord_deafen"),
        ("przełącz na kanał gaming", "discord_switch_channel"),
        ("dołącz do kanału ogólny", "discord_join_channel"),
        ("opuść kanał", "discord_leave_channel"),
        ("wycisz użytkownika kowalski", "discord_mute_user"),
        ("pokaż ekran kowalskiego", "discord_view_screen"),
        # System
        ("jaka jest godzina", "system_time"),
        ("która godzina", "system_time"),
        ("wyłącz się", "system_exit"),
        ("zamknij się", "system_exit"),
    ],
)
def test_rozpoznaje_komendy(parser, text, expected):
    command, confidence, _ = parser.parse(text)
    assert command == expected
    assert confidence >= MATCH_THRESHOLD


def test_kazda_komenda_z_bazy_ma_handler(parser, executor):
    """Każda komenda znana parserowi musi mieć obsługę w executorze — i odwrotnie."""
    assert set(parser.commands_db) == set(executor.handlers)


def test_przyklady_z_bazy_parsuja_sie_na_wlasna_komende(parser):
    """Przykłady deklarowane przy komendzie muszą faktycznie na nią wskazywać."""
    for name, info in parser.commands_db.items():
        for example in info["examples"]:
            assert parser.parse(example)[0] == name, f"{example!r} nie trafia w {name}"


@pytest.mark.parametrize(
    "text",
    [
        "dżarwis, opowiedz mi żart o kotach",
        "no dobra to co teraz",
        "",
        "   ",
    ],
)
def test_odrzuca_wypowiedzi_bez_komendy(parser, text):
    command, confidence, params = parser.parse(text)
    assert command is None
    assert confidence == 0.0
    assert params == {}


def test_rdzen_nie_lapie_przypadkowego_slowa(parser):
    """Rdzeń 'ad' (od 'reklamy') nie może trafiać w środek innego wyrazu."""
    assert parser.parse("pokaż ekran adama")[0] == "discord_view_screen"


# ------------------------------------------------------------ słowo aktywacyjne

@pytest.mark.parametrize(
    "text,expected",
    [
        ("dżarwis, pauza", "pauza"),
        ("Dżarwis pauza", "pauza"),
        ("jarvis pauza", "pauza"),
        ("pauza", "pauza"),
    ],
)
def test_usuwa_slowo_aktywacyjne(parser, text, expected):
    assert parser.strip_activation_keyword(text) == expected


def test_wykrywa_slowo_aktywacyjne(parser):
    assert parser.was_activated("dżarwis, pauza")
    assert not parser.was_activated("pauza")


# ------------------------------------------------------------------- parametry

@pytest.mark.parametrize(
    "text,key,expected",
    [
        ("przełącz na kanał ogólny", "channel_name", "ogólny"),
        ("przełącz na kanał gaming lobby", "channel_name", "gaming lobby"),
        ("dołącz do kanału muzyka", "channel_name", "muzyka"),
        ("wycisz użytkownika kowalski", "user_name", "kowalski"),
        ("pokaż ekran kowalskiego", "user_name", "kowalskiego"),
    ],
)
def test_wyciaga_parametry(parser, text, key, expected):
    assert parser.parse(text)[2].get(key) == expected


def test_wyciaga_liczbe_sekund(parser):
    assert parser.parse("pomiń reklamę 15 sekund")[2].get("seconds") == 15


# ------------------------------------------------------------------- executor

def test_executor_wykonuje_znana_komende(executor):
    assert executor.execute("system_time", {}) is True
    executor.tts.speak.assert_called_once()


def test_executor_odrzuca_nieznana_komende(executor):
    assert executor.execute("nie_ma_takiej", {}) is False


def test_executor_nie_wywala_sie_gdy_handler_rzuca(executor):
    """Błąd integracji ma być zaraportowany, a nie wywrócić aplikację."""
    executor.handlers["system_time"] = MagicMock(side_effect=RuntimeError("bum"))
    assert executor.execute("system_time", {}) is False


def test_executor_pomija_komende_bez_wymaganego_parametru(executor):
    """Brak nazwy kanału nie może skończyć się próbą sterowania Discordem."""
    executor._get_discord = MagicMock()
    executor.execute("discord_switch_channel", {})
    executor._get_discord.assert_not_called()


def test_executor_przekazuje_nazwe_kanalu_do_discorda(executor):
    discord = MagicMock()
    executor._get_discord = MagicMock(return_value=discord)
    executor.execute("discord_switch_channel", {"channel_name": "gaming"})
    discord.switch_channel.assert_called_once_with("gaming")


def test_executor_przekazuje_sekundy_do_youtube(executor):
    youtube = MagicMock()
    executor._get_youtube = MagicMock(return_value=youtube)
    executor.execute("youtube_skip_ad", {"seconds": 15})
    youtube.skip_ad.assert_called_once_with(skip_time=15)


def test_shutdown_zamyka_przegladarke(executor):
    youtube = MagicMock()
    executor._youtube = youtube
    executor.shutdown()
    youtube.close.assert_called_once()
    assert executor._youtube is None


def test_shutdown_nie_zamyka_cudzego_tts(executor):
    """TTS wstrzyknięty z zewnątrz należy do wołającego — executor go nie gasi."""
    executor.shutdown()
    executor.tts.shutdown.assert_not_called()
