# SuperInstance Research Platform - Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install CuPy for GPU support (optional)
# Uncomment the appropriate line for your CUDA version:
# RUN pip install cupy-cuda12x  # For CUDA 12.x
# RUN pip install cupy-cuda11x  # For CUDA 11.x

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /app/research/phase8_platform/data/{cache,results,experiments}

# Set environment variables
ENV PYTHONPATH=/app
ENV PLATFORM_DATA_DIR=/app/research/phase8_platform/data
ENV PLATFORM_LOG_LEVEL=INFO

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "web_interface:app", "--host", "0.0.0.0", "--port", "8000"]
