import requests
import sys
import re
from bs4 import BeautifulSoup

base_url = "http://api.genius.com"
headers = {'Authorization': 'Bearer pK1oU0Bm61LXt1JUe-EfLAGaxGIUqrfBg3jnFHonx4Kd-AiGfq5cxV--jytXZJZJ', 'User-Agent': "CompuServe Classic/1.22"}

def get_artist_id(artist):
    search_url = base_url + "/search"
    data = {'q': artist}
    response = requests.get(search_url, params=data, headers=headers)
    json = response.json()
    return json['response']['hits'][0]['result']['primary_artist']['id']

def get_n_songs_by_artist(n, artist_id):
	f = open('lyrics_file.txt', 'w')
	search_url = base_url + "/artists/" + str(artist_id) + "/songs"
	data = {'sort': 'popularity', 'per_page': str(n)}
	response = requests.get(search_url, params=data, headers=headers)
	songs = response.json()['response']['songs']
	for song in songs:
		 f.write(get_lyrics(song['path']))
	f.close()

def get_lyrics(path):
    url = 'https://www.genius.com' + path
    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'}
    page = requests.get(url, headers=headers)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.find('lyrics').get_text().encode(sys.stdout.encoding, errors='replace')
    lyrics = re.sub('\[.*\]','',lyrics)
    return lyrics

if __name__ == '__main__':
    artist_id = get_artist_id('Eminem')
    get_n_songs_by_artist(10,artist_id)