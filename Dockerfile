# Use an official lightweight Python image.
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required by psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Gunicorn will listen on this port. Fly.io will map it to 80/443.
EXPOSE 8080

# The command to run your application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "manage:app"]