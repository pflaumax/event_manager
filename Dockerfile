FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc libpq-dev pkg-config git curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копіюємо код (для production збірки)
COPY . /app

ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=event_manager.settings
# CMD задається у docker-compose (dev/prod)
