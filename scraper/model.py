import datetime
import gzip
import json
from peewee import *
import pymysql

db = MySQLDatabase('sport_betting', host='127.0.0.1', port=6603, user='root', password='12345')

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
        return json.loads(gzip.decompress(self.match_details_extended).decode(encoding='utf-8'))

    @property
    def data_stats_match_form(self):
        if not self.stats_match_form:
            return None
        return json.loads(gzip.decompress(self.stats_match_form).decode(encoding='utf-8'))

    @property
    def data_match_timeline_delta(self):
        if not self.match_timeline_delta:
            return None
        return json.loads(gzip.decompress(self.match_timeline_delta).decode(encoding='utf-8'))

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

#db.connect()
try:
    db.create_tables([NikeFootballMatchSnapshot])
except Exception as e:
    print(e)
