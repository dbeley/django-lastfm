import logging
from datetime import datetime

import pylast
from django.http import HttpResponse
from django.shortcuts import render

from lastfm_django.utils import lastfmconnect
from lastfm_wordcloud.__main__ import create_lastfm_wordcloud

from .forms import LastfmWCForm

logger = logging.getLogger(__name__)

FORBIDDEN_TAGS = ["seen live", "alternative", "indie", "rock"]

def get_lastfm_wordcloud(form):
    username = form.cleaned_data["username"]
    timeframe = form.cleaned_data["timeframe"]
    artists_count = form.cleaned_data["artists_count"]
    top_tags_count = form.cleaned_data["top_tags_count"]

    logger.info(
        "Getting wordcloud for %s (%s , artists %s, top_tags %s",
        username,
        timeframe,
        artists_count,
        top_tags_count,
    )

    network = lastfmconnect()
    user = network.get_user(username)
    return create_lastfm_wordcloud(user, timeframe, artists_count, top_tags_count, FORBIDDEN_TAGS)


# Create your views here.
def lastfm_wordcloud(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = LastfmWCForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            try:
                content = get_lastfm_wordcloud(form)
            except pylast.WSError as e:
                logger.error("Last.fm API error for user %s: %s", form.cleaned_data.get("username"), e)
                return HttpResponse(
                    content=f"Last.fm API error: {str(e)}. Please check the username and try again.",
                    status=400
                )
            except pylast.NetworkError as e:
                logger.error("Network error while generating wordcloud: %s", e)
                return HttpResponse(
                    content="Network error. Please try again later.",
                    status=503
                )
            except Exception:
                logger.exception("Unexpected error generating wordcloud for user %s", form.cleaned_data.get("username"))
                return HttpResponse(
                    content="An unexpected error occurred while generating the wordcloud. Please try again later.",
                    status=500
                )

            response = HttpResponse(content.getvalue(), content_type="image/png")
            timestamp = int(datetime.timestamp(datetime.now()))
            response["Content-Disposition"] = (
                f"attachment; filename=wordcloud_{form.cleaned_data['username']}"
                f"_{form.cleaned_data['timeframe']}_{timestamp}.png"
            )

            # Clean up BytesIO object
            content.close()

            return response

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LastfmWCForm()

    return render(request, "lastfm_wordcloud/lastfm_wordcloud.html", {"form": form})
