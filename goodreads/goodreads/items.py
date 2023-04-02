# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from itemloaders.processors import Identity, TakeFirst


class IntermediaryItem(Item):
    """ Base class used for defining items. """

    def __add__(self, other_item):
        """Overloading of the addition operator so we can add items and get
        items as a result contrary to {**item1, **item2}"""
        current_type = type(self)
        other_type = type(other_item)
        if not isinstance(other_item, current_type):
            raise TypeError('Added items should be of the same type. '
                            f'Got {current_type} and {other_type}')
        temp_item = {**self, **other_item}
        return current_type(temp_item)


class GoodreadsItemLoader(ItemLoader):
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
    reviews_in = Identity()


class GoodreadsItem(IntermediaryItem):
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
    reviews = Field()