import re

from django import forms

from lastfm_django.constants import TIMEFRAME_CHOICES


class LastfmPGForm(forms.Form):
    username = forms.CharField(
        label="Lastfm username",
        max_length=100,
        min_length=1,
        help_text="Enter your Last.fm username"
    )
    timeframe = forms.ChoiceField(choices=TIMEFRAME_CHOICES)
    playlist_size = forms.IntegerField(
        label="Playlist size (1-100)", min_value=1, max_value=100, initial=5
    )
    only_favorites = forms.BooleanField(
        label="Only favorites tracks", required=False, initial=False
    )
    csv = forms.BooleanField(label="CSV Export", required=False, initial=False)

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError("Username cannot be empty.")
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise forms.ValidationError(
                "Username can only contain letters, numbers, hyphens, and underscores."
            )
        return username
