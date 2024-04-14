import time
import re

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

#import base
#from base import Crawler

class NikeCrawler:

    _NIKE_LIVE_FOOTBALL_BASE_URL = 'https://www.nike.sk/live-stavky/futbal'
    _NIKE_LIVE_FOOTBALL_MATCH_URL = 'https://www.nike.sk/live-stavky/futbal/{}'

    def __init__(self):
        self._webdriver_options = webdriver.ChromeOptions()
        self._webdriver_options.add_argument('--headless')
        self._webdriver_options.page_load_strategy = 'none'

        self._driver = Chrome(options=self._webdriver_options)
        self._driver.implicitly_wait(5)

    def get_current_live_matches(self):
        self._driver.get(self._NIKE_LIVE_FOOTBALL_BASE_URL)
        time.sleep(2)
        page_source = self._driver.page_source
        return page_source

    def parse_current_live_matches(self, page_source):
        soup = BeautifulSoup(page_source, 'lxml')
        match_elements = soup.find_all('div', {'data-atid': re.compile(r'^Match-[0-9]+$')})
        matches = []
        for i in match_elements:
            #print(i)
            # Match-123456
            id_match = i.attrs['data-atid'].split('-')[1]
            matches.append(id_match)

        return matches

    def process_match(self, id_match):
        self._driver.get(self._NIKE_LIVE_FOOTBALL_MATCH_URL.format(id_match))
        time.sleep(1)
        page_source = self._driver.page_source

        soup = BeautifulSoup(page_source, 'lxml')

        try:
            tournament = soup.find('span', {'class': 'ellipsis c-white px-10'}).contents[0]
            home_team = soup.find('span', {'data-atid': 'scoreboard-opponent-home'}).contents[0]
            away_team = soup.find('span', {'data-atid': 'scoreboard-opponent-away'}).contents[0]
            total_score = soup.find('span', {'data-atid': 'tlv-matchDetail-totalScore'}).contents[0]
            match_timer = soup.find('div', {'data-atid': 'match-timer'})
            period = match_timer.contents[0].contents[0]
            match_time = match_timer.contents[1].contents[0]
        except:
            pass

        #data-tab-id="generalStatistics"
        try:
            statistic_button = self._driver.find_element(By.XPATH, "//button[@data-tab-id='generalStatistics']")
            statistic_button.click()

            time.sleep(1)
            main_statistics = self._driver.find_element(By.XPATH, value="//div[contains(text(), 'Hlavná štatistika')]")
            main_statistics.click()

            time.sleep(1)
            main_statistics_button = main_statistics.find_element(By.XPATH, '..')
            main_statistics_button.click()
            from selenium.webdriver.common.action_chains import ActionChains
            ActionChains(self._driver).move_to_element(main_statistics_button).click().perform()
            time.sleep(1)


            #main_statistics_2 = self._driver.find_element(By.XPATH, value="//div[contains(text(), 'Hlavná štatistika')]//..")

            #main_statistics = soup.find('button', {'class': 'infocentre-holder-with-loader-title text-extra-bold py-10 px-20 fs-14 c-black-100 bg-black-5 full-width text-left flex justify-between align-middle'})
            #main_statistics.click()
            #main_statistics_2.click()
            time.sleep(1)

            self._driver.get_screenshot_as_file('screenshot.png')


            #self._driver.get(self._NIKE_LIVE_FOOTBALL_MATCH_URL.format(id_match))
            #self._driver.refresh()
            page_source = self._driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')

            stats = soup.find_all('div', {'class': 'sr-general-statistics__labels'})
            stats = soup.find_all('div', {'class': 'sr-general-statistics__stats-wrapper'})

        except Exception as e:
            pass

        #self._driver.find_element(By.CLASS_NAME,)
        print('a')

