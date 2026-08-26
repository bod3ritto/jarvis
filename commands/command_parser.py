"""
commands/command_parser.py — Parser komend: tekst -> (komenda, pewność, parametry).

Dopasowanie działa na tokenach (granice słów), nie na surowych podciągach —
dzięki temu rdzeń "ad" nie trafia już w "adama". Polską fleksję obsługują
rdzenie: "kanał" łapie "kanału"/"kanale", "reklam" łapie "reklamę"/"reklamy".

Pewność = jaka część wypowiedzi została wyjaśniona przez daną komendę
(pokrycie), a NIE ile z jej słów kluczowych trafiło. To istotne: słowa
kluczowe to warianty/synonimy, więc dopisanie kolejnego synonimu nie może
obniżać pewności — na tym błędzie poprzednia wersja wykładała się na
jednowyrazowych komendach ("pauza", "wyłącz się", "jaka godzina").

Moduł jest celowo bez zewnętrznych zależności — testy parsera uruchamiają się
bez instalowania czegokolwiek.
"""
import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Sequence, Tuple

import config
from utils.logger import get_logger

logger = get_logger(__name__)

MATCH_THRESHOLD = 0.35  # Minimalne pokrycie wypowiedzi, żeby uznać komendę za trafną
FUZZY_THRESHOLD = 0.87  # Podobieństwo tokena do rdzenia przy literówkach STT
FUZZY_WEIGHT = 0.5  # Trafienie fuzzy liczy się słabiej niż dokładne
MIN_PREFIX_LEN = 4  # Krótsze rdzenie muszą trafiać w cały token (bez prefiksów)

# Słowa funkcyjne — nie niosą treści, więc nie rozcieńczają pokrycia.
STOPWORDS = frozenset(
    {
        "a", "aby", "ale", "by", "co", "czy", "do", "dla", "i", "jest", "już", "juz",
        "ja", "mi", "mnie", "na", "nam", "no", "o", "od", "oraz", "po", "proszę",
        "prosze", "przez", "się", "sie", "tam", "te", "tego", "ten", "teraz", "to",
        "tu", "tę", "w", "we", "z", "za", "ze", "the",
    }
)


