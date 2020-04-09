# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from blogparse.items import ZillowItem
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


class ZillowSpider(scrapy.Spider):
    name = 'zillow'
    allowed_domains = ['www.zillow.com']
    start_urls = ['https://www.zillow.com/San-Francisco-ca/']

    browser=webdriver.Firefox()

    def parse(self, response):

         for pag_url in response.xpath('//nav[@aria-label="Pagination"]/ul/li/a/@href'):
             yield response.follow(pag_url, callback=self.parse)
         for ads_url in response.xpath('//ul[contains(@class, "photo-cards_short")]/li/article/div[@class="list-card-info"]/a/@href'):
             yield response.follow(ads_url, callback=self.ads_parse)

    def ads_parse(self, response):
        item = ItemLoader(ZillowItem(), response)
        self.browser.get(response.url)
        media_col = self.browser.find_element_by_css_selector('.ds-media-col')
        photo_pic_len = len(
            self.browser.find_elements_by_xpath('//ul[@class="media-stream"]/li/picture/source[@type="image/jpeg"]')
        )
        while True:
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            media_col.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)
            tmp = len(
                self.browser.find_elements_by_xpath('//ul[@class="media-stream"]/li/picture/source[@type="image/jpeg"]')
            )
            if tmp == photo_pic_len:
                break
            photo_pic_len=tmp
        images = [itm.get_attribute('srcset').split (' ')[-2] for itm in self.browser.find_elements_by_xpath('//ul[@class="media-stream"]/li/picture/source[@type="image/jpeg"]')]
        tmp =  response.xpath('//h1[@class = "ds-address-container"]//span/text()').getall()
        item.add_value('photos',images )
        item.add_value('url', response.url)
        item.add_value ('price', response.xpath('//span[@class="ds-value"]/text()').get ())
        item.add_value('adress', f'{tmp[0]} {tmp[2]}')
        item.add_value ('sqft',response.xpath('//span[@class = "ds-bed-bath-living-area"]/span/text()').getall()[-3])
        yield item.load_item()
