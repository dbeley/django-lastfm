from django import forms


class LastfmCGForm(forms.Form):
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
    rows = forms.IntegerField(label="Row number", min_value=1, max_value=100, initial=5)
    columns = forms.IntegerField(
        label="Column number", min_value=1, max_value=100, initial=5
    )
    top100 = forms.BooleanField(
        label="Top 100 (special collage mode, will override row and column number)",
        required=False,
        initial=False,
    )
