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
                    content = fetch_new_tracks.delay(
                        formtimeline.cleaned_data["username"]
                    )
                    while content.state not in ("SUCCESS", "FAILURE"):
                        time.sleep(0.5)
                    content = content.get()
                except Exception as e:
                    return HttpResponseNotFound(e)
                return HttpResponse(content, content_type="text/plain")
        elif "formfavorite" in request.POST:
            # create a form instance and populate it with data from the request:
            try:
                formfavorite = LastfmAllFavoriteTracks(request.POST)
            except Exception as e:
                return HttpResponseNotFound(e)
            # check whether it's valid:
            if formfavorite.is_valid():
                try:
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
