"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import requests
from bs4 import BeautifulSoup
import re
import sys
import logging
import random
import jsonpickle


base_url = "http://api.genius.com"
headers = {'Authorization': 'Bearer pK1oU0Bm61LXt1JUe-EfLAGaxGIUqrfBg3jnFHonx4Kd-AiGfq5cxV--jytXZJZJ', 'User-Agent': "CompuServe Classic/1.22"}
artist_to_lyrics = {'4' : {}, '72' : {}, '130' : {}} # Lil Wayne, Kanye West, Drake



f = open('hashmap.txt', 'r')
artist_to_lyrics = jsonpickle.decode(f.readline())

logger = logging.getLogger()

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "hackathon":
        return rapping(intent, session)
    else:
        return rapping(intent, session)

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------
 
def rapping(intent, session):
    session_attributes = {}
    should_end_session = False
    logger.info(intent['slots']['artist'])
    print(intent['slots']['artist'])
    print(intent['slots']['keyword'])

    if 'value' in intent['slots']['artist']:
        speech_output,randcount = rap_like_artist(intent['slots']['artist']['value'])
        speech_output = speech_output[0:7000]
        speech_output = "<break time=\"0.4s\"/>".join(speech_output.split("\n"))
        reprompt_text = ""
        return build_response(session_attributes, build_speechlet_response(
            "", speech_output, reprompt_text, should_end_session))
    elif 'value' in intent['slots']['keyword']:
         #calls the first function we setup about most popular song with keyword value
        speech_output = rap_from_keyword(intent['slots']['keyword']['value'])
        speech_output = speech_output[0:7000]
        speech_output = "<p><break time=\"0.4s\"/></p>".join(speech_output.split("\n"))
        reprompt_text = ""
        return build_response(session_attributes, build_speechlet_response(
            "", speech_output, reprompt_text, should_end_session))  
    else:
        speech_output = rapFreestyle()
        speech_output = speech_output[0:7000]
        speech_output = "<p></p>".join(speech_output.split("\n"))
        reprompt_text = ""
        return build_response(session_attributes, build_speechlet_response(
            "", speech_output, reprompt_text, should_end_session))  

   

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


def rapFreestyle():
    return get_lyrics(get_path_from_search('money'))
    
def rap_from_keyword(search):
    path = get_path_from_search(search)
    lyrics = get_lyrics(path)
    verses = lyrics.split('\n\n\n')
    for v in verses:
        if(v.find(search) != -1):
            return v
    return lyrics

def rap_like_artist(artist_name):
    artist_id = get_artist_id(artist_name)
    return generate_freestyle(str(artist_id))


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
    logger.info("Sys standard out")

    #logger.info(sys.stdout.encoding)
    #print(sys.stdout.encoding)
    lyrics = html.find('lyrics').get_text()
    lyrics = re.sub('\[.*\]','',lyrics)
    lyrics = re.sub('\&', 'and', lyrics)
    lyrics = re.sub('[^[0-9A-Za-z,\s\']+', '', lyrics)
    

    return lyrics


# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak><audio src=\"https://s3.amazonaws.com/alexarapforme/MLG+Air+Horn.mp3\" />" + output + "</speak>"
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
