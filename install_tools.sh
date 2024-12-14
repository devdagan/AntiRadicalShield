#!/bin/bash

set -euo pipefail

# =========================================
# Configuration Variables
# =========================================
GIT_EMAIL="devdagan@gmail.com"
GIT_USERNAME="devdagan@gmail.com"
GRAFANA_VERSION="10.2.2"

# =========================================
# Update and Upgrade the System
# =========================================
echo "Updating and upgrading system..."
sudo apt-get update -y
sudo apt-get upgrade -y

# =========================================
# Install General Prerequisites
# =========================================
echo "Installing general prerequisites..."
sudo apt-get install -y \
    curl \
    wget \
    gnupg \
    apt-transport-https \
    software-properties-common \
    lsb-release \
    ca-certificates \
    tar \
    dpkg

# =========================================
# Remove Conflicting Docker Packages
# =========================================
echo "Removing conflicting Docker packages..."
sudo apt-get remove -y docker docker-engine docker.io containerd runc || true

# =========================================
# Install Docker
# =========================================
echo "Installing Docker..."
sudo rm -f /usr/share/keyrings/docker-archive-keyring.gpg
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor \
    -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
 https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
    sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER

# =========================================
# Install Kubectl (Direct Binary Installation)
# =========================================
echo "Installing Kubectl directly from the binary..."
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl

# =========================================
# Install Node.js (v18.x)
# =========================================
echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# =========================================
# Install PostgreSQL
# =========================================
echo "Installing PostgreSQL..."
sudo apt-get install -y postgresql postgresql-contrib

# =========================================
# Install Prometheus
# =========================================
echo "Installing Prometheus..."
PROM_VERSION="2.45.0"
wget https://github.com/prometheus/prometheus/releases/download/v${PROM_VERSION}/prometheus-${PROM_VERSION}.linux-amd64.tar.gz
tar -xvf prometheus-${PROM_VERSION}.linux-amd64.tar.gz
sudo mv prometheus-${PROM_VERSION}.linux-amd64/prometheus /usr/local/bin/
sudo mv prometheus-${PROM_VERSION}.linux-amd64/promtool /usr/local/bin/
sudo mkdir -p /etc/prometheus
sudo mv prometheus-${PROM_VERSION}.linux-amd64/prometheus.yml /etc/prometheus/prometheus.yml
sudo rm -rf prometheus-${PROM_VERSION}.linux-amd64 prometheus-${PROM_VERSION}.linux-amd64.tar.gz

# =========================================
# Install Grafana (From Binary Tarball)
# =========================================
echo "Installing Grafana from binary..."
sudo apt-get install -y adduser libfontconfig1 musl
wget https://dl.grafana.com/enterprise/release/grafana-enterprise_11.4.0_amd64.deb
sudo dpkg -i grafana-enterprise_11.4.0_amd64.deb

# =========================================
# Install Git
# =========================================
echo "Installing Git..."
sudo apt-get install -y git

# =========================================
# Configure Git
# =========================================
echo "Configuring Git..."
git config --global user.email "$GIT_EMAIL"
git config --global user.name "$GIT_USERNAME"

# =========================================
# Final Message
# =========================================
echo "All tools installed and configured!"
echo "Please log out and log back in (or restart) for Docker group changes to take effect."
