import torch
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import os

data_dir = "data/masked"

# preprocessing for model - using Grayscale for thermal images
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.Grayscale(num_output_channels=3),  # Convert to standard 3-channel grayscale for ResNet
    transforms.ToTensor()
])

# Load validation dataset
val_dataset = datasets.ImageFolder(os.path.join(data_dir,"val"), transform=transform)
val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load model
model = models.resnet50(pretrained=False)
num_features = model.fc.in_features
model.fc = torch.nn.Linear(num_features, len(val_dataset.classes))

# Load trained weights
model_path = "models/masktif_model.pth"
if not os.path.exists(model_path):
    print(f"Error: Model not found at {model_path}")
    exit(1)

model.load_state_dict(torch.load(model_path, map_location=device))
model = model.to(device)
model.eval()

all_preds = []
all_labels = []

print("Running evaluation on validation dataset...")
with torch.no_grad():
    for images, labels in val_loader:
        images = images.to(device)
        labels = labels.to(device)
        
        outputs = model(images)
        _, preds = torch.max(outputs, 1)
        
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

# Calculate metrics
accuracy = accuracy_score(all_labels, all_preds)
precision = precision_score(all_labels, all_preds, average='weighted', zero_division=0)
recall = recall_score(all_labels, all_preds, average='weighted', zero_division=0)
f1 = f1_score(all_labels, all_preds, average='weighted', zero_division=0)

print("\n--- Model Evaluation Metrics ---")
print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")
print("--------------------------------")