import logging
import random
import time
from typing import Optional

from selenium import webdriver  # type: ignore
from selenium.common.exceptions import ElementClickInterceptedException  # type: ignore
from selenium.webdriver.chrome.options import Options  # type: ignore
from selenium.webdriver.common.by import By  # type: ignore
from selenium.webdriver.support import expected_conditions as EC  # type: ignore
from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
from utils import ControlledException, dragons, get_custom_logger


class WebAutomation:
    def __init__(
        self, start_station: str, end_station: str, travel_date: str, people: int, logger: logging.Logger
    ) -> None:
        self.driver: webdriver = self._setup_driver()
        self.start_station: str = start_station
        self.end_station: str = end_station
        self.travel_date: str = travel_date
        self.people: int = people
        self.logger: logging.Logger = logger

        self.timeout: int = 60

    def _setup_driver(self, is_headless: Optional[bool] = False) -> webdriver:
        options: Options = Options()
        options.add_argument("disable-blink-features=AutomationControlled")  # 자동화 탐지 방지
        options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 자동화 표시 제거
        options.add_experimental_option("useAutomationExtension", False)  # 자동화 확장 기능 사용 안 함
        options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"  # # noqa: E501
        )

        if is_headless:
            options.add_argument("--headless")

        driver: webdriver = webdriver.Chrome(options=options)
        return driver

    def _random_sleep(self, min_seconds: int = 1, max_seconds: int = 3) -> None:
        sleep_time: float = random.uniform(min_seconds, max_seconds)
        time.sleep(sleep_time)

    def _safe_get(self, url: str) -> None:
        self._random_sleep()
        self.driver.get(url)

    def _safe_click(self, by: By, tag: str, timeout: Optional[int] = None) -> webdriver:
        timeout = self.timeout if not timeout else timeout
        self._random_sleep()
        field: webdriver = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((by, tag)))
        field.click()
        return field

    def _safe_send_keys(self, by: By, tag: str, val: str) -> None:
        element: webdriver = self._safe_click(by, tag)

        self._random_sleep()
        element.send_keys(val)

    def _login(self) -> None:
        # Get to the login page
        self._safe_get("https://www.korail.com/ticket/login")

        # Input dragons
        self._safe_send_keys(By.ID, "id", dragons.id)
        self._safe_send_keys(By.ID, "password", dragons.pwd)

        # Click login button
        self._safe_click(By.CSS_SELECTOR, ".btn_bn-depblue")

        # Wait until login is successful
        while (
            WebDriverWait(self.driver, self.timeout)
            .until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btnGoLogout")))
            .is_displayed()
        ):
            self.logger.info("Login successful.")
            break

    def _find_ticket(self):
        # Get to ticketing page
        self._safe_get("https://www.korail.com/ticket/search/general")

        # Select start/end stations
        self._safe_click(By.CSS_SELECTOR, ".start")
        self._safe_click(By.XPATH, f"//a[text()='{self.start_station}']")

        self._safe_click(By.CSS_SELECTOR, ".end")
        self._safe_click(By.XPATH, f"//a[text()='{self.end_station}']")

        # Select travel date
        self._safe_click(By.XPATH, "//label[text()='출발일']")
        while True:
            cur_ym_: str = (
                WebDriverWait(self.driver, self.timeout)
                .until(EC.presence_of_element_located((By.XPATH, "//p[@class='date']")))
                .text
            )
            if cur_ym_ == "":
                continue
            cur_ym: int = int("".join([i.strip() for i in cur_ym_.split(".")]))

            target_ym: int = int(self.travel_date.replace("-", "")[:6])
            target_dt: int = int(self.travel_date[-2:])

            if cur_ym < target_ym:
                try:
                    self._safe_click(By.CSS_SELECTOR, ".slick-arrow.slick-next")
                except ElementClickInterceptedException:
                    raise ControlledException("Provided travel date is not available to book yet.")
            elif cur_ym > target_ym:
                raise ControlledException("The travel date is in the past.")
            elif cur_ym == target_ym:
                self._safe_click(By.XPATH, f"//span[@class='day'][text()='{target_dt}']")
                break

    def __call__(self):
        # self._login()
        self._find_ticket()

        time.sleep(5)


if __name__ == "__main__":
    start_station = "수원"
    end_station = "평택"
    travel_date = "2026-02-03"
    people = 2

    logger = get_custom_logger("../../logs")

    try:
        web_automation = WebAutomation(start_station, end_station, travel_date, people, logger)
        web_automation()
    except Exception:
        logger.exception("An error occurred during web automation.", exc_info=True)
        time.sleep(5)
