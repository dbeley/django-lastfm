from django.shortcuts import render
from django.http import HttpResponse

from .forms import LastfmPGForm
from .lastfm_pg import get_lastfm_playlist, lastfmconnect, format_playlist
import logging

logger = logging.getLogger()


def get_lastfm_pg(form):
    username = form.cleaned_data["username"]
    timeframe = form.cleaned_data["timeframe"]
    playlist_size = form.cleaned_data["playlist_size"]
    only_favorites = form.cleaned_data["only_favorites"]
    csv = form.cleaned_data["csv"]

    logger.info("Getting playlist for %s (%s , size %s, only_favorites %s, csv %s", username, timeframe, playlist_size, only_favorites, csv)

    network = lastfmconnect()
    user = network.get_user(username)
    playlist = get_lastfm_playlist(
        user, timeframe, playlist_size, only_favorites
    )
    return format_playlist(
        playlist, f"Top {playlist_size} tracks of {username}, {timeframe}", csv
    )


# Create your views here.
def lastfm_pg(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = LastfmPGForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            try:
                content = get_lastfm_pg(form)
            except Exception as e:
                print(e)
                return HttpResponse(content=e, status=400)
            return HttpResponse(content, content_type="text/plain")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LastfmPGForm()

    return render(request, "lastfm_pg/lastfm_pg.html", {"form": form})


def index(request):
    return render(request, "lastfm_pg/index.html")
