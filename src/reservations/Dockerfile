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

# Install required Python packages
RUN pip install --no-cache-dir \
    pydantic \
    "pydantic[email]" \
    sqlalchemy \
    pymysql \
    cryptography \
    python-dotenv \
    "fastapi[all]" \
    uvicorn \
    python-dateutil \
    icecream

# Set PYTHONPATH so you can import from `src/`
ENV PYTHONPATH=/app/src

# Expose the port for Uvicorn
EXPOSE 8000