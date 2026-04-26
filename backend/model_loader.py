import os
import torch
from PIL import Image
from torchvision import models, transforms

from config import Config

# ------------------------------------------
# global variables
# ------------------------------------------
model = None
class_names = []

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ------------------------------------------
# get class names from train folder
# ------------------------------------------
def get_class_names(train_dir):

    if not os.path.isdir(train_dir):
        print(f"Warning: {train_dir} not found")
        return []

    classes = [
        folder_name
        for folder_name in os.listdir(train_dir)
        if os.path.isdir(
            os.path.join(train_dir, folder_name)
        )
    ]

    classes.sort()

    return classes


# ------------------------------------------
# load trained model
# ------------------------------------------
def load_model(
    path=Config.MODEL_PATH,
    train_dir=Config.TRAIN_DIR
):

    global model
    global class_names

    # already loaded
    if model is not None:
        return model, class_names

    # model file check
    if not os.path.exists(path):

        print("Model file not found.")

        raise FileNotFoundError(
            "Trained model file is missing."
        )

    # get classes
    class_names = get_class_names(train_dir)

    # fallback classes
    if not class_names:

        class_names = [
            "person_1",
            "person_2",
            "person_3",
            "person_4",
            "person_5",
            "person_6",
            "person_7",
            "person_8",
            "person_group1"
        ]

    # load weights
    state_dict = torch.load(
        path,
        map_location=device
    )

    # create model architecture
    resnet = models.resnet50(
        weights=None
    )

    num_features = resnet.fc.in_features

    num_classes = len(class_names)

    # detect classes from weights
    if "fc.weight" in state_dict:

        num_classes = state_dict[
            "fc.weight"
        ].shape[0]

    resnet.fc = torch.nn.Linear(
        num_features,
        num_classes
    )

    resnet.load_state_dict(state_dict)

    resnet.to(device)
    resnet.eval()

    model = resnet

    print(f"Model loaded on {device}")

    return model, class_names


# ------------------------------------------
# image preprocessing
# ------------------------------------------
preprocess = transforms.Compose([

    transforms.Resize((224, 224)),

    transforms.Grayscale(
        num_output_channels=3
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# ------------------------------------------
# predict image
# ------------------------------------------
def predict_image(image_path):

    global model
    global class_names

    if model is None:
        raise Exception(
            "Model not loaded yet"
        )

    if not os.path.exists(image_path):
        raise FileNotFoundError(
            "Image file not found"
        )

    # open image
    image = Image.open(
        image_path
    ).convert("RGB")

    # preprocess
    tensor = preprocess(
        image
    ).unsqueeze(0).to(device)

    # prediction
    with torch.no_grad():

        output = model(tensor)

        probs = torch.softmax(
            output,
            dim=1
        )[0]

        confidence, pred_idx = torch.max(
            probs,
            dim=0
        )

    idx = pred_idx.item()

    conf = float(
        confidence.item()
    )

    # confidence threshold
    if conf < 0.60:

        label = "Unknown"

    else:

        if (
            class_names and
            0 <= idx < len(class_names)
        ):
            label = class_names[idx]
        else:
            label = f"class_{idx}"

    print(
        f"Prediction: {label} "
        f"({conf:.2f})"
    )

    return label, conf