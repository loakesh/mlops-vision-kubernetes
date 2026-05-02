pipeline {
    agent any

    environment {
        AWS_REGION = 'us-east-1'
        // In a real pipeline, you would extract the account ID dynamically or inject it via Jenkins parameters
        ECR_REGISTRY = '579763396128.dkr.ecr.us-east-1.amazonaws.com'
        ECR_REPOSITORY = 'cv-pipeline'
        IMAGE_TAG = "${env.BUILD_NUMBER}" // Uses the Jenkins build number as the tag
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('AWS ECR Login') {
            steps {
                // Notice we DO NOT use 'withAWS(credentials: ...)' here!
                // Because the Jenkins EC2 instance has an IAM Role attached, 
                // the AWS CLI automatically picks up the permissions!
                sh '''
                # Retrieve a login token and pipe it into the Docker login command
                aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG} ."
                sh "docker tag ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest"
            }
        }

        stage('Push to ECR') {
            steps {
                sh "docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"
                sh "docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest"
            }
        }

        stage('Deploy to AWS EKS') {
            steps {
                sh '''
                # 1. Authenticate with the EKS cluster (Jenkins has permission via its IAM Role!)
                aws eks update-kubeconfig --region ${AWS_REGION} --name cv-pipeline-cluster

                # 2. Update the deployment file to use the exact image tag we just built
                sed -i "s|image: .*|image: ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}|g" k8s/deployment.yaml

                # 3. Apply the changes to the cluster
                kubectl apply -f k8s/
                '''
            }
        }
    }
}
