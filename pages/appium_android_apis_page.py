import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from appium.webdriver.common.appiumby import AppiumBy

class AppiumApiPage:
    PACKAGE = "io.appium.android.apis"

    def __init__(self, driver):
        self.driver = driver

    def current_package(self) -> str:
        return self.driver.current_package

    def click_by_accessibility(self, name: str):
        self.driver.find_element (
            AppiumBy.ACCESSIBILITY_ID,
            name
        ).click ()

    def get_items_list(self) -> list [str]:
        elements = self.driver.find_elements (
            AppiumBy.ID,
            "android:id/text1"
        )
        return [el.text for el in elements] #->list[str]
        # list comprehension

        # texts = []
        # for el in elements:
        #     texts.append (el.text)
        # return texts
    # def check_frame_label(self, text):
    #
    #     title = self.driver.find_element (
    #         AppiumBy.ANDROID_UIAUTOMATOR,
    #         f'new UiSelector().text("{text}")'
    #     )
    #     assert title.is_displayed ()
    #     return True

    def check_frame_label(self, expected: str, timeout: int = 10) -> bool:
        locator = (
            AppiumBy.ANDROID_UIAUTOMATOR,
            f'new UiSelector().text("{expected}")'
        )
        try:
            el = WebDriverWait (self.driver, timeout).until (
                EC.presence_of_element_located (locator)
            )
            return expected in el.text
        except TimeoutException:
            return False

    def go_back(self):
        self.driver.back ()