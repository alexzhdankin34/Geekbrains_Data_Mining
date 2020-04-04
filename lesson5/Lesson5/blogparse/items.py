# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
import re


class BlogparseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def clean_photo (values):
    if values[:2] == '//':
        return f'http:{values}'
    elif values[:1] == '/':
        return f'https://avito.ru{values}'
    return values


def clean_data (data):
     return re.sub("^\s+|\n|\r|\s+$", '', data)


def clean_author(data):
    data['name'] = clean_data(data['name'])
    data['url'] = clean_photo(data['url'])
    return data


def clean_flat_details(data):
    values = [value for value in data[1] if value != " " and value != "\n "]
    result = {data[0][i]: values[i] for i in range(len(values))}
    return result


class AvitoRealEstateItem (scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(clean_photo))
    publish_date = scrapy.Field(input_processor=MapCompose(clean_data), output_processor=TakeFirst())
    author = scrapy.Field(input_processor=MapCompose(clean_author), output_processor=TakeFirst())
    flat_details = scrapy.Field(input_processor=clean_flat_details, output_processor=TakeFirst())
    #phone = scrapy.Field(input_processor=clean_flat_details, output_processor=TakeFirst())
