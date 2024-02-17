from typing import Generator
from pathlib import Path

import pytest
from selenium.webdriver.common.by import By

from reflex.testing import AppHarness, WebDriver, webdriver


@pytest.fixture()
def counter_app():
    with AppHarness.create(root=Path(__file__).parent.parent) as harness:
        yield harness


def test_counter_app(counter_app: AppHarness):
    driver = counter_app.frontend()

    state_manager = counter_app.app_instance.state_manager
    assert len(counter_app.poll_for_clients()) == 1
    backend_state = list(state_manager.states.values())[0].get_substate(
        ["state", "state"]
    )

    count = driver.find_element(By.TAG_NAME, "h1")
    assert counter_app.poll_for_content(count) == "0"

    buttons = driver.find_elements(By.TAG_NAME, "button")
    assert len(buttons) == 3
    decrement, randomize, increment = buttons

    decrement.click()
    assert counter_app.poll_for_content(count, exp_not_equal="0") == "-1"
    assert backend_state.count == -1

    increment.click()
    assert counter_app.poll_for_content(count, exp_not_equal="-1") == "0"
    increment.click()
    assert counter_app.poll_for_content(count, exp_not_equal="0") == "1"
    assert backend_state.count == 1

    randomize.click()
    random_count = counter_app.poll_for_content(count, exp_not_equal="1")
    assert backend_state.count == int(random_count)
    decrement.click()
    dec_value = str(int(random_count) - 1)
    assert counter_app.poll_for_content(count, exp_not_equal=random_count) == dec_value
    increment.click()
    assert counter_app.poll_for_content(count, exp_not_equal=dec_value) == random_count
    assert count.text == random_count
