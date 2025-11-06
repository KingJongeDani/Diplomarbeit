# import os
# from PIL import Image

# # Pfad zu deinem Dataset
# base_path = "D:\\Diplomarbeit\\Diplomarbeit\\Daniel\\Diplomarbeit_KI\\Dataset\\Sign_recognition\\GTS\\GTSDB\\TrainIJCNN2013\\TrainIJCNN2013"

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





# import csv

# # Pfade zur Eingabe- und Ausgabedatei
# input_file = "D:\\Diplomarbeit\\Diplomarbeit\\Daniel\\Diplomarbeit_KI\\Dataset\\Sign_recognition\\GTS\\GTSDB\\TrainIJCNN2013\\TrainIJCNN2013\\ex.txt"
# output_file = "D:\\Diplomarbeit\\Diplomarbeit\\Daniel\\Diplomarbeit_KI\\Dataset\\Sign_recognition\\GTS\\GTSDB\\TrainIJCNN2013\\TrainIJCNN2013\\annotations.csv"

# # CSV schreiben
# with open(input_file, "r") as txt_file, open(output_file, "w", newline="") as csv_file:
#     reader = txt_file.readlines()
#     writer = csv.writer(csv_file)

#     # Kopfzeile (optional)
#     writer.writerow(["filename", "x_min", "y_min", "x_max", "y_max"])

#     for line in reader:
#         # Entferne Zeilenumbrüche und splitte anhand von Semikolon
#         parts = line.strip().split(";")
#         if len(parts) == 5:
#             writer.writerow(parts)

# print(f"✅ Konvertierung abgeschlossen: {output_file}")



# import pandas as pd
# import os

# # Pfade
# base_dir = r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\Sign_recognition\GTS_without_130_endof_vorangssttrasse\GTSRB"
# csv_path = os.path.join(base_dir, "Test.csv")

# # Alte CSV laden
# df = pd.read_csv(csv_path)

# # Mapping alte ID -> neue ID + Ordnername
# id_map = {
#     0:  ("00_speedlimit_20", 0),
#     1:  ("01_speedlimit_30", 1),
#     2:  ("02_speedlimit_50", 2),
#     3:  ("03_speedlimit_60", 3),
#     4:  ("04_speedlimit_70", 4),
#     5:  ("05_speedlimit_80", 5),
#     6:  ("06_end_of_speedlimit_80", 6),
#     7:  ("07_speedlimit_100", 7),
#     9:  ("08_no_overtaking", 8),
#     13: ("09_yield", 9),
#     14: ("10_stop", 10),
#     15: ("11_no_vehicles", 11),
#     17: ("12_no_entry", 12),
#     32: ("13_end_all_limits", 13),
#     41: ("14_end_of_no_overtaking", 14)
# }

# # Nur Zeilen behalten, deren alte ClassId im Mapping vorkommt
# df = df[df["ClassId"].isin(id_map.keys())].copy()

# # Neue Pfade und ClassIds zuweisen
# def update_row(row):
#     folder_name, new_id = id_map[row["ClassId"]]
#     filename = os.path.basename(row["Path"])
#     row["Path"] = os.path.join("Train", folder_name, filename).replace("\\", "/")
#     row["ClassId"] = new_id
#     return row

# df = df.apply(update_row, axis=1)

# # Neue CSV speichern
# output_path = os.path.join(base_dir, "Train_updated.csv")
# df.to_csv(output_path, index=False)

# print(f"Neue CSV gespeichert unter: {output_path}")





import os
import pandas as pd

# ==== Pfade anpassen ====
root_dir = r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\Sign_recognition\GTS_without_130_endof_vorangssttrasse\GTSRB"
csv_path = os.path.join(root_dir, "Train", "Train_Train.csv")
output_csv = os.path.join(root_dir, "annotations_roboflow.csv")

# ==== CSV laden ====
df = pd.read_csv(csv_path)

# ==== Spalten anpassen ====
df = df.rename(columns={
    "Roi.X1": "x_min",
    "Roi.Y1": "y_min",
    "Roi.X2": "x_max",
    "Roi.Y2": "y_max",
    "ClassId": "class"
})

# ==== Nur relevante Spalten behalten ====
df = df[["Path", "x_min", "y_min", "x_max", "y_max", "class"]]
df = df.rename(columns={"Path": "filename"})

