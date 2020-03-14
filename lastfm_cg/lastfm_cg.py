import os
import pylast
import requests
import configparser
import numpy as np
from PIL import Image
from io import BytesIO


def lastfmconnect():  # pragma: no cover
    try:
        config = configparser.ConfigParser()
        config.read("config_lastfm.ini")
        api_key = config["lastfm"]["api_key"]
        api_secret = config["lastfm"]["api_secret"]
        username = config["lastfm"]["username"]

        network = pylast.LastFMNetwork(
            api_key=api_key, api_secret=api_secret, username=username
        )
    except Exception as e:
        print(e)
        api_key = os.environ["PYLAST_API_KEY"].strip()
        api_secret = os.environ["PYLAST_API_SECRET"].strip()
        username = os.environ["PYLAST_USERNAME"].strip()
    network = pylast.LastFMNetwork(
        api_key=api_key, api_secret=api_secret, username=username
    )
    return network


def get_lastfm_collage(user, timeframe, rows, columns):
    list_covers = get_list_covers(user, rows * columns, timeframe)
    image = create_image(list_covers, columns)
    return image


def chunks(l, n):
    # generator of chunks of size l for a iterable n
    for i in range(0, len(l), n):
        yield l[i : i + n]


def create_image(list_covers, nb_columns):
    # create image from list_covers with nb_columns columns
    imgs = [Image.open(BytesIO(i)).convert("RGB") for i in list_covers]

    min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]

    list_comb = []
    for img in chunks(imgs, nb_columns):
        # list of rows of x columns
        list_arrays = [np.asarray(i.resize(min_shape)) for i in img]
        i = 0
        while len(list_arrays) < nb_columns:
            i += 1
            list_arrays.append(
                np.asarray(
                    np.zeros((min_shape[0], min_shape[1], 4), dtype=np.uint8)
                )
            )
        list_comb.append(np.hstack(list_arrays))

    # combine rows to create image
    list_comb_arrays = [np.asarray(i) for i in list_comb]
    imgs_comb = np.vstack(list_comb_arrays)
    imgs_comb = Image.fromarray(imgs_comb)
    return imgs_comb


def get_cover_for_album(index, album):
    # returns an img object for an album or None
    nb_tries = 0
    while True:
        try:
            nb_tries += 1
            url = album.item.get_cover_image()
            break
        except Exception as e:
            print(
                "Error retrieving cover url for %s - %s : %s. " "Retrying.",
                index,
                album.item,
                e,
            )
            if nb_tries > 4:
                print(
                    "Couldn't retrieve cover url for %s - %s after "
                    "4 tries.",
                    index,
                    album.item,
                )
                url = None
                break
    if url:
        if url.endswith(".png") or url.endswith(".jpg"):
            img = requests.get(url).content
            if img:
                try:
                    Image.open(BytesIO(img)).seek(1)
                except EOFError:
                    return img
                else:
                    # image is a gif
                    print("Image is a gif. Skipping")
            else:
                # link returned by get_cover_image() doesn't work
                print("No image returned by url %s", url)
        else:
            # url doesn't host a png or jpg image
            print("Wrong filetype for %s", url)
    else:
        # no url returned by get_cover_image()
        print("No cover image found for %s - %s", index, album.item)
    return None


def extract_covers_from_top_albums(top_albums):
    # extract all correct img from a top_albums list
    list_covers = []
    for index, album in enumerate(top_albums, 1):
        img = get_cover_for_album(index, album)
        if img:
            list_covers.append(img)
    return list_covers


def get_list_covers(user, nb_covers, timeframe):
    # extract the top available covers for the specified timeframe and user
    nb_failed = 0
    nb_failed_global = 0
    list_covers = []
    # while at least one cover extraction fails
    while True:
        # keep track of all the failed ones, in case of several iterations
        nb_failed_global += nb_failed
        limit = nb_covers + nb_failed_global
        if nb_failed > 0:
            print(
                "Some covers weren't properly extracted. "
                "Adding %s albums to the grid.",
                nb_failed,
            )
        if limit > 1000:
            print(
                "Can't extract more than 1000 albums. "
                "Choose smaller number of rows/columns."
            )
            exit()
        top_albums = user.get_top_albums(period=timeframe, limit=limit)
        if len(top_albums) != limit:
            print(
                "Not enough albums played in the selected timeframe. "
                "Choose a lower rows/columns value or another timeframe."
            )
            exit()
        top_albums = top_albums[-nb_failed:]
        nb_failed = 0
        list_covers_partial = extract_covers_from_top_albums(top_albums)
        nb_failed = len(top_albums) - len(list_covers_partial)
        list_covers += list_covers_partial
        if nb_failed == 0:
            break
    return list_covers
