# Use the official Python 3.12 slim image as the base
FROM python:3.12-slim

# Install PostgreSQL dependencies instead of MySQL
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the contents of the current directory to /app in the container
COPY . .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Start the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
