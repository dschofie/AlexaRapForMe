import requests
import sys
import re
import random
import jsonpickle
from bs4 import BeautifulSoup
from boto.s3.connection import S3Connection

base_url = "http://api.genius.com"
headers = {'Authorization': 'Bearer pK1oU0Bm61LXt1JUe-EfLAGaxGIUqrfBg3jnFHonx4Kd-AiGfq5cxV--jytXZJZJ', 'User-Agent': "CompuServe Classic/1.22"}
artist_to_lyrics = {'4' : {}, '72' : {}, '130' : {}} # Lil Wayne, Kanye West, Drake

def generate_map():
	artist_id_list = artist_to_lyrics.keys()
	for artist_id in artist_id_list:
		search_url = base_url + "/artists/" + artist_id + "/songs"
		data = {'sort': 'popularity', 'per_page': '50'}
		response = requests.get(search_url, params=data, headers=headers)
		songs = response.json()['response']['songs']

		for song in songs:
			lyrics = get_lyrics(song['path'])
			lyrics = lyrics.split('\n')
			for line in lyrics:
				line = re.sub('[^[0-9A-Za-z,\s]+', '', line)
				words = line.split(" ")
				last_word = words[len(words)-1]
				if words != [''] and last_word not in artist_to_lyrics.get(artist_id).keys():
					if artist_to_lyrics[artist_id] is None:
						artist_to_lyrics[artist_id] = {last_word : line}
					else:
						artist_to_lyrics[artist_id][last_word] = line

def get_artist_id(artist):
    search_url = base_url + "/search"
    data = {'q': artist}
    response = requests.get(search_url, params=data, headers=headers)
    json = response.json()
    return json['response']['hits'][0]['result']['primary_artist']['id']

def get_lyrics(path):
    url = 'https://www.genius.com' + path
    page = requests.get(url, headers=headers)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.find('lyrics').get_text().encode(sys.stdout.encoding, errors='replace')
    lyrics = re.sub('\[.*\]','',lyrics)
    return lyrics

def get_path_from_search(search_param):
    search_url = base_url + "/search"
    data = {'q': search_param}
    response = requests.get(search_url, params=data, headers=headers)
    json = response.json()
    return json['response']['hits'][0]['result']['path']

def generate_freestyle(artist_id):
	song = ''
	artist_hash = artist_to_lyrics[artist_id]
	keys = artist_hash.keys()
	rnd = random.randint(0, len(keys)-1)
	search_key = keys[rnd]
	song += artist_hash[search_key] + '\n'
	randcount = 0

	words_seen = [search_key]

	for i in range (0,7):
		base_url = 'https://api.datamuse.com/words?rel_'
		arr = requests.get(base_url + "rhy=" + search_key).json()
		arr.extend(requests.get(base_url + "nry=" + search_key).json())

		rhyme_found = False

		for obj in arr:
			word = str(obj['word'])
			if word in artist_hash and word not in words_seen:
				song += artist_hash[word] + '\n'
				rhyme_found = True
				search_key = word
				words_seen.append(search_key)
				break

		if not rhyme_found:
			randcount = randcount + 1
			rnd = random.randint(0, len(keys)-1)
			search_key = keys[rnd]
			words_seen.append(search_key)
			song += artist_hash[search_key] + '\n'

	return (song, randcount)

def rap_from_keyword(search):
	path = get_path_from_search(search)
	lyrics = get_lyrics(path)
	verses = str.split(lyrics, '\n\n\n')
	for v in verses:
		if(str.find(v, search) != -1):
			return v

def rap_like_artist(artist_name):
	artist_id = get_artist_id(artist_name)
	return generate_freestyle(str(artist_id))


f = open('hashmap.txt', 'r')
artist_to_lyrics = jsonpickle.decode(f.readline())

if __name__ == '__main__':
	
	(song, randcount ) = rap_like_artist('Lil Wayne')
	print song
	print randcount

	print rap_from_keyword('basketball')
	"""
	generate_map()
	json = jsonpickle.encode(artist_to_lyrics)
	f = open('hashmap.txt', 'w')
	f.write(json)
	"""