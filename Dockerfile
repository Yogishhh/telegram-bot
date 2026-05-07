# Use a slim Python image for efficiency
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create database directory (just in case SQLite is used temporarily)
RUN mkdir -p database

# Expose the port for the keep-alive server
EXPOSE 8080

# Command to run the bot
CMD ["python", "main.py"]
