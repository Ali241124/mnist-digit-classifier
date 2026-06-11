"""
MNIST CNN Training Script — PyTorch
=====================================
Trains a CNN on the MNIST dataset and saves the model to model/mnist_cnn.pth

Usage:
    python train.py

Output:
    model/mnist_cnn.pth      — trained PyTorch model state dict
    model/accuracy.json      — test accuracy metadata
"""

import os
import json
import time

print("\n" + "="*60)
print("  [MNIST] CNN Training Script (PyTorch)")
print("="*60)

# ── Imports ───────────────────────────────────────────────────────────────────
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"\n  Device: {DEVICE}")

# ── 1. Data Loading ────────────────────────────────────────────────────────────
print("\n[1/5] Loading MNIST dataset...")

transform = transforms.Compose([
    transforms.ToTensor(),           # HxW → 1xHxW, scales to [0,1]
    transforms.Normalize((0.1307,), (0.3081,))  # MNIST mean/std
])

train_data = datasets.MNIST('./data', train=True,  download=True, transform=transform)
test_data  = datasets.MNIST('./data', train=False, download=True, transform=transform)

train_loader = DataLoader(train_data, batch_size=64, shuffle=True,  num_workers=0)
test_loader  = DataLoader(test_data,  batch_size=64, shuffle=False, num_workers=0)

print(f"      Training samples : {len(train_data):,}")
print(f"      Test samples     : {len(test_data):,}")

# ── 2. Model Definition ───────────────────────────────────────────────────────
print("\n[2/5] Building CNN model...")

class MNISTConvNet(nn.Module):
    """
    CNN Architecture:
      Conv2D(32, 3×3, ReLU) → MaxPool(2×2)
      Conv2D(64, 3×3, ReLU) → MaxPool(2×2)
      Flatten → Dense(128, ReLU) → Dropout(0.5) → Dense(10, Softmax)
    """
    def __init__(self):
        super(MNISTConvNet, self).__init__()

        # Conv Block 1
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=0),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        # Conv Block 2
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=0),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        # Classifier Head
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 5 * 5, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, 10),
        )

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.classifier(x)
        return x  # raw logits (CrossEntropyLoss handles softmax)

    def predict_proba(self, x):
        """Return softmax probabilities."""
        with torch.no_grad():
            logits = self.forward(x)
            return torch.softmax(logits, dim=1)


model = MNISTConvNet().to(DEVICE)

# Print architecture summary
total_params = sum(p.numel() for p in model.parameters())
print(f"      Total parameters: {total_params:,}")
print(f"      Architecture: Conv32 -> Pool -> Conv64 -> Pool -> Dense128 -> Dense10")

# ── 3. Training Setup ─────────────────────────────────────────────────────────
print("\n[3/5] Setting up training...")

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)
scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

EPOCHS = 2

# ── 4. Training Loop ──────────────────────────────────────────────────────────
print(f"\n[4/5] Training ({EPOCHS} epochs)...")
print(f"{'Epoch':>6} {'Train Loss':>11} {'Train Acc':>10} {'Time':>7}")
print("-" * 40)

history = {'train_loss': [], 'train_acc': [], 'val_acc': []}

for epoch in range(1, EPOCHS + 1):
    t0 = time.time()
    model.train()
    total_loss, correct, total = 0.0, 0, 0

    for images, labels in train_loader:
        images, labels = images.to(DEVICE), labels.to(DEVICE)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += images.size(0)

    scheduler.step()

    train_loss = total_loss / total
    train_acc  = correct / total
    elapsed    = time.time() - t0

    history['train_loss'].append(round(train_loss, 4))
    history['train_acc'].append(round(train_acc, 4))

    print(f"{epoch:>6} {train_loss:>11.4f} {train_acc*100:>9.2f}% {elapsed:>6.1f}s")

# ── 5. Evaluation & Save ──────────────────────────────────────────────────────
print("\n[5/5] Evaluating on test set...")

model.eval()
correct, total = 0, 0
with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(DEVICE), labels.to(DEVICE)
        outputs = model(images)
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += images.size(0)

test_acc = correct / total
print(f"\n  [OK] Test Accuracy : {test_acc * 100:.2f}%")

# Create model directory
os.makedirs('model', exist_ok=True)

# Save state dict
model_path = os.path.join('model', 'mnist_cnn.pth')
torch.save(model.state_dict(), model_path)
print(f"  [Saved] Model saved to: {model_path}")

# Save metadata
meta = {
    'accuracy': round(float(test_acc), 6),
    'epochs': EPOCHS,
    'training_samples': len(train_data),
    'test_samples': len(test_data),
    'device': str(DEVICE),
    'framework': 'PyTorch',
}
with open(os.path.join('model', 'accuracy.json'), 'w') as f:
    json.dump(meta, f, indent=2)

print(f"  [Saved] Metadata saved to: model/accuracy.json")
print("\n" + "="*60)
print(f"  Training complete! Test Accuracy: {test_acc*100:.2f}%")
print("  Run: python app.py")
print("="*60 + "\n")
