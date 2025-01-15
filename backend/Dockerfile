FROM python:3.10-slim

LABEL maintainer="your_name <your_email@example.com>"
LABEL description="Backend for DELTA hydrological AI research assistant"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONIOENCODING=utf-8

WORKDIR /app

# Install system dependencies including wget for downloading wait-for-it
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    wget \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Download wait-for-it script
RUN wget -O /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh \
    && chmod +x /usr/local/bin/wait-for-it.sh

# Copy requirements first for better caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application files
COPY api /app/api
COPY alembic /app/alembic
COPY modules /app/modules
COPY utils /app/utils
COPY alembic.ini /app/alembic.ini
COPY request.json /app/request.json

# Copy the Google Cloud credentials file (now using relative path)
COPY google-credentials.json /app/google-credentials.json

EXPOSE 8000
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/google-credentials.json

# Create and setup start script
COPY <<EOF /app/start.sh
#!/bin/bash
wait-for-it.sh db:5432 -t 60 -- echo "Database is up"
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
EOF

RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]