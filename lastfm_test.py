import unittest
import httpretty  # for great http testing
import json
from datetime import datetime, timedelta

import fetch
import lastfm

__author__ = 'Ariadni-Karolina Alexiou'
__email__ = 'carolinegr@gmail.com'


class TestLastfmFetch(unittest.TestCase):
    @httpretty.activate
    def test_parse_info(self):
        """ Check the parsing of data from the lastfm api """

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

        url = lastfm.create_url(user_name, api_key, page, to_date)

        httpretty.register_uri(httpretty.GET, url,
                               body=json_result)

        tracks = lastfm.get_tracks(user_name, api_key, page, to_date)
        self.assertEquals(len(tracks), 2)
        track = tracks[0]
        info = lastfm.clean_track_info(track)
        self.assertEquals(info["song"], "Riverside - 2006 Remastered")
        self.assertEquals(info["artist"], "America")
        self.assertLessEqual(datetime.utcnow() - info["date_listened"],
                             timedelta(minutes=1))  # because it is "now playing"

        track = tracks[1]
        info = lastfm.clean_track_info(track)
        self.assertEquals(info["song"], "I Need You - 2006 Remastered")
        self.assertEquals(info["artist"], "America")
        self.assertEquals(info["date_listened"], datetime(2014, 3, 26, 17, 47))


if __name__ == '__main__':
    unittest.main()
