import os
import shutil

LABEL_DIR = r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\stage2\2\Traffic_sign_detection_data\labels"
IMAGE_DIR = r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\stage2\2\Traffic_sign_detection_data\images"
OUTPUT_DIR = r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\stage2\2\Traffic_sign_detection_data\test"

os.makedirs(OUTPUT_DIR, exist_ok=True)

found_classes = {}

for label_file in os.listdir(LABEL_DIR):
    if not label_file.endswith(".txt"):
        continue

    label_path = os.path.join(LABEL_DIR, label_file)

    base = os.path.splitext(label_file)[0]
    img_path = None
    for ext in [".jpg", ".png", ".jpeg", ".JPG", ".PNG"]:
        candidate = os.path.join(IMAGE_DIR, base + ext)
        if os.path.exists(candidate):
            img_path = candidate
            break

    if img_path is None:
        continue

    with open(label_path, "r") as f:
        lines = f.readlines()

    # class_id als float einlesen → int casten
    class_ids = set(int(float(line.split()[0])) for line in lines)

    for cid in class_ids:
        if cid in found_classes:
            continue

        class_folder = os.path.join(OUTPUT_DIR, f"class_{cid}")
        os.makedirs(class_folder, exist_ok=True)

        new_img_name = f"class_{cid}.jpg"
        new_txt_name = f"class_{cid}.txt"

        shutil.copy(img_path, os.path.join(class_folder, new_img_name))
        shutil.copy(label_path, os.path.join(class_folder, new_txt_name))

        found_classes[cid] = True
        print(f"Gespeichert: Klasse {cid} → {class_folder}")

print("Fertig!")
