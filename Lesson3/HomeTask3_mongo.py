import requests
import bs4
import time
from pymongo import MongoClient

headers = {'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0'}
URL = 'https://habr.com/ru/top/weekly/'
BASE_URL = 'https://habr.com'



def get_next_page (soap):
     ul=soap.find('ul', attrs={'class': 'arrows-pagination'})
     a = ul.find(lambda tag: tag.name == 'a' and tag['id'] == 'next_page')
     return f'{BASE_URL}{a["href"]}' if a else None


def get_post_url(soap: bs4.BeautifulSoup) -> set:
    post_a = soap.find_all('a', attrs={'class': 'post__title_link'})
    return set(a["href"] for a in post_a)


def get_page(url):
    while url:
        print(url)
        time.sleep(2)
        response = requests.get(url, headers=headers)
        soap = bs4.BeautifulSoup(response.text, 'lxml')
        yield soap
        url = get_next_page(soap)


def clean_comments (list_of_comments):
    dict = {}
    for comment in list_of_comments:
        try:
            comment.select_one('a').get('data-user-login')
        except AttributeError:
            list_of_comments.remove(comment)
    return list_of_comments



def get_post_data(post_url: str) -> dict:
    template_data = {'url': '',
                     'title': '',
                     'comments': int,
                     'timing': {'date': '', 'time': ''},
                     'writer': {'name': '',
                                'url': ''},
                     'commented_by': {}
                     }
    response = requests.get(post_url, headers=headers)
    soap = bs4.BeautifulSoup(response.text, 'lxml')

    template_data['url'] = post_url
    template_data['title'] = soap.select_one('.post__title-text').text
    template_data['comments'] = 0 if not soap.select_one('.post-stats__comments-count') else int(soap.select_one('.post-stats__comments-count').text)
    template_data['timing'] = {'ISO_format': soap.select_one(".post__time").get ("data-time_published"), 'date': soap.select_one('.post__time').text}
    template_data['writer']['name'] = soap.select_one('.post__user-info > span:nth-child(2)').text
    template_data['writer']['url'] = soap.select_one('.post__user-info')['href']
    comments = soap.find_all('div', attrs={'class': 'comment'})
    comments = clean_comments(comments)
    template_data['commented_by'] = {itm.select_one('a').get('data-user-login'): itm.select_one('a').get('href') for itm in comments}
    return template_data


if __name__ == '__main__':
    client = MongoClient('mongodb://localhost:27017/')
    db = client['habr_blog']


    for soap in get_page(URL):
        time.sleep(3)
        posts =get_post_url(soap)
        data = [get_post_data(url) for url in posts]
        db['posts'].insert_many(data)