# ==== Klassen-Namen hinzufügen ====
class_map = {
    0: "00_speedlimit_20",
    1: "01_speedlimit_30",
    2: "02_speedlimit_50",
    3: "03_speedlimit_60",
    4: "04_speedlimit_70",
    5: "05_speedlimit_80",
    6: "06_end_of_speedlimit_80",
    7: "07_speedlimit_100",
    8: "08_no_overtaking",
    9: "09_yield",
    10: "10_stop",
    11: "11_no_vehicles",
    12: "12_no_entry",
    13: "13_end_all_limits",
    14: "14_end_of_no_overtaking"
}
df["class_name"] = df["class"].map(class_map)

# ==== Pfade anpassen ====
# Beispiel: "Train/00_speedlimit_20/00000_00000_00022.png"
# → soll bleiben, aber Backslashes durch / ersetzen (Roboflow-kompatibel)
df["filename"] = df["filename"].apply(lambda x: x.replace("\\", "/"))

# Prüfen, ob "Train/" am Anfang fehlt – wenn nicht vorhanden, hinzufügen
df["filename"] = df["filename"].apply(lambda x: x if x.startswith("Train/") else f"Train/{x}")

# ==== CSV speichern ====
df.to_csv(output_csv, index=False)

print(f"\n✅ CSV für Roboflow gespeichert unter: {output_csv}")
print("📂 Bilder bleiben in den bestehenden Klassenordnern.")
print("⚙️ Beim Upload auf Roboflow: 'Object Detection' auswählen.")









# # Bounding Boxes schauen
# import os
# import shutil
# import pandas as pd
# import cv2

# # ===== Pfade anpassen =====
# base_path = r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\Sign_recognition\GTS_without_130_endof_vorangssttrasse\GTSDB\TrainIJCNN2013\TrainIJCNN2013"
# csv_path = os.path.join(base_path, "filtered_dataset", "annotations_filtered.csv")
# images_path = os.path.join(base_path, "filtered_dataset", "images")

# # Neuer Zielordner
# output_base = os.path.join(base_path, "dataset_split")
# output_images = os.path.join(output_base, "images")
# os.makedirs(output_images, exist_ok=True)

# # ===== CSV laden =====
# df = pd.read_csv(csv_path)

# # Neue CSV-Einträge
# new_rows = []

# # ===== Alle Bilder durchgehen =====
# for filename, group in df.groupby("filename"):
#     image_path = os.path.join(images_path, filename)

#     if not os.path.exists(image_path):
#         print(f"⚠️ Bild fehlt: {image_path}")
#         continue

#     if len(group) == 1:
#         # Bild einfach kopieren
#         shutil.copy(image_path, os.path.join(output_images, filename))
#         new_rows.append(group.iloc[0].to_dict())
#     else:
#         # Mehrere Bounding Boxes → Bild mehrfach kopieren
#         for i, (_, row) in enumerate(group.iterrows(), start=1):
#             name, ext = os.path.splitext(filename)
#             new_filename = f"{name}_{i}{ext}"

#             # Bild kopieren
#             shutil.copy(image_path, os.path.join(output_images, new_filename))

#             # CSV-Eintrag anpassen
#             row_dict = row.to_dict()
#             row_dict["filename"] = new_filename
#             new_rows.append(row_dict)

# # ===== Neue CSV speichern =====
# new_df = pd.DataFrame(new_rows)
# new_csv_path = os.path.join(output_base, "annotations_split.csv")
# new_df.to_csv(new_csv_path, index=False)

# print(f"✅ Fertig! Neue Daten liegen in: {output_base}")








# # Image Test
# import cv2
# import pandas as pd
# import os

# # ===== Pfade anpassen =====
# base_path = r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\Sign_recognition\GTS_without_130_endof_vorangssttrasse\GTSDB\TrainIJCNN2013\TrainIJCNN2013"
# csv_path = os.path.join(base_path, "filtered_dataset", "annotations_filtered.csv")
# images_path = os.path.join(base_path, "filtered_dataset", "images")

# # ===== CSV laden =====
# df = pd.read_csv(csv_path)

# # ===== Beispielbild auswählen =====
# # (Ändere diesen Namen oder wähle zufällig eines)
# image_name = "00004.png"  # erstes Bild aus der CSV
# print(f"Zeige Beispielbild: {image_name}")

# image_path = os.path.join(images_path, image_name)

