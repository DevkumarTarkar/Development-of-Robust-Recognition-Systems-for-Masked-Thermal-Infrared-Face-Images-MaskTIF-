import os
import random
import shutil

# input folder
input_path = "data/processed/faces_by_person"

# output folder
output_path = "data/split"

# if output folder already exists then delete old data
if os.path.exists(output_path):
    shutil.rmtree(output_path)

# create main folders
os.makedirs(os.path.join(output_path, "train"))
os.makedirs(os.path.join(output_path, "val"))
os.makedirs(os.path.join(output_path, "test"))

# split ratio
train_ratio = 0.70
val_ratio = 0.15
test_ratio = 0.15

# random seed for same result every time
random.seed(42)

total_files = 0

# read all person folders
persons = os.listdir(input_path)

for person in persons:

    person_folder = os.path.join(input_path, person)

    # check folder
    if not os.path.isdir(person_folder):
        continue

    # take only image files
    images = []

    for file in os.listdir(person_folder):

        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            images.append(file)

    # skip if no images
    if len(images) == 0:
        continue

    # shuffle images
    random.shuffle(images)

    total = len(images)

    # count images
    train_count = int(total * train_ratio)
    val_count = int(total * val_ratio)

    # split images
    train_images = images[:train_count]
    val_images = images[train_count:train_count + val_count]
    test_images = images[train_count + val_count:]

    # create person folders
    train_folder = os.path.join(output_path, "train", person)
    val_folder = os.path.join(output_path, "val", person)
    test_folder = os.path.join(output_path, "test", person)

    os.makedirs(train_folder, exist_ok=True)
    os.makedirs(val_folder, exist_ok=True)
    os.makedirs(test_folder, exist_ok=True)

    # copy train images
    for img in train_images:

        src = os.path.join(person_folder, img)
        dst = os.path.join(train_folder, img)

        shutil.copy(src, dst)
        total_files += 1

    # copy val images
    for img in val_images:

        src = os.path.join(person_folder, img)
        dst = os.path.join(val_folder, img)

        shutil.copy(src, dst)
        total_files += 1

    # copy test images
    for img in test_images:

        src = os.path.join(person_folder, img)
        dst = os.path.join(test_folder, img)

        shutil.copy(src, dst)
        total_files += 1

    # print split result
    print(person)
    print("Train Images =", len(train_images))
    print("Validation Images =", len(val_images))
    print("Test Images =", len(test_images))
    print("----------------------")

print("Dataset split completed")
print("Total files copied =", total_files)