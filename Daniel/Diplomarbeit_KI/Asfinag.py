import pandas as pd
import cv2
import os
import shutil
from tqdm import tqdm

# --------------------------------------------------
# 1. Pfade anpassen
# --------------------------------------------------
csv_path = r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\Sign_recognition\ASFINAG\ATSD_V1_0_signs_scenes\scenes\train\meta_train.csv"
image_folder = r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\Sign_recognition\ASFINAG\ATSD_V1_0_signs_scenes\scenes\train\imgs"
output_folder = r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\ASFINAG_r"

os.makedirs(output_folder, exist_ok=True)

# --------------------------------------------------
# 2. Deine vollständige YOLO-Labelmap (0–22)
# --------------------------------------------------
labelmap = [
    "00_speedlimit_20",
    "01_speedlimit_30",
    "02_speedlimit_50",
    "03_speedlimit_60",
    "04_speedlimit_70",
    "05_speedlimit_80",
    "06_end_of_speedlimit_80",
    "07_speedlimit_100",
    "08_no_overtaking",
    "09_yield",
    "10_stop",
    "11_no_vehicles",
    "12_no_entry",
    "13_end_all_limits",
    "14_end_of_no_overtaking",
    "15_end_of_speedlimit_20",
    "16_end_of_speedlimit_30",
    "17_end_of_speedlimit_50",
    "18_end_of_speedlimit_60",
    "19_end_of_speedlimit_70",
    "20_end_of_speedlimit_100",
    "21_speedlimit_130",
    "22_end_of_speedlimit_130"
]

# --------------------------------------------------
# 3. ASFINAG class_id → YOLO-ID Mapping
#    (Nur Klassen, die im Dataset vorkommen!)
# --------------------------------------------------
asfinag_to_yolo = {
    "01_01": 1,   # speedlimit_30
    "01_03": 2,   # speedlimit_50
    "01_04": 3,   # speedlimit_60
    "01_05": 4,   # speedlimit_70
    "01_06": 5,   # speedlimit_80
    "05_07": 6,   # end_of_speedlimit_80
    "01_08": 7,   # speedlimit_100
    "01_11": 8,   # no_overtaking
    "03_01": 9,   # yield
    "03_02": 10,  # stop
    "01_14": 11,  # no_vehicles
    "01_13": 12,  # no_entry
    "01_21": 13,  # end_all_limits
    "01_22": 14,  # end_of_no_overtaking
    "05_08": 20,  # end_of_speedlimit_100
    "01_10": 21   # speedlimit_130
}

# --------------------------------------------------
# 4. CSV laden und filtern
# --------------------------------------------------
df = pd.read_csv(csv_path)

# Nur Zeilen behalten, die wir mappen können
df = df[df["class_id"].isin(asfinag_to_yolo.keys())]

print(f"Gefundene relevante Annotationen: {len(df)}")
print(f"Bilder mit relevanten Klassen: {df['image_id'].nunique()}")

# --------------------------------------------------
# 5. Bilder + YOLO-Labels erzeugen
# --------------------------------------------------
for image_id in tqdm(df["image_id"].unique(), desc="Verarbeite Bilder"):
    img_path = os.path.join(image_folder, f"{image_id}.jpg")
    if not os.path.exists(img_path):
        continue

    # Bild kopieren
    out_img_path = os.path.join(output_folder, f"{image_id}.jpg")
    if not os.path.exists(out_img_path):
        shutil.copy(img_path, out_img_path)

    # Bildgröße laden
    img = cv2.imread(img_path)
    if img is None:
        continue
    h, w = img.shape[:2]

    # Label-Datei schreiben
    label_path = os.path.join(output_folder, f"{image_id}.txt")
    with open(label_path, "w") as f:
        boxes = df[df["image_id"] == image_id]

        for _, row in boxes.iterrows():
            xtl = float(row["xtl"])
            ytl = float(row["ytl"])
            xbr = float(row["xbr"])
            ybr = float(row["ybr"])

            # YOLO-Format
            x_center = ((xtl + xbr) / 2) / w
            y_center = ((ytl + ybr) / 2) / h
            bw = (xbr - xtl) / w
            bh = (ybr - ytl) / h

            # Klasse mappen
            yolo_id = asfinag_to_yolo[row["class_id"]]

            # Schreiben
            f.write(f"{yolo_id} {x_center:.6f} {y_center:.6f} {bw:.6f} {bh:.6f}\n")

print("\n✅ Fertig! Alle Bilder + YOLO-Labels korrekt erzeugt.")
