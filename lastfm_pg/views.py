from django.shortcuts import render
from django.http import HttpResponse

from lastfm_pg.utils import get_lastfm_playlist, format_playlist
from lastfm_django.utils import lastfmconnect
from .forms import LastfmPGForm
import logging
import pylast

logger = logging.getLogger(__name__)


def get_lastfm_pg(form):
    username = form.cleaned_data["username"]
    timeframe = form.cleaned_data["timeframe"]
    playlist_size = form.cleaned_data["playlist_size"]
    only_favorites = form.cleaned_data["only_favorites"]
    csv = form.cleaned_data["csv"]

    logger.info(
        "Getting playlist for %s (%s , size %s, only_favorites %s, csv %s",
        username,
        timeframe,
        playlist_size,
        only_favorites,
        csv,
    )

    network = lastfmconnect()
    user = network.get_user(username)
    playlist = get_lastfm_playlist(user, timeframe, playlist_size, only_favorites)
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
            except pylast.WSError as e:
                logger.error("Last.fm API error for user %s: %s", form.cleaned_data.get("username"), e)
                return HttpResponse(
                    content=f"Last.fm API error: {str(e)}. Please check the username and try again.",
                    status=400
                )
            except pylast.NetworkError as e:
                logger.error("Network error while fetching playlist: %s", e)
                return HttpResponse(
                    content="Network error. Please try again later.",
                    status=503
                )
            except Exception as e:
                logger.exception("Unexpected error generating playlist for user %s", form.cleaned_data.get("username"))
                return HttpResponse(
                    content="An unexpected error occurred. Please try again later.",
                    status=500
                )
            return HttpResponse(content, content_type="text/plain")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LastfmPGForm()

    return render(request, "lastfm_pg/lastfm_pg.html", {"form": form})


def index(request):
    return render(request, "index.html")
