import os
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import mlflow
import mlflow.pytorch
import boto3
from model import SimpleCNN

# Hyperparameters
BATCH_SIZE = 64
EPOCHS = 2 # Keeping it small for demonstration
LEARNING_RATE = 0.001

def upload_to_s3(file_path, bucket_name, object_name):
    """Uploads a file to AWS S3"""
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f"Successfully uploaded {file_path} to s3://{bucket_name}/{object_name}")
    except Exception as e:
        print(f"Failed to upload to S3: {e}")

def main():
    # 1. Setup Data
    print("Downloading/Loading CIFAR-10 Dataset...")
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    
    # Using ./data relative to execution path
    os.makedirs("./data", exist_ok=True)
    trainset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
    trainloader = torch.utils.data.DataLoader(trainset, batch_size=BATCH_SIZE, shuffle=True)

    # 2. Setup Model, Loss, Optimizer
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")
    model = SimpleCNN().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    # 3. Setup MLflow
    mlflow.set_experiment("CIFAR10_Classification")
    
    with mlflow.start_run():
        mlflow.log_param("batch_size", BATCH_SIZE)
        mlflow.log_param("epochs", EPOCHS)
        mlflow.log_param("learning_rate", LEARNING_RATE)

        # 4. Training Loop
        for epoch in range(EPOCHS):
            running_loss = 0.0
            for i, data in enumerate(trainloader, 0):
                inputs, labels = data[0].to(device), data[1].to(device)

                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                running_loss += loss.item()
                if i % 200 == 199:    # Print every 200 mini-batches
                    print(f'[{epoch + 1}, {i + 1:5d}] loss: {running_loss / 200:.3f}')
                    mlflow.log_metric("loss", running_loss / 200, step=(epoch * len(trainloader)) + i)
                    running_loss = 0.0

        print('Finished Training')
        
        # 5. Save locally and log to MLflow
        model_path = "simple_cnn.pth"
        torch.save(model.state_dict(), model_path)
        mlflow.pytorch.log_model(model, "model")
        print(f"Model saved locally as {model_path}")

        # 6. Upload to AWS S3 (if configured)
        s3_bucket = os.getenv("S3_BUCKET")
        if s3_bucket:
            print(f"S3_BUCKET environment variable found: {s3_bucket}. Uploading artifact...")
            upload_to_s3(model_path, s3_bucket, "models/simple_cnn.pth")
        else:
            print("S3_BUCKET environment variable not set. Skipping AWS S3 upload.")

if __name__ == "__main__":
    main()
