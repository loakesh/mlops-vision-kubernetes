#!/bin/bash
# Update OS
yum update -y

# Install Java 17 (Required for Jenkins)
yum install -y fontconfig java-17-amazon-corretto-devel

# Add Jenkins Repo and Key
wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key

# Install Jenkins
yum install -y jenkins
systemctl enable jenkins
systemctl start jenkins

# Install Docker
yum install -y docker
systemctl enable docker
systemctl start docker

# Add Jenkins user to Docker group so it can build images
usermod -aG docker jenkins
systemctl restart jenkins

# Install Git (Needed for Jenkins to checkout code)
yum install -y git
