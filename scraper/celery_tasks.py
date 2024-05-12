from celery import Celery
#from scraper import celeryconfig
#from scraper.nike import NikeCrawler
import celeryconfig
from nike import NikeCrawler
import os

print(os.getcwd())
app = Celery(config_source=celeryconfig.__name__)

#@app.task(bind=True)
#def find_live_matches(self, ):
#    scraper = NikeCrawler()
#    page_source = scraper.get_current_live_matches()
#    live_matches = scraper.parse_current_live_matches(page_source)
#
#    for id_match in live_matches:
#        match_scraper = NikeCrawler()
#        match_scraper.process_match(id_match)

@app.task(bind=True)
def process_match(self, id_match):
    match_scraper = NikeCrawler()
    match_scraper.process_match(id_match)


if __name__ == '__main__':
    args = ['worker', '--loglevel=INFO']
    app.worker_main(argv=args)
