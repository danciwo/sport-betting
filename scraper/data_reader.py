import gzip
import json
import pprint

from nike import NikeCrawler
from model import NikeFootballMatchSnapshot

def main():
    record: NikeFootballMatchSnapshot = NikeFootballMatchSnapshot.get(NikeFootballMatchSnapshot.id == 933)
    period = record.match_period
    time = record.period_time_seconds



    print(record)



if __name__ == '__main__':
    main()
