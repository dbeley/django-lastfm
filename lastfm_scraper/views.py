from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from .forms import (
    LastfmArtistsByGenre,
    LastfmArtistInformation,
    LastfmCompleteTimeline,
    LastfmAllFavoriteTracks,
)

# from .lastfm_scraper import (
from .tasks import (
    fetch_new_tracks,
    get_all_favorite_tracks,
    get_artist_info,
    get_artists_genre,
)
import time
import pandas as pd
import logging

logger = logging.getLogger()

# Create your views here.
def lastfm_scraper(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        if "formtimeline" in request.POST:
            # create a form instance and populate it with data from the request:
            try:
                formtimeline = LastfmCompleteTimeline(request.POST)
            except Exception as e:
                return HttpResponseNotFound(e)
            # check whether it's valid:
            if formtimeline.is_valid():
                try:
                    logger.info("Fetching complete timeline for %s", formtimeline.cleaned_data["username"])
                    content = fetch_new_tracks.delay(
                        formtimeline.cleaned_data["username"]
                    )
                    while content.state not in ("SUCCESS", "FAILURE"):
                        time.sleep(0.5)
                    # content = content.get()
                    content = pd.read_json(content.get())
                except Exception as e:
                    return HttpResponseNotFound(e)
                # return HttpResponse(content, content_type="text/plain")
                response = HttpResponse(content_type="text/plain")
                if formtimeline.cleaned_data["export_format"] == "csv":
                    response[
                        "Content-Disposition"
                    ] = f"attachment; filename=timeline_{formtimeline.cleaned_data['username']}.csv"
                    content.to_csv(response, index=False, sep="\t")
                elif formtimeline.cleaned_data["export_format"] == "xlsx":
                    response[
                        "Content-Disposition"
                    ] = f"attachment; filename=timeline_{formtimeline.cleaned_data['username']}.xlsx"
                    content.to_excel(response, index=False)
                return response
        elif "formfavorite" in request.POST:
            # create a form instance and populate it with data from the request:
            try:
                formfavorite = LastfmAllFavoriteTracks(request.POST)
            except Exception as e:
                return HttpResponseNotFound(e)
            # check whether it's valid:
            if formfavorite.is_valid():
                try:
                    logger.info("Fetching favorite tracks for %s", formfavorite.cleaned_data["username"])
                    content = get_all_favorite_tracks.delay(
                        formfavorite.cleaned_data["username"]
                    )
                    while content.state not in ("SUCCESS", "FAILURE"):
                        time.sleep(0.5)
                    content = content.get()
                except Exception as e:
                    return HttpResponseNotFound(e)
                return HttpResponse(content, content_type="text/plain")
        elif "formgenre" in request.POST:
            # create a form instance and populate it with data from the request:
            try:
                formgenre = LastfmArtistsByGenre(request.POST)
            except Exception as e:
                return HttpResponseNotFound(e)
            # check whether it's valid:
            if formgenre.is_valid():
                try:
                    logger.info("Fetching artists for genre %s", formgenre.cleaned_data["genre"])
                    content = get_artists_genre.delay(
                        formgenre.cleaned_data["genre"]
                    )
                    while content.state not in ("SUCCESS", "FAILURE"):
                        time.sleep(0.5)
                    content = content.get()
                except Exception as e:
                    return HttpResponseNotFound(e)
                return HttpResponse(content, content_type="text/plain")
        elif "forminfo" in request.POST:
            # create a form instance and populate it with data from the request:
            try:
                forminfo = LastfmArtistInformation(request.POST)
            except Exception as e:
                return HttpResponseNotFound(e)
            # check whether it's valid:
            if forminfo.is_valid():
                try:
                    logger.info("Fetching artists info for %s", forminfo.cleaned_data["artist"])
                    content = get_artist_info.delay(
                        forminfo.cleaned_data["artist"]
                    )
                    while content.state not in ("SUCCESS", "FAILURE"):
                        time.sleep(0.5)
                    content = content.get()
                except Exception as e:
                    return HttpResponseNotFound(e)
                return HttpResponse(content, content_type="text/plain")

    # if a GET (or any other method) we'll create a blank form
    else:
        formtimeline = LastfmCompleteTimeline()
        formfavorite = LastfmAllFavoriteTracks()
        forminfo = LastfmArtistInformation()
        formgenre = LastfmArtistsByGenre()
    return render(
        request,
        "lastfm_scraper/lastfm_scraper.html",
        {
            "formtimeline": formtimeline,
            "formfavorite": formfavorite,
            "forminfo": forminfo,
            "formgenre": formgenre,
        },
    )
