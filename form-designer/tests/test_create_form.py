from __future__ import annotations

import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from reflex.testing import AppHarness, WebDriver


ADD_FIELD_XPATH = "//*[ contains(text(), 'Add Field') ]"
SAVE_XPATH = "//*[ contains(text(), 'Save') ]"
DONE_XPATH = "//*[ contains(text(), 'Done') ]"
EDIT_OPTIONS_XPATH = "//*[ contains(text(), 'Edit Options') ]"
LABEL_INPUT_XPATH = "//div[contains(@class, 'fd-Option-Label')]/input"
PREVIEW_XPATH = "//*[ contains(text(), 'Preview') ]"
SUBMIT_XPATH = "//*[ contains(text(), 'Submit') ]"
LOGOUT_XPATH = "//*[ contains(text(), 'Logout') ]"


def test_create_form(
    form_designer_app: AppHarness,
    driver: WebDriver,
    test_user: tuple[str, str],
    wait_url_to_be,
    wait_url_matches,
    wait_clickable,
    wait_clickable_xpath,
    wait_presence,
    wait_presence_xpath,
):
    driver.get(form_designer_app.frontend_url)
    wait_url_to_be(form_designer_app.frontend_url + "/")
    wait_clickable((By.LINK_TEXT, "Create or Edit Forms")).click()
    wait_url_to_be(form_designer_app.frontend_url + "/login/")

    # Attempt to login
    wait_clickable((By.ID, "username")).send_keys(test_user[0])
    wait_clickable((By.ID, "password")).send_keys(test_user[1])
    wait_clickable((By.TAG_NAME, "button")).click()

    # Should redirect back to the edit form page
    wait_url_to_be(form_designer_app.frontend_url + "/edit/form/")

    # Type something into the form name to create it
    wait_clickable((By.NAME, "name")).send_keys("Test Form")
    wait_url_matches(form_designer_app.frontend_url + "/edit/form/[0-9]+/")

    # Add a field
    wait_clickable_xpath(ADD_FIELD_XPATH).click()
    wait_url_matches("/edit/form/[0-9]+/field/new/")
    wait_clickable((By.NAME, "prompt"))
    name_inputs = driver.find_elements(By.NAME, "name")
    assert len(name_inputs) == 2
    wait_clickable(name_inputs[-1]).send_keys("Test Field")
    wait_clickable_xpath(SAVE_XPATH).click()
    wait_url_matches("/edit/form/[0-9]+/")

    # Expect the field to show up in the and click to edit it
    wait_clickable_xpath("//*[ contains(text(), 'Test Field') ]").click()
    wait_url_matches("/edit/form/[0-9]+/field/[0-9]+/")
    wait_clickable((By.NAME, "prompt"))
    name_inputs = driver.find_elements(By.NAME, "name")
    assert len(name_inputs) == 2
    wait_clickable(name_inputs[-1]).send_keys("Rename Field")
    wait_clickable_xpath(SAVE_XPATH).click()
    wait_url_matches("/edit/form/[0-9]+/")

    # The name should be updated in the list
    wait_clickable_xpath("//*[ contains(text(), 'Rename Field') ]")

    # Add an enumerated field
    wait_clickable_xpath(ADD_FIELD_XPATH).click()
    wait_url_matches("/edit/form/[0-9]+/field/new/")
    wait_clickable((By.NAME, "prompt"))
    name_inputs = driver.find_elements(By.NAME, "name")
    assert len(name_inputs) == 2
    wait_clickable(name_inputs[-1]).send_keys("Reflex?")
    type_select = Select(wait_clickable((By.NAME, "type_")))
    type_select.select_by_visible_text("select")
    wait_clickable_xpath(EDIT_OPTIONS_XPATH).click()
    wait_clickable((By.CLASS_NAME, "rt-IconButton")).click()
    wait_clickable_xpath(LABEL_INPUT_XPATH).send_keys("Yes")
    wait_clickable((By.CLASS_NAME, "rt-IconButton")).click()
    form_designer_app._poll_for(
        lambda: len(driver.find_elements(By.XPATH, LABEL_INPUT_XPATH)) == 2
    )
    second_label = driver.find_elements(By.XPATH, LABEL_INPUT_XPATH)[-1]
    wait_clickable(second_label).send_keys("Assuredly")
    wait_clickable_xpath(DONE_XPATH).click()
    wait_clickable_xpath(SAVE_XPATH).click()
    wait_url_matches("/edit/form/[0-9]+/")

    # Click the preview button to fill out the form
    wait_clickable_xpath(PREVIEW_XPATH).click()
    WebDriverWait(driver, 10).until_not(EC.url_matches("/edit/form/[0-9]+/"))
    wait_url_matches("/form/[0-9]+/")
    form_fill_url = driver.current_url
    wait_clickable((By.NAME, "Rename Field")).send_keys("Logged in")
    type_select = Select(wait_clickable((By.NAME, "Reflex?")))
    type_select.select_by_visible_text("Assuredly")
    wait_clickable_xpath(SUBMIT_XPATH).click()
    wait_url_matches("/form/success/")
    wait_clickable((By.LINK_TEXT, "< Back")).click()
    wait_url_matches("/edit/form/[0-9]+/")

    # Log out and fill out the form again
    wait_clickable((By.CLASS_NAME, "lucide-menu")).click()
    wait_clickable_xpath(LOGOUT_XPATH).click()
    wait_clickable((By.CLASS_NAME, "lucide-menu")).click()
    WebDriverWait(driver, 10).until_not(
        EC.presence_of_element_located(
            (By.XPATH, f"//*[ contains(text(), '{test_user[0]}') ]")
        )
    )
    driver.get(form_fill_url)
    wait_url_to_be(form_fill_url)

    # Fill out the form as an anon user
    wait_clickable((By.NAME, "Rename Field")).send_keys("Not logged in")
    type_select = Select(wait_clickable((By.NAME, "Reflex?")))
    type_select.select_by_visible_text("Yes")
    wait_clickable_xpath(SUBMIT_XPATH).click()
    wait_url_matches("/form/success/")
    WebDriverWait(driver, 10).until_not(
        EC.element_to_be_clickable((By.LINK_TEXT, "< Back"))
    )

    # Log back in and check responses
    form_id = form_fill_url.strip("/").rpartition("/")[2]
    driver.get(form_designer_app.frontend_url + f"/responses/{form_id}/")
    wait_url_to_be(form_designer_app.frontend_url + "/login/")

    # Attempt to login
    wait_clickable((By.ID, "username")).send_keys(test_user[0])
    wait_clickable((By.ID, "password")).send_keys(test_user[1])
    wait_clickable((By.TAG_NAME, "button")).click()

    # Should redirect back to the responses page
    wait_url_to_be(form_designer_app.frontend_url + f"/responses/{form_id}/")

    # There should be two responses
    wait_presence((By.CLASS_NAME, "AccordionTrigger"))
    triggers = driver.find_elements(By.CLASS_NAME, "AccordionTrigger")
    assert len(triggers) == 2
    contents = driver.find_elements(By.CLASS_NAME, "AccordionContent")
    assert len(contents) == 2

    # Open the second response
    triggers[1].click()
    form_designer_app.poll_for_content(contents[1], exp_not_equal="")
    assert "\nRename Field\nNot logged in\nReflex?\nYes" in contents[1].text

    # Delete the second response
    triggers[1].find_element(By.CLASS_NAME, "rt-Button").click()

    # Open the first response
    triggers[0].click()
    form_designer_app.poll_for_content(contents[0], exp_not_equal="")
    assert "\nRename Field\nLogged in\nReflex?\nAssuredly" in contents[0].text
    triggers[0].click()

    # There should be one response now
    wait_presence((By.CLASS_NAME, "AccordionTrigger"))
    triggers = driver.find_elements(By.CLASS_NAME, "AccordionTrigger")
    assert len(triggers) == 1
