FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p /tmp/uploads /app/static/results

# Environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Command to run
CMD gunicorn --bind 0.0.0.0:$PORT app:app