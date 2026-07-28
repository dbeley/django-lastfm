import logging

import pandas as pd
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from .forms import (
    LastfmAllFavoriteTracks,
    LastfmArtistInformation,
    LastfmArtistsByGenre,
    LastfmCompleteTimeline,
)
from .tasks import (
    fetch_new_tracks,
    get_all_favorite_tracks,
    get_artist_info,
    get_artists_genre,
)

logger = logging.getLogger(__name__)


# Create your views here.
def lastfm_scraper(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        if "formtimeline" in request.POST:
            try:
                formtimeline = LastfmCompleteTimeline(request.POST)
            except Exception:
                logger.exception("Error creating timeline form")
                return HttpResponseBadRequest("Invalid form data")

            if formtimeline.is_valid():
                try:
                    logger.info(
                        "Fetching complete timeline for %s",
                        formtimeline.cleaned_data["username"],
                    )
                    content = pd.read_json(fetch_new_tracks(
                        formtimeline.cleaned_data["username"]
                    ))
                except Exception:
                    logger.exception("Error fetching timeline for user %s", formtimeline.cleaned_data.get("username"))
                    return HttpResponseBadRequest("An error occurred while fetching the timeline.")

                response = HttpResponse(content_type="text/plain")
                if formtimeline.cleaned_data["export_format"] == "csv":
                    response["Content-Disposition"] = (
                        f"attachment; filename=timeline_{formtimeline.cleaned_data['username']}.csv"
                    )
                    content.to_csv(response, index=False, sep="\t")
                elif formtimeline.cleaned_data["export_format"] == "xlsx":
                    response["Content-Disposition"] = (
                        f"attachment; filename=timeline_{formtimeline.cleaned_data['username']}.xlsx"
                    )
                    content.to_excel(response, index=False)
                return response

        elif "formfavorite" in request.POST:
            try:
                formfavorite = LastfmAllFavoriteTracks(request.POST)
            except Exception:
                logger.exception("Error creating favorite tracks form")
                return HttpResponseBadRequest("Invalid form data")

            if formfavorite.is_valid():
                try:
                    logger.info(
                        "Fetching favorite tracks for %s",
                        formfavorite.cleaned_data["username"],
                    )
                    content = get_all_favorite_tracks(
                        formfavorite.cleaned_data["username"]
                    )
                except Exception:
                    logger.exception("Error fetching favorites for user %s", formfavorite.cleaned_data.get("username"))
                    return HttpResponseBadRequest("An error occurred while fetching favorite tracks.")

                return HttpResponse(content, content_type="text/plain")

        elif "formgenre" in request.POST:
            try:
                formgenre = LastfmArtistsByGenre(request.POST)
            except Exception:
                logger.exception("Error creating genre form")
                return HttpResponseBadRequest("Invalid form data")

            if formgenre.is_valid():
                try:
                    logger.info(
                        "Fetching artists for genre %s", formgenre.cleaned_data["genre"]
                    )
                    content = get_artists_genre(formgenre.cleaned_data["genre"])
                except Exception:
                    logger.exception("Error fetching artists for genre %s", formgenre.cleaned_data.get("genre"))
                    return HttpResponseBadRequest("An error occurred while fetching artists.")

                return HttpResponse(content, content_type="text/plain")

        elif "forminfo" in request.POST:
            try:
                forminfo = LastfmArtistInformation(request.POST)
            except Exception:
                logger.exception("Error creating artist info form")
                return HttpResponseBadRequest("Invalid form data")

            if forminfo.is_valid():
                try:
                    logger.info(
                        "Fetching artists info for %s", forminfo.cleaned_data["artist"]
                    )
                    content = get_artist_info(forminfo.cleaned_data["artist"])
                except Exception:
                    logger.exception("Error fetching info for artist %s", forminfo.cleaned_data.get("artist"))
                    return HttpResponseBadRequest("An error occurred while fetching artist information.")

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
