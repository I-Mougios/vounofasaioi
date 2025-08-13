FROM python:3.13-slim

WORKDIR /app

# Install system dependencies first
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .

RUN mkdir -p "src"

RUN pip install --upgrade pip && pip install -e .
