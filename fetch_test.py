import StringIO
import fetch
import pandas as pd
import numpy as np
import unittest
from datetime import datetime,timedelta
import requests
import httpretty # for graet http testing

__author__ = 'Ariadni-Karolina Alexiou'
__email__ = 'karolina.alexiou@teralytics.ch'


class TestLastfmFetch(unittest.TestCase):

	@httpretty.activate
	def test_http_pretty_lol(self):
		""" convince yourself that http pretty does what you think it does """

		lol_json ="""{"recenttracks":{"track":[{"artist":{"#text":"America","mbid":"34cf95c7-4be9-4efd-a48a-c2ea4a0bb114"},"name":"Riverside - 2006 Remastered","streamable":"0","mbid":"","album":{"#text":"","mbid":""},"url":"http:\/\/www.last.fm\/music\/America\/_\/Riverside+-+2006+Remastered","image":[{"#text":"","size":"small"},{"#text":"","size":"medium"},{"#text":"","size":"large"},{"#text":"","size":"extralarge"}],"@attr":{"nowplaying":"true"}},{"artist":{"#text":"America","mbid":"34cf95c7-4be9-4efd-a48a-c2ea4a0bb114"},"name":"I Need You - 2006 Remastered","streamable":"0","mbid":"","album":{"#text":"Definitive Pop: America","mbid":""},"url":"http:\/\/www.last.fm\/music\/America\/_\/I+Need+You+-+2006+Remastered","image":[{"#text":"http:\/\/userserve-ak.last.fm\/serve\/34s\/50439711.jpg","size":"small"},{"#text":"http:\/\/userserve-ak.last.fm\/serve\/64s\/50439711.jpg","size":"medium"},{"#text":"http:\/\/userserve-ak.last.fm\/serve\/126\/50439711.jpg","size":"large"},{"#text":"http:\/\/userserve-ak.last.fm\/serve\/300x300\/50439711.jpg","size":"extralarge"}],"date":{"#text":"26 Mar 2014, 17:47","uts":"1395856027"}}]}}"""

		user_name = "badabing"
		api_key = "yoloswag"
		page = 1
		to_date = 10000
		
		url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user="+user_name+"&api_key="+api_key+"&format=json&page="+str(page)+"&to="+str(to_date)
		
		httpretty.register_uri(httpretty.GET, url,
				   body=lol_json)

		text = fetch.query_lastfm(user_name,api_key,page,to_date)
		print text
		assert(lol_json==text)

		
if __name__ == '__main__':
    	unittest.main()
