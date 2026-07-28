FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1
WORKDIR /code

# Install system dependencies for Pillow, numpy, matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libjpeg-dev zlib1g-dev libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=lastfm_django.settings \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /code

# Install only runtime system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

EXPOSE 8000

RUN python manage.py collectstatic --noinput --clear 2>/dev/null || true

CMD ["gunicorn", "lastfm_django.wsgi", "--bind", "0.0.0.0:8000", "--timeout", "600"]
