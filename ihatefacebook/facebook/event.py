from selenium.common.exceptions import StaleElementReferenceException


class FacebookEvent:
    def __init__(self, title, date, daytime):
        self.title = title
        self.date = date
        self.daytime = daytime

    def __eq__(self, other):
        return self.title == other.title and self.date == other.date and self.daytime == other.daytime

    @staticmethod
    def extract_upcoming_events(driver):
        """
        Extract the 'Upcoming Events' section from Events of a Facebook page. Reports an error to logs and exists the
        script if element isn't found.

        :param driver: The Selenium WebDriver.
        :raises: Whatever Exception the driver may raise.
        :return: List of upcoming events.
        """

        try:
            last_node_xpath = '//*[@id="upcoming_events_card"]/div/div[last()]'
            last_node = driver.find_element_by_xpath(last_node_xpath)
            while len(last_node.text) == 0:
                driver.execute_script("window.scrollTo(0, %s);" % last_node.location['y'])
                last_node = driver.find_element_by_xpath(last_node_xpath)
        except StaleElementReferenceException:
            pass

        nodes = driver.find_elements_by_xpath('//*[@id="upcoming_events_card"]/div/*')
        title_xpath = 'table/tbody/tr/td[2]/div/div[1]/a/span'
        date_xpath = 'table/tbody/tr/td[1]/span/*'
        daytime_xpath = 'table/tbody/tr/td[2]/div/div[2]/span[1]'
        i = 1  # Because the first div is for the big title.
        n = len(nodes)
        events = list()
        while i < n:
            node = nodes[i]
            title = node.find_element_by_xpath(title_xpath).text
            date = node.find_elements_by_xpath(date_xpath)
            date = "%s %s" % (date[0].text, date[1].text)
            daytime = node.find_element_by_xpath(daytime_xpath).text
            events.append(FacebookEvent(title, date, daytime))
            i += 1
        return events
