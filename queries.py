import numpy as np

__author__ = 'carolinux'


def topk_artists(songdf, num=10):
    by_artist = songdf.groupby("artist")
    return by_artist.count().sort("song", ascending=False)[:num]["artist"]


def num_unique_songs(songdf):
    return len(songdf.groupby(["song", "artist"]))

def num_unique_songs_per_day(songdf):
    songdf["day"] = songdf["date_listened"].apply(
        lambda x: x.date())  # extract the date from datetime

    if len(songdf.day.unique())>0:
        songs_per_day = (len(songdf) + 0.0) / len(songdf.day.unique())
    else:
        songs_per_day = 0.0
    return songs_per_day


def most_popular_day(songdf):
    songdf["day_of_week"] = songdf["date_listened"].apply(lambda x: x.strftime("%A"))
    by_weekday = songdf.groupby("day_of_week")
    sortd = by_weekday.count().sort("song", ascending=False)
    return sortd.iloc[0].name, sortd.iloc[0].song

def most_popular_day_with_pivot(songdf):
    songdf["day_of_week"] = songdf["date_listened"].apply(lambda x: x.strftime("%A"))
    songdf["cnt"] = 1  # helper column to show that each entry counts for one
    #pivot call creates a pandas series, which can be ordered by value (the sum of 1s, ie the count)
    return songdf.pivot_table(rows="day_of_week", values="cnt", aggfunc=np.sum).order(
        ascending=False).index[0]
