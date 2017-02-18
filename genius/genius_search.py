import requests
from bs4 import BeautifulSoup

def get_path_from_search(search_param):
    base_url = "http://api.genius.com"
    headers = {'Authorization': 'Bearer pK1oU0Bm61LXt1JUe-EfLAGaxGIUqrfBg3jnFHonx4Kd-AiGfq5cxV--jytXZJZJ', 'User-Agent': "CompuServe Classic/1.22"}

    #search_url = base_url + "/artists/1/songs"
    search_url = base_url + "/search"
    data = {'q': search_param}

    response = requests.get(search_url, params=data, headers=headers)
    json = response.json()
    return json['response']['hits'][0]['result']['path']

def get_lyrics(path):
    url = 'https://www.genius.com/' + path
    page = requests.get(url)
    html = BeautifulSoup(page.text, "html5lib")
    [h.extract() for h in html('script')]
    lyrics = html.find('div', class_='song_body-lyrics')
    print lyrics

if __name__ == '__main__':
    path = get_path_from_search('i was a little bit taller')
    get_lyrics(path)