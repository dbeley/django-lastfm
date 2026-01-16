from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from .forms import (
    LastfmArtistsByGenre,
    LastfmArtistInformation,
    LastfmCompleteTimeline,
    LastfmAllFavoriteTracks,
)

from .tasks import (
    fetch_new_tracks,
    get_all_favorite_tracks,
    get_artist_info,
    get_artists_genre,
)
import pandas as pd
import logging

logger = logging.getLogger(__name__)


# Create your views here.
def lastfm_scraper(request):
    # if this is a POST request we need to process the form data
    if request.method == "POST":
        if "formtimeline" in request.POST:
            try:
                formtimeline = LastfmCompleteTimeline(request.POST)
            except Exception as e:
                logger.exception("Error creating timeline form")
                return HttpResponseBadRequest("Invalid form data")
            
            if formtimeline.is_valid():
                try:
                    logger.info(
                        "Fetching complete timeline for %s",
                        formtimeline.cleaned_data["username"],
                    )
                    task = fetch_new_tracks.delay(
                        formtimeline.cleaned_data["username"]
                    )
                    
                    # Return task ID for client-side polling instead of blocking
                    # TODO: Implement proper async handling with task status endpoint
                    # For now, we wait with a timeout to maintain backward compatibility
                    # but this should be replaced with a proper async solution
                    max_wait = 300  # 5 minutes timeout
                    waited = 0
                    while task.state not in ("SUCCESS", "FAILURE") and waited < max_wait:
                        import time
                        time.sleep(0.5)
                        waited += 0.5
                    
                    if task.state == "FAILURE":
                        logger.error("Task failed for user %s", formtimeline.cleaned_data["username"])
                        return HttpResponseBadRequest("Failed to fetch timeline. Please try again.")
                    elif waited >= max_wait:
                        logger.warning("Task timed out for user %s", formtimeline.cleaned_data["username"])
                        return HttpResponseBadRequest(
                            "Request timed out. The task is still running in background. "
                            "Task ID: " + str(task.id)
                        )
                    
                    content = pd.read_json(task.get())
                except Exception as e:
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
            except Exception as e:
                logger.exception("Error creating favorite tracks form")
                return HttpResponseBadRequest("Invalid form data")
            
            if formfavorite.is_valid():
                try:
                    logger.info(
                        "Fetching favorite tracks for %s",
                        formfavorite.cleaned_data["username"],
                    )
                    task = get_all_favorite_tracks.delay(
                        formfavorite.cleaned_data["username"]
                    )
                    
                    max_wait = 300
                    waited = 0
                    while task.state not in ("SUCCESS", "FAILURE") and waited < max_wait:
                        import time
                        time.sleep(0.5)
                        waited += 0.5
                    
                    if task.state == "FAILURE":
                        logger.error("Task failed for user %s", formfavorite.cleaned_data["username"])
                        return HttpResponseBadRequest("Failed to fetch favorite tracks. Please try again.")
                    elif waited >= max_wait:
                        logger.warning("Task timed out for user %s", formfavorite.cleaned_data["username"])
                        return HttpResponseBadRequest("Request timed out. Please try again.")
                    
                    content = task.get()
                except Exception as e:
                    logger.exception("Error fetching favorites for user %s", formfavorite.cleaned_data.get("username"))
                    return HttpResponseBadRequest("An error occurred while fetching favorite tracks.")
                
                return HttpResponse(content, content_type="text/plain")
                
        elif "formgenre" in request.POST:
            try:
                formgenre = LastfmArtistsByGenre(request.POST)
            except Exception as e:
                logger.exception("Error creating genre form")
                return HttpResponseBadRequest("Invalid form data")
            
            if formgenre.is_valid():
                try:
                    logger.info(
                        "Fetching artists for genre %s", formgenre.cleaned_data["genre"]
                    )
                    task = get_artists_genre.delay(formgenre.cleaned_data["genre"])
                    
                    max_wait = 300
                    waited = 0
                    while task.state not in ("SUCCESS", "FAILURE") and waited < max_wait:
                        import time
                        time.sleep(0.5)
                        waited += 0.5
                    
                    if task.state == "FAILURE":
                        logger.error("Task failed for genre %s", formgenre.cleaned_data["genre"])
                        return HttpResponseBadRequest("Failed to fetch artists. Please try again.")
                    elif waited >= max_wait:
                        logger.warning("Task timed out for genre %s", formgenre.cleaned_data["genre"])
                        return HttpResponseBadRequest("Request timed out. Please try again.")
                    
                    content = task.get()
                except Exception as e:
                    logger.exception("Error fetching artists for genre %s", formgenre.cleaned_data.get("genre"))
                    return HttpResponseBadRequest("An error occurred while fetching artists.")
                
                return HttpResponse(content, content_type="text/plain")
                
        elif "forminfo" in request.POST:
            try:
                forminfo = LastfmArtistInformation(request.POST)
            except Exception as e:
                logger.exception("Error creating artist info form")
                return HttpResponseBadRequest("Invalid form data")
            
            if forminfo.is_valid():
                try:
                    logger.info(
                        "Fetching artists info for %s", forminfo.cleaned_data["artist"]
                    )
                    task = get_artist_info.delay(forminfo.cleaned_data["artist"])
                    
                    max_wait = 300
                    waited = 0
                    while task.state not in ("SUCCESS", "FAILURE") and waited < max_wait:
                        import time
                        time.sleep(0.5)
                        waited += 0.5
                    
                    if task.state == "FAILURE":
                        logger.error("Task failed for artist %s", forminfo.cleaned_data["artist"])
                        return HttpResponseBadRequest("Failed to fetch artist information. Please try again.")
                    elif waited >= max_wait:
                        logger.warning("Task timed out for artist %s", forminfo.cleaned_data["artist"])
                        return HttpResponseBadRequest("Request timed out. Please try again.")
                    
                    content = task.get()
                except Exception as e:
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
