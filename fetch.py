import pandas as pd
import sys
import urllib2
import json
from datetime import datetime
import time
import os 
import numpy as np

USER_FOLDER = "./users/"

if not os.path.exists(USER_FOLDER):
	os.mkdir(USER_FOLDER)
user_name = sys.argv[1] 
api_key = os.environ['LAST_FM_API_KEY']
save_file = os.path.join(USER_FOLDER,user_name+".csv")


if len(sys.argv)<3:

	page_limit = 5
else:
	page_limit = int(sys.argv[2])

songs = []

for page in range(1,page_limit+1):
	url="http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user="+user_name+"&api_key="+api_key+"&format=json&page="+str(page)
	print "Loading stuff from url: {}".format(url)

	time.sleep(1)

	text = urllib2.urlopen(url).read()

	try:
		tracks = json.loads(text)["recenttracks"]["track"]
	except:
		print "Unexpected json format. Either no moar songs or last.fm thinks I am spamming.. will work with what I have"
		break


	for track in tracks:
	

		artist = track["artist"]["#text"]
		song = track["name"]
		date_str = track["date"]["#text"]
		date_listened = datetime.strptime(date_str,"%d %b %Y, %H:%M")
		songs.append({"artist":artist,"song":song,"date_listened":date_listened})

if len(songs)==0:

	print "No songs for user {}".format(user_name)
	sys.exit(0)

songdf = pd.DataFrame(songs).drop_duplicates() # if there are two entries with same artist,song and timestamp, only one will be kept
songdf.index.name = "idx"

if os.path.exists(save_file):
	songdf_archive = pd.read_csv(save_file, encoding='utf-8')
	songdf_archive.date_listened = songdf_archive.date_listened.apply(lambda x: datetime.strptime(x,"%Y-%m-%d %H:%M:%S"))
        songdf_archive = songdf_archive.set_index("idx")
	songdf = songdf_archive.append(songdf).drop_duplicates()

songdf.to_csv(save_file,encoding='utf-8')

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





	
