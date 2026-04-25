import os
import cv2

# input folder
input_path = "data/preprocessed"

# output folder
output_path = "data/masked"

# dataset folders
folders = ["train", "val", "test"]

# mask start position (55% from top)
mask_ratio = 0.55

total_images = 0
saved_images = 0

for folder in folders:

    split_folder = os.path.join(input_path, folder)

    # skip if folder not found
    if not os.path.exists(split_folder):
        continue

    persons = os.listdir(split_folder)

    for person in persons:

        person_folder = os.path.join(split_folder, person)

        if not os.path.isdir(person_folder):
            continue

        # output person folder
        save_person = os.path.join(output_path, folder, person)
        os.makedirs(save_person, exist_ok=True)

        images = os.listdir(person_folder)

        for img in images:

            # only image files
            if not img.lower().endswith((".jpg", ".jpeg", ".png")):
                continue

            total_images += 1

            img_path = os.path.join(person_folder, img)

            # read image
            image = cv2.imread(img_path)

            if image is None:
                continue

            h, w = image.shape[:2]

            # mask start point
            y = int(h * mask_ratio)

            # black mask on lower face
            cv2.rectangle(
                image,
                (0, y),
                (w, h),
                (0, 0, 0),
                -1
            )

            # save image
            save_path = os.path.join(save_person, img)

            cv2.imwrite(save_path, image)

            saved_images += 1

print("Masked dataset created")
print("Total Images =", total_images)
print("Saved Images =", saved_images)