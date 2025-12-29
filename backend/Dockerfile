# Use the official Python image as the base image
FROM python:3.9-slim

# Install system dependencies for scientific libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgdal-dev \
    libproj-dev \
    gdal-bin \
    netcdf-bin \
    libnetcdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt /app/

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Install psycopg2-binary explicitly
RUN pip install --no-cache-dir psycopg2-binary

# Copy the api directory
COPY api /app/api

# Copy alembic configuration and migrations
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic

# Copy utils
COPY utils /app/utils

# Copy modules
COPY modules /app/modules

# Copy the google-credentials.json file
RUN echo "{}" > /app/google-credentials.json

# Expose the port that the application will run on
EXPOSE 8000

# Copy the wait-for-it.sh script into the container
COPY wait-for-it.sh /app/wait-for-it.sh

# Give execution permissions to the wait-for-it.sh script
RUN chmod +x /app/wait-for-it.sh

# Copy the start.sh script into the container
COPY start.sh /app/start.sh

# Give execution permissions to the start.sh script
RUN chmod +x /app/start.sh

# Set the command to run when the container starts
CMD ["/app/start.sh"]