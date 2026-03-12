# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for ML packages and health checks
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (default for uvicorn but overridden by PORT environment variable)
EXPOSE 8080

# Use a shell to allow environment variable expansion for the PORT
CMD uvicorn render_app:app --host 0.0.0.0 --port ${PORT:-10000} --timeout-keep-alive 120
