# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# No system graphics dependencies needed with opencv-python-headless

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

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
