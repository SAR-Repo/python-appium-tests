from pages.appium_android_apis_page import AppiumApiPage
import pytest
import allure

@pytest.mark.mobile
@pytest.mark.smoke
def test_appium_api_opened(driver):
    # driver.activate_app ("com.android.settings")
    # минимально: проверяем, что открылось приложение
    assert driver.current_package == "io.appium.android.apis"



@pytest.mark.mobile
@allure.title("Navigate through Accessibility and Views")
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Navigation")
@allure.story("Basic menu navigation")
# @allure.
def test_navigation_accessibility_back_views(driver):
    item_name="Accessibility"
    items_list="Accessibility Node Provider","Accessibility Node Querying","Accessibility Service","Custom View"
    page = AppiumApiPage(driver)
    page.click_by_accessibility(item_name)
    assert page.get_items_list()== list(items_list)
    for item in items_list:
        page.click_by_accessibility (item)
        assert page.check_frame_label(item_name+'//'+item)
        page.go_back()
