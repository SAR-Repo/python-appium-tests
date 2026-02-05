import pytest
import os
from datetime import datetime
from pathlib import Path
import allure

PROJECT_ROOT = Path(__file__).parent
SCREENSHOTS_DIR = PROJECT_ROOT / "artifacts" / "screenshots"

pytest_plugins = ["tests.steps.appiumapi_steps"]

def pytest_configure(config):
    # Это Хук
    # Он вызывается:
    # 	•	один раз
    # 	•	в самом начале запуска pytest
    # 	•	до:
    # 	•	фикстур
    # 	•	тестов
    # 	•	BDD сценариев
    #
    # 👉 Идеальное место для:
    # 	•	глобальной конфигурации
    # 	•	генерации файлов
    # 	•	подготовки Allure environment
    # Run Examples:
    # ENV=local pytest --alluredir=artifacts/allure-results
    # ENV=browserstack pytest --alluredir=artifacts/allure-results

    allure_dir = config.getoption ("--alluredir")
    if not allure_dir:
        return

    env_file = Path(allure_dir) / "environment.properties"
    env_file.parent.mkdir(parents=True, exist_ok=True)

    env = os.getenv("ENV", "Def. local")

    if env == "browserstack":
        device = os.getenv ("BS_DEVICE", "Def. Google Pixel 7")
        provider = "BrowserStack"
    else:
        device = "Android Emulator"
        provider = "Local"

    os_ver = os.getenv ("BS_OS_VERSION", "Def. 13.0")
    # build = os.getenv ("GITHUB_RUN_NUMBER", "Def. local")
    build = os.getenv ("BUILD_NUMBER", "Def. local")

    env_file.write_text(
        f"Environment={env}\n"
        "Platform=Android\n"
        f"buildName={build}\n"
        f"Device={device}\n"
        f"osVersion={os_ver}\n"
        "App=ApiDemos\n"
        "Framework=Python+Appium\n"
        f"Provider={provider}\n"
    )

#нужен для работы с фикстурами
# Потому что:
# 	•	@pytest.fixture — это декоратор pytest
# 	•	без pytest Python просто не знает, что такое fixture
#
# pytest здесь нужен только для фикстур и управления жизненным циклом теста.

from appium import webdriver #webdriver — это клиент Appium.
# 	•	не управляет устройством напрямую
# 	•	отправляет HTTP-команды на Appium Server (localhost:4723)
# 	•	получает ответы и превращает их в Python-объекты
# Проще:
# webdriver = “пульт управления”,
# Appium Server = “мозг”,
# Emulator = “телефон”.

from appium.options.android import UiAutomator2Options
# Это класс с настройками сессии Android.
# Он нужен, чтобы:
# 	•	сказать Appium с каким устройством
# 	•	какое приложение
# 	•	каким драйвером Android (UiAutomator2)
# Раньше это делали через словарь desired_capabilities, сейчас — через объект options (современно и правильно).



@pytest.fixture
# Это декоратор pytest
# Что мы делаем в фикстуре driver() глобально?
# Создаём одну сессию Appium для теста
# # Это:
# 	•	запуск приложения
# 	•	подключение к эмулятору
# 	•	получение объекта driver, через который мы управляем приложением
def driver(request):
    # if os.getenv ("CI") == "true":
    #     pytest.skip ("Mobile tests are skipped on CI (no Appium/emulator).")
    env = os.getenv ("ENV", "local")

    options = UiAutomator2Options ()
    options.platform_name = "Android"

    if env == "browserstack":
        options.set_capability ("platformName", "Android")
        options.set_capability ("appium:automationName", "UiAutomator2")
        options.set_capability ("appium:app", "bs://7b0adfefe5d9ba755b2a21e3d1da38fa3436e079")

        options.set_capability ("bstack:options", {
            "userName": os.getenv ("BROWSERSTACK_USERNAME"),
            "accessKey": os.getenv ("BROWSERSTACK_ACCESS_KEY"),
            "deviceName": "Google Pixel 7",
            "osVersion": "13.0",
            "projectName": "Python Appium Tests",
            "buildName": "GitHub Actions Build",
            "sessionName": "Mobile tests",
        })

        remote_url = "https://hub-cloud.browserstack.com/wd/hub"

    else:
        options.device_name = "emulator-5554"
        options.app_package = "io.appium.android.apis"
        options.app_activity = ".ApiDemos"
        remote_url = "http://127.0.0.1:4723"


    d = webdriver.Remote(remote_url, options=options)
    #   1.	Python отправляет HTTP-запрос на Appium Server
    # 	2.	Appium Server:
    # 	•	читает options
    # 	•	подключается к эмулятору через ADB
    # 	•	запускает приложение
    # 	•	создаёт Appium session
    # 	3.	Appium возвращает sessionId
    # 	4.	Python получает объект driver
    # сохраним driver в item, чтобы hooks могли достать
    request.node._driver = d
    # ВАЖНО: сохраняем driver и session url для сылок при падении теста
    # если BrowserStack — положим session url в env/аттач
    if env == "browserstack":
        session_id = d.session_id
        bs_url = f"https://app-automate.browserstack.com/dashboard/v2/sessions/{session_id}"
        request.node._bs_session_url = bs_url

    yield d
    d.quit()

# Хук                           Когда
# pytest_runtest_setup          перед тестом
# pytest_runtest_call           во время теста
# pytest_runtest_teardown       после
# pytest_runtest_makereport     результат
# pytest_sessionstart           cтарт pytest
# pytest_sessionfinish          конец


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    # yield здесь значит:
    # 	•	«дай pytest выполнить тест»
    # 	•	потом вернись сюда с результатом

    rep = outcome.get_result()
    # rep = TestReport
    #
    # В нём лежит:
    # 	•	прошёл тест или нет
    # 	•	на каком этапе упал
    # 	•	traceback
    # Самое важное:
    # rep.failed  # True / False
    # rep.when  # "setup" (подготовка) | "call" (выполнеие) | "teardown" (конец)

    if rep.failed and rep.when in ("setup", "call"):
        driver = item.funcargs.get ("driver") or getattr (item, "_driver", None)

        bs_url = getattr (item, "_bs_session_url", None)
        if bs_url:
            allure.attach (bs_url, name = "BrowserStack session", attachment_type = allure.attachment_type.URI_LIST)

        #Тут ищем Appium driver, который был передан в тест.
        # Что есть item? item — это объект pytest для конкретного теста
        # item.funcargs -Словарь всех фикстур теста:
        # item.funcargs.get("driver") — основной способ достать driver.
        # or getattr(item, "_driver", None)
        # Запасной вариант, если:
        # •	драйвер был сохранён вручную как item._driver
        # •	(редко, но бывает в сложных BDD кейсах)

        if rep.failed and rep.when in ("setup", "call"):
            driver = item.funcargs.get ("driver")
            if not driver:
                return

            ts = datetime.now ().strftime ("%Y-%m-%d_%H-%M-%S")
            name = f"{item.name}_{rep.when}_{ts}"

            # 1) В Allure — сразу байты (самый надёжный путь)
            png_bytes = driver.get_screenshot_as_png ()
            allure.attach (
                png_bytes,
                name = name,
                attachment_type = allure.attachment_type.PNG,
            )

            # 2) Параллельно сохраним в одну папку (опционально)
            # SCREENSHOTS_DIR.mkdir (parents = True, exist_ok = True)
            # (SCREENSHOTS_DIR / f"{name}.png").write_bytes (png_bytes)