provider "aws" {
  region = "us-east-1"
}

# 1. S3 Bucket for Artifacts
resource "aws_s3_bucket" "mlops_artifacts" {
  bucket = "mlops-cv-artifacts-bucket-${random_id.bucket_suffix.hex}"
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# 2. ECR Repository for Docker Images
resource "aws_ecr_repository" "cv_pipeline_repo" {
  name                 = "cv-pipeline"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# 3. Security Group for Jenkins EC2
resource "aws_security_group" "jenkins_sg" {
  name        = "jenkins_sg"
  description = "Allow SSH and Jenkins inbound traffic"

  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Jenkins UI from anywhere"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# 4. EC2 Instance for Jenkins Server
resource "aws_instance" "jenkins_server" {
  # Amazon Linux 2023 AMI in us-east-1
  ami           = "ami-051f8a213df8bc089" 
  instance_type = "t3.medium" # t3.medium recommended for Jenkins to avoid memory issues

  vpc_security_group_ids = [aws_security_group.jenkins_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.jenkins_profile.name

  # Run the bash script on startup to install Jenkins and Docker
  user_data = file("${path.module}/install_jenkins.sh")

  tags = {
    Name = "Jenkins-MLOps-Server"
  }
}

output "jenkins_url" {
  value = "http://${aws_instance.jenkins_server.public_ip}:8080"
}
