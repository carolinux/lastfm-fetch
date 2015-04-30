import StringIO
import fetch
import pandas as pd
import numpy as np
import unittest
from datetime import datetime, timedelta
import requests
import httpretty  # for graet http testing
import json

__author__ = 'Ariadni-Karolina Alexiou'
__email__ = 'carolinegr@gmail.com'


class TestLastfmFetch(unittest.TestCase):
    @httpretty.activate
    def test_parse_info(self):
        """ convince yourself that http pretty does what you think it does """

        json_result = """{"recenttracks":{"track":[{"artist":{"#text":"America",
        "mbid":"34cf95c7-4be9-4efd-a48a-c2ea4a0bb114"},"name":"Riverside - 2006 Remastered",
        "streamable":"0","mbid":"","album":{"#text":"","mbid":""},
        "url":"http:\/\/www.last.fm\/music\/America\/_\/Riverside+-+2006+Remastered","image":
        [{"#text":"","size":"small"},{"#text":"","size":"medium"},{"#text":"","size":"large"},
        {"#text":"","size":"extralarge"}],"@attr":{"nowplaying":"true"}},{"artist":{"#text":"America",
        "mbid":"34cf95c7-4be9-4efd-a48a-c2ea4a0bb114"},"name":"I Need You - 2006 Remastered",
        "streamable":"0","mbid":"","album":{"#text":"Definitive Pop: America","mbid":""},
        "url":"http:\/\/www.last.fm\/music\/America\/_\/I+Need+You+-+2006+Remastered",
        "image":[{"#text":"http:\/\/userserve-ak.last.fm\/serve\/34s\/50439711.jpg",
        "size":"small"},{"#text":"http:\/\/userserve-ak.last.fm\/serve\/64s\/50439711.jpg","size":"medium"},
        {"#text":"http:\/\/userserve-ak.last.fm\/serve\/126\/50439711.jpg","size":"large"},
        {"#text":"http:\/\/userserve-ak.last.fm\/serve\/300x300\/50439711.jpg","size":"extralarge"}],
        "date":{"#text":"26 Mar 2014, 17:47","uts":"1395856027"}}]}}"""

        user_name = "badabing"
        api_key = "yoloswag"
        page = 1
        to_date = 10000

        url = fetch.create_url(user_name, api_key, page, to_date)

        httpretty.register_uri(httpretty.GET, url,
                               body=json_result)

        text = fetch.query_lastfm(user_name, api_key, page, to_date)
        assert (json_result == text)
        tracks = json.loads(text)["recenttracks"]["track"]
        assert (len(tracks) == 2)
        now = datetime.now()
        track = tracks[0]
        info = fetch.parse_track_info(track, now)
        assert (info["song"] == "Riverside - 2006 Remastered")
        assert (info["artist"] == "America")
        assert (info["date_listened"] == now)  # because it is "now playing"
        track = tracks[1]
        info = fetch.parse_track_info(track, now)
        assert (info["song"] == "I Need You - 2006 Remastered")
        assert (info["artist"] == "America")
        assert (info["date_listened"] == datetime(2014, 3, 26, 17, 47))


if __name__ == '__main__':
    unittest.main()
