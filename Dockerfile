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
