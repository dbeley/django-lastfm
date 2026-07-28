import re

from django import forms

from lastfm_django.constants import TIMEFRAME_CHOICES


class LastfmWCForm(forms.Form):
    username = forms.CharField(
        label="Lastfm username",
        max_length=100,
        min_length=1,
        help_text="Enter your Last.fm username"
    )
    timeframe = forms.ChoiceField(label="Timeframe", choices=TIMEFRAME_CHOICES)
    artists_count = forms.IntegerField(
        label="Artist count", min_value=1, max_value=500, initial=50
    )
    top_tags_count = forms.IntegerField(
        label="Top tags by artist", min_value=1, max_value=30, initial=4
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError("Username cannot be empty.")
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise forms.ValidationError(
                "Username can only contain letters, numbers, hyphens, and underscores."
            )
        return username
