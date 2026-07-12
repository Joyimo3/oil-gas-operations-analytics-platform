# ============================================================
# OIL & GAS OPERATIONS - DOCKERFILE
# Defines the container environment for the pipeline
# ============================================================

# Base image - Python 3.12 on lightweight Linux
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project into container
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/clean data/errors data/alerts logs monitoring

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command - runs the full pipeline
CMD ["python", "-m", "Scripts.run_pipeline"]