# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LinkedinScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class PostItem(scrapy.Item):
    content = scrapy.Field()
   # post_url = scrapy.Field()
    owner_name = scrapy.Field()  # Company name
   # created_at = scrapy.Field()  # Post date

