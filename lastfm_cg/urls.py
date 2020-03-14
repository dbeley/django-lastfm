from django.urls import path

from . import views

urlpatterns = [
    path("", views.lastfm_cg, name="lastfm_cg"),
]
