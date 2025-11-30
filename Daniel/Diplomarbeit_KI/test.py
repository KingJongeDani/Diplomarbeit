import glob, os
from ultralytics import YOLO
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Modell laden
model = YOLO(r"C:\Users\kraxn\Downloads\best(2).pt")

# Testbild (achte auf die Endung!)
test_image = r"C:\Users\kraxn\Downloads\test_no_entry.jpg"

# Prediction
results = model.predict(source=test_image, save=True)

# Neuester Vorhersageordner finden
result_folders = sorted(glob.glob("runs/detect/predict*"))
if not result_folders:
    print("❌ Keine Prediction-Ergebnisse gefunden.")
else:
    result_folder = result_folders[-1]
    basename = os.path.basename(test_image)
    result_path = os.path.join(result_folder, basename)

    if os.path.exists(result_path):
        img = mpimg.imread(result_path)
        plt.imshow(img)
        plt.axis("off")
        plt.show()
    else:
        print(f"{result_path} wurde nicht gefunden.")
