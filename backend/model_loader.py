"""Model loading and inference utilities for the MaskTIF backend.

Loads the trained ResNet50 model once at application startup and exposes
simple prediction helpers for use by API routes.
"""

import logging
import os
from typing import List, Tuple

import torch
from PIL import Image
from torchvision import models, transforms

from config import Config


logger = logging.getLogger(__name__)

_model = None
_class_names: List[str] = []
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _discover_class_names(train_dir: str) -> List[str]:
    """Infer class labels from the training directory subfolders."""

    if not os.path.isdir(train_dir):
        logger.warning("Training directory %s does not exist; class names empty.", train_dir)
        return []

    class_dirs = [
        d
        for d in os.listdir(train_dir)
        if os.path.isdir(os.path.join(train_dir, d))
    ]
    class_dirs.sort()

    logger.info("Discovered %d classes from %s", len(class_dirs), train_dir)
    return class_dirs


def load_model(
    model_path: str = Config.MODEL_PATH, train_dir: str = Config.TRAIN_DIR
):
    """Load the trained ResNet50 model and cache it globally.

    This function is intended to be called once when the Flask app starts.
    """

    global _model, _class_names

    if _model is not None:
        return _model, _class_names

    if not os.path.exists(model_path):
        logger.error("Model file not found at %s", model_path)
        raise FileNotFoundError(f"Model file not found at {model_path}")

    _class_names = _discover_class_names(train_dir)

    # Create a ResNet50 architecture and adjust the final layer to match
    # the number of classes from the training data.
    resnet = models.resnet50(weights=None)
    num_features = resnet.fc.in_features
    num_classes = len(_class_names) if _class_names else None

    if num_classes:
        resnet.fc = torch.nn.Linear(num_features, num_classes)

    state_dict = torch.load(model_path, map_location=_device)
    resnet.load_state_dict(state_dict)
    resnet.to(_device)
    resnet.eval()

    _model = resnet

    logger.info("Model loaded successfully from %s on device %s", model_path, _device)
    return _model, _class_names


_preprocess = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.Grayscale(num_output_channels=3),
        transforms.ToTensor(),
    ]
)


def predict_image(image_path: str) -> Tuple[str, float]:
    """Run inference on a single image file and return (label, confidence)."""

    if _model is None:
        raise RuntimeError("Model is not loaded. Call load_model() at startup.")

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")

    image = Image.open(image_path).convert("RGB")
    tensor = _preprocess(image).unsqueeze(0).to(_device)

    with torch.no_grad():
        outputs = _model(tensor)
        probabilities = torch.softmax(outputs, dim=1)[0]
        confidence, predicted_idx = torch.max(probabilities, dim=0)

    idx = predicted_idx.item()
    if _class_names and 0 <= idx < len(_class_names):
        label = _class_names[idx]
    else:
        label = f"class_{idx}"

    logger.info(
        "Prediction for %s: label=%s confidence=%.4f", image_path, label, float(confidence)
    )
    return label, float(confidence.item())

