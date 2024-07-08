from __future__ import annotations

from pathlib import Path

import pytest
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import reflex as rx
from reflex.testing import AppHarness, WebDriver
from reflex_local_auth import LocalUser


@pytest.fixture(scope="session")
def form_designer_app():
    with AppHarness.create(root=Path(__file__).parent.parent) as harness:
        yield harness


@pytest.fixture(scope="session")
def driver(form_designer_app: AppHarness) -> WebDriver:
    driver = form_designer_app.frontend()
    return driver


TEST_USER = "test_user"
TEST_PASSWORD = "foobarbaz43"


@pytest.fixture()
def test_user() -> tuple[str, str]:
    with rx.session() as session:
        test_user = session.exec(
            LocalUser.select().where(LocalUser.username == TEST_USER)
        ).one_or_none()
        if test_user is None:
            new_user = LocalUser()  # type: ignore
            new_user.username = TEST_USER
            new_user.password_hash = LocalUser.hash_password(TEST_PASSWORD)
            new_user.enabled = True
            session.add(new_user)
            session.commit()
    return TEST_USER, TEST_PASSWORD


@pytest.fixture(scope="session")
def wait_clickable(driver: WebDriver):
    def _wait_clickable(selector):
        return WebDriverWait(driver, 10).until(EC.element_to_be_clickable(selector))

    return _wait_clickable


@pytest.fixture(scope="session")
def wait_clickable_xpath(driver: WebDriver):
    def _wait_clickable_xpath(xpath):
        return WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )

    return _wait_clickable_xpath


@pytest.fixture(scope="session")
def wait_url_to_be(driver: WebDriver):
    def _wait_url_to_be(url):
        return WebDriverWait(driver, 10).until(EC.url_to_be(url))

    return _wait_url_to_be


@pytest.fixture(scope="session")
def wait_url_matches(driver: WebDriver):
    def _wait_url_matches(url):
        return WebDriverWait(driver, 10).until(EC.url_matches(url))

    return _wait_url_matches


@pytest.fixture(scope="session")
def wait_presence(driver: WebDriver):
    def _wait_presence(selector):
        return WebDriverWait(driver, 10).until(EC.presence_of_element_located(selector))

    return _wait_presence


@pytest.fixture(scope="session")
def wait_presence_xpath(driver: WebDriver):
    def _wait_presence_xpath(xpath):
        return WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

    return _wait_presence_xpath
