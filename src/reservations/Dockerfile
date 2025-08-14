FROM python:3.13-slim

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN mkdir -p "src"

# Install Poetry
RUN pip install --upgrade pip \
    && pip install poetry==2.1.4


RUN poetry install --no-root

# Expose the port for Uvicorn
EXPOSE 8000