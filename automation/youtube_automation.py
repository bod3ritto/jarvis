"""
automation/youtube_automation.py — Sterowanie YouTube przez Selenium.

Decyzja architektoniczna: JARVIS uruchamia WŁASNĄ, oddzielną przeglądarkę Chrome
(nie podłącza się do przeglądarki użytkownika). Żeby nie trzeba było logować się
do Google/YouTube przy każdym starcie, przeglądarka używa dedykowanego, trwałego
profilu Chrome zapisanego w data/chrome_profile/ — zaloguj się tam RAZ ręcznie,
sesja zostanie zapamiętana.
"""
import os
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import config
from utils.logger import get_logger

logger = get_logger(__name__)

CHROME_PROFILE_DIR = os.path.join(config.DATA_DIR, "chrome_profile")
ELEMENT_WAIT_TIMEOUT = 5  # sekund na pojawienie się elementu (np. przycisku skip)


class YouTubeAutomation:
    def __init__(self, browser: str = config.YOUTUBE_BROWSER):
        self.browser = browser
        self.driver = None

    def initialize(self) -> None:
        """Uruchamia dedykowaną przeglądarkę Chrome z trwałym profilem."""
        if self.driver is not None:
            logger.warning("⚠️ Przeglądarka już uruchomiona")
            return

        os.makedirs(CHROME_PROFILE_DIR, exist_ok=True)

        if self.browser != "chrome":
            logger.warning(
                f"⚠️ Silnik '{self.browser}' nieobsługiwany jeszcze — używam Chrome"
            )

        options = Options()
        options.add_argument(f"--user-data-dir={CHROME_PROFILE_DIR}")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        logger.info("🌐 Przeglądarka YouTube (Selenium) uruchomiona")

    def is_running(self) -> bool:
        return self.driver is not None

    def close(self) -> None:
        if self.driver:
            self.driver.quit()
            self.driver = None
            logger.info("🌐 Przeglądarka YouTube zamknięta")

    def open_video(self, url: str) -> None:
        """Otwiera dany URL (np. konkretne wideo lub youtube.com)."""
        if not self.is_running():
            self.initialize()
        self.driver.get(url)

    def _get_video_element(self):
        return WebDriverWait(self.driver, ELEMENT_WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )

    def skip_ad(self, skip_time: int = config.YOUTUBE_SKIP_AD_TIME) -> bool:
        """Kliknij 'Pomiń reklamę' jeśli dostępny, inaczej przewiń wideo do przodu."""
        if not self.is_running():
            logger.warning("⚠️ Przeglądarka nieuruchomiona — nie mogę pominąć reklamy")
            return False

        try:
            skip_button = WebDriverWait(self.driver, ELEMENT_WAIT_TIMEOUT).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "ytp-ad-skip-button"))
            )
            skip_button.click()
            logger.info("✅ Reklama pominięta (przycisk Skip)")
            return True
        except (TimeoutException, NoSuchElementException):
            try:
                video = self._get_video_element()
                video.send_keys(Keys.ARROW_RIGHT * skip_time)
                logger.info(f"⏭️ Brak przycisku Skip — przewinięto o {skip_time}s")
                return True
            except (TimeoutException, NoSuchElementException):
                logger.error("❌ Nie znaleziono elementu wideo")
                return False

    def play_pause(self) -> bool:
        """Toggle (spacja) — przełącza stan niezależnie od tego, co gra."""
        try:
            video = self._get_video_element()
            video.send_keys(Keys.SPACE)
            logger.info("▶️/⏸️ Play/Pause (toggle)")
            return True
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"❌ Błąd play/pause: {e}")
            return False

    def play(self) -> bool:
        """Jednoznacznie wznów odtwarzanie (nie toggle) — przez JS, sprawdza stan .paused."""
        try:
            video = self._get_video_element()
            self.driver.execute_script(
                "if (arguments[0].paused) { arguments[0].play(); }", video
            )
            logger.info("▶️ Odtwarzanie wznowione")
            return True
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"❌ Błąd odtwarzania: {e}")
            return False

    def pause(self) -> bool:
        """Jednoznacznie zatrzymaj odtwarzanie (nie toggle) — przez JS, sprawdza stan .paused."""
        try:
            video = self._get_video_element()
            self.driver.execute_script(
                "if (!arguments[0].paused) { arguments[0].pause(); }", video
            )
            logger.info("⏸️ Odtwarzanie zatrzymane")
            return True
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"❌ Błąd pauzy: {e}")
            return False

    def next_video(self) -> bool:
        """Następne wideo (działa tylko w kontekście playlisty/kolejki)."""
        try:
            next_btn = WebDriverWait(self.driver, ELEMENT_WAIT_TIMEOUT).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "ytp-next-button"))
            )
            next_btn.click()
            logger.info("⏭️ Następne wideo")
            return True
        except (TimeoutException, NoSuchElementException):
            logger.warning("⚠️ Brak przycisku 'następne' (poza playlistą?)")
            return False

    def previous_video(self) -> bool:
        """Cofnij do poprzedniej strony w historii przeglądarki (YouTube nie ma natywnego 'previous')."""
        try:
            self.driver.back()
            logger.info("⏪ Cofnięto do poprzedniej strony")
            return True
        except Exception as e:
            logger.error(f"❌ Błąd przy cofaniu: {e}")
            return False

    def fullscreen(self) -> bool:
        try:
            video = self._get_video_element()
            video.send_keys("f")
            logger.info("🖥️ Pełny ekran")
            return True
        except (TimeoutException, NoSuchElementException) as e:
            logger.error(f"❌ Błąd pełnego ekranu: {e}")
            return False
