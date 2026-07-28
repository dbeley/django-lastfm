import re

from django import forms


class LastfmArtistsByGenre(forms.Form):
    genre = forms.CharField(
        label="Genres (separated by comma).",
        max_length=1000,
        help_text="Enter one or more genres separated by commas"
    )

    def clean_genre(self):
        genre = self.cleaned_data.get('genre', '')
        # Remove excessive whitespace and validate
        genres = [g.strip() for g in genre.split(',') if g.strip()]
        if not genres:
            raise forms.ValidationError("Please enter at least one genre.")
        if len(genres) > 20:
            raise forms.ValidationError("Maximum 20 genres allowed.")
        return ', '.join(genres)


class LastfmArtistInformation(forms.Form):
    artist = forms.CharField(
        label="Artists (separated by comma).",
        max_length=1000,
        help_text="Enter one or more artist names separated by commas"
    )

    def clean_artist(self):
        artist = self.cleaned_data.get('artist', '')
        # Remove excessive whitespace and validate
        artists = [a.strip() for a in artist.split(',') if a.strip()]
        if not artists:
            raise forms.ValidationError("Please enter at least one artist name.")
        if len(artists) > 50:
            raise forms.ValidationError("Maximum 50 artists allowed.")
        return ', '.join(artists)


class LastfmCompleteTimeline(forms.Form):
    username = forms.CharField(
        label="Lastfm username",
        max_length=100,
        min_length=1,
        help_text="Enter your Last.fm username"
    )

    export_format = forms.ChoiceField(
        label="Export format",
        choices=(("csv", "Export in csv"), ("xlsx", "Export in xlsx")),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not username:
            raise forms.ValidationError("Username cannot be empty.")
        # Last.fm usernames: alphanumeric, hyphens, underscores (2-15 chars typically)
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise forms.ValidationError(
                "Username can only contain letters, numbers, hyphens, and underscores."
            )
        return username


class LastfmAllFavoriteTracks(forms.Form):
    username = forms.CharField(
        label="Lastfm username",
        max_length=100,
        min_length=1,
        help_text="Enter your Last.fm username"
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
