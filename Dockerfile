FROM python:3.13-slim

WORKDIR /app

# Install system dependencies (ffmpeg is required for video processing)
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose FastAPI port
EXPOSE 8100

# Run FastAPI and Worker (assuming a startup script or uvicorn)
CMD ["uvicorn", "agent.api.main:app", "--host", "0.0.0.0", "--port", "8100"]
