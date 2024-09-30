import os
from io import BytesIO

import pylast
import configparser
import logging
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from wordcloud import WordCloud

logger = logging.getLogger(__name__)
matplotlib.use("Agg")  # Use a non-interactive backend
forbidden_tags = ["seen live", "indie", "rock", "alternative"]


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


def custom_color_func(
    word, font_size, position, orientation, random_state=None, **kwargs
):
    # Normalize the font size to get a value between 0 and 1
    normalized_font_size = (
        font_size / 350
    )  # Adjust this based on the expected max font size
    normalized_font_size = min(
        max(normalized_font_size, 0), 1
    )  # Ensure it's within [0, 1]

    # Get the color from a matplotlib colormap
    color = cm.Blues(1 - normalized_font_size)
    return f"rgb({int(color[0] * 255)}, {int(color[1] * 255)}, {int(color[2] * 255)})"


def create_lastfm_wordcloud(user, timeframe, artists_count, top_tags_count):
    dict_frequencies = {}
    logger.info("Computing word cloud for %s (timeframe %s).", user, timeframe)

    top_artists = user.get_top_artists(period=timeframe, limit=artists_count)
    for top_item in top_artists:
        top_tags = top_item.item.get_top_tags()
        top_tags = [
            top_tag
            for top_tag in top_tags
            if top_tag.item.name.lower() not in forbidden_tags
        ]
        for top_tag in top_tags[0:top_tags_count]:
            top_tag_name = top_tag.item.name.lower()
            if top_tag_name in dict_frequencies:
                dict_frequencies[top_tag_name] += int(top_item.weight) * int(
                    top_tag.weight
                )
            else:
                dict_frequencies[top_tag_name] = int(top_item.weight) * int(
                    top_tag.weight
                )

    wordcloud = WordCloud(
        background_color="black",
        colormap="binary",
        width=2560,
        height=1440,
        prefer_horizontal=1.0,
    ).generate_from_frequencies(dict_frequencies)

    plt.figure()
    plt.imshow(
        wordcloud.recolor(color_func=custom_color_func, random_state=3),
        interpolation="bilinear",
    )
    plt.axis("off")
    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=300, bbox_inches="tight", pad_inches=0)
    plt.close()  # Close the figure
    buf.seek(0)  # Move to the beginning of the BytesIO buffer
    return buf
