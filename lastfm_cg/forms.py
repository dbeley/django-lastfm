import re

from django import forms

from lastfm_django.constants import TIMEFRAME_CHOICES


class LastfmCGForm(forms.Form):
    username = forms.CharField(
        label="Lastfm username",
        max_length=100,
        min_length=1,
        help_text="Enter your Last.fm username"
    )
    timeframe = forms.ChoiceField(label="Timeframe", choices=TIMEFRAME_CHOICES)
    rows = forms.IntegerField(label="Row number", min_value=1, max_value=100, initial=5)
    columns = forms.IntegerField(
        label="Column number", min_value=1, max_value=100, initial=5
    )
    top100 = forms.BooleanField(
        label="Top 100 (special collage mode, will override row and column number)",
        required=False,
        initial=False,
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
