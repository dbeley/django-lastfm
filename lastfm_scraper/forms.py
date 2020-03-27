from django import forms


class LastfmArtistsByGenre(forms.Form):
    genre = forms.CharField(
        label="Genres (separated by comma).", max_length=1000
    )


class LastfmArtistInformation(forms.Form):
    artist = forms.CharField(
        label="Artists (separated by comma).", max_length=1000
    )


class LastfmCompleteTimeline(forms.Form):
    username = forms.CharField(label="Lastfm username", max_length=100)

    export_format = forms.ChoiceField(
        label="Export format",
        choices=(("csv", "Export in csv"), ("xlsx", "Export in xlsx")),
    )


class LastfmAllFavoriteTracks(forms.Form):
    username = forms.CharField(label="Lastfm username", max_length=100)
