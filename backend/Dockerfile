# --- Backend image: Flask JSON API served by gunicorn -------------------------
FROM python:3.12-slim

# Build tools + MySQL client headers. PyMySQL itself is pure-Python, but this is
# the standard "build deps for a MySQL driver" layer and covers building any
# wheel (e.g. cryptography) that lacks a prebuilt binary for this platform.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install dependencies first for better Docker layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Production process: gunicorn serving the WSGI app (prod config) on all IFs.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "wsgi:app"]
