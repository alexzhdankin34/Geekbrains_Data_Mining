# -*- coding: utf-8 -*-
from copy import deepcopy
import scrapy
import re
import json
from urllib.parse import urljoin, urlencode


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    start_urls = ['http://instagram.com/']
    pars_users = ['cherdakerka', 'maria_shipillo',]
    variables = {"id": '',
                 "include_reel": True,
                 "fetch_mutual": False,
                 "first": 100,
                 }

    def __init__(self, logpass: tuple, **kwargs):
        self.login, self.pwd = logpass
        self.query_hash  = {'followers':'c76146de99bb02f6415203be841dd25a', 'follows':'d04b0a864b4b54837c0d870b0e77e076'}
        super().__init__(**kwargs)

    def parse(self, response):
        login_url = 'https://www.instagram.com/accounts/login/ajax/'
        csrf_token = self.fetch_csrf_token(response.text)

        yield scrapy.FormRequest(
            login_url,
            method='POST',
            callback=self.main_parse,
            formdata={'username': self.login, 'password': self.pwd},
            headers={'X-CSRFToken': csrf_token}
        )

    def main_parse (self, response):
        j_resp = json.loads(response.text)
        if j_resp.get('authenticated') == True:
            for u_name in self.pars_users:
                yield response.follow(
                    urljoin(self.start_urls[0], u_name),
                    callback=self.parse_user,
                    cb_kwargs = {'user_name': u_name}
                )


    def parse_user(self, response, user_name:str) :
        user_id = self.fetch_user_id(response.text, user_name)
        user_vars = deepcopy(self.variables)
        user_vars.update({'id': user_id})

        """сначала будем парсить followers, передав в функцию parse_followers_and_follows 
        `соответствующий tag = followed_by"""

        url=self.make_grapthql_url(user_vars, query_hash=self.query_hash['followers'])
        tag = 'followed_by'
        yield response.follow(
            url,
            callback=self.parse_followers_and_follows,
            cb_kwargs={'user_vars': user_vars, 'user_name': user_name, 'tag': tag}
        )

        """после этого будем парсить follows, передав в функцию parse_followers_and_follows 
        `соответствующий tag = follows"""
        url = self.make_grapthql_url(user_vars, query_hash=self.query_hash['follows'])
        tag = 'follow'

        yield response.follow(
            url,
            callback=self.parse_followers_and_follows,
            cb_kwargs={'user_vars': user_vars, 'user_name': user_name, 'tag':tag}
        )

    def parse_followers_and_follows (self, response, user_vars, user_name, tag):
        j_response = json.loads(response.text)
        if j_response['data']['user'][f'edge_{tag}']['page_info']['has_next_page']:
            user_vars.update({'after': j_response['data']['user'][f'edge_{tag}']['page_info']['end_cursor']})
            url = self.make_grapthql_url(user_vars, self.query_hash['followers']) if tag == 'followed_by' else self.make_grapthql_url(user_vars, self.query_hash['follows'])
            yield response.follow(
                url,
                callback=self.parse_followers_and_follows,
                cb_kwargs={'user_vars': user_vars, 'user_name': user_name}
            )

            users = j_response['data']['user'][f'edge_{tag}']['edges']
            for user in users:
                yield {'user_name': user_name, 'user_id': user_vars['id'], 'follower': user['node']} if tag =='followed_by' else {'user_name': user_name, 'user_id': user_vars['id'], 'follow': user['node']}


    def fetch_csrf_token(self, text):

        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        """Используя регулярные выражения парсит переданную строку на наличие
        `id` нужного пользователя и возвращет его."""
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')

    def make_grapthql_url (self,  user_vars, query_hash):
        return f'{self.graphql_url}query_hash={query_hash}&{urlencode(user_vars)}'

