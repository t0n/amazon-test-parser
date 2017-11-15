#!/usr/bin/env python

from bs4 import BeautifulSoup as bs
from selenium import webdriver
import datetime
import logging
import os

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

BASE_URL = 'https://www.amazon.com'
COOKIE_DOMAIN = '.amazon.com'
HOME_URL = BASE_URL + '/'


# Setup a new root logging handler
while len(logging.root.handlers) > 0:
    logging.root.removeHandler(logging.root.handlers[-1])
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


class PhantomJSParser(object):

    site_login = None
    site_password = None
    driver = None

    def __init__(self, site_login, site_password):
        logger.debug("Initializing parser...")

        self.site_login = site_login
        self.site_password = site_password

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
            "(KHTML, like Gecko) Chrome/15.0.87"
        )

        logger.debug("Starting driver...")
        self.driver = webdriver.PhantomJS(desired_capabilities=dcap)

    def _make_screenshot(self):
        filename = datetime.datetime.now().strftime('%Y_%m_%d__%H_%M_%S_%f') + '.png'
        filename = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'screenshots', filename)
        logging.debug('saving screenshot to: ' + filename)
        self.driver.save_screenshot(filename)

    def _parse_page(self, url):
        """
        :param url: URL of page to parse
        :return: BS object (not HTML text)
        """
        cookies = self.driver.get_cookies()
        logger.debug('_parse_page - cookies BEFORE get: ' + str(cookies))

        logger.debug("_parse_page - Getting URL {0}...".format(url))
        self.driver.get(url)

        self._make_screenshot()

        logger.debug("_parse_page - Starting parsing...")
        html_page = bs(self.driver.page_source, "html.parser")

        return html_page

    def _get_login_url(self, soup):
        login_link = soup.find(id='nav-link-accountList')
        logger.debug('_get_login_url - login_link: ' + str(login_link.attrs))

        login_page_url = login_link.attrs['href']
        logger.debug('_get_login_url - login_page_url: ' + str(login_page_url))

        return BASE_URL + login_page_url

    def _login_to_site(self, soup):

        login_element = self.driver.find_element_by_id('ap_email')
        logger.debug('_login_to_site - login_element: ' + str(login_element))

        login_element.send_keys(self.site_login)

        password_element = self.driver.find_element_by_id('ap_password')
        logger.debug('_login_to_site - password_element: ' + str(password_element))

        password_element.send_keys(self.site_password)

        submit_button = self.driver.find_element_by_id('signInSubmit')
        logger.debug('_login_to_site - submit_button: ' + str(submit_button))

        logger.debug('_login_to_site - cookies BEFORE click: ' + str(self.driver.get_cookies()))

        logger.debug('_login_to_site - submitting form...')
        submit_button.click()

        # Get Current URL
        current_url = self.driver.current_url
        logger.debug('_login_to_site URL: ' + current_url)

        self._make_screenshot()

        return self._parse_page(HOME_URL)

    def _do_search(self, soup, search_query):

        search_box_element = self.driver.find_element_by_id('twotabsearchtextbox')
        logger.debug('_do_search - search_box_element: ' + str(search_box_element))

        search_box_element.send_keys(search_query)

        submit_button = self.driver.find_element_by_css_selector('.nav-search-submit input')
        logger.debug('_do_search - submit_button: ' + str(submit_button))

        logger.debug('_do_search - submitting form...')
        submit_button.click()

        current_url = self.driver.current_url
        logger.debug('_do_search URL: ' + current_url)

        self._make_screenshot()

        return self._parse_page(current_url)

    def _parse_search_results_item(self, search_result):
        result = dict()
        logger.debug('_parse_search_results_item - search_result: ' + str(search_result))

        # 1. Image
        image = search_result.find('img')
        result['image'] = image.attrs['src'] if image else None

        # 2. Title
        title = search_result.find('h2')
        result['title'] = title.text if title else None

        # 3. Price
        price_whole = search_result.find('span', {'class': 'sx-price-whole'})
        price_fractional = search_result.find('sup', {'class': 'sx-price-fractional'})
        result['price'] = \
            (price_whole.text if price_whole else '') + \
            '.' + \
            (price_fractional.text if price_fractional else '')

        return result

    def _parse_search_results(self, soup):
        results = []

        results_list = soup.find(id='s-results-list-atf')

        for search_result in results_list.findAll('li'):
            parsed_search_result = self._parse_search_results_item(search_result)
            if parsed_search_result['title']:
                results.append(parsed_search_result)

        return results

    def parse(self, search_query):

        logger.debug('parse - Starting parsing scenario...')

        main_page_soup = self._parse_page(HOME_URL)
        login_url = self._get_login_url(main_page_soup)
        login_page_soup = self._parse_page(login_url)
        after_login_page_soup = self._login_to_site(login_page_soup)
        search_results = self._do_search(after_login_page_soup, search_query)
        items = self._parse_search_results(search_results)

        logger.debug(">" * 120)
        logger.debug(">" * 120)
        logger.debug(">" * 120)
        logger.debug('parse - Parsing scenario finished!')

        logger.debug('parse - items:')

        for item in items:
            logger.debug(str(item))
