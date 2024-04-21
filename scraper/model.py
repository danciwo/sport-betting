import datetime
from peewee import *
import pymysql

db = MySQLDatabase('sport_betting', host='127.0.0.1', port=6603, user='root', password='12345')


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


#db.connect()
try:
    db.create_tables([NikeFootballMatchSnapshot])
except Exception as e:
    print(e)
