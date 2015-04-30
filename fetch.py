import pandas as pd
import sys
from datetime import datetime
import time
import os
import random

import queries
import lastfm
from datastore import CSVDataStore

__author__ = 'Ariadni-Karolina Alexiou'
__email__ = 'carolinegr@gmail.com'

USER_FOLDER = "./users/"
DEFAULT_QUERY_LIMIT = 5
API_ENV_NAME = "LAST_FM_API_KEY"
# could also be lastFm's launch date instead of 1970
DEFAULT_MIN_DATE = datetime.utcfromtimestamp(0)


def main():

    # parse args
    api_key, user_name, query_limit = parse_args(sys.argv[1:])

    # initialize data store and get existing date range
    store = CSVDataStore(USER_FOLDER)
    if store.user_exists(user_name):
        min_date, max_date = store.get_date_range(user_name)
    else:
        min_date = DEFAULT_MIN_DATE
        max_date = min_date

    # get new data from last fm and merge it with existing data
    new_songs = get_new_songs_as_df(query_limit, user_name, api_key, min_date, max_date)
    store.add_songs_df(user_name, new_songs,mode="append")
    all_songs = store.get_songs_as_df(user_name)

    # print out statistics report
    do_all_stats(all_songs)


def parse_args(args):
    api_key = os.environ[API_ENV_NAME]
    user_name = args[0]
    if len(args) < 2:
        query_limit = DEFAULT_QUERY_LIMIT
    else:
        query_limit = int(args[1])
    return api_key, user_name, query_limit


def get_new_songs_as_df(max_queries, user_name, api_key, min_date, max_date):
    """Get new (and backfilled) songs as a dataframe"""
    songs = []
    to_date_epoch = datetime_to_epoch(datetime.now())
    page = 1
    for query in range(max_queries):

        time.sleep(random.randrange(1,6)) # so as to not flood the API with calls
        try:
            tracks = lastfm.get_tracks(user_name, api_key, page, to_date_epoch)
        except lastfm.LastFmException, e:
            print "Unable to fetch any more data for user {} from lastfm".format(user_name)
            print "Json result: {}".format(e)
            print "Will work with what I have"
            break

        for i,track  in enumerate(tracks):
            track_info = lastfm.clean_track_info(track)
            if can_start_backfilling(track_info, max_date):
                # from now on will get songs before last stored date
                to_date_epoch = datetime_to_epoch(min_date)
                max_date = datetime.utcfromtimestamp(0)
                print "Page {}, track {} already in data: Will use remaining {} queries" \
                      " to query dates before and up to {}"\
                    .format(page, i + 1, max_queries - (query+1), min_date)
                page = 1
                break
            songs.append(track_info)
        page+=1

    # can build a dataframe easily from a list of json objects
    songdf = pd.DataFrame(songs).drop_duplicates()  # if there are two entries with same artist,song and timestamp, only one will be kept

    return songdf

def can_start_backfilling(track_info, max_date):
    # if the date listened of the newly fetched track is before the most recent stored track
    # start backfilling songs before the earliest stored date for this user
    return track_info["date_listened"] <= max_date


def do_all_stats(songdf):

    # unique tracks
    uniques = queries.num_unique_songs(songdf)
    print "Unique tracks: {} out of {}".format(uniques, len(songdf))

    # top5 artists
    top5 = queries.topk_artists(songdf, num=5)
    print "top 5 artists"
    print top5

    # average number of tracks per day
    songs_per_day = queries.num_unique_songs_per_day(songdf)
    print "Average songs per day: {}".format(songs_per_day)

    # most active day per week
    most_popular_day, num_songs = queries.most_popular_day(songdf)
    print "Most popular day : {} (songs: {})".format(most_popular_day, num_songs)

    # alternative way for most active day
    # to showcase pandas capabilities
    most_popular_day_alt = queries.most_popular_day_with_pivot(songdf)
    assert (most_popular_day == most_popular_day_alt)

def datetime_to_epoch(dt):
    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()


if __name__ == "__main__":
    main()
