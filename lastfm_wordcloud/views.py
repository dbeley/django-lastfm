from django.shortcuts import render

from deps.lastfm_wordcloud.lastfm_wordcloud.__main__ import create_lastfm_wordcloud
from lastfm_django.utils import lastfmconnect
from .forms import LastfmWCForm
from django.http import HttpResponse
from datetime import datetime
import logging

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
            except Exception as e:
                print(e)
                return HttpResponse(content=e, status=400)
            response = HttpResponse(content.getvalue(), content_type="image/png")
            response["Content-Disposition"] = (
                f"attachment; filename=wordcloud_{form.cleaned_data['username']}_{form.cleaned_data['timeframe']}_{int(datetime.timestamp(datetime.now()))}.png"
            )
            return response

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LastfmWCForm()

    return render(request, "lastfm_wordcloud/lastfm_wordcloud.html", {"form": form})
