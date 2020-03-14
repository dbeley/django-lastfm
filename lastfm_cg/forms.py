from django import forms


class LastfmCGForm(forms.Form):
    username = forms.CharField(label="lastfm username", max_length=100)
    TIMEFRAME_CHOICES = (
        ("7day", "last week"),
        ("1month", "last month"),
        ("3month", "last 3 months"),
        ("6month", "last 6 months"),
        ("12month", "last year"),
        ("overall", "overall"),
    )
    timeframe = forms.ChoiceField(choices=TIMEFRAME_CHOICES)
    columns = forms.IntegerField(min_value=1, max_value=100, initial=5)
    rows = forms.IntegerField(min_value=1, max_value=100, initial=5)
