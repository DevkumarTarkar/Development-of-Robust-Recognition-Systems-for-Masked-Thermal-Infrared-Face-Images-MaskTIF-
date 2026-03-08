"""
Export the trained MaskTIF model for deployment.

Saves the model in two formats:
  1. PyTorch (.pth) - for Python/PyTorch deployment
  2. ONNX (.onnx) - for deployment on other runtimes (TensorFlow, mobile, etc.)

Usage:
    python src/export_model.py

Output:
    models/masktif_model.pth (updated/copied if needed)
    models/masktif_model.onnx
"""

import os
import sys

import torch
from torchvision import models

# Add project root to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

DATA_DIR = os.path.join(PROJECT_ROOT, "data", "masked", "train")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
PTH_PATH = os.path.join(MODEL_DIR, "masktif_model.pth")
ONNX_PATH = os.path.join(MODEL_DIR, "masktif_model.onnx")
INPUT_SIZE = (224, 224)
BATCH_SIZE = 1
CHANNELS = 3


def get_num_classes():
    """Infer number of classes from train directory."""
    if not os.path.isdir(DATA_DIR):
        return None
    classes = [
        d
        for d in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, d))
    ]
    return len(classes) if classes else None


def main():
    if not os.path.exists(PTH_PATH):
        print(f"Error: Model not found at {PTH_PATH}")
        print("Run training first: python src/train_model.py")
        sys.exit(1)

    os.makedirs(MODEL_DIR, exist_ok=True)

    num_classes = get_num_classes()
    if num_classes is None:
        print("Warning: Could not infer num_classes from train dir. Using default 8.")
        num_classes = 8

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = models.resnet50(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
    model.load_state_dict(torch.load(PTH_PATH, map_location=device))
    model.to(device)
    model.eval()

    # 1. Ensure .pth is saved (in case we loaded from elsewhere)
    torch.save(model.state_dict(), PTH_PATH)
    print(f"Saved PyTorch model: {PTH_PATH}")

    # 2. Export to ONNX
    dummy_input = torch.randn(BATCH_SIZE, CHANNELS, *INPUT_SIZE).to(device)
    torch.onnx.export(
        model,
        dummy_input,
        ONNX_PATH,
        export_params=True,
        opset_version=12,
        do_constant_folding=True,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
    )
    print(f"Exported ONNX model: {ONNX_PATH}")
    print("Export complete.")


if __name__ == "__main__":
    main()
