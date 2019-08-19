# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Field, Item
from .datakeys import DataKeys


class YcombinatorItem(Item):
    job_msg = Field()
    job_id = Field()
    job_url = Field()
    position = Field()
    company_name = Field()
    job_location = Field()
