import requests
import bs4
import json
import re

Base_URL = 'https://geekbrains.ru'
URL = 'https://geekbrains.ru/posts'
headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0',
           }


def get_next_page(soap: bs4.BeautifulSoup) -> str:
    ul = soap.find('ul', attrs={'class': 'gb__pagination'})
    a = ul.find(lambda tag: tag.name == 'a' and tag.text == '›')
    return f'{Base_URL}{a["href"]}' if a else None


def get_post_url(soap: bs4.BeautifulSoup) -> list:
    post_a =soap.select('div.post-items-wrapper div.post-item a')
    return set(f'{Base_URL}{a["href"]}' for a in post_a)


def get_page(url):

        while url:
            response = requests.get(url, headers=headers)
            soap = bs4.BeautifulSoup(response.text, 'lxml')
            yield soap
            url = get_next_page(soap)


def record_to_json(data: dict):
    filename = re.sub(r"[#%!@*/\n/\":]", "", data["url"]) + '.json'
    #filename = f'{data["url"]}.json'
    print(filename)
    with open(filename, 'w') as file:
        file.write(json.dumps(data))
        print ('записано')


def get_post_data(post_url: str) -> dict:
    template_data = {'url': '', 'image': '', 'writer': {'name': '', 'url': ''}, 'title': '', 'tags': []}
    response = requests.get(post_url, headers=headers)
    soap = bs4.BeautifulSoup(response.text, 'lxml')
    template_data['url'] = post_url
    template_data['image'] = soap.select_one ('img').get('src')
    template_data['title'] = soap.select_one('article h1.blogpost-title').text
    template_data['tags'] = {item.text: f'{Base_URL}{item["href"]}' for item in soap.select('article a.small')}
    template_data['writer']['name'] = soap.select_one('div.text-lg').text
    template_data['writer']['url'] = f'{Base_URL}{soap.select("div.col-md-5 a")[0].get("href")}'
    record_to_json(template_data)
    #print(1)
    return template_data


if __name__ == '__main__':
    tag_data = {}
    for soap in get_page(URL):
        posts = get_post_url(soap)
        post_data = [get_post_data(url) for url in posts]

        for post in post_data:

            for name, url in post['tags'].items():
                if not tag_data.get(name):
                    tag_data[name] = {'posts': []}
                tag_data[name]['url'] = url
                tag_data[name]['posts'].append(post['url'])

    with open('tags.json', 'w') as file:
        file.write(json.dumps(tag_data))
        print(1)

