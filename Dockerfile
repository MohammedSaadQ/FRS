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
CMD ["python", "main.py"]

# fix issues in images
F# Use the official Debian Bullseye image as the base
FROM debian:bullseye

# Update package list and install the specific versions of packages
RUN apt-get update && \
    apt-get install -y \
    libssl3=3.0.13-1~deb12u1 \
    openssl=3.0.13-1~deb12u1 \
    libgnutls30=3.7.9-2+deb12u3 \
    libudev1=252.23-1~deb12u1 \
    libsystemd0=252.23-1~deb12u1 \
    libkrb5-3=1.20.1-2+deb12u2 \
    libkrb5support0=1.20.1-2+deb12u2 \
    libgssapi-krb5-2=1.20.1-2+deb12u2 \
    libk5crypto3=1.20.1-2+deb12u2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


