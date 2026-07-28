import configparser
import logging
import os

import pylast

logger = logging.getLogger(__name__)


def lastfmconnect():  # pragma: no cover
    """Connect to Last.fm API using credentials from config file or environment variables.

    Returns:
        pylast.LastFMNetwork: Authenticated Last.fm network instance

    Raises:
        ValueError: If credentials are not found in config file or environment
    """
    try:
        config = configparser.ConfigParser()
        config.read("config_lastfm.ini")
        api_key = config["lastfm"]["api_key"]
        api_secret = config["lastfm"]["api_secret"]
        username = config["lastfm"]["username"]
        logger.info("Loaded Last.fm credentials from config_lastfm.ini")
    except Exception as e:
        logger.info("Config file not found, trying environment variables: %s", e)
        api_key = os.environ.get("PYLAST_API_KEY", "").strip()
        api_secret = os.environ.get("PYLAST_API_SECRET", "").strip()
        username = os.environ.get("PYLAST_USERNAME", "").strip()

        if not all([api_key, api_secret, username]):
            raise ValueError(
                "Last.fm credentials not found. Please provide them either in config_lastfm.ini "
                "or via PYLAST_API_KEY, PYLAST_API_SECRET, and PYLAST_USERNAME environment variables."
            )

    network = pylast.LastFMNetwork(
        api_key=api_key, api_secret=api_secret, username=username
    )
    return network
