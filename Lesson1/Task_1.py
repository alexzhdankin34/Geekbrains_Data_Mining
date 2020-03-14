import requests
import json
import time
import re

URL = 'https://5ka.ru/api/v2/special_offers/'
headers = {'User-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
CAT_URL = 'https://5ka.ru/api/v2/categories/'


def x5ka(url, params):
    result = []
    while url:
        response = requests.get(url, headers=headers, params=params) if params else requests.get(url, headers=headers)
        params =None
        data = response.json()
        result.extend(data.get('results'))
        url = data.get('next')
        time.sleep(1)
    return result


def create_file_from_item(item):
    data = x5ka(URL, {'categories': item['parent_group_code']})
    filename = item['parent_group_name']
    filename = re.sub(r"[#%!@*/\n/\"]", "", filename)+'.json'
    with open(filename, 'w') as file:
        file.write(json.dumps(data))
        print(f"done: {filename}")


if __name__ == '__main__':
    categories = requests.get(CAT_URL, headers=headers).json()
    for item in categories:
        create_file_from_item(item)
    print("Готово, все файлы записаны!")

