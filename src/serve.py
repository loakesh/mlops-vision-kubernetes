import os
import io
import torch
import boto3
from fastapi import FastAPI, File, UploadFile, HTTPException
from PIL import Image
from torchvision import transforms
from model import SimpleCNN

app = FastAPI(title="CV MLOps Pipeline API")

# CIFAR-10 classes
CLASSES = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

# Initialize model
device = torch.device("cpu") # Usually serve on CPU for simple APIs unless GPU is explicitly provisioned
model = SimpleCNN()
MODEL_PATH = "simple_cnn.pth"

def download_from_s3(bucket_name, object_name, local_path):
    s3_client = boto3.client('s3')
    try:
        s3_client.download_file(bucket_name, object_name, local_path)
        print(f"Successfully downloaded {object_name} from S3.")
        return True
    except Exception as e:
        print(f"Failed to download from S3: {e}")
        return False

# Load Model Weights on Startup
@app.on_event("startup")
async def load_model():
    global model
    
    s3_bucket = os.getenv("S3_BUCKET")
    if s3_bucket:
        print(f"Attempting to fetch model from S3 Bucket: {s3_bucket}")
        download_from_s3(s3_bucket, "models/simple_cnn.pth", MODEL_PATH)
    
    if not os.path.exists(MODEL_PATH):
        raise RuntimeError(f"Model file {MODEL_PATH} not found. Please train the model first.")
        
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model.eval()
    print("Model loaded successfully into memory.")

def transform_image(image_bytes):
    try:
        # Load image and convert to RGB
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # Standard CIFAR-10 transforms: Resize to 32x32, ToTensor, Normalize
        my_transforms = transforms.Compose([
            transforms.Resize((32, 32)),
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        ])
        return my_transforms(image).unsqueeze(0) # Add batch dimension
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image file")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
        
    # Read image
    image_bytes = await file.read()
    tensor = transform_image(image_bytes)
    
    # Inference
    with torch.no_grad():
        outputs = model(tensor)
        _, predicted = torch.max(outputs, 1)
        class_idx = predicted.item()
        
    return {
        "class_id": class_idx,
        "class_name": CLASSES[class_idx]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
