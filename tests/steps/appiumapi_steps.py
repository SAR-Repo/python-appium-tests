from pytest_bdd import given, then, parsers
from pages.appium_android_apis_page import AppiumApiPage

@given("app is opened")
def app_opened(driver):
    return AppiumApiPage(driver)

@then(parsers.parse('package should be "{pkg}"'))
def package_should_be(driver, pkg):
    page = AppiumApiPage(driver)
    assert page.current_package() == pkg

@then("menu is not empty")
def menu_not_empty(driver):
    page = AppiumApiPage(driver)
    assert len(page.get_items_list()) > 0