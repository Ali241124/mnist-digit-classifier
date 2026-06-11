"""
Convert mnist_cnn.pth (PyTorch) -> mnist_cnn.onnx for lightweight Vercel deployment.
Run locally: python export_onnx.py

Compatible with PyTorch 2.9+ (uses legacy TorchScript path with explicit file path).
"""
import os
import sys

os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

import torch
import torch.nn as nn

# ── Same model definition as app.py ──────────────────────────────────────────
class MNISTConvNet(nn.Module):
    def __init__(self):
        super(MNISTConvNet, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=0),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=0),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
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
        return x

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'mnist_cnn.pth')
ONNX_PATH  = os.path.join(os.path.dirname(__file__), 'model', 'mnist_cnn.onnx')

print(f"[ONNX] Loading PyTorch model from {MODEL_PATH} ...")
model = MNISTConvNet()
model.load_state_dict(torch.load(MODEL_PATH, map_location='cpu'))
model.eval()

dummy_input = torch.zeros(1, 1, 28, 28)

print(f"[ONNX] Exporting to {ONNX_PATH} ...")

# PyTorch 2.9+ new dynamo-based export API
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    export_output = torch.onnx.export(
        model,
        (dummy_input,),
        dynamo=True,
    )

export_output.save(ONNX_PATH)

size_kb = os.path.getsize(ONNX_PATH) / 1024
print(f"[ONNX] Done! Saved to {ONNX_PATH}  ({size_kb:.1f} KB)")
print("[ONNX] You can now safely remove model/mnist_cnn.pth from Vercel (keep for local use).")
