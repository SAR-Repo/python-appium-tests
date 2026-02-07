from appium import webdriver
from appium.options.android import UiAutomator2Options
import allure

@allure.parent_suite("Mobile")
@allure.suite("Manual")
@allure.sub_suite("3")
def test_open_settings():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = "emulator-5554"
    options.app_package = "com.android.settings"
    options.app_activity = ".Settings"

    driver = webdriver.Remote(
        command_executor="http://127.0.0.1:4723",
        options=options
    )

    print("App opened")
    driver.quit()