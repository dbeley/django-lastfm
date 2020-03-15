from django.shortcuts import render
from django.http import HttpResponse
from .forms import (
    LastfmArtistsByGenre,
    LastfmArtistInformation,
    LastfmCompleteTimeline,
    LastfmAllFavoriteTracks,
)
from .lastfm_scraper import (
    fetch_new_tracks,
    get_all_favorite_tracks,
    get_artist_info,
    get_artists_genre,
)


# Create your views here.
def lastfm_scraper(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        if "formtimeline" in request.POST:
            # create a form instance and populate it with data from the request:
            formtimeline = LastfmCompleteTimeline(request.POST)
            # check whether it's valid:
            if formtimeline.is_valid():
                content = fetch_new_tracks(
                    formtimeline.cleaned_data["username"]
                )
                return HttpResponse(content, content_type="text/plain")
    if request.method == "POST":
        if "formfavorite" in request.POST:
            # create a form instance and populate it with data from the request:
            formfavorite = LastfmAllFavoriteTracks(request.POST)
            # check whether it's valid:
            if formfavorite.is_valid():
                content = get_all_favorite_tracks(
                    formfavorite.cleaned_data["username"]
                )
                return HttpResponse(content, content_type="text/plain")
    if request.method == "POST":
        if "formgenre" in request.POST:
            # create a form instance and populate it with data from the request:
            formgenre = LastfmArtistsByGenre(request.POST)
            # check whether it's valid:
            if formgenre.is_valid():
                content = get_artists_genre(formgenre.cleaned_data["genre"])
                return HttpResponse(content, content_type="text/plain")
    if request.method == "POST":
        if "forminfo" in request.POST:
            # create a form instance and populate it with data from the request:
            forminfo = LastfmArtistInformation(request.POST)
            # check whether it's valid:
            if forminfo.is_valid():
                content = get_artist_info(forminfo.cleaned_data["artist"])
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
