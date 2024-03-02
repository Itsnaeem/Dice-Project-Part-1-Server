# Dice-Project-Part-1-Server

In this part, build Server container using Docker.

# Server Application

This repository contains the server application for serving files and their checksums to clients.

## Setup Instructions

1. **Choose an appropriate base image from the Official Images list.**

2. **Create a Dockerfile for the server container with the following specifications:**

    ```Dockerfile
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
    ```

3. **Use Docker Compose to define and run the server container:**

    ```yaml
    version: '3'

    services:
      server:
        build: ./server
        ports:
          - "5000:5000"
        volumes:
          - serverdata:/app/serverdata
        networks:
          - app-network

    volumes:
      serverdata:
    ```

4. **Write a server application in your preferred language that does the following:**

    ```python
    import os
    import random
    import hashlib
    from flask import Flask, send_file

    app = Flask(__name__)

    @app.route('/')
    def index():
        return 'This is the server. To get a file, go to /get_file.'

    @app.route('/get_file')
    def get_file():
        file_path = '/app/serverfile.txt'  # Adjusted file path
        file_size = 1024  # 1KB
        random_data = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', k=file_size))
        with open(file_path, 'w') as file:
            file.write(random_data)
        checksum = hashlib.sha256(random_data.encode()).hexdigest()
        return send_file(file_path), 200, {'Checksum': checksum}

    if __name__ == '__main__':
        if not os.path.exists('/app'):
            os.makedirs('/app')
        app.run(host='0.0.0.0', port=5000)
    ```

5. **Ensure the client application is running and accessible at the specified URL (`http://client:5001`).**

6. **Run the server application by building the Docker container and starting it with Docker Compose.**

7. **Pull both the coded in one directory & run the docker compose up**