# Use the official Python image as the base image
FROM python:3.12.2-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Update the package list and install necessary packages
RUN apt-get update && apt-get install -y \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python application code into the container
COPY . .

# Expose the port that the application will listen on
EXPOSE 8080

# Set the command to run the Python application
#CMD ["python", "main.py"]
CMD ["python", "appv3.py"]
#CMD ["python", "New.py"]
