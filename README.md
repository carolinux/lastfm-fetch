lastfm-fetch
============

Fetches user statistics for last.fm users. An exercise in using json &amp; pandas.
You need to add a last.fm API key to your environment variables via:

**export LAST_FM_API_KEY="yourkey"**

run as:

**python fetch.py username [number_of_pages_to_look_at]**

Requires pandas (and httpretty for testing)
If installing pandas via pip doesn't work try your OS's equivalent of:
```
sudo apt-get install python-pandas
```
