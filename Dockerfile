FROM python:3.12-slim

LABEL maintainer="IngredientIQ Team"
LABEL description="IngredientIQ - Product Safety Intelligence API"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libtesseract-dev \
    libopencv-dev \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt .
COPY src/ ./src/
COPY pipeline/ ./pipeline/
COPY data/ ./data/
COPY models/ ./models/
COPY run_pipeline.py .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN useradd -m -u 1000 ingredientiq && \
    chown -R ingredientiq:ingredientiq /app

USER ingredientiq

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Start API server
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
