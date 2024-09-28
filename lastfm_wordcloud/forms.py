from django import forms


class LastfmWCForm(forms.Form):
    username = forms.CharField(label="Lastfm username", max_length=100)
    TIMEFRAME_CHOICES = (
        ("7day", "last week"),
        ("1month", "last month"),
        ("3month", "last 3 months"),
        ("6month", "last 6 months"),
        ("12month", "last year"),
        ("overall", "overall"),
    )
    timeframe = forms.ChoiceField(label="Timeframe", choices=TIMEFRAME_CHOICES)
    artists_count = forms.IntegerField(
        label="Artist count", min_value=1, max_value=500, initial=50
    )
    top_tags_count = forms.IntegerField(
        label="Top tags by artist", min_value=1, max_value=30, initial=4
    )
