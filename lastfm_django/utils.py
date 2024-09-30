import configparser
import os

import pylast


def lastfmconnect():  # pragma: no cover
    try:
        config = configparser.ConfigParser()
        config.read("config_lastfm.ini")
        api_key = config["lastfm"]["api_key"]
        api_secret = config["lastfm"]["api_secret"]
        username = config["lastfm"]["username"]
    except Exception as e:
        print(e)
        api_key = os.environ["PYLAST_API_KEY"].strip()
        api_secret = os.environ["PYLAST_API_SECRET"].strip()
        username = os.environ["PYLAST_USERNAME"].strip()
    network = pylast.LastFMNetwork(
        api_key=api_key, api_secret=api_secret, username=username
    )
    return network
