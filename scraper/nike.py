import time
import re
import json
import gzip

from selenium import webdriver
#from selenium.webdriver import Chrome
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup

#import base
#from base import Crawler

BR_MATCH_DETAILS_EXTENDED = '/match_detailsextended/'
BR_MATCH_DETAILS = '/match_details/'
BR_STATS_MATCH_FORM = '/stats_match_form/'
BR_MATCH_TIMELINE_DELTA = '/match_timelinedelta/'
BR_MATCH_BOOKMAKER_ODDS = '/match_bookmakerodds/'
BR_MATCH_INFO = '/match_info/'
class NikeFootballMatchSnapshot:

    def __init__(self, id_match, betradar_id_match, tournament, home_team, away_team, total_score, period, match_time,
                 match_details, match_details_extended, stats_match_form, match_timeline_delta, match_bookmaker_odds,
                 match_info):

        self.id_match = id_match
        self.betradar_id_match = betradar_id_match
        self.tournament = tournament
        self.home_team = home_team
        self.away_team = away_team
        self.total_score = total_score
        self.period = period
        self.match_time = match_time

        self.match_details = match_details
        self.match_details_extended = match_details_extended
        self.stats_match_form = stats_match_form
        self.match_timeline_delta = match_timeline_delta
        self.match_bookmaker_odds = match_bookmaker_odds
        self.match_info = match_info

