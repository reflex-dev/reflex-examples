from typing import Generator
from pathlib import Path

import pytest
from selenium.webdriver.common.by import By

from reflex.testing import AppHarness, WebDriver, webdriver


@pytest.fixture()
def counter_app():
    with AppHarness.create(root=Path(__file__).parent.parent) as harness:
        yield harness


@pytest.fixture()
def driver() -> Generator[WebDriver, None, None]:
    """Temporary until reflex ships a version that respects APP_HARNESS_HEADLESS."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


def test_counter_app(counter_app: AppHarness, driver: WebDriver):
    # Use the fixture until reflex ships a version that respects APP_HARNESS_HEADLESS.
    #driver = counter_app.frontend()
    driver.get(counter_app.frontend_url)

    state_manager = counter_app.app_instance.state_manager
    assert len(counter_app.poll_for_clients()) == 1
    backend_state = list(state_manager.states.values())[0]

    count = driver.find_element(By.TAG_NAME, "h2")
    assert counter_app.poll_for_content(count) == "0"

    buttons = driver.find_elements(By.TAG_NAME, "button")
    assert len(buttons) == 3
    decrement, randomize, increment = buttons

    decrement.click()
    assert count.text == "-1"
    assert backend_state.count == -1

    increment.click()
    increment.click()
    assert count.text == "1"
    assert backend_state.count == 1

    randomize.click()
    random_count = count.text
    assert backend_state.count == int(random_count)
    decrement.click()
    assert count.text == str(int(random_count) - 1)
    increment.click()
    assert count.text == random_count