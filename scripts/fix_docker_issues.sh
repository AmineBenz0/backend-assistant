#!/bin/bash
# Docker troubleshooting script for Linux/WSL

echo "=== Docker Troubleshooting Script ==="

# Check Docker status
echo "1. Checking Docker status..."
sudo systemctl status docker

# Stop Docker services
echo "2. Stopping Docker services..."
sudo systemctl stop docker
sudo systemctl stop docker.socket

# Clean up Docker resources
echo "3. Cleaning up Docker resources..."
sudo docker system prune -af --volumes 2>/dev/null || true
sudo rm -rf /var/lib/docker/tmp/* 2>/dev/null || true

# Restart Docker
echo "4. Restarting Docker..."
sudo systemctl start docker
sudo systemctl enable docker

# Wait for Docker to be ready
echo "5. Waiting for Docker to be ready..."
sleep 5

# Test Docker
echo "6. Testing Docker..."
docker --version
docker info

echo "=== Docker troubleshooting complete ==="
echo "Try running your docker-compose command again"