import time
from typing import Any, Optional

from selenium import webdriver  # type: ignore
from selenium.common.exceptions import TimeoutException  # type: ignore
from selenium.webdriver.chrome.options import Options  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore
from selenium.webdriver.support import expected_conditions as EC  # type: ignore
from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
from utils import dragons, get_custom_logger


class WebAutomation:
    def __init__(self):
        self.driver = self._setup_driver()

    def _setup_driver(self, is_headless: Optional[bool] = False) -> webdriver:
        options = Options()
        if is_headless:
            options.add_argument("--headless")

        driver = webdriver.Chrome(options=options)
        return driver

    def _safe_get(self, url: str, elements: list[dict[str, Any]], timeout: int = 60) -> None:
        self.driver.get(url)
        for element in elements:
            try:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((element["by"], element["tag"]))
                )
            except TimeoutException:
                raise Exception(f"Element with {element['by']}='{element['tag']}' not found within {timeout} seconds.")

    def _login(self):
        self._safe_get(
            "https://www.korail.com/ticket/login",
            [
                {"by": By.ID, "tag": "id"},
                {"by": By.ID, "tag": "password"},
                {"by": By.XPATH, "tag": "//button('로그인'"},
            ],
        )

        # Input dragons
        id_field = self.driver.find_element(By.ID, "id")
        id_field.send_keys(dragons.id)

        pwd_field = self.driver.find_element(By.ID, "password")
        pwd_field.send_keys(dragons.pwd)

        # Click login button
        login_button = self.driver.find_element(By.XPATH, "//button('로그인')")
        login_button.click()

    def __call__(self):
        self._login()

        time.sleep(5)


if __name__ == "__main__":
    logger = get_custom_logger("../../logs")

    try:
        web_automation = WebAutomation()
        web_automation()
    except Exception:
        logger.exception("An error occurred during web automation.", exc_info=True)
        time.sleep(5)