# # ===== Bild laden =====
# image = cv2.imread(image_path)
# if image is None:
#     print(f"⚠️ Konnte Bild nicht laden: {image_path}")
#     exit()

# # ===== Alle Bounding Boxes für dieses Bild laden =====
# image_annotations = df[df["filename"] == image_name]

# # ===== Bounding Boxes zeichnen =====
# for _, row in image_annotations.iterrows():
#     xmin, ymin, xmax, ymax = int(row['x_min']), int(row['y_min']), int(row['x_max']), int(row['y_max'])
#     label = row['class_name'] if 'class_name' in row else str(row['class'])

#     # Rechteck zeichnen
#     cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)

#     # Text-Hintergrund für bessere Lesbarkeit
#     (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
#     cv2.rectangle(image, (xmin, ymin - h - 8), (xmin + w, ymin), (0, 255, 0), -1)

#     # Text über dem Rechteck zeichnen
#     cv2.putText(image, label, (xmin, ymin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

# # ===== Bild anzeigen =====
# cv2.imshow("Bounding Boxes Test", image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()








# import os
# import shutil

# # --- Pfade zu deinem Dataset (raw strings verwenden!) ---
# images_root = r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\Road_recognition\driver_161_90frame"
# masks_root  = r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\Road_recognition\driver_161_90frame_labels"

# # --- Zielordner ---
# output_images = r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\Road_recognition\images"
# output_masks  = r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\Road_recognition\masks"

# os.makedirs(output_images, exist_ok=True)
# os.makedirs(output_masks, exist_ok=True)

# # --- Durch alle Unterordner gehen ---
# for subfolder in os.listdir(images_root):
#     img_subdir = os.path.join(images_root, subfolder)
#     mask_subdir = os.path.join(masks_root, subfolder)

#     if not os.path.isdir(img_subdir):
#         continue  # nur Ordner

#     print(f"Bearbeite Unterordner: {subfolder}")

#     # Alle Dateien im Unterordner durchgehen
#     for filename in os.listdir(img_subdir):
#         file_path = os.path.join(img_subdir, filename)

#         # 1️⃣ Bilder kopieren
#         if filename.lower().endswith(".jpg"):
#             mask_path = os.path.join(mask_subdir, filename.replace(".jpg", ".png"))

#             if not os.path.exists(mask_path):
#                 print(f"Mask fehlt für {file_path}, überspringe...")
#                 continue

#             # Neuer eindeutiger Name
#             new_name = f"{subfolder}_{filename}"
#             shutil.copy(file_path, os.path.join(output_images, new_name))
#             shutil.copy(mask_path, os.path.join(output_masks, new_name.replace(".jpg", ".png")))
#             print(f"Kopiert: {new_name}")

#         # 2️⃣ .txt Dateien löschen
#         elif filename.lower().endswith(".txt"):
#             try:
#                 os.remove(file_path)
#                 print(f"Gelöscht: {file_path}")
#             except Exception as e:
#                 print(f"Fehler beim Löschen {file_path}: {e}")

# print("✅ Fertig! Alle Bilder und Masken flach kopiert, Dateinamen umbenannt, .txt Dateien gelöscht.")












# import os
# import pandas as pd
# import shutil

# # ===== Pfade anpassen =====
# base_path = r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\Sign_recognition\GTS_without_130_endof_vorangssttrasse\GTSDB\TrainIJCNN2013\TrainIJCNN2013"
# csv_path = os.path.join(base_path, "annotations.csv")

# # Neuer Ordner für Ergebnisse
# output_path = os.path.join(base_path, "filtered_dataset")
# images_output = os.path.join(output_path, "images")
# os.makedirs(images_output, exist_ok=True)

# # ===== CSV einlesen =====
# df = pd.read_csv(csv_path)

# # ===== Mapping: alte Klassen -> neue Namen =====
# class_map = {
#     0: "00_speedlimit_20",
#     1: "01_speedlimit_30",
#     2: "02_speedlimit_50",
#     3: "03_speedlimit_60",
#     4: "04_speedlimit_70",
#     5: "05_speedlimit_80",
#     6: "06_end_of_speedlimit_80",
#     7: "07_speedlimit_100",
#     9: "08_no_overtaking",
#     13: "09_yield",
#     14: "10_stop",
#     15: "11_no_vehicles",
#     17: "12_no_entry",
#     32: "13_end_all_limits",
#     41: "14_end_of_no_overtaking"
# }

# valid_classes = list(class_map.keys())

