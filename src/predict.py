import torch
import os
from PIL import Image

from torchvision import transforms, models

# image path
img_path = "data/masked/test/person_1/1_101.jpeg"

# model path
model_path = "models/masktif_model.pth"

# class names from train folder
train_path = "data/masked/train"
classes = os.listdir(train_path)
classes.sort()

# image transform
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485,0.456,0.406],
        std=[0.229,0.224,0.225]
    )
])

# device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# load model
model = models.resnet50(weights=None)

in_features = model.fc.in_features
model.fc = torch.nn.Linear(in_features, len(classes))

# check model file
if not os.path.exists(model_path):
    print("Model file not found")
    exit()

# load weights
model.load_state_dict(torch.load(model_path, map_location=device))

model = model.to(device)
model.eval()

# check image file
if not os.path.exists(img_path):
    print("Image not found")
    exit()

# open image
img = Image.open(img_path)

# transform image
img = transform(img)
img = img.unsqueeze(0)
img = img.to(device)

# prediction
with torch.no_grad():

    output = model(img)

    prob = torch.softmax(output, dim=1)

    confidence, pred = torch.max(prob, 1)

# result
conf = confidence.item() * 100
name = classes[pred.item()]

# unknown detection
if conf < 70:
    print("Unknown Person")
    print("Confidence =", round(conf,2), "%")

else:
    print("Prediction =", name)
    print("Confidence =", round(conf,2), "%")