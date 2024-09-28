from django.urls import path

from . import views

urlpatterns = [
    path("", views.lastfm_wordcloud, name="lastfm_wordcloud"),
]