# # ===== Nur relevante Klassen behalten =====
# filtered_df = df[df["class"].isin(valid_classes)].copy()

# # ===== Neue Spalte mit Klassennamen =====
# filtered_df["class_name"] = filtered_df["class"].map(class_map)

# # ===== Nur benötigte Bilder kopieren =====
# unique_images = filtered_df["filename"].unique()

# print(f"➡️ Kopiere {len(unique_images)} Bilder ...")

# for img_name in unique_images:
#     src = os.path.join(base_path, img_name)
#     dst = os.path.join(images_output, img_name)
#     if os.path.exists(src):
#         shutil.copy(src, dst)
#     else:
#         print(f"⚠️ Bild nicht gefunden: {img_name}")

# # ===== Gefilterte CSV speichern =====
# filtered_csv_path = os.path.join(output_path, "annotations_filtered.csv")
# filtered_df.to_csv(filtered_csv_path, index=False)

# print("\n✅ Fertig!")
# print(f"Neue CSV gespeichert unter: {filtered_csv_path}")
# print(f"Gefilterte Bilder im Ordner: {images_output}")
# print(f"Behaltene Klassen: {sorted(valid_classes)}")












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

# import os
# import csv
# import random
# import shutil

# # --- PFAD ZUM TESTDATENSATZ ---
# base_path = "D:\\Diplomarbeit\\Diplomarbeit\\Daniel\\Diplomarbeit_KI\\Dataset\\Sign_recognition\\Test\\GTSRB\\Final_Test"
# images_path = os.path.join(base_path, "Images")
# csv_path = os.path.join(images_path, "GT-final_test.test.csv")  # Pfad zur CSV-Datei

# # --- ZIELORDNER ---
# output_base = "D:\\Diplomarbeit\\Diplomarbeit\\Daniel\\Diplomarbeit_KI\\Dataset\\Processed"
# os.makedirs(os.path.join(output_base, "valid", "images"), exist_ok=True)
# os.makedirs(os.path.join(output_base, "valid", "labels"), exist_ok=True)
# os.makedirs(os.path.join(output_base, "test", "images"), exist_ok=True)
# os.makedirs(os.path.join(output_base, "test", "labels"), exist_ok=True)

# # --- CSV LESEN ---
# image_label_pairs = []

# print("📂 Verwende CSV:", csv_path)

# with open(csv_path, newline='') as csvfile:
#     reader = csv.reader(csvfile, delimiter=';')  # Semikolon als Trennzeichen
#     next(reader, None)  # Header überspringen
#     for row in reader:
#         if len(row) != 7:
#             print("⚠️ Ungültige Zeile, wird übersprungen:", row)
#             continue

#         filename, width, height, x1, y1, x2, y2 = row
#         width, height = int(width), int(height)
#         x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
#         class_id = 0  # feste Klasse, da CSV keine Klasse enthält

#         # --- YOLO-Format ---
#         x_center = ((x1 + x2) / 2) / width
#         y_center = ((y1 + y2) / 2) / height
#         bbox_width = (x2 - x1) / width
#         bbox_height = (y2 - y1) / height

#         image_path = os.path.join(images_path, filename)
#         if not os.path.exists(image_path):
#             print("⚠️ Bild nicht gefunden:", image_path)
#             continue

#         label_name = os.path.splitext(filename)[0] + ".txt"
#         label_content = f"{class_id} {x_center} {y_center} {bbox_width} {bbox_height}\n"

#         image_label_pairs.append((image_path, label_name, label_content))

# print(f"📸 {len(image_label_pairs)} Bilder gefunden. Starte Aufteilung...")

# # --- AUFTEILUNG (80% valid, 20% test) ---
# random.shuffle(image_label_pairs)
# split_idx = int(0.8 * len(image_label_pairs))
# splits = {
#     "valid": image_label_pairs[:split_idx],
#     "test": image_label_pairs[split_idx:]
# }

# # --- DATEIEN KOPIEREN ---
# for split_name, data in splits.items():
#     for img_path, label_name, label_content in data:
#         img_dest = os.path.join(output_base, split_name, "images", os.path.basename(img_path))
#         lbl_dest = os.path.join(output_base, split_name, "labels", label_name)

#         shutil.copy(img_path, img_dest)
#         with open(lbl_dest, "w") as f:
#             f.write(label_content)

# print("✅ Validierung & Test erfolgreich erstellt!")





