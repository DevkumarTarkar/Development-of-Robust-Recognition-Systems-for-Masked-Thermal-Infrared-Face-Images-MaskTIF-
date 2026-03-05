import os
import cv2

input_dir = "data/split"
output_dir = "data/preprocessed"

size = (224, 224)

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

            # resize image
            image = cv2.resize(image, size)

            save_path = os.path.join(output_person, img)

            cv2.imwrite(save_path, image)

print("Preprocessing completed!")