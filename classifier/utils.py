# classifier/utils.py
import pandas as pd
import time
from pytubefix import YouTube
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
import xml.etree.ElementTree as ET

def get_video_id(url):
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ['www.youtube.com', 'youtube.com']:
        if query.path == '/watch':
            return parse_qs(query.query).get('v', [None])[0]
        elif query.path.startswith('/embed/'):
            return query.path.split('/')[2]
    return None

def fetch_title_description(url):
    try:
        yt = YouTube(url)
        return yt.title.lower(), yt.description.lower()
    except Exception:
        return "", ""

def fetch_transcript_text(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t['text'] for t in transcript]).lower()
    except (TranscriptsDisabled, NoTranscriptFound, ET.ParseError):
        return ""
    except Exception:
        return ""

def classify_content(title, description, transcript):
    music_keywords = ['music', 'song', 'track', 'remix', 'album', 'beats', 'dj', 'official music video']
    speech_keywords = ['speech', 'talk', 'podcast', 'lecture', 'interview', 'discussion', 'address']

    text = " ".join([title, description, transcript])
    music_count = sum(text.count(word) for word in music_keywords)
    speech_count = sum(text.count(word) for word in speech_keywords)

    if music_count > speech_count:
        return 'music'
    elif speech_count > music_count:
        return 'speech'
    elif music_count == speech_count and music_count > 0:
        return 'music_speech'
    else:
        return 'unknown'

def process_urls(url_list):
    results = []
    for index, url in enumerate(url_list):
        video_id = get_video_id(url)
        if not video_id:
            results.append({'url': url, 'title': '', 'label': 'invalid_url'})
            continue
        title, description = fetch_title_description(url)
        transcript = fetch_transcript_text(video_id)
        label = classify_content(title, description, transcript)
        results.append({'url': url, 'title': title, 'label': label})
        time.sleep(1)  # avoid rate limits
    return pd.DataFrame(results)
