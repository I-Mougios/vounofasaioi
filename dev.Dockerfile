FROM python:3.13-slim

WORKDIR /app

# Install system dependencies first
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN mkdir -p "src"
RUN touch /app/src/__init__.py

# Install Poetry
RUN pip install --upgrade pip \
    && pip install poetry==2.1.4

RUN poetry install --with dev
