# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt requirements.txt

# Install curl and other dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get clean

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python packages with specific index for torch and torchvision CPU versions
RUN pip install --no-cache-dir --default-timeout=1200 \
    -r requirements.txt \
    -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Copy the rest of the application code
COPY . .

# Set environment variables for Flask
ENV FLASK_APP=server.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Command to run the Flask application
CMD ["flask", "run"]
