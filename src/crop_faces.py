import os
import cv2
image_path = "data/raw/Chips_Thermal_Face_Dataset/images"
label_path = "data/raw/Chips_Thermal_Face_Dataset/annotations_yolo_format"
output_path = "data/processed/faces"

# create output folder
os.makedirs(output_path, exist_ok=True)

total_images = 0
saved_images = 0
missing_label = 0

# all images
files = os.listdir(image_path)

for file in files:

    # only image files
    if not file.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    total_images += 1

    img_file = os.path.join(image_path, file)

    # label file name
    name = os.path.splitext(file)[0]
    txt_file = os.path.join(label_path, name + ".txt")

    # if label not found
    if not os.path.exists(txt_file):
        missing_label += 1
        continue

    # read image
    img = cv2.imread(img_file)

    if img is None:
        continue

    h, w = img.shape[:2]

    # read label file
    f = open(txt_file, "r")
    lines = f.readlines()
    f.close()

    last_crop = None

    for line in lines:

        data = line.strip().split()

        # yolo format can be 5 values
        if len(data) < 5:
            continue

        # class id ignore
        x = float(data[1])
        y = float(data[2])
        bw = float(data[3])
        bh = float(data[4])

        # convert to pixel values
        center_x = int(x * w)
        center_y = int(y * h)

        box_w = int(bw * w)
        box_h = int(bh * h)

        x1 = int(center_x - box_w / 2)
        y1 = int(center_y - box_h / 2)
        x2 = int(center_x + box_w / 2)
        y2 = int(center_y + box_h / 2)

        # boundary check
        if x1 < 0:
            x1 = 0
        if y1 < 0:
            y1 = 0
        if x2 > w:
            x2 = w
        if y2 > h:
            y2 = h

        crop = img[y1:y2, x1:x2]

        if crop.size == 0:
            continue

        last_crop = crop

    # save last valid crop
    if last_crop is not None:

        save_file = os.path.join(output_path, file)

        cv2.imwrite(save_file, last_crop)
        saved_images += 1

print("Face cropping completed")
print("Total Images =", total_images)
print("Faces Saved =", saved_images)
print("Missing Labels =", missing_label)