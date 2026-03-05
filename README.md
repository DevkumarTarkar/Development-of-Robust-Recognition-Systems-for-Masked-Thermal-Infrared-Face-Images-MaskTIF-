# MaskTIF – Robust Recognition of Masked Thermal Infrared Face Images

## Overview

MaskTIF is a machine learning pipeline designed to recognize individuals from **thermal infrared face images even when masks are present**. The system performs dataset preprocessing, synthetic mask generation, deep learning model training, and evaluation using a convolutional neural network.

The project demonstrates how thermal imaging combined with deep learning can improve face recognition robustness in masked scenarios.

---

## Features

* Dataset preprocessing and face cropping
* Identity-based dataset organization
* Synthetic mask generation for thermal faces
* Deep learning model training using ResNet50
* Model evaluation with accuracy, precision, recall, and F1-score
* Confusion matrix visualization
* Prediction on new thermal face images

---

## Project Pipeline

Thermal Face Dataset
↓
Face Cropping
↓
Dataset Organization
↓
Dataset Split (Train / Validation / Test)
↓
Image Preprocessing
↓
Synthetic Mask Generation
↓
Model Training (ResNet50)
↓
Model Evaluation
↓
Prediction

---

## Dataset

The dataset consists of **thermal infrared face images from multiple individuals**.
Each person contains **100+ images** to ensure adequate training data.

Dataset structure:

data/
└── raw/
├── person_1
├── person_2
├── person_3
├── person_4
├── person_5
├── person_6
├── person_7
└── person_8

After preprocessing:

data/masked/
├── train
├── val
└── test

---

## Model Architecture

The system uses **ResNet50**, a deep convolutional neural network widely used for image classification tasks.

Model configuration:

* Input size: 224 × 224
* Architecture: ResNet50
* Loss function: CrossEntropyLoss
* Optimizer: Adam
* Training epochs: 20

---

## Evaluation Metrics

The model performance was evaluated using:

* Accuracy
* Precision
* Recall
* F1 Score
* Confusion Matrix

Results:

Accuracy: **62.5%**
Precision: **0.67**
Recall: **0.63**
F1 Score: **0.63**

These results demonstrate that the system can correctly identify masked thermal faces with moderate reliability.

---

## Confusion Matrix

The confusion matrix shows the classification performance across all identity classes.
Most predictions fall along the diagonal, indicating correct classifications.

---

## Technologies Used

* Python
* PyTorch
* OpenCV
* Scikit-learn
* Matplotlib
* NumPy

---

## Installation

Clone the repository:

```
git clone https://github.com/DevkumarTarkar/Development-of-Robust-Recognition-Systems-for-Masked-Thermal-Infrared-Face-Images-MaskTIF-.git
cd Development-of-Robust-Recognition-Systems-for-Masked-Thermal-Infrared-Face-Images-MaskTIF-
```

Install dependencies:

```
pip install -r requirements.txt
```

---

## Training the Model

Run the training script:

```
python src/train_model.py
```

---

## Evaluating the Model

```
python src/evaluate_model.py
```

This will generate evaluation metrics and a confusion matrix.

---



## Project Structure

MaskTIF_Project
├── data
├── models
├── outputs
├── src
│   ├── crop_faces.py
│   ├── organize_faces.py
│   ├── split_dataset.py
│   ├── preprocess_images.py
│   ├── generate_masks.py
│   ├── train_model.py
│   ├── evaluate_model.py
│   └── predict.py
├── README.md
├── requirements.txt
└── .gitignore

---

## Future Improvements

* Larger thermal datasets
* Real-time webcam inference
* Deployment using Streamlit or Flask
* Model optimization for edge devices

---

## Author

Dev Kumar Tarkar

---


