__author__ = 'carolinux'

"""Functionality that requires knowledge of the lastFM api"""

import json
import requests
from datetime import datetime


class LastFmException(Exception):
    pass

def create_url(user_name, api_key, page, to_date):
    return "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={}&api_key={}"\
           "&format=json&page={}&to={}".format(user_name, api_key, page, to_date)


def get_tracks(user_name, api_key, page, to_date):
    """ Get all tracks from page
    to_date must be in epoch timestamp format (integer)
    """
    url = create_url(user_name, api_key, page, to_date)
    print "Loading stuff from url: {}".format(url)

    text = requests.get(url).text
    try:
        tracks = json.loads(text)["recenttracks"]["track"]
    except:
        raise LastFmException(text)
    return tracks


def clean_track_info(track):
    """Create a more compact json object out of the lastfm track json"""
    artist = track["artist"]["#text"]
    song = track["name"]
    if "@attr" in track.keys() and track["@attr"]["nowplaying"] == "true":
        date_listened = datetime.now()
    else:
        date_str = track["date"]["#text"]
        date_listened = datetime.strptime(date_str, "%d %b %Y, %H:%M")
    return {"artist": artist, "song": song, "date_listened": date_listened}

