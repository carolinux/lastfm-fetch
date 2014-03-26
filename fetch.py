import pandas as pd
import sys
import requests
import json
from datetime import datetime
import time
import os 
import numpy as np

__author__ = 'Ariadni-Karolina Alexiou'
__email__ = 'karolina.alexiou@teralytics.ch'

IDX_NAME="idx"

def datetime_to_epoch(dt):
    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

def query_lastfm(user_name,api_key,page,to_date):
	""" to_date must be in epoch timestamp format (integer)"""
	url="http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user="+user_name+"&api_key="+api_key+"&format=json&page="+str(page)+"&to="+str(to_date)
	print "Loading stuff from url: {}".format(url)

	return requests.get(url).text

def parse_track_info(track):
	artist = track["artist"]["#text"]
	song = track["name"]
	date_str = track["date"]["#text"]
	date_listened = datetime.strptime(date_str,"%d %b %Y, %H:%M")
	return {"artist":artist,"song":song,"date_listened":date_listened}


def main():
	USER_FOLDER = "./users/"

	## parse input data ##

	if not os.path.exists(USER_FOLDER):
		os.mkdir(USER_FOLDER)
	user_name = sys.argv[1] 
	api_key = os.environ['LAST_FM_API_KEY']
	save_file = os.path.join(USER_FOLDER,user_name+".csv")
	if os.path.exists(save_file):
		have_data = True
	else:
		have_data = False

	if len(sys.argv)<3:

		query_limit = 5
	else:
		query_limit = int(sys.argv[2])

	## load archived data, if any ##

	if have_data == True:
		songdf_archive = pd.read_csv(save_file, encoding='utf-8')
		songdf_archive.date_listened = songdf_archive.date_listened.apply(lambda x: datetime.strptime(x,"%Y-%m-%d %H:%M:%S"))
		songdf_archive = songdf_archive.set_index(IDX_NAME)
		max_date = songdf_archive.date_listened.max()
		min_date = songdf_archive.date_listened.min()
	else:
		songdf_archive = None
		max_date = datetime.datetime.utcfromtimestamp(0)
		min_date = max_date

	songdf = run_queries(query_limit,user_name,api_key,min_date,max_date)

	if songdf is None and have_data == False:
		print "No songs for user {}".format(user_name)
		sys.exit(0)

	if have_data == True:
		songdf = songdf_archive.append(songdf).drop_duplicates()
		
	songdf.to_csv(save_file,encoding='utf-8')

	do_all_stats(songdf)

def run_queries(query_limit,user_name,api_key,min_date,max_date):

	songs = []

	start_date_epoch = datetime_to_epoch(datetime.now())

	page = 1

	## query last.fm for recent tracks ##

	for queries in range(0,query_limit):
	
		time.sleep(1)

		text = query_lastfm(user_name,api_key,page,int(start_date_epoch))

		try:
			tracks = json.loads(text)["recenttracks"]["track"]
		except:
			print "Unexpected json format. Either no moar songs or last.fm thinks I am spamming.. will work with what I have"
			break

		page+=1

		for track,i in zip(tracks,range(0,len(tracks))):
	
			track_info = parse_track_info(track)

			if track_info["date_listened"]<=max_date:
				# if the date listened of the newly fetched track is before the most recent stored track 
				# start teh backfilling
				start_date_epoch = datetime_to_epoch(min_date)
				max_date = datetime.utcfromtimestamp(0)
				print "Page {}, track {} already in data: Will use remaining queries to query dates before and up to {}".format(page-1,i+1,min_date)
				page=1			
				break
		
			songs.append(track_info)

	if len(songs)==0:
		return None


	songdf = pd.DataFrame(songs).drop_duplicates() # if there are two entries with same artist,song and timestamp, only one will be kept
	songdf.index.name = IDX_NAME #could use timestamp as the index...

	return songdf


def do_all_stats(songdf):	

	## Do statistics on the data , create views etc ##

	#unique tracks

	uniques = len(songdf.groupby(["song","artist"])) #how many groups of unique combinations of song/artist are there?
	print "Unique tracks: {} out of {}".format(uniques,len(songdf))

	#top5 artists

	by_artist = songdf.groupby("artist")
	top5 = by_artist.count().sort("artist",ascending=False)[:5]["artist"].index
	top5counts = by_artist.count().sort("artist",ascending=False)[:5]["artist"].values
	print "top 5 artists"
	for idx,artist,cnt in zip(range(1,6),top5,top5counts):
		print idx,artist,cnt

	#average number of tracks per day

	songdf["day"] = songdf["date_listened"].apply(lambda x: x.date()) # extract the date from datetime 

	songs_per_day = (len(songdf)+0.0)/len(songdf.day.unique())

	print "Average songs per day: {}".format(songs_per_day)

	#most active day per week

	songdf["day_of_week"] = songdf["date_listened"].apply(lambda x: x.strftime("%A"))
	by_weekday = songdf.groupby("day_of_week")
	most_popular_day =  by_weekday.count().sort("song",ascending=False).iloc[0].name
	print "Most popular day : {}".format(most_popular_day)

	#alternative way for most active day
	songdf["cnt"]=1 # helper column to show that each entry counts for one
	#pivot call creates a pandas series, which can be ordered by value (the sum of 1s, ie the count)
	most_popular_day_alt = songdf.pivot_table(rows="day_of_week",  values="cnt", aggfunc=np.sum).order(ascending=False).index[0]
	assert(most_popular_day == most_popular_day_alt)



if __name__=="__main__":
	main()	
