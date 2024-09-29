from django.shortcuts import render
from .forms import LastfmCGForm
from django.http import HttpResponse
from .lastfm_cg import lastfmconnect, get_lastfm_collage
from datetime import datetime
import logging

logger = logging.getLogger()


def get_lastfm_cg(form):
    username = form.cleaned_data["username"]
    timeframe = form.cleaned_data["timeframe"]
    rows = form.cleaned_data["rows"]
    columns = form.cleaned_data["columns"]
    top100 = form.cleaned_data["top100"]

    logger.info(
        "Getting collage for %s (%s , rows %s, columns %s, top100 %s",
        username,
        timeframe,
        rows,
        columns,
        top100,
    )

    network = lastfmconnect()
    user = network.get_user(username)
    return get_lastfm_collage(user, timeframe, rows, columns, top100)


# Create your views here.
def lastfm_cg(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = LastfmCGForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            try:
                content = get_lastfm_cg(form)
            except Exception as e:
                print(e)
                return HttpResponse(content=e, status=400)
            response = HttpResponse(content_type="image/png")
            if form.cleaned_data["top100"]:
                response["Content-Disposition"] = (
                    f"attachment; filename=collage_{form.cleaned_data['username']}_{form.cleaned_data['timeframe']}_top100_{int(datetime.timestamp(datetime.now()))}.png"
                )
            else:
                response["Content-Disposition"] = (
                    f"attachment; filename=collage_{form.cleaned_data['username']}_{form.cleaned_data['timeframe']}_{form.cleaned_data['rows']}x{form.cleaned_data['columns']}_{int(datetime.timestamp(datetime.now()))}.png"
                )
            content.save(response, "PNG")
            return response

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LastfmCGForm()

    return render(request, "lastfm_cg/lastfm_cg.html", {"form": form})
