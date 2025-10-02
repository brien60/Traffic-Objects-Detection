# Imports
from pathlib import Path
import os

from PIL import Image

# Constants
labels_path = Path("labels")
images_path = Path("images")

label_files_list = list(labels_path.glob("*.txt"))

num_files = len(label_files_list)
split = int(num_files * 0.8)

kitti_path = Path("datasets/kitti")



# process images
os.makedirs(kitti_path / "images" / "train")
os.mkdir(kitti_path / "images" / "val")
os.mkdir(kitti_path / "images" / "test")

train_image_files_list = list((images_path/"train").glob("*.png"))

for image_path in train_image_files_list:
    split_type = "train" if int(image_path.stem) < split else "val"
    image_path.rename(kitti_path / "images" / split_type / image_path.name)


test_image_files_list = list((images_path/"test").glob("*.png"))
for image_path in test_image_files_list:
    image_path.rename(kitti_path / "images" / "test" / image_path.name)

os.removedirs("images/train")
os.removedirs("images/test")

images_path = kitti_path / "images"


# process labels
os.makedirs(kitti_path / "labels" / "train")
os.mkdir(kitti_path / "labels" / "val")


object_classes = ['Car', 'Van', 'Truck', 'Pedestrian', 'Person_sitting', 'Cyclist', 'Tram']
class_to_idx = {object_classes[i] : i for i in range(len(object_classes))}


for label_path in label_files_list:
    new_lines = []

    split_type = "train" if int(label_path.stem) < split else "val"


    with open(label_path, 'r', encoding="utf-8") as f:
        for line in f:
            if "DontCare" in line or "Misc" in line:
                continue
            
            line_entries = line.split(" ")

            L, T, R, B = [float(i) for i in line_entries[4:8]]
            
            x_center = (L + R) / 2; y_center = (T + B) / 2

            width = R - L; height = B - T

            img_path = images_path / split_type / (label_path.stem + ".png")
            img = Image.open(img_path)

            img_width, img_height = img.size

            x_center /= img_width; y_center /= img_height
            width /= img_width; height /= img_height

            new_lines.append(f"{class_to_idx[line_entries[0]]} {x_center:.7f} {y_center:.7f} {width:.7f} {height:.7f}\n")

    label_path.unlink()

    output_path = kitti_path / "labels" / split_type / label_path.name
    with open(output_path, 'x', encoding="utf-8") as f:
        f.writelines(new_lines)

os.removedirs("labels")
labels_path = kitti_path / "labels"
