
import json

import pandas as pd

from .lastfm_scraper import lastfmconnect


def get_artists_genre(genres):
    genres = [x.strip() for x in genres.split(",")]
    network = lastfmconnect()
    list_artists = []
    for genre in genres:
        try:
            artists = network.get_tag(genre).get_top_artists(limit=1000)
            list_artists.extend([x.item.name for x in artists])
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("Error fetching artists for genre %s: %s", genre, e)
    # remove duplicates
    list_artists = list(set(list_artists))
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
    return json.dumps(list_dict, indent=4)

def fetch_new_tracks(user, min_timestamp=None, max_timestamp=None):
    import logging
    logger = logging.getLogger(__name__)

    network = lastfmconnect()
    user = network.get_user(user)
    complete_tracks = []
    # Can't do limit=None here, it throws an error after some time.
    new_tracks = user.get_recent_tracks(
        limit=100, time_from=min_timestamp, time_to=max_timestamp
    )
    complete_tracks.extend(new_tracks)

    while new_tracks:
        last_timestamp = new_tracks[-1].timestamp
        try:
            new_tracks = user.get_recent_tracks(
                limit=100, time_to=last_timestamp, time_from=min_timestamp
            )
            complete_tracks.extend(new_tracks)
        except Exception as e:
            logger.error("Error fetching tracks at timestamp %s: %s", last_timestamp, e)
            break

    list_dict = []
    for index, track in enumerate(reversed(complete_tracks), 1):
        list_dict.append(
            {
                "Index": index,
                "Artist": track.track.artist.name,
                "Album": track.album,
                "Title": track.track.title,
                # "Date": track.playback_date,
                "Date": track.timestamp,
            }
        )
    df = pd.DataFrame(list_dict)
    return df.to_json()

def get_all_favorite_tracks(user):
    network = lastfmconnect()
    user = network.get_user(user)
    loved_tracks = user.get_loved_tracks(limit=None)
    loved_tracks = [
        f"{track.track.artist} - {track.track.title}" for track in loved_tracks
    ]
    return "\n".join(loved_tracks)
