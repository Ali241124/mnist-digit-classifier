"""
MNIST Digit Classifier — Flask Application (PyTorch)
======================================================
Routes:
  GET  /          → Serve the main page
  POST /predict   → Accept base64 canvas image, return CNN prediction
  GET  /health    → Model status check
  GET  /train     → Trigger model training (if model not found)
"""

import os
import io
import base64
import json
import numpy as np
from flask import Flask, render_template, request, jsonify
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms

# ── App Setup ────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'mnist_cnn.pth')
DEVICE = torch.device('cpu') # Use CPU for inference in Flask

# ── Model Definition (Must match train.py) ──────────────────────────────────
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

    def predict_proba(self, x):
        with torch.no_grad():
            logits = self.forward(x)
            return torch.softmax(logits, dim=1)

# ── Lazy Model Loading ────────────────────────────────────────────────────────
_model = None
_model_accuracy = None

def load_model():
    """Load the PyTorch model lazily on first prediction request."""
    global _model, _model_accuracy
    if _model is not None:
        return _model

    if not os.path.exists(MODEL_PATH):
        return None

    try:
        model = MNISTConvNet()
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        model.eval() # Set to evaluation mode
        _model = model

        # Read stored accuracy if available
        acc_file = os.path.join(os.path.dirname(MODEL_PATH), 'accuracy.json')
        if os.path.exists(acc_file):
            with open(acc_file) as f:
                data = json.load(f)
                _model_accuracy = data.get('accuracy')

        print(f"[Flask] Model loaded from {MODEL_PATH}")
        return _model
    except Exception as e:
        print(f"[Flask] Error loading model: {e}")
        return None


def preprocess_canvas_image(base64_str: str) -> torch.Tensor:
    """
    Convert base64 PNG from drawing canvas or upload to a model-ready PyTorch tensor.
    """
    if ',' in base64_str:
        base64_str = base64_str.split(',', 1)[1]

    img_bytes = base64.b64decode(base64_str)
    img = Image.open(io.BytesIO(img_bytes)).convert('RGBA')

    # Composite on black background (preserves drawn strokes, makes transparent bg black)
    background = Image.new('RGBA', img.size, (0, 0, 0, 255))
    background.paste(img, mask=img.split()[3])
    img = background.convert('L')

    # Find the bounding box of non-black pixels (this crops out the black canvas padding)
    img_array = np.array(img)
    non_empty_columns = np.where(img_array.max(axis=0) > 10)[0]
    non_empty_rows = np.where(img_array.max(axis=1) > 10)[0]
    
    if len(non_empty_columns) > 0 and len(non_empty_rows) > 0:
        left, right = non_empty_columns[0], non_empty_columns[-1]
        top, bottom = non_empty_rows[0], non_empty_rows[-1]
        cropped = img.crop((left, top, right + 1, bottom + 1))
        
        # Check if the cropped image has a light background (e.g. uploaded photo of paper)
        crop_array = np.array(cropped)
        border_pixels = np.concatenate([
            crop_array[0, :], crop_array[-1, :], crop_array[:, 0], crop_array[:, -1]
        ])
        
        if np.mean(border_pixels) > 127:
            # It's a photo with a light background. 
            # 1. Invert it so ink is bright, paper is dark.
            inverted = 255 - crop_array
            
            # 2. Dynamic threshold to isolate ink from paper and shadows.
            # Ink will be the brightest part of the inverted image.
            threshold = np.max(inverted) * 0.6
            binarized = np.where(inverted > threshold, 255, 0).astype(np.uint8)
            cropped = Image.fromarray(binarized)
            
            # 3. Re-crop tightly around the isolated white digit
            crop_array = np.array(cropped)
            ne_cols = np.where(crop_array.max(axis=0) > 127)[0]
            ne_rows = np.where(crop_array.max(axis=1) > 127)[0]
            if len(ne_cols) > 0 and len(ne_rows) > 0:
                cropped = cropped.crop((ne_cols[0], ne_rows[0], ne_cols[-1] + 1, ne_rows[-1] + 1))

        # MNIST expects the digit to fit in a 20x20 box, preserving aspect ratio
        w, h = cropped.size
        if w > 0 and h > 0:
            if w > h:
                new_w = 20
                new_h = int(20 * (h / w))
            else:
                new_h = 20
                new_w = int(20 * (w / h))
            
            new_w, new_h = max(1, new_w), max(1, new_h)
            cropped = cropped.resize((new_w, new_h), Image.LANCZOS)
            
            # Paste into center of 28x28 black image
            final_img = Image.new('L', (28, 28), 0)
            paste_x = (28 - new_w) // 2
            paste_y = (28 - new_h) // 2
            final_img.paste(cropped, (paste_x, paste_y))
            img = final_img
        else:
            img = img.resize((28, 28), Image.LANCZOS)
    else:
        img = img.resize((28, 28), Image.LANCZOS)
        
    # Use PyTorch transforms
    transform = transforms.Compose([
        transforms.ToTensor(), # Scales to [0,1]
        transforms.Normalize((0.1307,), (0.3081,)) # MNIST normalization
    ])
    
    tensor = transform(img).unsqueeze(0) # Add batch dimension -> (1, 1, 28, 28)
    return tensor


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    model = load_model()
    model_loaded = model is not None
    accuracy = _model_accuracy

    return render_template(
        'index.html',
        model_loaded=model_loaded,
        model_accuracy=accuracy,
    )


@app.route('/predict', methods=['POST'])
def predict():
    model = load_model()
    if model is None:
        return jsonify({
            'error': 'Model not loaded. Please run train.py first.',
            'status': 503
        }), 503

    data = request.get_json(silent=True)
    if not data or 'image' not in data:
        return jsonify({'error': 'No image provided', 'status': 400}), 400

    try:
        tensor = preprocess_canvas_image(data['image']).to(DEVICE)
    except Exception as e:
        return jsonify({'error': f'Image processing failed: {str(e)}', 'status': 400}), 400

    try:
        probs = model.predict_proba(tensor)[0].cpu().numpy()
        prediction = int(np.argmax(probs))
        confidence = float(np.max(probs))
        all_probs = [round(float(p), 6) for p in probs]

        return jsonify({
            'prediction': prediction,
            'confidence': round(confidence, 4),
            'all_probs': all_probs,
        })
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}', 'status': 500}), 500


@app.route('/health')
def health():
    model = load_model()
    return jsonify({
        'status': 'ok' if model is not None else 'model_not_found',
        'model_path': MODEL_PATH,
        'model_loaded': model is not None,
        'accuracy': _model_accuracy,
    })


@app.route('/train', methods=['POST'])
def train_route():
    import subprocess, sys
    train_script = os.path.join(os.path.dirname(__file__), 'train.py')
    result = subprocess.run(
        [sys.executable, train_script],
        capture_output=True, text=True, timeout=600
    )
    if result.returncode == 0:
        global _model
        _model = None 
        return jsonify({'status': 'ok', 'output': result.stdout[-2000:]})
    else:
        return jsonify({'status': 'error', 'output': result.stderr[-2000:]}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  [MNIST] Digit Classifier — Flask Server (PyTorch)")
    print("="*60)
    if not os.path.exists(MODEL_PATH):
        print("  [!]  Model not found. Run: python train.py")
    else:
        print(f"  [OK] Model found at: {MODEL_PATH}")
    print("  [Web] Starting server at http://localhost:5000")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
