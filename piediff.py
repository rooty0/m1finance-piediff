import yaml
import json
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from pprint import pprint
from time import sleep
from deepdiff import DeepDiff
from pygments import highlight, lexers, formatters
wait_for_slices_current_content = None

config_handler = open('config.yaml', 'r')
config = yaml.safe_load(config_handler)

driver = webdriver.Chrome(config['SELENIUM_DRIVER_PATH'])
driver.get("https://dashboard.m1finance.com/d/invest/portfolio")
driver.execute_script(
    "window.sessionStorage.setItem(arguments[0], arguments[1]);",
    "m1_finance_auth.refreshToken",
    config['REFRESH_TOKEN'],
)
driver.execute_script(
    "window.sessionStorage.setItem(arguments[0], arguments[1]);",
    "m1_finance_auth.accessToken",
    config['ACCESS_TOKEN'],
)


def wait_for_slices_set(xpath):
    """
    Run this function before go to another page or back to previous page
    :param xpath: xpath lol
    :return:
    """
    global wait_for_slices_current_content
    try:
        wait_for_slices_current_content = driver.find_element_by_xpath(xpath).id
    except exceptions.NoSuchElementException:
        pass


def wait_for_slices_sync(xpath, stupid_wait=0):
    global wait_for_slices_current_content

    try:
        while wait_for_slices_current_content == driver.find_element_by_xpath(xpath).id:
            sleep(0.5)
    except exceptions.NoSuchElementException:
        pass

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (
                By.XPATH,
                xpath
            )
        ))
        WebDriverWait(driver, 10).until(lambda dr: dr.execute_script('return document.readyState') == 'complete')
    except exceptions.TimeoutException:
        driver.quit()
        raise

    # This is ugly fix for the case when slices comes NOT all together but slice by slice
    # so we can't predict how much we should wait
    if stupid_wait:
        sleep(stupid_wait)


def generate_pie(pie_slices_path_template, option_target_pos, div_span_row_size, stupid_wait=0, click_text=None, deep=2):
    """

    :param pie_slices_path_template: xpath to access pie slices, this is a template should be good for any page
    :param option_target_pos: Position of "target" cell starting from 0
    :param div_span_row_size: Specify how many <div> or <span> tags are in a row
    :param stupid_wait: see function
    :param click_text: click link name
    :param deep: recursion count
    :return:
    """
    # Base
    if deep == 0:
        return {}

    if click_text:
        wait_for_slices_set(pie_slices_path_template)
        driver.find_element_by_xpath(
            '//*[@id="root"]/div/div//*/div/span[text()="{}"]'.format(click_text)
        ).click()

    wait_for_slices_sync(pie_slices_path_template, stupid_wait)  # should be after click

    pie = {}
    slices_data = [
        a.text for a in driver.find_elements_by_xpath(pie_slices_path_template) if a.get_attribute('color') != 'neutral06'
    ]

    for i in range(0, len(slices_data), div_span_row_size):

        child = generate_pie(
            pie_slices_path_template,
            option_target_pos,
            stupid_wait=stupid_wait,
            click_text=slices_data[i],
            div_span_row_size=div_span_row_size,
            deep=deep - 1
        )

        if child:
            pie[slices_data[i]] = {
                'target': slices_data[i + option_target_pos],
                'child': child
            }
        else:
            pie[slices_data[i]] = {
                'target': slices_data[i + option_target_pos]
            }

    if click_text:
        wait_for_slices_set(pie_slices_path_template)
        driver.execute_script("window.history.go(-1)")
        wait_for_slices_sync(pie_slices_path_template)
    return pie


driver.get(config['SHARED_PIE'])
# pprint(
#     generate_pie(
#         pie_slices_path_template=
#         '/html/body/div[2]/div/div/div[2]/div/div[2]/div[4]//div[contains(@class, "style__sliceContainer")]//span',
#         option_target_pos=1,
#         div_span_row_size=2
#     )
# )
SHARED_PIE_DICT = generate_pie(
    pie_slices_path_template=
    '/html/body/div[2]/div/div/div[2]/div/div[2]/div[4]//div[contains(@class, "style__sliceContainer")]//span',
    option_target_pos=1,
    div_span_row_size=2,
    stupid_wait=1
)

driver.get(config['MY_PIE'])
# pprint(
#     generate_pie(
#         pie_slices_path_template=
#         '//*[@id="root"]/div/div/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/a//*[self::span[@font-size="14px"] or self::div/b]',
#         option_target_pos=1,
#         div_span_row_size=2
#     )
# )
MY_SHARED_PIE_DICT = generate_pie(
    pie_slices_path_template=
    '//*[@id="root"]/div/div/div/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/a//*[self::span[@font-size="14px"] or self::div/b]',
    option_target_pos=1,
    div_span_row_size=2
)

print("Public Shared PIE:")
formatted_json = json.dumps(SHARED_PIE_DICT, sort_keys=True, indent=2)
print(highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter()))
print("My PIE:")
formatted_json = json.dumps(MY_SHARED_PIE_DICT, sort_keys=True, indent=2)
print(highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter()))
print("Difference:")
# Set verbose level to 2 in order to see the added or removed items with their values
formatted_json = json.dumps(json.loads(DeepDiff(MY_SHARED_PIE_DICT, SHARED_PIE_DICT, verbose_level=2).to_json()), sort_keys=True, indent=2)
print(highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter()))

driver.close()
