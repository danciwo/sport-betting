import time
import re
import json
import gzip
import datetime

#from selenium import webdriver
#from selenium.webdriver import Chrome
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup

from model import NikeFootballMatchSnapshot, NikeMatch

#import base
#from base import Crawler

BR_MATCH_DETAILS_EXTENDED = '/match_detailsextended/'
BR_MATCH_DETAILS = '/match_details/'
BR_STATS_MATCH_FORM = '/stats_match_form/'
BR_MATCH_TIMELINE_DELTA = '/match_timelinedelta/'
BR_MATCH_BOOKMAKER_ODDS = '/match_bookmakerodds/'
BR_MATCH_INFO = '/match_info/'


#class NikeFootballMatchSnapshot:
#
#    def __init__(self, id_match, betradar_id_match, tournament, home_team, away_team, total_score, period, match_time,
#                 match_details, match_details_extended, stats_match_form, match_timeline_delta, match_bookmaker_odds,
#                 match_info):
#
#        self.id_match = id_match
#        self.betradar_id_match = betradar_id_match
#        self.tournament = tournament
#        self.home_team = home_team
#        self.away_team = away_team
#        self.total_score = total_score
#        self.period = period
#        self.match_time = match_time
#
#        self.match_details = match_details
#        self.match_details_extended = match_details_extended
#        self.stats_match_form = stats_match_form
#        self.match_timeline_delta = match_timeline_delta
#        self.match_bookmaker_odds = match_bookmaker_odds
#        self.match_info = match_info


class NikeCrawler:

    _NIKE_LIVE_FOOTBALL_BASE_URL = 'https://www.nike.sk/live-stavky/futbal'
    _NIKE_LIVE_FOOTBALL_MATCH_URL = 'https://www.nike.sk/live-stavky/futbal/{}'

    def __init__(self):
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

        self._webdriver_options = webdriver.ChromeOptions()
        self._webdriver_options.add_argument('--headless')
        self._webdriver_options.add_argument("--enable-javascript")
        self._webdriver_options.page_load_strategy = 'normal'

        self._driver = webdriver.Chrome(
            options=self._webdriver_options,
            #desired_capabilities = capabilities,
        )
        self._driver.implicitly_wait(5)

    def __del__(self):
        self._driver.close()
        self._driver.quit()

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

        nike_match = None

        match_url = self._NIKE_LIVE_FOOTBALL_MATCH_URL.format(id_match)
        self._driver.get(match_url)

        try:
            cookies_button = self._driver.find_element(By.ID, 'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll')
            cookies_button.click()
            time.sleep(1)
        except:
            pass

        while(self._driver.current_url == match_url):
            page_source = self._driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')

            tournament, home_team, away_team, total_score = (None, None, None, None)

            try:
                tournament = soup.find('span', {'class': 'ellipsis c-white px-10'}).contents[0]
                home_team = soup.find('span', {'data-atid': 'scoreboard-opponent-home'}).contents[0]
                away_team = soup.find('span', {'data-atid': 'scoreboard-opponent-away'}).contents[0]
                total_score = soup.find('span', {'data-atid': 'tlv-matchDetail-totalScore'}).contents[0]
            except Exception:
                return None

            try:

                statistic_button = self._driver.find_element(By.XPATH, "//button[@data-tab-id='generalStatistics']")
                statistic_button.click()
                time.sleep(5)

                (match_details, match_details_extended, stats_match_form,
                 match_timeline_delta, match_bookmaker_odds, match_info) = (None, None, None, None, None, None)

                for request in reversed(self._driver.requests):
                    if request.response:
                        # str_data = gzip.decompress(request.response.body)
                        # data = json.loads(str_data)
                        # print(data)
                        if BR_MATCH_DETAILS in request.url:
                            match_details = request.response.body if not match_details else match_details
                        if BR_MATCH_DETAILS_EXTENDED in request.url:
                            match_details_extended = request.response.body if not match_details_extended else match_details_extended
                        if BR_MATCH_INFO in request.url:
                            match_info = request.response.body if not match_info else match_info
                        if BR_STATS_MATCH_FORM in request.url:
                            stats_match_form = request.response.body if not stats_match_form else stats_match_form
                        if BR_MATCH_BOOKMAKER_ODDS in request.url:
                            match_bookmaker_odds = request.response.body if not match_bookmaker_odds else match_bookmaker_odds
                        if BR_MATCH_TIMELINE_DELTA in request.url:
                            match_timeline_delta = request.response.body if not match_timeline_delta else match_timeline_delta

                    if (
                        match_details and match_details_extended
                        and stats_match_form and match_timeline_delta and match_bookmaker_odds
                    ):
                        break

                period, match_time, betradar_id_match = (None, None, None)
                try:
                    page_source = self._driver.page_source
                    soup = BeautifulSoup(page_source, 'lxml')

                    bets_source_tag = soup.find('div', {'data-atid': 'tlv-detail-bets'})
                    bets_source = str(bets_source_tag.contents)

                    match_timer = soup.find('div', {'data-atid': 'match-timer'})
                    period = match_timer.contents[0].contents[0]
                    match_time = match_timer.contents[1].contents[0]

                    stats = soup.find_all('div', {'data-sr-widget': 'match.generalstatistics'})
                    betradar_id_match = json.loads(stats[0].attrs['data-sr-input-props'])['matchId']
                except Exception:
                    pass

                if not betradar_id_match:
                    break

                if nike_match is None:
                    nike_match = NikeMatch(
                        id_match=id_match,
                        betradar_id_match=betradar_id_match,
                        timestamp=datetime.datetime.utcnow()
                    )
                    nike_match.save()

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
                    match_info=match_info,
                    page_source=gzip.compress(bytes(bets_source, 'utf8')),
                    timestamp=datetime.datetime.utcnow()
                )

                result.save()
                time.sleep(30)
            except Exception as e:
                pass
