"""
MNIST Digit Classifier — Flask Application (ONNX Runtime)
===========================================================
Uses onnxruntime (~30 MB) instead of PyTorch (~500 MB) for Vercel deployment.
Routes:
  GET  /          → Serve the main page
  POST /predict   → Accept base64 canvas image, return CNN prediction
  GET  /health    → Model status check
"""

import os
import io
import base64
import json
import numpy as np
from flask import Flask, render_template, request, jsonify
from PIL import Image
import onnxruntime as ort

# ── App Setup ────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'mnist_cnn.onnx')
ACC_PATH   = os.path.join(os.path.dirname(__file__), 'model', 'accuracy.json')

# ── Lazy Model Loading ────────────────────────────────────────────────────────
_session = None
_model_accuracy = None

def load_model():
    """Load the ONNX model session lazily on first prediction request."""
    global _session, _model_accuracy
    if _session is not None:
        return _session

    if not os.path.exists(MODEL_PATH):
        return None

    try:
        _session = ort.InferenceSession(MODEL_PATH, providers=['CPUExecutionProvider'])

        if os.path.exists(ACC_PATH):
            with open(ACC_PATH) as f:
                data = json.load(f)
                _model_accuracy = data.get('accuracy')

        print(f"[Flask] ONNX model loaded from {MODEL_PATH}")
        return _session
    except Exception as e:
        print(f"[Flask] Error loading ONNX model: {e}")
        return None


def preprocess_canvas_image(base64_str: str) -> np.ndarray:
    """
    Convert base64 PNG from drawing canvas or upload to a model-ready numpy array.
    Returns shape (1, 1, 28, 28) float32 — ONNX input format.
    """
    if ',' in base64_str:
        base64_str = base64_str.split(',', 1)[1]

    img_bytes = base64.b64decode(base64_str)
    img = Image.open(io.BytesIO(img_bytes)).convert('RGBA')

    # Composite on black background (preserves drawn strokes)
    background = Image.new('RGBA', img.size, (0, 0, 0, 255))
    background.paste(img, mask=img.split()[3])
    img = background.convert('L')

    # Find bounding box of non-black pixels
    img_array = np.array(img)
    non_empty_columns = np.where(img_array.max(axis=0) > 10)[0]
    non_empty_rows    = np.where(img_array.max(axis=1) > 10)[0]

    if len(non_empty_columns) > 0 and len(non_empty_rows) > 0:
        left, right = non_empty_columns[0], non_empty_columns[-1]
        top, bottom = non_empty_rows[0], non_empty_rows[-1]
        cropped = img.crop((left, top, right + 1, bottom + 1))

        # Detect light background (uploaded photo of paper)
        crop_array = np.array(cropped)
        border_pixels = np.concatenate([
            crop_array[0, :], crop_array[-1, :], crop_array[:, 0], crop_array[:, -1]
        ])

        if np.mean(border_pixels) > 127:
            inverted  = 255 - crop_array
            threshold = np.max(inverted) * 0.6
            binarized = np.where(inverted > threshold, 255, 0).astype(np.uint8)
            cropped   = Image.fromarray(binarized)

            crop_array = np.array(cropped)
            ne_cols = np.where(crop_array.max(axis=0) > 127)[0]
            ne_rows = np.where(crop_array.max(axis=1) > 127)[0]
            if len(ne_cols) > 0 and len(ne_rows) > 0:
                cropped = cropped.crop((ne_cols[0], ne_rows[0], ne_cols[-1] + 1, ne_rows[-1] + 1))

        # Fit into 20x20 preserving aspect ratio, then pad to 28x28
        w, h = cropped.size
        if w > 0 and h > 0:
            if w > h:
                new_w, new_h = 20, max(1, int(20 * (h / w)))
            else:
                new_h, new_w = 20, max(1, int(20 * (w / h)))

            cropped   = cropped.resize((new_w, new_h), Image.LANCZOS)
            final_img = Image.new('L', (28, 28), 0)
            final_img.paste(cropped, ((28 - new_w) // 2, (28 - new_h) // 2))
            img = final_img
        else:
            img = img.resize((28, 28), Image.LANCZOS)
    else:
        img = img.resize((28, 28), Image.LANCZOS)

    # Normalise to float32 with MNIST mean/std, shape (1, 1, 28, 28)
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = (arr - 0.1307) / 0.3081
    return arr[np.newaxis, np.newaxis, :, :]   # (1, 1, 28, 28)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    model   = load_model()
    return render_template(
        'index.html',
        model_loaded=model is not None,
        model_accuracy=_model_accuracy,
    )


@app.route('/predict', methods=['POST'])
def predict():
    session = load_model()
    if session is None:
        return jsonify({'error': 'Model not loaded.', 'status': 503}), 503

    data = request.get_json(silent=True)
    if not data or 'image' not in data:
        return jsonify({'error': 'No image provided', 'status': 400}), 400

    try:
        inp = preprocess_canvas_image(data['image'])
    except Exception as e:
        return jsonify({'error': f'Image processing failed: {str(e)}', 'status': 400}), 400

    try:
        input_name  = session.get_inputs()[0].name
        logits      = session.run(None, {input_name: inp})[0][0]  # shape (10,)

        # Softmax
        e = np.exp(logits - np.max(logits))
        probs = e / e.sum()

        prediction = int(np.argmax(probs))
        confidence = float(np.max(probs))
        all_probs  = [round(float(p), 6) for p in probs]

        return jsonify({
            'prediction': prediction,
            'confidence': round(confidence, 4),
            'all_probs':  all_probs,
        })
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}', 'status': 500}), 500


@app.route('/health')
def health():
    session = load_model()
    return jsonify({
        'status':       'ok' if session is not None else 'model_not_found',
        'model_path':   MODEL_PATH,
        'model_loaded': session is not None,
        'accuracy':     _model_accuracy,
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  [MNIST] Digit Classifier — Flask Server (ONNX Runtime)")
    print("="*60)
    if not os.path.exists(MODEL_PATH):
        print("  [!]  ONNX model not found. Run: python export_onnx.py")
    else:
        print(f"  [OK] ONNX model found at: {MODEL_PATH}")
    print("  [Web] Starting server at http://localhost:5000")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
