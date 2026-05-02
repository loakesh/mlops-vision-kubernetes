# 🖼️ Image Classification API (CIFAR-10)

This application is a complete Machine Learning service that can automatically classify images into 10 different categories using a custom-built Convolutional Neural Network (CNN).

## ✨ What this Application Does

### 1. The Machine Learning Model (`src/model.py`)
At the core of the application is a custom PyTorch Convolutional Neural Network built from scratch. 
*   It accepts standard RGB images resized to 32x32 pixels.
*   It uses multiple Convolutional and Max Pooling layers to extract shapes, edges, and colors.
*   It outputs a prediction matching the image to one of 10 categories.

### 2. The Training Pipeline (`src/train.py`)
This script handles teaching the model how to see.
*   **Dataset:** It automatically downloads the famous **CIFAR-10** dataset (60,000 labeled images of airplanes, cars, birds, cats, deer, dogs, frogs, horses, ships, and trucks).
*   **Training Loop:** It feeds the images through the network in batches, calculating the error (`CrossEntropyLoss`) and tweaking the math (`Adam Optimizer`) so the model gets smarter over time.
*   **Tracking:** It uses **MLflow** to log hyperparameters (Batch Size, Epochs, Learning Rate) and track the model's accuracy.
*   **Storage:** Once fully trained, it automatically saves the "brain" (`.pth` file) to AWS S3.

### 3. The FastAPI Backend (`src/serve.py`)
This script exposes the trained model to the real world as a web service.
*   **Initialization:** When the server starts up, it connects to AWS S3 and downloads the fully trained `.pth` model into memory.
*   **Data Transformation:** When an end-user uploads a high-resolution image, the API acts as a translator, squishing and converting the image into a 32x32 mathematical Tensor that the model can understand.
*   **Inference (`/predict`):** The transformed image is fed into the PyTorch model, and the highest probability guess is returned to the user in a clean JSON response.

## 🚀 How to Test the API
FastAPI automatically generates an interactive testing interface. 

1. Ensure the server is running.
2. Open your web browser and navigate to `http://<your-server-ip>:8000/docs`
3. Click the **`POST /predict`** endpoint and click **"Try it out"**.
4. Upload an image of a dog, car, or airplane from your computer.
5. Click **Execute**. The API will instantly return a JSON response with the classified category!

## 🛠️ Tech Stack
- **Machine Learning:** PyTorch, Torchvision, MLflow
- **API Serving:** FastAPI, Uvicorn
- **Containerization & Cloud:** Docker, AWS EKS, S3
