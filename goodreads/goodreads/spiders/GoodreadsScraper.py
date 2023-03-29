from scrapy import Request
import logging
import scrapy
import json

from goodreads.items import GoodreadsItemLoader, GoodreadsItem


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
                          callback=self.parse_book,
                          )

        more_link = response.xpath(
            "//*[has-class('moreLink')]//@href"
        ).extract_first()
        if more_link:
            yield Request(self.home_page + more_link,
                          callback=self.parse_more_genre)

    def parse_more_genre(self, response):
        books = response.xpath("//*[has-class('bookTitle')]/@href").extract()
        for book in books:
            book_url = self.home_page + book
            yield Request(book_url,
                          callback=self.parse_book)

    def parse_book(self, response):
        loader = GoodreadsItemLoader(item=GoodreadsItem(),
                                             response=response)
        title = response.xpath(
            '//*[@data-testid="bookTitle"]/text()'
        ).extract_first()
        loader.add_value('book_title', title)
        logging.info(f'title {title}')

        genres = response.xpath(
            "//*[@aria-label='Top genres for this book']//text()"
        ).extract()
        genres = [genre.strip() for genre in genres if 'Genres' not in genre and
                  'more' not in genre and genre.strip()]
        loader.add_value('genres', genres)

        product_script = response.xpath(
            "//script[@type='application/ld+json']/text()"
        ).extract_first()
        product_data = json.loads(product_script)
        isbn = product_data['isbn']
        loader.add_value('isbn', isbn)

        authors = [author['name'] for author in product_data['author']
                   if author['name'] != 'Unknown']
        loader.add_value('authors', authors)

        no_pages = product_data['numberOfPages']
        loader.add_value('pages', no_pages)

        avg_rating = product_data['aggregateRating']['ratingValue']
        loader.add_value('avg_rating', avg_rating)

        rating_count = product_data['aggregateRating']['ratingCount']
        loader.add_value('number_of_reviews', rating_count)

        languages = product_data['inLanguage']
        loader.add_value('languages', languages)

        book_format = product_data['bookFormat']
        loader.add_value('book_format', book_format)

        reviews_script = response.xpath(
            "//script[@id='__NEXT_DATA__']/text()"
        ).extract_first()
        reviews_data = json.loads(reviews_script)
        user_keys = [key for key in
                     reviews_data['props']['pageProps']['apolloState'].keys() if
                     'user' in key.lower()]
        loader.add_value('reviewers', user_keys)

        goodreads_item = loader.load_item()
        yield goodreads_item





# if __name__ == "__main__":
#     goodreads_scraper = GoodreadsScraper()
#     goodreads_scraper.start_requests()
