import os
import logging
import numpy as np
import onnxruntime as ort
from PIL import Image

from config import Config

# ------------------------------------------
# global variables
# ------------------------------------------
session = None
class_names = []
logger = logging.getLogger(__name__)

# ------------------------------------------
# get class names
# ------------------------------------------
def get_class_names(train_dir):

    if not os.path.isdir(train_dir):
        logger.warning("Train dir not found for class names: %s", train_dir)
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
# load onnx model
# ------------------------------------------
def load_model(
    path=Config.MODEL_PATH,
    train_dir=Config.TRAIN_DIR
):
    global session
    global class_names

    if session is not None:
        return session, class_names

    if not os.path.exists(path):
        raise FileNotFoundError(
            "ONNX model file not found."
        )

    class_names = get_class_names(train_dir)

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

    session = ort.InferenceSession(
        path,
        providers=["CPUExecutionProvider"]
    )

    logger.info("ONNX model loaded: %s", path)

    return session, class_names


# ------------------------------------------
# preprocess image
# ------------------------------------------
def preprocess_image(image_path):

    image = Image.open(image_path).convert("RGB")
    image = image.resize((224, 224))

    img = np.array(image).astype(np.float32) / 255.0

    mean = np.array(
        [0.485, 0.456, 0.406],
        dtype=np.float32
    )

    std = np.array(
        [0.229, 0.224, 0.225],
        dtype=np.float32
    )

    img = (img - mean) / std

    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, axis=0)

    return img.astype(np.float32)


# ------------------------------------------
# softmax
# ------------------------------------------
def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


# ------------------------------------------
# predict image
# ------------------------------------------
def predict_image(image_path):

    global session
    global class_names

    if session is None:
        load_model()

    if not os.path.exists(image_path):
        raise FileNotFoundError(
            "Image file not found"
        )

    input_tensor = preprocess_image(
        image_path
    )

    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    output = session.run(
        [output_name],
        {input_name: input_tensor}
    )[0][0]

    probs = softmax(output)

    pred_idx = int(np.argmax(probs))
    conf = float(probs[pred_idx])

    if conf < 0.60:
        label = "Unknown"
    else:
        if (
            class_names and
            0 <= pred_idx < len(class_names)
        ):
            label = class_names[pred_idx]
        else:
            label = f"class_{pred_idx}"

    logger.info("Prediction: %s (%.2f) image=%s", label, conf, os.path.basename(image_path))

    return label, conf