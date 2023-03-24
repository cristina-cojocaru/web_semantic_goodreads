from scrapy import Request
import logging
import scrapy


class GoodreadsScraper(scrapy.Spider):
    name = 'goodreads'

    def __init__(self):
        self.start_urls = ['https://www.goodreads.com/genres/list']
        self.home_page = 'https://www.goodreads.com/'

    def start_requests(self):
        print('ba')
        print(f'here with url {self.start_urls[0]}')
        for url in self.start_urls:
            yield Request(url,
                          callback=self.parse)

    def parse(self, response):
        genres = response.xpath(
            "//*[has-class('actionLinkLite')]/@href"
        ).extract()

        for genre in genres:
            yield Request(self.home_page + genre,
                          callback=self.parse_genre)
        next_page = response.xpath(
            "//*[has-class('next_page')]/@href"
        ).extract_first()
        if next_page:
            yield Request(self.home_page + next_page,
                          callback=self.parse)

    def parse_genre(self, response):
        books = response.xpath(
            "//*[has-class('coverWrapper')]//@href"
        ).extract()
        for book in books:
            book_url = self.home_page + book
            yield Request(book_url,
                          callback=self.parse_book)

    def parse_book(self, response):
        title = response.xpath(
            '//*[@data-testid="bookTitle"]/text()'
        ).extract_first()
        logging.info(f'title {title}')


# if __name__ == "__main__":
#     goodreads_scraper = GoodreadsScraper()
#     goodreads_scraper.start_requests()
