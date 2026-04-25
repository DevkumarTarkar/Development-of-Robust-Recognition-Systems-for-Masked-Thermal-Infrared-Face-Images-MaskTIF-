import torch
import os

from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader

from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

# dataset path
path = "data/masked"

# image preprocessing
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),

    # same normalize as training
    transforms.Normalize(
        mean=[0.485,0.456,0.406],
        std=[0.229,0.224,0.225]
    )
])

# load validation data
val_data = datasets.ImageFolder(
    os.path.join(path, "val"),
    transform=transform
)

val_loader = DataLoader(
    val_data,
    batch_size=16,
    shuffle=False
)

# number of classes
num_classes = len(val_data.classes)

# device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# load model
model = models.resnet50(weights=None)

in_features = model.fc.in_features
model.fc = torch.nn.Linear(in_features, num_classes)

# model path
model_path = "models/masktif_model.pth"

if os.path.exists(model_path):

    model.load_state_dict(torch.load(model_path, map_location=device))

else:
    print("Model file not found")
    exit()

model = model.to(device)
model.eval()

all_pred = []
all_label = []

print("Testing started...")

with torch.no_grad():

    for images, labels in val_loader:

        images = images.to(device)
        labels = labels.to(device)

        output = model(images)

        _, pred = torch.max(output, 1)

        all_pred.extend(pred.cpu().numpy())
        all_label.extend(labels.cpu().numpy())

# metrics
acc = accuracy_score(all_label, all_pred)
pre = precision_score(all_label, all_pred, average="weighted", zero_division=0)
rec = recall_score(all_label, all_pred, average="weighted", zero_division=0)
f1 = f1_score(all_label, all_pred, average="weighted", zero_division=0)

# print result
print("\n----- Result -----")
print("Accuracy  =", round(acc * 100, 2), "%")
print("Precision =", round(pre * 100, 2), "%")
print("Recall    =", round(rec * 100, 2), "%")
print("F1 Score  =", round(f1 * 100, 2), "%")

# confusion matrix
print("\nConfusion Matrix")
print(confusion_matrix(all_label, all_pred))

# classification report
print("\nClassification Report")
print(classification_report(
    all_label,
    all_pred,
    target_names=val_data.classes,
    zero_division=0
))