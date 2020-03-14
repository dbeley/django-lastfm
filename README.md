# lastfm_django

## Secrets

You need some config files for the apps to work.

### secret.ini
```
[django]
SECRET_KEY = secret_key_here
```

### config_lastfm.ini
```
[lastfm]
username=username_here
api_key=api_key_here
api_secret=api_secret_here
```

### Environment variables

If you can't use ini files (i.e. when deploying for heroku), you can use those environment variables :

- `PYLAST_USERNAME`
- `PYLAST_API_KEY`
- `PYLAST_API_SECRET`
- `DJANGO_SECRET_KEY`
