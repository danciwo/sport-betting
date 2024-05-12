from nike import NikeCrawler
from celery_tasks import process_match
from model import NikeFootballMatchSnapshot

def main():

    scraper = NikeCrawler()
    page_source = scraper.get_current_live_matches()
    live_matches = scraper.parse_current_live_matches(page_source)

    for id_match in live_matches[0:20]:
        process_match.apply_async(kwargs={'id_match': id_match})
        #match_scraper = NikeCrawler()
        #match_scraper.process_match(id_match)

    #with open('nike-live.thml', 'w') as file:
    #    file.write(page_source)


if __name__ == '__main__':
    main()