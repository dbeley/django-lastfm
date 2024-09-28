import os
import configparser
import pylast
import random
from collections import defaultdict


def lastfmconnect():  # pragma: no cover
    try:
        config = configparser.ConfigParser()
        config.read("config_lastfm.ini")
        api_key = config["lastfm"]["api_key"]
        api_secret = config["lastfm"]["api_secret"]
        username = config["lastfm"]["username"]
    except Exception as e:
        print(e)
        api_key = os.environ.get("PYLAST_API_KEY", "").strip()
        api_secret = os.environ.get("PYLAST_API_SECRET", "").strip()
        username = os.environ.get("PYLAST_USERNAME", "").strip()
    network = pylast.LastFMNetwork(
        api_key=api_key, api_secret=api_secret, username=username
    )
    return network


def get_lastfm_playlist(user, timeframe, playlist_length, only_favorites=True):
    # List of recently played tracks
    top_tracks = user.get_top_tracks(period=timeframe, limit=1000)
    if only_favorites:
        try:
            # List of all loved tracks
            # Need to extract all loved tracks, get_userloved() function doesn't seems to work
            loved_tracks = user.get_loved_tracks(limit=None)
            loved_tracks = [x.track for x in loved_tracks]

            # List of tracks presents in both lists
            playlist_potential_tracks = [
                (x.weight, x.item) for x in top_tracks if x.item in loved_tracks
            ]
        except Exception as e:
            print(e)
    else:
        # List of tracks presents in both lists
        playlist_potential_tracks = [(x.weight, x.item) for x in top_tracks]

    # dict where keys : weight, values : list of tracks
    dd_tracks = defaultdict(list)
    for track in playlist_potential_tracks:
        dd_tracks[track[0]].append(track[1])

    # Create final playlist
    playlist_tracks = []
    count = max(dd_tracks.keys())
    while len(playlist_tracks) <= playlist_length | count >= 1:
        if len(playlist_tracks) >= playlist_length:
            break
        # randomize to not take the first item by alphabetical order
        randomized_dd_tracks = random.sample(dd_tracks[count], len(dd_tracks[count]))
        for track in randomized_dd_tracks:
            playlist_tracks.append([track, count])
            if len(playlist_tracks) >= playlist_length:
                break
        count -= 1
    return playlist_tracks


def format_playlist(playlist_tracks, title, csv):
    # Creating message list
    # headers_message = [title, "Made with https://github.com/dbeley/lastfm_pg"]
    list_message = []
    if csv:
        # header
        headers_message = []
        list_message.append("position;artist;title;playcount")
    else:
        headers_message = [title]

    for index, track in list(enumerate(playlist_tracks, 1)):
        if csv:
            list_message.append(
                f"{str(index).zfill(2)};{track[0].artist};{track[0].title};{track[1]}"
            )
        else:
            list_message.append(
                f"{str(index).zfill(2)}: {track[0].artist} - {track[0].title} ({track[1]} plays)"
            )
    if not csv:
        list_message.insert(0, headers_message[0])
    return "\n".join(list_message)
