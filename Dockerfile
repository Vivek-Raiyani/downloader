# Use an official Python slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DOWNLOAD_DIR=/app/downloads

# Repository URL (You can pass this as a build arg or hardcode it)
ARG REPO_URL="https://github.com/Vivek-Raiyani/downloader.git"

# Install system dependencies (ffmpeg and git)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Clone the repository
RUN git clone ${REPO_URL} .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create downloads directory
RUN mkdir -p /app/downloads

# Expose the application port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
