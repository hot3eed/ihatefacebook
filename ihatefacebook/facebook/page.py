import re
import sys

from selenium import webdriver


def get_page_title(page_id):
    """
    Get the title of a Facebook page. Reports an error and exits if no page was found.

    :param page_id: Facebook ID of the page
    :return:
        string of the title of the page, if found
    """
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript': 2})
    options.add_experimental_option("prefs", {'profile.managed_default_content_settings.images': 2})
    driver = webdriver.Chrome(options=options)
    url = "https://www.facebook.com/%s/" % page_id
    driver.get(url)
    try:
        title = re.search('(.+)\s-', driver.title).group(1)
        return title
    except:
        print("ERROR: Page not found.")
        sys.exit(1)
