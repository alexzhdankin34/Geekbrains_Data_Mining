# -*- coding: utf-8 -*-
import scrapy
import datetime


class HabrBlogSpider(scrapy.Spider):
    name = 'habr_blog'
    allowed_domains = ['habr.com']
    start_urls = ['https://habr.com/ru/top/weekly/']

    def parse(self, response):

        pagination_urls = response.xpath("//a[contains(@class, 'toggle-menu__item-link toggle-menu__item-link_pagination')]/@href").extract()
        for itm in pagination_urls:
            yield response.follow(f'https://habr.com{itm}', callback=self.parse)

        for post_url in (response.xpath ("//a[contains(@class, 'post__title_link')]/@href").extract()):
            yield response.follow(post_url, callback=self.post_parse)


    def post_parse (self, response):

        tags_names = response.xpath("//ul[contains(@class, 'inline-list inline-list_fav-tags js-post-tags')]//a/text()").getall()
        tags_url = response.xpath("//ul[contains(@class, 'inline-list inline-list_fav-tags js-post-tags')]//a/@href").getall()
        tags=[{tags_names[i].replace(".","_"): tags_url[i]} for i in range (len(tags_names))]
        habs_names =response.xpath("//ul[contains(@class, 'inline-list inline-list_fav-tags js-post-hubs')]//a/text()").getall()
        habs_url = response.xpath("//ul[contains(@class, 'inline-list inline-list_fav-tags js-post-hubs')]//a/@href").getall()
        habs = [{habs_names[i].replace(".","_"): habs_url[i]} for i in range(len(habs_names))]
        data ={
            'url': response.url,
            'post_title': response.xpath('//h1//span[contains(@class, "post__title-text")]/text()').extract_first().replace(".","_"),
            'writer': {response.xpath('//span[contains(@class, "user-info__nickname user-info__nickname_small")]/text()').get(): response.xpath('//a[contains(@class, "post__user-info user-info")]/@href').get()},
            'publish_date': response.xpath('//span[contains(@class, "post__time")]/@data-time_published').get(),
            'comments': 0 if not response.xpath('//span[contains(@class, "post-stats__comments-count")]/text()').get() else int(response.xpath('//span[contains(@class, "post-stats__comments-count")]/text()').get()),
            'tags': tags,
            'habs': habs,
            'parsing_date': datetime.datetime.now(),
        }
        print (1)
        yield data
