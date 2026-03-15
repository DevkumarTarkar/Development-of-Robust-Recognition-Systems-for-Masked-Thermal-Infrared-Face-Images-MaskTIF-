# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# No system graphics dependencies needed with opencv-python-headless

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the large model into the Docker image directly.
# This prevents downloading it during cold starts, bypassing Render's 100-second timeout.
RUN mkdir -p /app/models
RUN gdown --id 1eLD9E7SAu76ksd25AquQmVJpo-_MQ2F9 -O /app/models/masktif_model.pth

# Copy the backend code and models into the container
COPY backend/ ./backend/
COPY models/ ./models/
COPY config.py .

# Set the working directory to the backend folder for execution
WORKDIR /app/backend

# Expose the port Gunicorn will run on
EXPOSE 5001

# Run the Flask app using Gunicorn for production readiness
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--timeout", "120", "--workers", "1", "app:app"]
