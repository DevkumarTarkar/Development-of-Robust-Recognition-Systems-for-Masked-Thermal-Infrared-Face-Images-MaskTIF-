import torch
import torch.nn as nn
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import numpy as np

data_dir = "data/masked"

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor()
])

test_dataset = datasets.ImageFolder(data_dir + "/test", transform=transform)
test_loader = DataLoader(test_dataset, batch_size=16)

model = models.resnet50(pretrained=False)
model.fc = nn.Linear(model.fc.in_features, len(test_dataset.classes))

model.load_state_dict(torch.load("models/masktif_model.pth"))
model.eval()

all_preds = []
all_labels = []

with torch.no_grad():
    for images, labels in test_loader:

        outputs = model(images)
        _, preds = torch.max(outputs,1)

        all_preds.extend(preds.numpy())
        all_labels.extend(labels.numpy())

# metrics
accuracy = accuracy_score(all_labels, all_preds)
precision = precision_score(all_labels, all_preds, average='weighted')
recall = recall_score(all_labels, all_preds, average='weighted')
f1 = f1_score(all_labels, all_preds, average='weighted')

cm = confusion_matrix(all_labels, all_preds)

print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
print("F1 Score:", f1)

print("\nConfusion Matrix:\n", cm)

print("\nDetailed Classification Report:\n")
print(classification_report(all_labels, all_preds, target_names=test_dataset.classes))

# confusion matrix heatmap
plt.imshow(cm)
plt.title("Confusion Matrix")
plt.colorbar()

tick_marks = np.arange(len(test_dataset.classes))
plt.xticks(tick_marks, test_dataset.classes, rotation=45)
plt.yticks(tick_marks, test_dataset.classes)

plt.xlabel("Predicted")
plt.ylabel("Actual")

plt.show()