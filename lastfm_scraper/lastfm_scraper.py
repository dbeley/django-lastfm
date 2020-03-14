import configparser
import pylast
import json


def lastfmconnect():  # pragma: no cover
    config = configparser.ConfigParser()
    config.read("config_lastfm.ini")
    api_key = config["lastfm"]["api_key"]
    api_secret = config["lastfm"]["api_secret"]
    username = config["lastfm"]["username"]

    network = pylast.LastFMNetwork(
        api_key=api_key, api_secret=api_secret, username=username
    )
    return network


def get_artists_genre(genres):
    genres = [x.strip() for x in genres.split(",")]
    network = lastfmconnect()
    list_artists = []
    for genre in genres:
        try:
            list_artists += [
                x.item.name
                for x in network.get_tag(genre).get_top_artists(limit=1000)
            ]
        except Exception as e:
            print("%s", e)
    return "\n".join(list_artists)


def get_artist_info(artists):
    network = lastfmconnect()
    artists = [x.strip() for x in artists.split(",")]

    list_dict = []
    for artist in artists:
        artist_dict = {}
        a = network.get_artist(artist)
        artist_dict["Name"] = a.get_name()
        artist_dict["URL"] = a.get_url()
        artist_dict["Listeners"] = a.get_listener_count()
        artist_dict["Playcount"] = a.get_playcount()
        # dict["Country"] = get_country(dict["URL"])
        list_dict.append(artist_dict)
    return json.dumps(list_dict)


def fetch_new_tracks(user, min_timestamp=None, max_timestamp=None):
    network = lastfmconnect()
    user = network.get_user(user)
    complete_tracks = []
    # Can't do limit=None here, it throws an error after some time.
    new_tracks = user.get_recent_tracks(
        limit=100, time_from=min_timestamp, time_to=max_timestamp
    )
    complete_tracks = complete_tracks + new_tracks
    while new_tracks:
        last_timestamp = new_tracks[-1].timestamp
        try:
            new_tracks = user.get_recent_tracks(
                limit=100, time_to=last_timestamp, time_from=min_timestamp
            )
            complete_tracks = complete_tracks + new_tracks
        except Exception as e:
            print(e)
    return "\n".join(complete_tracks)


def get_all_favorite_tracks(user):
    network = lastfmconnect()
    user = network.get_user(user)
    loved_tracks = user.get_loved_tracks(limit=None)
    loved_tracks = [x.track for x in loved_tracks]
    return "\n".join(loved_tracks)
