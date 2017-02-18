import requests
import sys
import re
from bs4 import BeautifulSoup

def get_path_from_search(search_param):
    base_url = "http://api.genius.com"
    headers = {'Authorization': 'Bearer pK1oU0Bm61LXt1JUe-EfLAGaxGIUqrfBg3jnFHonx4Kd-AiGfq5cxV--jytXZJZJ', 'User-Agent': "CompuServe Classic/1.22"}
    search_url = base_url + "/search"
    data = {'q': search_param}
    response = requests.get(search_url, params=data, headers=headers)
    json = response.json()
    return json['response']['hits'][0]['result']['path']

def get_lyrics(path):
    url = 'https://www.genius.com' + path
    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'}
    page = requests.get(url, headers=headers)
    html = BeautifulSoup(page.text, 'html.parser')
    body = html.find('body', class_='full_browser_heigh_body snarly')
    [h.extract() for h in html('script')]
    lyrics = html.find('lyrics').get_text().encode(sys.stdout.encoding, errors='replace')
    lyrics = re.sub('\[.*\]','',lyrics)
    print lyrics

if __name__ == '__main__':
    path = get_path_from_search('pineapple')
    get_lyrics(path)