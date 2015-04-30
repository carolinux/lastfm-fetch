__author__ = 'carolinux'

import abc
import os
import pandas as pd
import numpy as np
from datetime import datetime

"""Classes to help store, load and query the song data"""

class DataStore:
    """Abstract base class to define interface for functionality.
    Could extend this to a number of concrete implementations
    (csv, sqlite, pickles -if we must- etc)"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def user_exists(self, username):
        pass

    @abc.abstractmethod
    def get_date_range(self, username):
        pass

    @abc.abstractmethod
    def get_songs_as_df(self, username):
        pass

    @abc.abstractmethod
    def add_songs_df(self, username, df, mode):
        """add a songdata dataframe to the store"""
        pass


class CSVDataStore(DataStore):

    SEP = "|" # song names unlikely to have pipes in the name
    def __init__(self, folder):
        if not os.path.exists(folder):
            os.mkdir(folder)
        self.folder = folder
        self.header = ["artist","date_listened","song"]

    def _user_file(self, username):
        return os.path.join(self.folder, username + ".csv")


    def user_exists(self, user):
        return os.path.exists(self._user_file(user))

    def get_songs_as_df(self, user):
        if self.user_exists(user):
            songdf_archive = pd.read_csv(self._user_file(user), encoding='utf-8', sep=self.SEP)
            songdf_archive.date_listened = songdf_archive.date_listened.apply(
                lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
        else:
            songdf_archive = self._get_empty_df()
        return songdf_archive

    def get_date_range(self, user):
        songdf_archive = self.get_songs_as_df(user)
        max_date = songdf_archive.date_listened.max()
        min_date = songdf_archive.date_listened.min()
        return min_date, max_date

    def _get_empty_df(self):
        df = pd.DataFrame(columns=["artist","date_listened","song"])
        df.date_listened = df.date_listened.astype(np.datetime64)
        return df

    def add_songs_df(self, user, df, mode):
        if mode == "append":
            existing_songs  = self.get_songs_as_df(user)
            all_songs = existing_songs.append(df)
        elif mode == "overwrite":
            all_songs = df
        else:
            raise Exception("Invalid mode")
        # check schema
        all_songs.to_csv(self._user_file(user), index=False, encoding='utf-8', sep=self.SEP)

