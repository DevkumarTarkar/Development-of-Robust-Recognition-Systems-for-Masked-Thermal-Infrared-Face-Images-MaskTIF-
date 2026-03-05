import os
import shutil

input_dir = "data/processed/faces"
output_dir = "data/processed/faces_by_person"

os.makedirs(output_dir, exist_ok=True)

for img in os.listdir(input_dir):

    if not img.endswith(".jpeg"):
        continue

    person_id = img.split("_")[0]

    person_folder = os.path.join(output_dir, f"person_{person_id}")

    os.makedirs(person_folder, exist_ok=True)

    src = os.path.join(input_dir, img)
    dst = os.path.join(person_folder, img)

    shutil.copy(src, dst)

print("Dataset organized by person successfully!")