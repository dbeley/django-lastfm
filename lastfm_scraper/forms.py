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


class LastfmAllFavoriteTracks(forms.Form):
    username = forms.CharField(label="Lastfm username", max_length=100)
