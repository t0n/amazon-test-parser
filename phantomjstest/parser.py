#!/usr/bin/env python

from bs4 import BeautifulSoup as bs
from selenium import webdriver
import datetime
import time

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

BASE_URL = 'https://www.amazon.com'
COOKIE_DOMAIN = '.amazon.com'
HOME_URL = BASE_URL + '/'


class PhantomJSParser(object):

    site_login = None
    site_password = None
    driver = None
    driver2 = None

    def __init__(self, site_login, site_password):
        print("Initializing parser...")
        self.site_login = site_login
        self.site_password = site_password

        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 "
            "(KHTML, like Gecko) Chrome/15.0.87"
        )

        print("Starting driver...")
        self.driver = webdriver.PhantomJS(desired_capabilities=dcap)
        self.driver2 = webdriver.PhantomJS(desired_capabilities=dcap)

    def _parse_page(self, url):
        """
        :param url: URL of page to parse
        :return: BS object (not HTML text)
        """
        cookies = self.driver.get_cookies()
        print('_parse_page - cookies BEFORE get: ' + str(cookies))

        print("_parse_page - Getting URL {0}...".format(url))
        self.driver.get(url)

        self._fix_cookies(url)

        self.driver2.get(url)  # DRIVER2

        print("_parse_page - Saving page to file...")
        filename = datetime.datetime.now().strftime('%Y_%m_%d__%H_%M_%S_%f')
        text_file = open(filename + '.html', "w")
        text_file.write(self.driver2.page_source)  # DRIVER2
        text_file.close()

        self.driver2.save_screenshot(filename + '.png')  # DRIVER2

        print("_parse_page - Starting parsing...")
        html_page = bs(self.driver2.page_source, "html.parser")  # DRIVER2

        return html_page

    def _fix_cookies(self, url):
        print('_fix_cookies - fixing cookies...')
        cookies = self.driver.get_cookies()
        self.driver2.get(url)  # DRIVER2
        self.driver2.implicitly_wait(1)  # DRIVER2
        self.driver2.delete_all_cookies()  # DRIVER2
        for cookie in cookies:
            print('cookie: {0} ==> {1}'.format(cookie['name'], cookie['value']))
            new_cookie = dict()
            for k, v in cookie.items():
                print('   {0}: {1}'.format(k, v))
                # if 'domain' == k:
                #     new_cookie[k] = COOKIE_DOMAIN
                # else:
                #     new_cookie[k] = v
                new_cookie[k] = v
            if 'expiry' not in cookie:
                new_cookie['expiry'] = 1575825481
            try:
                self.driver2.add_cookie(new_cookie)  # DRIVER2
            except WebDriverException:
                print('ERROR, cannot set this cookie!')
        self.driver2.implicitly_wait(1)  # DRIVER2

    def _get_login_url(self, soup):
        login_link = soup.find(id='nav-link-accountList')
        print('_get_login_url - login_link: ' + str(login_link.attrs))

        login_page_url = login_link.attrs['href']
        print('_get_login_url - login_page_url: ' + str(login_page_url))

        return BASE_URL + login_page_url

    def _login_to_site(self, soup):

        login_element = self.driver.find_element_by_id('ap_email')
        print('_login_to_site - login_element: ' + str(login_element))

        login_element.send_keys(self.site_login)

        password_element = self.driver.find_element_by_id('ap_password')
        print('_login_to_site - password_element: ' + str(password_element))

        password_element.send_keys(self.site_password)

        # submit_button = self.driver.find_element_by_id('a-autoid-0')
        submit_button = self.driver.find_element_by_id('signInSubmit')
        print('_login_to_site - submit_button: ' + str(submit_button))

        print('_login_to_site - cookies BEFORE click: ' + str(self.driver.get_cookies()))

        print('_login_to_site - submitting form...')
        submit_button.click()

        print('_login_to_site - waiting for a page to refresh...')
        self.driver.save_screenshot(datetime.datetime.now().strftime('%Y_%m_%d__%H_%M_%S_%f') + '__wait.png')
        print('_login_to_site URL: ' + self.driver.current_url)
        time.sleep(5)
        self.driver.save_screenshot(datetime.datetime.now().strftime('%Y_%m_%d__%H_%M_%S_%f') + '__wait.png')
        print('_login_to_site URL: ' + self.driver.current_url)
        time.sleep(5)

        # Get Current URL
        current_url = self.driver.current_url
        print('_login_to_site URL: ' + current_url)

        # return self._parse_page(current_url)
        return self._parse_page(HOME_URL)

    def _do_search(self, soup, search_query):

        search_box_element = self.driver.find_element_by_id('twotabsearchtextbox')
        print('_do_search - search_box_element: ' + str(search_box_element))

        search_box_element.send_keys(search_query)

        submit_button = self.driver.find_element_by_css_selector('.nav-search-submit input')
        print('_do_search - submit_button: ' + str(submit_button))

        print('_do_search - submitting form...')
        submit_button.click()

        print('_do_search - waiting for a page to refresh...')
        self.driver.save_screenshot(datetime.datetime.now().strftime('%Y_%m_%d__%H_%M_%S_%f') + '__wait.png')
        print('_do_search URL: ' + self.driver.current_url)
        time.sleep(5)

        # Get Current URL
        current_url = self.driver.current_url
        print('_do_search URL: ' + current_url)

        return self._parse_page(current_url)

    def _parse_search_results_item(self, search_result):
        result = dict()
        print('_parse_search_results_item - search_result: ' + str(search_result))

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
        # print('_parse_search_results - results_list: ' + str(results_list))

        for search_result in results_list.findAll('li'):
            parsed_search_result = self._parse_search_results_item(search_result)
            if parsed_search_result['title']:
                results.append(parsed_search_result)

        return results

    def parse(self, search_query):

        print('parse - Starting parsing scenario...')

        main_page_soup = self._parse_page(HOME_URL)
        login_url = self._get_login_url(main_page_soup)
        login_page_soup = self._parse_page(login_url)
        after_login_page_soup = self._login_to_site(login_page_soup)
        search_results = self._do_search(after_login_page_soup, search_query)
        items = self._parse_search_results(search_results)

        print(">" * 120)
        print(">" * 120)
        print(">" * 120)
        print('parse - Parsing scenario finished!')

        print('parse - items:')

        for item in items:
            print(str(item))
