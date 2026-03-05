import os
import cv2

# input dataset (preprocessed images)
input_dir = "data/preprocessed"

# output dataset (masked images)
output_dir = "data/masked"

for split in ["train", "val", "test"]:

    split_path = os.path.join(input_dir, split)

    for person in os.listdir(split_path):

        person_path = os.path.join(split_path, person)

        output_person = os.path.join(output_dir, split, person)

        os.makedirs(output_person, exist_ok=True)

        for img in os.listdir(person_path):

            img_path = os.path.join(person_path, img)

            image = cv2.imread(img_path)

            if image is None:
                continue

            h, w, _ = image.shape

            # mask position (lower part of face)
            mask_start = int(h * 0.55)

            # draw synthetic mask
            cv2.rectangle(image, (0, mask_start), (w, h), (0, 0, 0), -1)

            save_path = os.path.join(output_person, img)

            cv2.imwrite(save_path, image)

print("Synthetic masked dataset generated successfully!")