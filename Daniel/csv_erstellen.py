import os
import cv2
import pandas as pd

# Hauptordner mit Unterordnern (z. B. dataset/30_limit, dataset/stop, ...)
base_dir = "D:\\Diplomarbeit\\Diplomarbeit\\Daniel\\Diplomarbeit_KI\\Dataset\\Sign_recognition\\real_dataset_without end of\\test"

# Ausgabedatei
output_csv = "roboflow_dataset.csv"

rows = []

for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(root, file)
            
            # Klassenname = Ordnername
            class_name = os.path.basename(root)
            
            # Bild laden
            img = cv2.imread(image_path)
            if img is None:
                print(f"Konnte {image_path} nicht lesen, überspringe...")
                continue

            height, width, _ = img.shape

            # Bounding Box = gesamtes Bild
            xmin, ymin, xmax, ymax = 0, 0, width, height

            # Bildname (optional eindeutiger machen)
            rows.append([file, width, height, class_name, xmin, ymin, xmax, ymax])

df = pd.DataFrame(rows, columns=["filename", "width", "height", "class", "xmin", "ymin", "xmax", "ymax"])
df.to_csv(output_csv, index=False)

print(f"CSV erfolgreich erstellt: {output_csv}")
print("CSV gespeichert unter:", os.path.abspath(output_csv))
print(f"Anzahl Bilder: {len(df)}")

