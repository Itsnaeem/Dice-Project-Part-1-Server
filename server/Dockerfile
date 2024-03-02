# Use an appropriate base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy server application files
COPY server.py .

# Expose port if needed
EXPOSE 5000

# Command to run the server application
CMD ["python", "server.py"]
