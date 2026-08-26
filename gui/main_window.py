"""
gui/main_window.py — Główne okno GUI JARVIS (PyQt6).

Nasłuch mikrofonu działa w osobnym QThread (recognize() jest blokujące),
komunikacja z UI przez sygnały Qt (bezpieczne wątkowo — nie dotykamy
widgetów bezpośrednio z wątku nasłuchu).

Dwa tryby:
- "Słuchaj (jedno polecenie)" — jednorazowe rozpoznanie, wykonuje się od razu
  (świadome działanie użytkownika = nie trzeba mówić słowa aktywacyjnego).
- "Nasłuchuj ciągle" — pętla w tle; wykonuje komendę TYLKO jeśli usłyszy
  słowo aktywacyjne ("Dżarwis"), żeby nie reagować na przypadkową mowę/rozmowy.
"""
from datetime import datetime
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from commands.command_executor import CommandExecutor
from commands.command_parser import CommandParser
from voice.speech_engine import SpeechEngine
from voice.tts_engine import TTSEngine
from utils.logger import get_logger

logger = get_logger(__name__)


class ListenerThread(QThread):
    """Nasłuchuje z mikrofonu w tle. single_shot=True -> jedno rozpoznanie i koniec wątku."""

    recognized = pyqtSignal(str)
    no_speech = pyqtSignal()

    def __init__(self, speech_engine: SpeechEngine, single_shot: bool = False, parent=None):
        super().__init__(parent)
        self.speech_engine = speech_engine
        self.single_shot = single_shot
        self._running = True

    def run(self) -> None:
        while self._running:
            text = self.speech_engine.recognize()
            if not self._running:
                break
            if text:
                self.recognized.emit(text)
            else:
                self.no_speech.emit()

            if self.single_shot:
                break

    def stop(self) -> None:
        self._running = False


class JarvisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎤 JARVIS — Asystent Głosowy")
        self.setGeometry(100, 100, 900, 600)

        self.speech_engine = SpeechEngine()
        self.tts = TTSEngine()
        self.parser = CommandParser()
        self.executor = CommandExecutor(tts=self.tts)

        self.listener_thread: Optional[ListenerThread] = None

        self._setup_ui()
        self._apply_styles()

    # ---------------- UI setup ----------------
    def _setup_ui(self) -> None:
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()

        header = QLabel("🎤 JARVIS — Asystent Głosowy")
        header.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        layout.addWidget(header)

        self.status_label = QLabel("Status: Gotowy")
        self.status_label.setFont(QFont("Segoe UI", 13))
        layout.addWidget(self.status_label)

        btn_layout = QHBoxLayout()

        self.btn_listen = QPushButton("🎤 Słuchaj (jedno polecenie)")
        self.btn_listen.clicked.connect(self.start_single_listen)
        btn_layout.addWidget(self.btn_listen)

        self.btn_continuous = QPushButton("🔁 Nasłuchuj ciągle")
        self.btn_continuous.setCheckable(True)
        self.btn_continuous.clicked.connect(self.toggle_continuous_listening)
        btn_layout.addWidget(self.btn_continuous)

        self.btn_stop = QPushButton("⏹️ Stop")
        self.btn_stop.clicked.connect(self.stop_listening)
        btn_layout.addWidget(self.btn_stop)

        layout.addLayout(btn_layout)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 10))
        layout.addWidget(self.text_edit)

        main_widget.setLayout(layout)

    def _apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow { background-color: #2c3e50; }
            QLabel { color: white; }
            QPushButton {
                background-color: #3498db; color: white; border: none;
                padding: 10px; border-radius: 5px; font-size: 13px;
            }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:checked { background-color: #27ae60; }
            QTextEdit {
                background-color: #1a252f; color: #ecf0f1;
                border: 1px solid #3498db; border-radius: 5px;
            }
            """
        )

    def _log(self, text: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text_edit.append(f"[{timestamp}] {text}")

    def _set_status(self, text: str, color: str = "white") -> None:
        self.status_label.setText(f"Status: {text}")
        self.status_label.setStyleSheet(f"color: {color};")

    # ---------------- Tryb jednorazowy ----------------
    def start_single_listen(self) -> None:
        if self.listener_thread and self.listener_thread.isRunning():
            logger.warning("⚠️ Nasłuch już trwa")
            return

        self._set_status("Słucham...", "#2ecc71")
        self.listener_thread = ListenerThread(self.speech_engine, single_shot=True)
        self.listener_thread.recognized.connect(self._on_recognized_single_shot)
        self.listener_thread.no_speech.connect(self._on_no_speech)
        self.listener_thread.finished.connect(lambda: self._set_status("Gotowy", "white"))
        self.listener_thread.start()

    def _on_recognized_single_shot(self, text: str) -> None:
        self._process_recognized_text(text, require_activation=False)

    def _on_no_speech(self) -> None:
        self._log("❌ Nie usłyszałem nic / nie zrozumiałem")

    # ---------------- Tryb ciągły (wymaga słowa aktywacyjnego) ----------------
    def toggle_continuous_listening(self, checked: bool) -> None:
        if checked:
            self._set_status("Nasłuchuję ciągle (powiedz 'Dżarwis, ...')", "#2ecc71")
            self.btn_continuous.setText("🔁 Nasłuchiwanie WŁ.")
            self.listener_thread = ListenerThread(self.speech_engine, single_shot=False)
            self.listener_thread.recognized.connect(self._on_recognized_continuous)
            self.listener_thread.start()
        else:
            self.stop_listening()

    def _on_recognized_continuous(self, text: str) -> None:
        self._process_recognized_text(text, require_activation=True)

    def _process_recognized_text(self, text: str, require_activation: bool) -> None:
        self._log(f"🎤 Rozpoznano: {text}")

        if require_activation and not self.parser.was_activated(text):
            logger.info("🙉 Brak słowa aktywacyjnego — ignoruję")
            return

        command, confidence, params = self.parser.parse(text)
        self._log(f"📊 Pewność: {confidence:.0%}")

        if command:
            self._log(f"✅ Komenda: {command} {params or ''}")
            self.executor.execute(command, params)
        else:
            self._log("❌ Nie rozpoznano komendy")

    def stop_listening(self) -> None:
        if self.listener_thread:
            self.listener_thread.stop()
            self.listener_thread.wait(1000)
        self.btn_continuous.setChecked(False)
        self.btn_continuous.setText("🔁 Nasłuchuj ciągle")
        self._set_status("Zatrzymano", "#e74c3c")

    def closeEvent(self, event) -> None:
        self.stop_listening()
        self.executor.shutdown()
        event.accept()
