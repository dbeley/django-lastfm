from django.shortcuts import render
from .forms import LastfmCGForm
from django.http import HttpResponse, FileResponse
from .lastfm_cg import lastfmconnect, get_lastfm_collage
import io


def get_lastfm_cg(form):
    username = form.cleaned_data["username"]
    timeframe = form.cleaned_data["timeframe"]
    rows = form.cleaned_data["rows"]
    columns = form.cleaned_data["columns"]

    network = lastfmconnect()
    user = network.get_user(username)
    return get_lastfm_collage(user, timeframe, rows, columns)


# Create your views here.
def lastfm_cg(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = LastfmCGForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            # return HttpResponseRedirect("/thanks/")
            # create object
            # return HttpResponse("<h1>marche</h1>")
            content = get_lastfm_cg(form)
            # response = FileResponse(as_attachment=True, filename="cover.jpg",)
            response = HttpResponse(content_type="image/png")
            response[
                "Content-Disposition"
            ] = "attachment; filename=lastfm_cg.png"
            content.save(response, "PNG")
            return response

    # if a GET (or any other method) we'll create a blank form
    else:
        # form = NameForm()
        form = LastfmCGForm()

    return render(request, "lastfm_cg/lastfm_cg.html", {"form": form})
