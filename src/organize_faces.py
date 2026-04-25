import os
import shutil

# input folder
input_path = "data/processed/faces"

# output folder
output_path = "data/processed/faces_by_person"

# create output folder
os.makedirs(output_path, exist_ok=True)

total_images = 0
copied_images = 0

# all files
files = os.listdir(input_path)

for file in files:

    # only image files
    if not file.lower().endswith((".jpg", ".jpeg", ".png")):
        continue

    total_images += 1

    # file name example: 1_1.jpeg
    parts = file.split("_")

    # if wrong name then skip
    if len(parts) < 2:
        continue

    person_id = parts[0]

    # create person folder
    person_folder = os.path.join(
        output_path,
        "person_" + person_id
    )

    os.makedirs(person_folder, exist_ok=True)

    # source and destination
    src = os.path.join(input_path, file)
    dst = os.path.join(person_folder, file)

    shutil.copy(src, dst)

    copied_images += 1

print("Dataset organized successfully")
print("Total Images =", total_images)
print("Copied Images =", copied_images)