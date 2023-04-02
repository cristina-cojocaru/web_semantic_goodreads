from scrapy import Request
import logging
import scrapy
import json
from collections import defaultdict

from goodreads.items import GoodreadsItemLoader, GoodreadsItem


class GoodreadsScraper(scrapy.Spider):
    name = 'goodreads'
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 20,
        'DOWNLOAD_DELAY': 1
    }
    allowed_domains = ['goodreads.com']

    def __init__(self):
        self.start_urls = ['https://www.goodreads.com/genres/list']
        self.home_page = 'https://www.goodreads.com'
        self.headers = {'Accept': 'text/html,application/xhtml+xml,'
                                  'application/xml;q=0.9,image/avif,image/webp,'
                                  'image/apng,*/*;q=0.8,application/'
                                  'signed-exchange;v=b3;q=0.7',
                        'Accept-Language': 'ro-RO,ro;q=0.9,ja-JP;q=0.8,ja;'
                                           'q=0.7,en-GB;q=0.6,en;q=0.5,en-US;'
                                           'q=0.4,de;q=0.3'
                        }

    def start_requests(self):
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
                          callback=self.parse_book,
                          headers=self.headers)

    def parse_book(self, response):
        loader = GoodreadsItemLoader(item=GoodreadsItem(), response=response)
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
        try:
            isbn = product_data['isbn']
        except KeyError:
            logging.info(f'Could not find isbn for {response.url}, dropping it')
            return
        loader.add_value('isbn', isbn)

        authors = [author['name'] for author in product_data['author']
                   if author['name'] != 'Unknown']
        loader.add_value('authors', authors)

        try:
            no_pages = product_data['numberOfPages']
        except KeyError:
            no_pages = None
        loader.add_value('pages', no_pages)

        try:
            avg_rating = product_data['aggregateRating']
        except KeyError:
            avg_rating = 0
        else:
            avg_rating = avg_rating['ratingValue']
        loader.add_value('avg_rating', avg_rating)

        try:
            rating_count = product_data['aggregateRating']['ratingCount']
        except KeyError:
            rating_count = 0
        loader.add_value('number_of_reviews', rating_count)

        languages = product_data.get('inLanguage')
        languages = languages if languages else ['English']
        loader.add_value('languages', languages)

        book_format = product_data['bookFormat']
        loader.add_value('book_format', book_format)

        reviews_script = response.xpath(
            "//script[@id='__NEXT_DATA__']/text()"
        ).extract_first()
        reviews_data = json.loads(reviews_script)
        reviews_data = reviews_data['props']['pageProps']['apolloState']
        user_keys = [key for key in reviews_data.keys() if
                     'user' in key.lower()]
        loader.add_value('reviewers', user_keys)

        reviews_keys = {reviews_data[key]['creator']['__ref']: key for key in
                        reviews_data.keys() if 'review:' in key.lower()}

        reviews_dict = defaultdict(dict)

        for user_key in user_keys:
            if user_key in list(reviews_keys.keys()):
                user_name = reviews_data[user_key]['name']
                reviews_dict[user_key]['user_name'] = user_name
                user_review = reviews_data[reviews_keys[user_key]]['text']
                user_rating = reviews_data[reviews_keys[user_key]]['rating']
                user_review_likes = reviews_data[reviews_keys[user_key]]['likeCount']
                reviews_dict[user_key]['user_review'] = user_review
                reviews_dict[user_key]['user_rating'] = user_rating
                reviews_dict[user_key]['user_review_likes'] = user_review_likes

        loader.add_value('reviews', reviews_dict)

        goodreads_item = loader.load_item()
        yield goodreads_item

