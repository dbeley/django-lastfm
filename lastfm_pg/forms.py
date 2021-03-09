from django import forms


class LastfmPGForm(forms.Form):
    username = forms.CharField(label="Lastfm username", max_length=100)
    TIMEFRAME_CHOICES = (
        ("7day", "last week"),
        ("1month", "last month"),
        ("3month", "last 3 months"),
        ("6month", "last 6 months"),
        ("12month", "last year"),
        ("overall", "overall"),
    )
    timeframe = forms.ChoiceField(choices=TIMEFRAME_CHOICES)
    playlist_size = forms.IntegerField(
        label="Playlist size (1-100)", min_value=1, max_value=100, initial=5
    )
    only_favorites = forms.BooleanField(
        label="Only favorites tracks", required=False, initial=False
    )
    csv = forms.BooleanField(label="CSV Export", required=False, initial=False)
