# Use lightweight Python image
FROM python:3.11-slim

# ------------------------------------------
# Set working directory
# ------------------------------------------
WORKDIR /app


# ------------------------------------------
# Copy requirements first
# ------------------------------------------
COPY requirements.txt .


# ------------------------------------------
# Install Python packages
# ------------------------------------------
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ------------------------------------------
# Create model folder
# ------------------------------------------
RUN mkdir -p /app/models


# ------------------------------------------
# Download trained model from Google Drive
# Fixed gdown syntax
# ------------------------------------------
RUN pip install --no-cache-dir gdown && \
    gdown "https://drive.google.com/uc?id=1eLD9E7SAu76ksd25AquQmVJpo-_MQ2F9" \
    -O /app/models/masktif_model.pth


# ------------------------------------------
# Copy project files
# ------------------------------------------
COPY backend/ ./backend/
COPY models/ ./models/
COPY config.py .


# ------------------------------------------
# Move into backend folder
# ------------------------------------------
WORKDIR /app/backend


# ------------------------------------------
# Expose Flask/Gunicorn port
# ------------------------------------------
EXPOSE 5001


# ------------------------------------------
# Start production server
# ------------------------------------------
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--timeout", "120", "--workers", "1", "app:app"]
