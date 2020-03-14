from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("lastfm_pg", views.lastfm_pg, name="lastfm_pg"),
]
