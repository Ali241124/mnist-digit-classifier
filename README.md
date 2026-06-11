# 🧠 MNIST Digit Classifier (CNN + Flask API)

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)](https://www.tensorflow.org/)
[![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey.svg)](https://flask.palletsprojects.com/)

## 📌 Overview

This project is an interactive **handwritten digit recognition web application**. It features a **Convolutional Neural Network (CNN)** trained on the MNIST dataset, achieving high accuracy. The model is integrated with a **Flask REST API** backend and a custom frontend UI, allowing users to draw digits on a canvas and get real-time predictions.

---

## 🚀 Features

* **Interactive Drawing Canvas**: A beautiful and responsive web UI to draw digits directly in the browser.
* **Deep Learning Model**: CNN-based deep learning model for digit classification (0–9) trained on the MNIST dataset.
* **Real-time API**: Flask backend providing real-time inference on drawn images.
* **Image Preprocessing**: Built-in preprocessing to match the canvas drawing with MNIST training data format.
* **Training Script**: Includes `train.py` to easily retrain the model locally.

---

## 🧠 Model Architecture

* Convolutional Layers + ReLU Activation
* Max Pooling Layers
* Fully Connected Dense Layers
* Softmax Output Layer (10 classes)

---

## 🛠️ Tech Stack

* **Frontend**: HTML5, CSS3, JavaScript (Canvas API)
* **Backend**: Python, Flask
* **Machine Learning**: TensorFlow / Keras, NumPy
* **Image Processing**: OpenCV, PIL

---

## 📂 Project Structure

```text
mnist-digit-classifier/
│
├── app.py                 # Flask web server and API
├── train.py               # Script to train the CNN model
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
│
├── model/                 # Saved Keras model files
├── data/                  # Dataset or related files
│
├── templates/             # HTML templates
│   └── index.html         # Main web interface
│
└── static/                # Static assets (CSS, JS, Images)
    ├── css/
    │   └── style.css      # Custom styling
    └── js/
        └── script.js      # Canvas drawing logic and API calls
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/mnist-digit-classifier.git
cd mnist-digit-classifier
```

### 2. Create a Virtual Environment (Optional but recommended)

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Train the model

If you want to retrain the model from scratch:
```bash
python train.py
```

### 5. Run the Flask app

```bash
python app.py
```

Open your browser and navigate to `http://localhost:5000` to use the drawing interface!

---

## 🌐 API Usage

If you want to use the API directly without the UI:

### Endpoint:

```http
POST /predict
```

### Input:

* Upload an image file of a handwritten digit (or base64 encoded image from the canvas).

### Response:

```json
{
  "prediction": 7,
  "confidence": 0.98
}
```

---

## 📊 Results

* **Test Accuracy**: High accuracy on standard MNIST test set.
* **Performance**: Fast real-time inference suitable for interactive web applications.

---

## 📌 Future Improvements

* Deploy using Docker + Cloud (AWS / Render)
* Implement data augmentation for better generalisation
* Add support for classifying letters (EMNIST dataset)

---

## 👨‍💻 Author

**Syed Ali Hassan**
* LinkedIn: https://www.linkedin.com/in/syedalihassan24

---

## ⭐ Support

If you like this project, please consider giving it a ⭐ on GitHub and feel free to fork it!
