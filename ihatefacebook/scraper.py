import smtplib
from email.message import Message
from os.path import isfile
from json.decoder import JSONDecodeError

import keyring
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from ihatefacebook.logger import Logger
from ihatefacebook.facebook.event import FacebookEvent
from ihatefacebook.paths import *
from ihatefacebook import helpers as helpers
from ihatefacebook import messages as messages


LOGGER = Logger()


def read_configs():
    """
    Reads the file ~/Library/Application Support/com.hot3eed.ihatefacebook/configs.json
    Reports an error and exits the script if an exception happens or a config is missing.

    :return: dict of configs
    """
    try:
        configs = helpers.read_json(CONFIG_F_PATH)
        if type(configs) is dict:
            legal_configs = ["smtp.host", "smtp.port", "user.email"]
            for config in legal_configs:
                if config not in configs:
                    LOGGER.log_error("ERROR: Config %s isn't set." % config)
            return configs
        elif type(configs) is bool:
            LOGGER.log_error(messages.NO_CONFIGS)
    except JSONDecodeError:
        LOGGER.log_error(messages.CORRUPTED_CONFIG_F_ERR)
    except Exception as ex:
        LOGGER.log_error('ERROR: %s' % ex)


def read_pages():
    """
    Reads the file ~/Library/Application Support/com.hot3eed.ihatefacebook/pages.json
    Reports and error and exits the script if an exception occurs.

    :return: list of pages
    """
    try:
        pages = helpers.read_json(PAGES_F_PATH)
        if type(pages) is bool:
            LOGGER.log_error(messages.NO_PAGES)
        else:
            return pages
    except JSONDecodeError:
        LOGGER.log_error(messages.CORRUPTED_PAGES_F_ERR)
    except Exception as ex:
        LOGGER.log_error('ERROR: %s' % ex)


def read_user_pass(email):
    """
    Reads the user saved password in the keychain.
    Reports an error and exists if no password is found or an exception occurs.

    :param email: User email that the password was saved with.
    :return: User password.
    """
    try:
        return keyring.get_password(SERVICE_ID, email)
    except Exception as err:
        LOGGER.log_error("ERROR: %s" % err)


def get_newest_events(driver, page_id):
    """
    Get the newest events of a Facebook page, after comparing them with local cache, if it exists.

    :param driver: The Selenium WebDriver to load the page.
    :param page_id: Facebook ID of the page.
    :return: list of the newest events
    """
    cache_f_path = '%s/%s.html' % (CACHE_DIR, page_id)
    page_url = 'https://facebook.com/pg/%s/events' % page_id

    try:
        if isfile(cache_f_path):
            driver.get('file://' + cache_f_path)
            cached_events = FacebookEvent.extract_upcoming_events(driver)
            driver.get(page_url)
            upcoming_events = FacebookEvent.extract_upcoming_events(driver)
            newest_events = helpers.get_complement_items(upcoming_events, cached_events)
        else:
            driver.get(page_url)
            newest_events = FacebookEvent.extract_upcoming_events(driver)
        return newest_events
    except NoSuchElementException:
        return list()
    except Exception as ex:
        LOGGER.log_error("ERROR: %s" % ex)


def save_cache(driver, page_id):
    """
    Save a local copy of the page's HTML. For later retrieval.

    :param driver: The Selenium WebDriver object which has just sent a get(page_url) request.
    :param page_id: ID of page whose cache file will be saved.
    """
    cache_html = driver.find_element_by_tag_name('html').get_attribute('innerHTML')
    cache_f_path = '%s/%s.html' % (CACHE_DIR, page_id)
    with open(cache_f_path, 'w') as cache_file:
        cache_file.write(cache_html)


def send_events_mail(server, user_email, page_title, events):
    """
    Send an email with the newest events of a Facebook page.

    :param server: SMTP server to send the emails with.
    :param user_email: User's email.
    :param page_title: Title of the page.
    :param events: List of FacebookEvent objects.
    """
    subject = "New event(s) from %s" % page_title
    body = ""
    for event in events:
        body += "•%s, %s, %s\n" % (event.title, event.date, event.daytime)

    message = Message()
    message.add_header('Subject', subject)
    message.set_payload(body)
    mail = message.as_string().encode('UTF-8')

    try:
        server.sendmail(user_email, user_email, mail)
    except Exception as ex:
        LOGGER.log_error("ERROR: %s" % ex)
        server.quit()


def main(**kwargs):
    if 'log_to_stdout' in kwargs:
        LOGGER.log_to_stdout = kwargs['log_to_stdout']

    helpers.cmk_dir(CACHE_DIR)

    pages = read_pages()

    configs = read_configs()
    smtp_host = configs['smtp.host']
    smtp_port = configs['smtp.port']

    smtp_server = smtplib.SMTP(smtp_host, smtp_port)
    smtp_server.starttls()

    user_email = configs['user.email']
    user_pass = read_user_pass(user_email)

    try:
        smtp_server.login(user_email, user_pass)
    except Exception as ex:
        LOGGER.log_error("ERROR: %s" % ex)

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_experimental_option("prefs", {'profile.managed_default_content_settings.images': 2})
    driver = webdriver.Chrome(options=options, executable_path='/usr/local/bin/chromedriver')

    for page in pages:
        newest_events = get_newest_events(driver, page['id'])
        if len(newest_events) == 0:
            continue
        send_events_mail(smtp_server, user_email, page['title'], newest_events)
        save_cache(driver, page['id'])

    driver.quit()
    smtp_server.quit()


if __name__ == '__main__':
    main(log_to_stdout=True)
