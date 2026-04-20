# AWS & Kubernetes MLOps CV Pipeline

This project contains an end-to-end Machine Learning pipeline for a Computer Vision model (Image Classification).

## Architecture
- **Model Training**: PyTorch (CNN on CIFAR-10)
- **Experiment Tracking**: MLflow
- **Artifact Storage**: AWS S3
- **Container Registry**: AWS ECR
- **Model Serving**: FastAPI running on Kubernetes (Minikube)
- **CI/CD**: GitHub Actions

## Phase 1: Local Setup & Training
1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/Scripts/activate # On Windows
   pip install -r requirements.txt
   ```
2. Train the model (this will log to local MLflow):
   ```bash
   python src/train.py
   ```
3. Run the inference server locally to test:
   ```bash
   uvicorn src.serve:app --reload
   ```

## Phase 2: AWS Infrastructure Setup
You need the AWS CLI installed and configured (`aws configure`).

1. **Create an S3 Bucket** for model artifacts:
   ```bash
   aws s3 mb s3://mlops-cv-artifacts-bucket --region us-east-1
   ```
2. **Create an ECR Repository** for the Docker images:
   ```bash
   aws ecr create-repository --repository-name cv-pipeline --region us-east-1
   ```

## Phase 3: Train & Push to S3
Now that S3 is ready, re-run training to push the model to AWS:
```bash
# On Windows PowerShell
$env:S3_BUCKET="mlops-cv-artifacts-bucket"
python src/train.py
```

## Phase 4: CI/CD Setup
1. Push this code to a GitHub repository.
2. Go to your GitHub Repo -> Settings -> Secrets and variables -> Actions.
3. Add two repository secrets:
   - `AWS_ACCESS_KEY_ID`: Your AWS IAM User access key.
   - `AWS_SECRET_ACCESS_KEY`: Your AWS IAM User secret key.
4. When you push to the `main` branch, the GitHub Action will automatically build your Docker container and push it to AWS ECR.

## Phase 5: Kubernetes Deployment (Minikube)
1. Start Minikube:
   ```bash
   minikube start
   ```
2. Open `k8s/aws-secret-template.yaml` and put your AWS keys inside. Then apply it:
   ```bash
   kubectl apply -f k8s/aws-secret-template.yaml
   ```
3. Edit `k8s/deployment.yaml` and replace `<AWS_ACCOUNT_ID>` and `<REGION>` with your actual AWS details for your ECR image.
4. Deploy the application:
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```
5. Expose the service locally:
   ```bash
   minikube tunnel
   ```
6. Access your API at `http://localhost/docs` or `http://127.0.0.1/docs`!
