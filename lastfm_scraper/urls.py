from django.urls import path

from . import views

urlpatterns = [
    path("", views.lastfm_scraper, name="scraping"),
]