class CommandParser:
    def __init__(self):
        self.commands_db = self._init_commands()

    def _init_commands(self) -> Dict[str, Dict]:
        """Baza komend. 'keywords' to RDZENIE — łapią też formy odmienione."""
        return {
            # --- YouTube ---
            "youtube_skip_ad": {
                "keywords": ["pomiń", "pomin", "reklam", "skip"],
                "examples": ["pomiń reklamę"],
                "priority": 10,
            },
            "youtube_play": {
                "keywords": ["odtwórz", "odtworz", "wznów", "wznow", "play", "graj"],
                "examples": ["odtwórz", "wznów"],
                "priority": 9,
            },
            "youtube_pause": {
                "keywords": ["pauz", "zatrzymaj", "stop", "pause"],
                "examples": ["pauza", "zatrzymaj"],
                "priority": 9,
            },
            "youtube_next": {
                "keywords": ["następn", "nastepn", "kolejn", "next", "dalej"],
                "examples": ["następne wideo"],
                "priority": 8,
            },
            "youtube_previous": {
                "keywords": ["poprzedni", "previous", "cofnij", "wróć", "wroc"],
                "examples": ["poprzednie wideo"],
                "priority": 8,
            },
            "youtube_fullscreen": {
                "keywords": ["pełn", "peln", "ekran", "fullscreen"],
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
                "keywords": ["włącz", "wlacz", "mikrofon", "unmute", "odcisz"],
                "examples": ["włącz mikrofon"],
                "priority": 10,
            },
            "discord_deafen": {
                "keywords": ["wycisz", "dźwięk", "dzwiek", "deafen", "ogłusz"],
                "examples": ["wycisz dźwięk"],
                "priority": 9,
            },
            "discord_switch_channel": {
                "keywords": ["przełącz", "przelacz", "kanał", "kanal", "channel"],
                "examples": ["przełącz na kanał gaming"],
                "priority": 8,
            },
            "discord_join_channel": {
                "keywords": ["dołącz", "dolacz", "kanał", "kanal", "join", "wejdź"],
                "examples": ["dołącz do kanału ogólny"],
                "priority": 8,
            },
            "discord_leave_channel": {
                "keywords": ["opuść", "opusc", "wyjdź", "wyjdz", "rozłącz", "leave", "kanał"],
                "examples": ["opuść kanał"],
                "priority": 8,
            },
            "discord_mute_user": {
                "keywords": ["wycisz", "użytkownik", "uzytkownik", "user", "osob", "gości"],
                "examples": ["wycisz użytkownika Kowalski"],
                "priority": 11,
            },
            "discord_view_screen": {
                "keywords": ["pokaż", "pokaz", "ekran", "stream", "udostępni"],
                "examples": ["pokaż ekran Kowalskiego"],
                "priority": 9,
            },
            # --- System ---
            "system_time": {
                "keywords": ["godzin", "która", "ktora", "czas", "time"],
                "examples": ["jaka godzina"],
                "priority": 6,
            },
            "system_exit": {
                "keywords": ["wyłącz", "wylacz", "zamknij", "koniec", "exit", "żegnaj"],
                "examples": ["wyłącz się"],
                "priority": 6,
            },
        }

    # ---------------- Słowo aktywacyjne ----------------

    def was_activated(self, text: str) -> bool:
        """True jeśli tekst zaczyna się od słowa aktywacyjnego (np. 'Dżarwis, ...')."""
        normalized = text.lower().strip()
        return self.strip_activation_keyword(normalized) != normalized

    def strip_activation_keyword(self, text: str) -> str:
        """Usuwa słowo aktywacyjne z początku tekstu, jeśli obecne."""
        text = text.strip()
        for variant in config.ACTIVATION_KEYWORDS_VARIANTS:
            pattern = rf"^{re.escape(variant)}\b[,\s]*"
            if re.match(pattern, text, flags=re.IGNORECASE):
                return re.sub(pattern, "", text, count=1, flags=re.IGNORECASE).strip()
        return text

    # ---------------- Parsowanie ----------------

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Dzieli tekst na tokeny słowne (z polskimi znakami), pomijając interpunkcję."""
        return re.findall(r"\w+", text.lower(), flags=re.UNICODE)

    def parse(self, text: str) -> Tuple[Optional[str], float, Dict]:
        """Zwraca (nazwa_komendy, pewność, parametry) lub (None, 0.0, {})."""
        stripped = self.strip_activation_keyword(text.lower().strip())
        tokens = self.tokenize(stripped)
        content_tokens = [t for t in tokens if t not in STOPWORDS]

        if not content_tokens:
            logger.info("❌ Pusta wypowiedź po odfiltrowaniu słów funkcyjnych")
            return None, 0.0, {}

        best_match: Optional[str] = None
        best_score = 0.0
        best_priority = -1

        for name, info in self.commands_db.items():
            score = self._coverage_score(content_tokens, info["keywords"])
            priority = info.get("priority", 0)
            if score > best_score or (score == best_score and score > 0 and priority > best_priority):
                best_score, best_match, best_priority = score, name, priority

        if best_match is not None and best_score >= MATCH_THRESHOLD:
            params = self._extract_parameters(tokens, best_match)
            logger.info(f"✅ Komenda: {best_match} (pewność: {best_score:.0%})")
            return best_match, best_score, params

        logger.info(f"❌ Brak pewnego dopasowania dla: '{stripped}'")
        return None, 0.0, {}

    def _coverage_score(self, content_tokens: Sequence[str], keywords: Sequence[str]) -> float:
        """Jaka część wypowiedzi (0-1) jest wyjaśniona przez słowa kluczowe komendy."""
        if not content_tokens:
            return 0.0
        matched = sum(
            max((self._token_weight(tok, kw) for kw in keywords), default=0.0)
            for tok in content_tokens
        )
        return min(matched / len(content_tokens), 1.0)

    @staticmethod
    def _token_weight(token: str, keyword: str) -> float:
        """1.0 = trafienie dokładne/rdzeniem, FUZZY_WEIGHT = literówka STT, 0.0 = brak."""
        if token == keyword:
            return 1.0
        if len(keyword) >= MIN_PREFIX_LEN and token.startswith(keyword):
            return 1.0
        if SequenceMatcher(None, keyword, token).ratio() >= FUZZY_THRESHOLD:
            return FUZZY_WEIGHT
        return 0.0

    # ---------------- Parametry ----------------

    # Słowo, po którym w wypowiedzi występuje nazwa kanału / użytkownika.
    PARAM_TRIGGERS = {
        "discord_switch_channel": ("kanał", "kanal", "channel"),
        "discord_join_channel": ("kanał", "kanal", "channel"),
        "discord_mute_user": ("użytkownik", "uzytkownik", "user", "osob"),
        "discord_view_screen": ("ekran",),
    }

    def _extract_parameters(self, tokens: List[str], command: str) -> Dict:
        """Wyciąga nazwę kanału/użytkownika (reszta zdania po wyzwalaczu) i liczbę sekund."""
        params: Dict = {}

        triggers = self.PARAM_TRIGGERS.get(command)
        if triggers:
            value = self._tail_after_trigger(tokens, triggers)
            if value:
                key = "channel_name" if command.endswith("_channel") else "user_name"
                params[key] = value

        if any(t.startswith("sekund") or t.startswith("second") for t in tokens):
            numbers = [t for t in tokens if t.isdigit()]
            if numbers:
                params["seconds"] = int(numbers[0])

        return params

    @staticmethod
    def _tail_after_trigger(tokens: List[str], triggers: Sequence[str]) -> Optional[str]:
        """Reszta wypowiedzi po słowie-wyzwalaczu — nazwy bywają wielowyrazowe."""
        for idx, token in enumerate(tokens):
            if any(token.startswith(trigger) for trigger in triggers):
                tail = [t for t in tokens[idx + 1:] if t not in STOPWORDS]
                return " ".join(tail) if tail else None
        return None
