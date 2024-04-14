from scraper.nike import NikeCrawler

def main():
    scraper = NikeCrawler()
    page_source = scraper.get_current_live_matches()
    live_matches = scraper.parse_current_live_matches(page_source)

    for id_match in live_matches:
        scraper.process_match(id_match)

    #with open('nike-live.thml', 'w') as file:
    #    file.write(page_source)


if __name__ == '__main__':
    main()