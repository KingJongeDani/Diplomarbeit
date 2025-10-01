# import os
# from PIL import Image

# # Pfad zu deinem Dataset
# base_path = "D:\Diplomarbeit_KI\Dataset\Training\GTSRB\Final_Training\Images"

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



import os
import csv

# Pfad
base_path = "D:\\Diplomarbeit_KI\\Dataset\\Training\\GTSRB\\Final_Training\\Images"

# Alle Unterordner durchlaufen
for folder in os.listdir(base_path):
    folder_path = os.path.join(base_path, folder)
    if not os.path.isdir(folder_path):
        continue
    
    # CSV-Datei finden (z. B. GT-00000.csv)
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            csv_path = os.path.join(folder_path, file)
            
            with open(csv_path, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=';')
                next(reader, None)  # Header überspringen
                for row in reader:
                    filename, width, height, x1, y1, x2, y2, class_id = row
                    width, height = int(width), int(height)
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    class_id = int(class_id)

                    # YOLO-Format berechnen (normiert auf 0–1)
                    x_center = ((x1 + x2) / 2) / width
                    y_center = ((y1 + y2) / 2) / height
                    bbox_width = (x2 - x1) / width
                    bbox_height = (y2 - y1) / height

                    # Bildpfad
                    image_path = os.path.join(folder_path, filename.replace(".ppm", ".png"))
                    label_path = image_path.replace(".png", ".txt")

                    # YOLO-Label speichern
                    with open(label_path, "w") as f:
                        f.write(f"{class_id} {x_center} {y_center} {bbox_width} {bbox_height}\n")

print("Alle CSV-Dateien wurden in YOLO-Labels konvertiert")


