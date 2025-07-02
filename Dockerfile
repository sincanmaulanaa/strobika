FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements file first for better caching
COPY requirements-prod.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application files
COPY app.py .
COPY best.pt .
COPY templates/ templates/
COPY static/ static/

# Create necessary directories
RUN mkdir -p /tmp/uploads /app/static/results

# Make PORT available to the application
ENV PORT=8080

# Run as non-root user for better security
RUN useradd -m appuser
USER appuser

# CMD will be overridden by Heroku
CMD gunicorn --bind 0.0.0.0:$PORT app:app