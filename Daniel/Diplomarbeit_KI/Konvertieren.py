# import os
# from PIL import Image

# # Pfad zu deinem Dataset
# base_path = "D:\\Diplomarbeit\\Diplomarbeit\\Daniel\\Diplomarbeit_KI\\Dataset\\Sign_recognition\\Test\\GTSRB\\Final_Test\\Images"

# # Alle Unterordner durchlaufen
# for root, dirs, files in os.walk(base_path):
#     for file in files:
#         if file.endswith(".ppm"):
#             ppm_path = os.path.join(root, file)
#             png_path = os.path.join(root, file.replace(".ppm", ".png"))

#             # Bild öffnen und als PNG speichern
#             with Image.open(ppm_path) as im:
#                 im.save(png_path)
#                 os.remove(ppm_path)

#             print(f"Konvertiert: {ppm_path} -> {png_path}")



# import os
# import csv

# # Pfad
# base_path = "D:\\Diplomarbeit\\Diplomarbeit\\Daniel\\Diplomarbeit_KI\\Dataset\\Sign_recognition\\Test\\GTSRB\\Final_Test\\Images"

# # Alle Unterordner durchlaufen
# for folder in os.listdir(base_path):
#     folder_path = os.path.join(base_path, folder)
#     if not os.path.isdir(folder_path):
#         continue
    
#     # CSV-Datei finden (z. B. GT-00000.csv)
#     for file in os.listdir(folder_path):
#         if file.endswith(".csv"):
#             csv_path = os.path.join(folder_path, file)
            
#             with open(csv_path, newline='') as csvfile:
#                 reader = csv.reader(csvfile, delimiter=';')
#                 next(reader, None)  # Header überspringen
#                 for row in reader:
#                     filename, width, height, x1, y1, x2, y2, class_id = row
#                     width, height = int(width), int(height)
#                     x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
#                     class_id = int(class_id)

#                     # YOLO-Format berechnen (normiert auf 0–1)
#                     x_center = ((x1 + x2) / 2) / width
#                     y_center = ((y1 + y2) / 2) / height
#                     bbox_width = (x2 - x1) / width
#                     bbox_height = (y2 - y1) / height

#                     # Bildpfad
#                     image_path = os.path.join(folder_path, filename.replace(".ppm", ".png"))
#                     label_path = image_path.replace(".png", ".txt")

#                     # YOLO-Label speichern
#                     with open(label_path, "w") as f:
#                         f.write(f"{class_id} {x_center} {y_center} {bbox_width} {bbox_height}\n")

# print("Alle CSV-Dateien wurden in YOLO-Labels konvertiert")

import os
import csv
import random
import shutil

# --- PFAD ZUM TESTDATENSATZ ---
base_path = "D:\\Diplomarbeit\\Diplomarbeit\\Daniel\\Diplomarbeit_KI\\Dataset\\Sign_recognition\\Test\\GTSRB\\Final_Test"
images_path = os.path.join(base_path, "Images")
csv_path = os.path.join(images_path, "GT-final_test.test.csv")  # Pfad zur CSV-Datei

# --- ZIELORDNER ---
output_base = "D:\\Diplomarbeit\\Diplomarbeit\\Daniel\\Diplomarbeit_KI\\Dataset\\Processed"
os.makedirs(os.path.join(output_base, "valid", "images"), exist_ok=True)
os.makedirs(os.path.join(output_base, "valid", "labels"), exist_ok=True)
os.makedirs(os.path.join(output_base, "test", "images"), exist_ok=True)
os.makedirs(os.path.join(output_base, "test", "labels"), exist_ok=True)

# --- CSV LESEN ---
image_label_pairs = []

print("📂 Verwende CSV:", csv_path)

with open(csv_path, newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=';')  # Semikolon als Trennzeichen
    next(reader, None)  # Header überspringen
    for row in reader:
        if len(row) != 7:
            print("⚠️ Ungültige Zeile, wird übersprungen:", row)
            continue

        filename, width, height, x1, y1, x2, y2 = row
        width, height = int(width), int(height)
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        class_id = 0  # feste Klasse, da CSV keine Klasse enthält

        # --- YOLO-Format ---
        x_center = ((x1 + x2) / 2) / width
        y_center = ((y1 + y2) / 2) / height
        bbox_width = (x2 - x1) / width
        bbox_height = (y2 - y1) / height

        image_path = os.path.join(images_path, filename)
        if not os.path.exists(image_path):
            print("⚠️ Bild nicht gefunden:", image_path)
            continue

        label_name = os.path.splitext(filename)[0] + ".txt"
        label_content = f"{class_id} {x_center} {y_center} {bbox_width} {bbox_height}\n"

        image_label_pairs.append((image_path, label_name, label_content))

print(f"📸 {len(image_label_pairs)} Bilder gefunden. Starte Aufteilung...")

# --- AUFTEILUNG (80% valid, 20% test) ---
random.shuffle(image_label_pairs)
split_idx = int(0.8 * len(image_label_pairs))
splits = {
    "valid": image_label_pairs[:split_idx],
    "test": image_label_pairs[split_idx:]
}

# --- DATEIEN KOPIEREN ---
for split_name, data in splits.items():
    for img_path, label_name, label_content in data:
        img_dest = os.path.join(output_base, split_name, "images", os.path.basename(img_path))
        lbl_dest = os.path.join(output_base, split_name, "labels", label_name)

        shutil.copy(img_path, img_dest)
        with open(lbl_dest, "w") as f:
            f.write(label_content)

print("✅ Validierung & Test erfolgreich erstellt!")





