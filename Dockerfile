# Dockerfile — FlowKit Backend & Pipeline Service
FROM python:3.11-slim

# Install system dependencies (FFmpeg, git, build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose API port
EXPOSE 8100

# Run FastAPI backend with Uvicorn
CMD ["uvicorn", "agent.main:app", "--host", "0.0.0.0", "--port", "8100"]
