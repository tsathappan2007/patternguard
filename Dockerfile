# Production Multi-Stage Dockerfile for Houdini
# Fully self-contained: includes Node.js (builds React UI), Python 3.11, Playwright Headless Chromium, & FastAPI

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8000

WORKDIR /app

# Install system dependencies, Node.js, and browser dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    build-essential \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    playwright install chromium --with-deps

# Copy Frontend and Build Production Bundle
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm install
COPY frontend/ ./
RUN npm run build

# Switch back to app root and copy Backend & source files
WORKDIR /app
COPY backend/ ./backend/
COPY README.md .

# Expose port (supports Render/Railway dynamic $PORT)
EXPOSE 8000

# Start FastAPI server with single-port fullstack hosting
CMD python -m uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}

