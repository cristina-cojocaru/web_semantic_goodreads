# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from itemloaders.processors import Identity, TakeFirst


class GoodreadsItem(ItemLoader):
    isbn_in = TakeFirst()
    book_title_in = TakeFirst()
    authors_in = TakeFirst()
    genres_in = Identity()
    avg_rating_in = Identity()
    pages_in = Identity()
    number_of_reviews_in = Identity()
    languages_in = Identity()
    book_format_in = Identity()
    reviewers_in = Identity()


class GoodreadsItemLoader(GoodreadsItem):
    # define the fields for your item here like:
    isbn = Field()
    book_title = Field()
    authors = Field()
    genres = Field()
    avg_rating = Field()
    pages = Field()
    number_of_reviews = Field()
    languages = Field()
    book_format = Field()
    reviewers = Field()