class NikeCrawler:

    _NIKE_LIVE_FOOTBALL_BASE_URL = 'https://www.nike.sk/live-stavky/futbal'
    _NIKE_LIVE_FOOTBALL_MATCH_URL = 'https://www.nike.sk/live-stavky/futbal/{}'

    def __init__(self):
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

        self._webdriver_options = webdriver.ChromeOptions()
        #self._webdriver_options.add_argument('--headless')
        self._webdriver_options.add_argument("--enable-javascript")
        self._webdriver_options.page_load_strategy = 'normal'

        self._driver = webdriver.Chrome(
            options=self._webdriver_options,
            #desired_capabilities = capabilities,
        )
        self._driver.implicitly_wait(5)

    def get_current_live_matches(self):
        self._driver.get(self._NIKE_LIVE_FOOTBALL_BASE_URL)
        self._driver.maximize_window()
        self._driver.get_screenshot_as_file('test')
        page_source = self._driver.page_source
        return page_source

    def parse_current_live_matches(self, page_source):
        soup = BeautifulSoup(page_source, 'lxml')
        match_elements = soup.find_all('div', {'data-atid': re.compile(r'^Match-[0-9]+$')})
        matches = []
        for i in match_elements:
            # Match-123456
            id_match = i.attrs['data-atid'].split('-')[1]
            matches.append(id_match)

        return matches

    def process_match(self, id_match):
        self._driver.get(self._NIKE_LIVE_FOOTBALL_MATCH_URL.format(id_match))
        try:
            cookies_button = self._driver.find_element(By.ID, 'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll')
            cookies_button.click()
        except:
            pass

        page_source = self._driver.page_source
        soup = BeautifulSoup(page_source, 'lxml')

        try:
            tournament = soup.find('span', {'class': 'ellipsis c-white px-10'}).contents[0]
            home_team = soup.find('span', {'data-atid': 'scoreboard-opponent-home'}).contents[0]
            away_team = soup.find('span', {'data-atid': 'scoreboard-opponent-away'}).contents[0]
            total_score = soup.find('span', {'data-atid': 'tlv-matchDetail-totalScore'}).contents[0]
        except Exception as exc:
            pass

        try:

            statistic_button = self._driver.find_element(By.XPATH, "//button[@data-tab-id='generalStatistics']")
            statistic_button.click()

            match_details = None
            match_details_extended = None
            stats_match_form = None
            match_timeline_delta = None
            match_bookmaker_odds = None

            for request in self._driver.requests:
                if request.response:
                    # str_data = gzip.decompress(request.response.body)
                    # data = json.loads(str_data)
                    # print(data)
                    if BR_MATCH_DETAILS in request.url:
                        match_details = request.response.body
                    if BR_MATCH_DETAILS_EXTENDED in request.url:
                        match_details_extended = request.response.body
                    if BR_MATCH_INFO in request.url:
                        match_info = request.response.body
                    if BR_STATS_MATCH_FORM in request.url:
                        stats_match_form = request.response.body
                    if BR_MATCH_BOOKMAKER_ODDS in request.url:
                        match_bookmaker_odds = request.response.body
                    if BR_MATCH_TIMELINE_DELTA in request.url:
                        match_timeline_delta = request.response.body

                if (
                    match_details and match_details_extended
                    and stats_match_form and match_timeline_delta and match_bookmaker_odds
                ):
                    break

            try:
                page_source = self._driver.page_source
                soup = BeautifulSoup(page_source, 'lxml')

                match_timer = soup.find('div', {'data-atid': 'match-timer'})
                period = match_timer.contents[0].contents[0]
                match_time = match_timer.contents[1].contents[0]

                stats = soup.find_all('div', {'data-sr-widget': 'match.generalstatistics'})
                betradar_id_match = json.loads(stats[0].attrs['data-sr-input-props'])['matchId']
            except Exception as ttt:
                pass

            result = NikeFootballMatchSnapshot(
                id_match=id_match,
                betradar_id_match=betradar_id_match,
                period=period,
                tournament=tournament,
                home_team=home_team,
                away_team=away_team,
                total_score=total_score,
                match_time=match_time,
                match_details=match_details,
                match_details_extended=match_details_extended,
                stats_match_form=stats_match_form,
                match_bookmaker_odds=match_bookmaker_odds,
                match_timeline_delta=match_timeline_delta,
                match_info=match_info
            )

            match_scoreboard = soup.find('div', {'data-sr-widget': 'match.scoreboard'})
            if (match_scoreboard):
                print(match_scoreboard)

            #statistic_button = self._driver.find_element(By.XPATH, "//button[@data-tab-id='generalStatistics']")
            #statistic_button = self._driver.find_element(By.XPATH, "//button[@data-tab-id='headToHead']")
            #statistic_button.click()

            #time.sleep(5)
            #main_statistics = self._driver.find_element(By.XPATH, value="//div[contains(text(), 'Hlavná štatistika')]")
            #main_statistics.click()

            #time.sleep(1)
            #main_statistics_button = main_statistics.find_element(By.XPATH, '..')
            #main_statistics_button.click()
            #from selenium.webdriver.common.action_chains import ActionChains
            #ActionChains(self._driver).move_to_element(main_statistics_button).click().perform()
            #time.sleep(1)

            #for i in self._driver.get_log('performance'):
            #    import json
            #    message = json.loads(i['message'])
            #    try:
            #        print(message['message']['params']['request']['url'])
            #    except:
            #        pass

            #main_statistics_2 = self._driver.find_element(By.XPATH, value="//div[contains(text(), 'Hlavná štatistika')]//..")

            #main_statistics = soup.find('button', {'class': 'infocentre-holder-with-loader-title text-extra-bold py-10 px-20 fs-14 c-black-100 bg-black-5 full-width text-left flex justify-between align-middle'})
            #main_statistics.click()
            #main_statistics_2.click()
            #self._driver.switch_to.default_content()
            #time.sleep(2)

            #self._driver.execute_async_script()
            #self._driver.get_screenshot_as_file('screenshot.png')



            #self._driver.get(self._NIKE_LIVE_FOOTBALL_MATCH_URL.format(id_match))
            #self._driver.refresh()
            #page_source = self._driver.page_source
            #soup = BeautifulSoup(page_source, 'lxml')

            #stats = soup.find_all('div', {'class': 'sr-general-statistics__labels'})
            #stats = soup.find_all('div', {'class': 'sr-general-statistics__stats-wrapper'})

        except Exception as e:
            pass

