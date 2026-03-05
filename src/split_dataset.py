import os
import shutil
import random

input_dir = "data/processed/faces_by_person"
output_dir = "data/split"

train_dir = os.path.join(output_dir, "train")
val_dir = os.path.join(output_dir, "val")
test_dir = os.path.join(output_dir, "test")

os.makedirs(train_dir, exist_ok=True)
os.makedirs(val_dir, exist_ok=True)
os.makedirs(test_dir, exist_ok=True)

for person in os.listdir(input_dir):

    person_path = os.path.join(input_dir, person)
    images = os.listdir(person_path)

    random.shuffle(images)

    train_split = int(0.7 * len(images))
    val_split = int(0.85 * len(images))

    train_imgs = images[:train_split]
    val_imgs = images[train_split:val_split]
    test_imgs = images[val_split:]

    for img in train_imgs:
        src = os.path.join(person_path, img)
        dst = os.path.join(train_dir, person)
        os.makedirs(dst, exist_ok=True)
        shutil.copy(src, dst)

    for img in val_imgs:
        src = os.path.join(person_path, img)
        dst = os.path.join(val_dir, person)
        os.makedirs(dst, exist_ok=True)
        shutil.copy(src, dst)

    for img in test_imgs:
        src = os.path.join(person_path, img)
        dst = os.path.join(test_dir, person)
        os.makedirs(dst, exist_ok=True)
        shutil.copy(src, dst)

print("Dataset split completed!")