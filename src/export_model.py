import os
import torch
import torch.nn as nn
from torchvision import models

# folders
model_folder = "models"
data_path = "data/masked/train"

# files
pth_file = os.path.join(model_folder, "masktif_model.pth")
onnx_file = os.path.join(model_folder, "masktif_model.onnx")

# check model file
if not os.path.exists(pth_file):
    print("Model file not found")
    exit()

# count classes
classes = os.listdir(data_path)
num_classes = len(classes)

# device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# load model
model = models.resnet50(weights=None)

in_features = model.fc.in_features
model.fc = nn.Linear(in_features, num_classes)

# load weights
model.load_state_dict(torch.load(pth_file, map_location=device))

model = model.to(device)
model.eval()

print("Model loaded successfully")

# dummy input
dummy_input = torch.randn(1, 3, 224, 224).to(device)

# export onnx
torch.onnx.export(
    model,
    dummy_input,
    onnx_file,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={
        "input": {0: "batch_size"},
        "output": {0: "batch_size"}
    },
    opset_version=18
)

print("ONNX model exported")
print("Saved file =", onnx_file)
print("Export completed")