import os
import cv2

# Paths
img_dir = "data/raw/Chips_Thermal_Face_Dataset/images"
label_dir = "data/raw/Chips_Thermal_Face_Dataset/annotations_yolo_format"

output_dir = "data/processed/faces"

# Create output folder
os.makedirs(output_dir, exist_ok=True)

for img_name in os.listdir(img_dir):

    img_path = os.path.join(img_dir, img_name)

    # label file name
    label_name = os.path.splitext(img_name)[0] + ".txt"
    label_path = os.path.join(label_dir, label_name)

    image = cv2.imread(img_path)

    if image is None:
        continue

    h, w, _ = image.shape

    if not os.path.exists(label_path):
        continue

    with open(label_path, "r") as f:
        lines = f.readlines()

    for line in lines:

        values = list(map(float, line.split()))

        # handle both formats
        if len(values) == 5:
            cls, x, y, bw, bh = values
        elif len(values) == 4:
            x, y, bw, bh = values
        else:
            continue

        # convert YOLO format to pixel coordinates
        x = int(x * w)
        y = int(y * h)
        bw = int(bw * w)
        bh = int(bh * h)

        x1 = int(x - bw / 2)
        y1 = int(y - bh / 2)
        x2 = int(x + bw / 2)
        y2 = int(y + bh / 2)

        face = image[y1:y2, x1:x2]

        if face.size == 0:
            continue

        save_path = os.path.join(output_dir, img_name)

        cv2.imwrite(save_path, face)

print("Faces cropped successfully!")