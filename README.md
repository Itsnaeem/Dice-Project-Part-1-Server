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

---


## Part 2: Creating VMs, Infrastructure as Code (IaC)

### 2a. AWS EC2 Instances Setup

Create two AWS EC2 instances:
- **Server Container Host**: To host the server application.
- **Client Container Host**: To host the client application.

Instance type for both: `t2.micro` (covered under the AWS free tier).

### 2b. VPC and Subnets Configuration

Configure the VPC and subnets to allow communication between the two EC2 instances, ensuring they can interact as required by the application architecture.

### 2c. Infrastructure Automation with Terraform

Automate the creation of AWS resources using Terraform. Place Terraform scripts in the "terraform" directory within both the client and server repositories.

#### Terraform Configuration Files

**main.tf**:

```hcl
resource "aws_instance" "server" {
  ami                    = "ami-0f5daaa3a7fb3378b"
  instance_type          = "t2.micro"
  subnet_id              = "subnet-0513fd176fd782647"
  vpc_security_group_ids = ["sg-0ed89c4f337f33716"]
  key_name               = "dice-project-ec2"

  tags = {
    Name = "ServerInstance"
  }
}
```

**provider.tf**:

```hcl
provider "aws" {
  region = "us-east-2"
}
```

## Part 3: Setting up Monitoring Stack

Setup a monitoring stack on each VM to monitor system and container metrics.

### Monitoring Stack Components

- **Prometheus**: For metrics collection.
- **Grafana**: For metrics visualization.
- **Node Exporter**: For host metrics collection.

#### Docker Compose for Monitoring

**docker-compose.monitoring.yml**:

```yaml
version: '3.7'

services:
  prometheus:
    image: prom/prometheus:v2.26.0
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
    command:
      - "--config.file=/etc/prometheus/prometheus.yml"

  grafana:
    image: grafana/grafana:7.5.4
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin  # Secure this
    ports:
      - "3020:3000"
    depends_on:
      - prometheus

  node_exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
```

Ensure Grafana is accessible on port `3020` of each VM, potentially over the internet for EC2 instances.

#### Prometheus Configuration

**prometheus.yml**:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

### Dashboard Configuration

Create dashboards in Grafana to visualize host system metrics and Docker container metrics, utilizing Prometheus as the data source.

---


# CI/CD Pipeline Setup Guide

## Step 1: Configure GitHub Actions for CI/CD

### Server Repository Setup

1. In your server repository, create a `.github/workflows` directory.
2. Add a `deploy.yml` file in the workflows directory with the following content:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Login to Docker Hub
      uses: docker/login-action@v1
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    - name: Build and push Docker image
      run: |
        docker build -t itsnaeemraza/server:${{ github.sha }} ./server
        docker push itsnaeemraza/server:${{ github.sha }}

  deploy:
    runs-on: ubuntu-latest
    needs: build-and-push
    steps:
    - name: Executing remote SSH commands to deploy
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.EC2_HOST }}
        username: ${{ secrets.EC2_USER }}
        key: ${{ secrets.EC2_SSH_KEY }}
        script: |
          cd /home/ubuntu
          git pull
          IMAGE_TAG=${{ github.sha }} sed -i 's|image: itsnaeemraza/server:.*|image: itsnaeemraza/server:'"$IMAGE_TAG"'|' docker-compose.yml
          docker-compose up -d 

   - name: Send notification to Gmail
      uses: dawidd6/action-send-mail@v2
      with:
        server_address: smtp.gmail.com
        server_port: 465
        username: ${{ secrets.EMAIL_USERNAME }}
        password: ${{ secrets.EMAIL_PASSWORD }}
        subject: Deployment Status
        body: Deployment of ${{ github.repository }} was successful. Commit SHA: ${{ github.sha }}
        to: itsnaeemraza@gmail.com
        from: "GitHub Actions <id.naeemraza@gmail.com>"
        secure: true
```

3. Replace placeholders (`yourdockerhubusername`, `your-email@example.com`, etc.) with your actual Docker Hub username, Gmail details, and other specific configurations.

## Step 2: Configure GitHub Secrets

In both repositories, go to Settings > Secrets and add the following secrets:

- `DOCKER_USERNAME`: Your Docker Hub username.
- `DOCKER_PASSWORD`: Your Docker Hub password or access token.
- `EC2_HOST`: Your VM's IP address or domain name.
- `EC2_USER`: The SSH username for your VM.
- `EC2_SSH_KEY`: Your VM's private SSH key.
- `EMAIL_USERNAME`: Your Gmail username.
- `EMAIL_PASSWORD`: Your Gmail password or app-specific password.

## Step 3: Deploy and Monitor

With the GitHub Actions workflows configured, any push to the `main` branch will trigger the CI/CD pipeline, building your Docker images, deploying them to your VM, and sending a deployment notification via Gmail.

