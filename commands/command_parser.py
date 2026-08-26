"""
commands/command_parser.py — Parser NLP: zamienia rozpoznany tekst na (komenda, pewność, parametry).

Wymaga modelu spaCy dla polskiego:
    python -m spacy download pl_core_news_sm

Dopasowanie oparte o słowa kluczowe (substring) + fuzzy fallback (difflib)
dla odporności na drobne błędy rozpoznawania mowy.
"""
import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

import spacy

import config
from utils.logger import get_logger

logger = get_logger(__name__)

MATCH_THRESHOLD = 0.3  # Minimalna pewność, żeby uznać dopasowanie za trafne
FUZZY_MATCH_THRESHOLD = 0.8  # Próg podobieństwa słów dla fuzzy fallback
FUZZY_PARTIAL_WEIGHT = 0.35  # Waga fuzzy trafienia (mniejsza niż exact match)


class CommandParser:
    def __init__(self, spacy_model: str = "pl_core_news_sm"):
        try:
            self.nlp = spacy.load(spacy_model)
        except OSError:
            logger.error(
                f"❌ Brak modelu spaCy '{spacy_model}'. Pobierz go przez:\n"
                f"    python -m spacy download {spacy_model}"
            )
            raise
        self.commands_db = self._init_commands()

    def _init_commands(self) -> Dict[str, Dict]:
        """Baza komend: słowa kluczowe, przykłady, priorytet (do rozstrzygania remisów)."""
        return {
            # --- YouTube ---
            "youtube_skip_ad": {
                "keywords": ["pomiń", "reklamę", "reklama", "skip", "ad"],
                "examples": ["pomiń reklamę", "skip ad"],
                "priority": 10,
            },
            "youtube_play": {
                "keywords": ["odtwórz", "wznów", "play", "start"],
                "examples": ["odtwórz", "wznów"],
                "priority": 9,
            },
            "youtube_pause": {
                "keywords": ["pauza", "zatrzymaj", "pause", "stop"],
                "examples": ["pauza", "zatrzymaj"],
                "priority": 9,
            },
            "youtube_next": {
                "keywords": ["następne", "następny", "kolejne", "next"],
                "examples": ["następne wideo"],
                "priority": 8,
            },
            "youtube_previous": {
                "keywords": ["poprzednie", "poprzedni", "previous", "wróć"],
                "examples": ["poprzednie wideo"],
                "priority": 8,
            },
            "youtube_fullscreen": {
                "keywords": ["pełny", "ekran", "fullscreen"],
                "examples": ["pełny ekran"],
                "priority": 7,
            },
            # --- Discord ---
            "discord_mute": {
                "keywords": ["wycisz", "mikrofon", "mute"],
                "examples": ["wycisz mikrofon"],
                "priority": 10,
            },
            "discord_unmute": {
                "keywords": ["włącz", "mikrofon", "unmute"],
                "examples": ["włącz mikrofon"],
                "priority": 10,
            },
            "discord_deafen": {
                "keywords": ["wycisz", "dźwięk", "deafen"],
                "examples": ["wycisz dźwięk"],
                "priority": 9,
            },
            "discord_switch_channel": {
                "keywords": ["przełącz", "kanał", "channel"],
                "examples": ["przełącz na kanał gaming"],
                "priority": 8,
            },
            "discord_join_channel": {
                "keywords": ["dołącz", "kanału", "join"],
                "examples": ["dołącz do kanału ogólny"],
                "priority": 8,
            },
            "discord_leave_channel": {
                "keywords": ["opuść", "kanał", "leave"],
                "examples": ["opuść kanał"],
                "priority": 8,
            },
            "discord_mute_user": {
                "keywords": ["wycisz", "użytkownika", "usera", "osobę"],
                "examples": ["wycisz użytkownika Kowalski"],
                "priority": 11,  # wyższy priorytet niż discord_mute (własny mikrofon)
            },
            "discord_view_screen": {
                "keywords": ["pokaż", "ekran", "udostępnia", "stream"],
                "examples": ["pokaż ekran Kowalskiego"],
                "priority": 9,
            },
            # --- System ---
            "system_time": {
                "keywords": ["godzina", "która", "czas", "time"],
                "examples": ["jaka godzina"],
                "priority": 6,
            },
            "system_exit": {
                "keywords": ["wyłącz", "zamknij", "koniec", "exit"],
                "examples": ["wyłącz się"],
                "priority": 6,
            },
        }

    def was_activated(self, text: str) -> bool:
        """True jeśli tekst zaczyna się od słowa aktywacyjnego (np. 'Dżarwis, ...')."""
        normalized = text.lower().strip()
        return self.strip_activation_keyword(normalized) != normalized

    def strip_activation_keyword(self, text: str) -> str:
        """Usuwa słowo aktywacyjne (np. 'dżarwis,') z początku tekstu, jeśli obecne."""
        text = text.strip()
        for variant in config.ACTIVATION_KEYWORDS_VARIANTS:
            pattern = rf"^{re.escape(variant)}[,\s]*"
            if re.match(pattern, text, flags=re.IGNORECASE):
                return re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
        return text

    def parse(self, text: str) -> Tuple[Optional[str], float, Dict]:
        """Parsuje tekst i zwraca (nazwa_komendy, pewność, parametry). (None, 0, {}) jeśli brak dopasowania."""
        text = self.strip_activation_keyword(text.lower().strip())
        doc = self.nlp(text)
        tokens = [t.text for t in doc]

        best_match = None
        best_score = 0.0
        best_priority = -1

        for command_name, command_info in self.commands_db.items():
            score = self._calculate_match_score(text, tokens, command_info)
            priority = command_info.get("priority", 0)

            if score > best_score or (score == best_score and priority > best_priority):
                best_score = score
                best_match = command_name
                best_priority = priority

        if best_score >= MATCH_THRESHOLD:
            params = self._extract_parameters(text, best_match)
            logger.info(f"✅ Komenda: {best_match} (pewność: {best_score:.2%})")
            return best_match, best_score, params

        logger.info(f"❌ Brak pewnego dopasowania dla: '{text}'")
        return None, 0.0, {}

    def _calculate_match_score(self, text: str, tokens: List[str], command_info: Dict) -> float:
        """Score = suma trafień słów kluczowych (exact substring lub fuzzy), znormalizowana."""
        keywords = command_info.get("keywords", [])
        if not keywords:
            return 0.0

        score = 0.0
        for keyword in keywords:
            if keyword in text:
                score += 1.0
            elif self._fuzzy_match(keyword, tokens):
                score += FUZZY_PARTIAL_WEIGHT

        return min(score / len(keywords), 1.0)

    def _fuzzy_match(self, keyword: str, tokens: List[str]) -> bool:
        """Sprawdza, czy jakiś token jest wystarczająco podobny do słowa kluczowego (błędy STT)."""
        return any(
            SequenceMatcher(None, keyword, token).ratio() >= FUZZY_MATCH_THRESHOLD
            for token in tokens
        )

    def _extract_parameters(self, text: str, command: str) -> Dict:
        """Wyciąga parametry z tekstu (nazwa kanału, nazwa użytkownika, liczba sekund)."""
        params: Dict = {}
        words = text.split()

        if command in ("discord_switch_channel", "discord_join_channel"):
            for trigger in ("kanał", "kanału", "channel"):
                if trigger in words:
                    idx = words.index(trigger)
                    if idx + 1 < len(words):
                        params["channel_name"] = words[idx + 1]
                        break

        if command == "discord_mute_user":
            for trigger in ("użytkownika", "usera", "osobę"):
                if trigger in words:
                    idx = words.index(trigger)
                    if idx + 1 < len(words):
                        params["user_name"] = words[idx + 1]
                        break

        if command == "discord_view_screen" and "ekran" in words:
            idx = words.index("ekran")
            if idx + 1 < len(words):
                params["user_name"] = words[idx + 1]

        if any(x in text for x in ("sekund", "seconds")):
            numbers = re.findall(r"\d+", text)
            if numbers:
                params["seconds"] = int(numbers[0])

        return params
