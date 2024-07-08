import pytest
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import reflex as rx
from reflex.testing import AppHarness, WebDriver

from reflex_local_auth import LocalUser

REGISTER_XPATH = "//*[ contains(text(), 'Register') ]"
LOGOUT_XPATH = "//*[ contains(text(), 'Logout') ]"
TEST_USER = "test_user"
TEST_PASSWORD = "foobarbaz43"


@pytest.fixture(scope="session")
def test_user_cleaned_up():
    with rx.session() as session:
        test_user = session.exec(
            LocalUser.select().where(LocalUser.username == TEST_USER)
        ).one_or_none()
        if test_user is not None:
            session.delete(test_user)
            session.commit()


@pytest.mark.usefixtures("test_user_cleaned_up")
def test_create_user(
    form_designer_app: AppHarness,
    driver: WebDriver,
    wait_url_to_be,
    wait_clickable,
    wait_clickable_xpath,
    wait_presence_xpath,
):
    driver.switch_to.new_window("window")
    driver.get(form_designer_app.frontend_url)
    wait_url_to_be(form_designer_app.frontend_url + "/")
    wait_clickable((By.CLASS_NAME, "lucide-menu")).click()
    wait_clickable_xpath(REGISTER_XPATH).click()
    wait_url_to_be(form_designer_app.frontend_url + "/register/")
    wait_clickable((By.ID, "username")).send_keys(TEST_USER)
    wait_clickable((By.ID, "password")).send_keys(TEST_PASSWORD)

    # Register without confirming password, should fail
    wait_clickable((By.TAG_NAME, "button")).click()
    wait_presence_xpath("//*[ contains(text(), 'Passwords do not match') ]")

    # Confirm password
    wait_clickable((By.ID, "confirm_password")).send_keys(TEST_PASSWORD)
    wait_clickable((By.TAG_NAME, "button")).click()

    # Should have redirected to the login page
    wait_url_to_be(form_designer_app.frontend_url + "/login/")

    # Attempt to login
    wait_clickable((By.ID, "username")).send_keys(TEST_USER)
    wait_clickable((By.ID, "password")).send_keys("Bad")

    # Using the wrong password should show an error
    wait_clickable((By.TAG_NAME, "button")).click()
    wait_presence_xpath(
        "//*[ contains(text(), 'There was a problem logging in, please try again.') ]"
    )
    wait_clickable((By.ID, "password")).send_keys(TEST_PASSWORD)
    wait_clickable((By.TAG_NAME, "button")).click()

    # Should redirect back to the home page
    wait_url_to_be(form_designer_app.frontend_url + "/")

    # Clicking the menu now should show the user's name
    wait_clickable((By.CLASS_NAME, "lucide-menu")).click()
    wait_presence_xpath(f"//*[ contains(text(), '{TEST_USER}') ]")

    # Logout
    wait_clickable((By.XPATH, LOGOUT_XPATH)).click()
    wait_clickable((By.CLASS_NAME, "lucide-menu")).click()
    WebDriverWait(driver, 10).until_not(
        EC.presence_of_element_located(
            (By.XPATH, f"//*[ contains(text(), '{TEST_USER}') ]")
        )
    )

    # Should not be able to re-register as the same user
    driver.get(form_designer_app.frontend_url + "/register/")
    wait_clickable((By.ID, "username")).send_keys(TEST_USER)
    wait_clickable((By.ID, "password")).send_keys(TEST_PASSWORD)
    wait_clickable((By.ID, "confirm_password")).send_keys(TEST_PASSWORD)
    wait_clickable((By.TAG_NAME, "button")).click()
    wait_presence_xpath(
        f"//*[ contains(text(), 'Username {TEST_USER} is already registered. Try a different name') ]"
    )
