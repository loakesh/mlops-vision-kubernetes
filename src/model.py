import torch.nn as nn
import torch.nn.functional as F

class SimpleCNN(nn.Module):
    def __init__(self, num_classes=10):
        super(SimpleCNN, self).__init__()
        # Input: 3 channels (RGB), 32x32 image (CIFAR-10)
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        # After 2 max pools, spatial dimension is 32 / 2 / 2 = 8
        # Flattened size: 32 channels * 8 * 8 = 2048
        self.fc1 = nn.Linear(32 * 8 * 8, 128)
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        # Convolution 1 -> ReLU -> MaxPool
        x = self.pool(F.relu(self.conv1(x)))
        # Convolution 2 -> ReLU -> MaxPool
        x = self.pool(F.relu(self.conv2(x)))
        # Flatten
        x = x.view(-1, 32 * 8 * 8)
        # Fully Connected 1 -> ReLU
        x = F.relu(self.fc1(x))
        # Fully Connected 2 -> Output (no softmax, handled by CrossEntropyLoss)
        x = self.fc2(x)
        return x
