import datetime
import gzip
import json
from enum import Enum
from peewee import *

db = MySQLDatabase('sport_betting', host='127.0.0.1', port=6603, user='root', password='12345')


class MatchDetailsExtendedIndex(Enum):
    YELLOW_CARDS = '40'
    YELLOW_RED_CARDS = '45'
    RED_CARDS = '50'
    BALL_POSSESSION = '110'
    SHOTS_ON_GOAL = '125'
    SHOTS_MISSED = '125'
    BLOCKED_SHOTS = '171'
    GOALKEEPER_SAVES = '127'
    CORNERS = '124'
    FREE_KICKS = '120'
    OFFSIDES = '123'
    FOULS = '129'
    GOAL_KICKS = '121'
    THROW_IN = '122'
    SUBSTITUTIONS = '60'
    INJURIES = '158'
    BALL_SAFE = '1030'
    BALL_SAFE_PERCENTAGE = 'ballsafepercentage'
    ATTACK = '1126'
    ATTACK_PERCENTAGE = 'attackpercentage'
    DANGEROUS_ATTACK = '1029'
    DANGEROUS_ATTACK_PERCENTAGE = 'dangerousattackpercentage'
    PENALTY_SCORE = '161'


class NikeMatch(Model):
    id_match = CharField(index=True)
    betradar_id_match = CharField(default=None, null=True, index=True)


class NikeFootballMatchSnapshot(Model):
    id_match = CharField(index=True)
    betradar_id_match = CharField(default=None, null=True, index=True)
    tournament = CharField(default=None, null=True, index=True)
    home_team = CharField(default=None, null=True, index=True)
    away_team = CharField(default=None, null=True, index=True)
    total_score = CharField(default=None, null=True)
    page_source = BlobField(default=None, null=True)
    period = CharField(default=None, null=True)
    match_time = CharField(default=None, null=True)

    match_details = BlobField(null=True, default=None)
    match_details_extended = BlobField(null=True, default=None)
    stats_match_form = BlobField(null=True, default=None)
    match_timeline_delta = BlobField(null=True, default=None)
    match_bookmaker_odds = BlobField(null=True, default=None)
    match_info = BlobField(null=True, default=None)

    timestamp = DateTimeField(default=datetime.datetime.utcnow())

    __cache_match_timeline_delta = None
    __cache_match_details_extended = None

    class Meta:
        database = db

    @property
    def data_match_details(self):
        if not self.match_details:
            return None
        return json.loads(gzip.decompress(self.match_details).decode(encoding='utf-8'))

    @property
    def data_match_details_extented(self):
        if not self.match_details_extended:
            return None

        if not self.__cache_match_details_extended:
            self.__cache_match_details_extended = json.loads(
                gzip.decompress(self.match_details_extended).decode(encoding='utf-8')
            )
        return self.__cache_match_details_extended

    @property
    def data_stats_match_form(self):
        if not self.stats_match_form:
            return None
        return json.loads(gzip.decompress(self.stats_match_form).decode(encoding='utf-8'))

    @property
    def data_match_timeline_delta(self):
        if not self.match_timeline_delta:
            return None
        if not self.__cache_match_timeline_delta:
            self.__cache_match_timeline_delta = (
                json.loads(gzip.decompress(self.match_timeline_delta).decode(encoding='utf-8'))
            )
        return self.__cache_match_timeline_delta

    @property
    def data_match_bookmaker_odds(self):
        if not self.match_bookmaker_odds:
            return None
        return json.loads(gzip.decompress(self.match_bookmaker_odds).decode(encoding='utf-8'))

    @property
    def data_match_info(self):
        if not self.match_info:
            return None
        return json.loads(gzip.decompress(self.match_info).decode(encoding='utf-8'))

    @property
    def match_period(self):
        return self.data_match_timeline_delta['doc'][0]['data']['match']['p']

    @property
    def period_time_seconds(self):
        match_data = self.data_match_timeline_delta['doc'][0]['data']['match']
        return (
            datetime.datetime.fromtimestamp(match_data['updated_uts'])
            - datetime.datetime.fromtimestamp(match_data['ptime'])

        ).total_seconds()

    @property
    def match_score(self):
        return (
            self.data_match_timeline_delta['doc'][0]['data']['match']['results']['home'],
            self.data_match_timeline_delta['doc'][0]['data']['match']['results']['away']
        )

    def match_details_extended_item(self, index: MatchDetailsExtendedIndex) -> (int, int):

        if index not in self.data_match_details_extented['doc'][0]['data']['values'][index]:
            # TODO: what return on non existing value?
            return -1, -1

        return (
            self.data_match_details_extented['doc'][0]['data']['values'][index]['value']['home'],
            self.data_match_details_extented['doc'][0]['data']['values'][index]['value']['away']
        )

    @property
    def get_match_details_extended_dna(self):
        pass


#db.connect()
try:
    db.create_tables([NikeFootballMatchSnapshot])
except Exception as e:
    print(e)
