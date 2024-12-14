#!/bin/bash

# Update system
echo "Updating system..."
sudo apt update && sudo apt upgrade -y

# Install prerequisites
echo "Installing prerequisites..."
sudo apt install -y curl wget gnupg apt-transport-https software-properties-common lsb-release

# Clean existing conflicting packages
echo "Cleaning conflicting packages..."
sudo apt remove -y docker docker-engine docker.io containerd runc

# Install Docker
echo "Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER

# Install Kubectl
echo "Installing Kubectl..."
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/kubernetes-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt update && sudo apt install -y kubectl

# Install Node.js
echo "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install PostgreSQL
echo "Installing PostgreSQL..."
sudo apt install -y postgresql postgresql-contrib

# Install Prometheus
echo "Installing Prometheus..."
PROM_VERSION="2.45.0"
wget https://github.com/prometheus/prometheus/releases/download/v$PROM_VERSION/prometheus-$PROM_VERSION.linux-amd64.tar.gz
tar -xvf prometheus-$PROM_VERSION.linux-amd64.tar.gz
sudo mv prometheus-$PROM_VERSION.linux-amd64/prometheus /usr/local/bin/
sudo mv prometheus-$PROM_VERSION.linux-amd64/promtool /usr/local/bin/
sudo mkdir -p /etc/prometheus
sudo mv prometheus-$PROM_VERSION.linux-amd64/prometheus.yml /etc/prometheus/prometheus.yml
sudo rm -rf prometheus-$PROM_VERSION.linux-amd64 prometheus-$PROM_VERSION.linux-amd64.tar.gz

# Install Grafana
echo "Installing Grafana..."
GRAFANA_VERSION="9.5.3"
wget https://dl.grafana.com/oss/release/grafana-$GRAFANA_VERSION_amd64.deb
sudo dpkg -i grafana-$GRAFANA_VERSION_amd64.deb
sudo systemctl enable --now grafana-server
sudo rm grafana-$GRAFANA_VERSION_amd64.deb

# Install Git
echo "Installing Git..."
sudo apt install -y git

# Configure Git
echo "Configuring Git..."
read -p "Please enter your GitHub email: " GIT_EMAIL
read -p "Please enter your GitHub username: " GIT_USERNAME
git config --global user.email "$GIT_EMAIL"
git config --global user.name "$GIT_USERNAME"

echo "All tools installed and configured! Please restart your terminal or system for changes to take effect."
