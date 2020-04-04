# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader
from blogparse.items import AvitoRealEstateItem





class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['www.avito.ru', 'avito.ru']
    start_urls = ['https://www.avito.ru/moskva/kvartiry']

    #def pars_phone(self, response, URL):
    #    response_for_mobile = response.follow(url=URL, headers={
    #        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'})
    #    print(1)

    def parse(self, response):
        for num in response.xpath('//div[@data-marker="pagination-button"]//span/text()'):
            try:
                tmp = int(num.get())
                yield response.follow(f'/moskva/kvartiry/?p={tmp}', callback=self.parse)
            except TypeError as e:
                continue
            except ValueError as e:
                continue

        for ads_url in response.xpath('//h3[@class = "snippet-title"]/a[@class="snippet-link"]/@href'):
           yield response.follow(ads_url, callback=self.ads_parse)



    def ads_parse(self, response):
        item = ItemLoader(AvitoRealEstateItem(), response)
        item.add_value('url', response.url)
        item.add_css('title', 'div.title-info-main h1.title-info-title span::text')
        item.add_xpath('photos', '//div[@class = "gallery-img-frame js-gallery-img-frame"]/@data-url')
        item.add_xpath('publish_date','//div[@class = "title-info-metadata-item-redesign"]/text()')
        item.add_value ('author', {'name': response.xpath('//div[@class="seller-info-name js-seller-info-name"]/a/text()').get(), 'url': response.xpath('//div[@class="seller-info-name js-seller-info-name"]/a/@href').get()})
        item.add_value('flat_details', [response.xpath('//li[@class = "item-params-list-item"]/span/text()').getall(), response.xpath('//li[@class = "item-params-list-item"]/text()').getall()])
        #item.add_value ('phone', self.pars_phone (response, response.url))
        yield item.load_item()






