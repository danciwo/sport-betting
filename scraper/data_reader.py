import gzip
import json
import pprint

from nike import NikeCrawler
from model import NikeFootballMatchSnapshot

def main():
    record = NikeFootballMatchSnapshot.get(NikeFootballMatchSnapshot.id == 622)
    pprint.pprint(record.data_match_details_extented)
    pprint.pprint(record.data_match_info)
    pprint.pprint(record.data_match_timeline_delta)
    #str_data = record.match_details.decode(encoding="utf-8")
    str_data = gzip.decompress(record.match_details)
    str = str_data.decode(encoding='utf-8')
    data = json.loads(str)
    pprint.pprint(data)


    print(record)



if __name__ == '__main__':
    main()
