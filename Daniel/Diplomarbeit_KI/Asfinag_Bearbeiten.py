import os, cv2, shutil, yaml
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# ==============================
# CONFIG – Pfade anpassen
# ==============================
labels_dir = Path(r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\ASFINAG_r")
images_dir = Path(r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\ASFINAG_r")
finished_folder = Path(r"D:\Diplomarbeit\Diplomarbeit\Daniel\Diplomarbeit_KI\Dataset\ASFINAG_finished")
finished_folder.mkdir(exist_ok=True)

# ==============================
# DEINE FIXE YOLO LABELMAP (0–22)
# ==============================
class_names = [
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

# ==============================
# Dataset laden
# ==============================
dataset = []
for label_file in labels_dir.glob("*.txt"):
    img_file = labels_dir / (label_file.stem + ".jpg")
    if not img_file.exists():
        continue

    if (finished_folder / img_file.name).exists():
        continue

    dataset.append((img_file, label_file))

index = 0
box_index = 0
photo = None
zoom_photo = None

# ==============================
# Hilfsfunktionen
# ==============================
def load_boxes(label_path):
    boxes = []
    try:
        with open(label_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 5:
                    cls, x, y, w, h = parts
                    boxes.append([int(cls), float(x), float(y), float(w), float(h)])
    except Exception as e:
        print("Label-Fehler:", e)
    return boxes

def save_boxes(label_path, boxes):
    with open(label_path, "w", encoding="utf-8") as f:
        for b in boxes:
            f.write(f"{b[0]} {b[1]:.6f} {b[2]:.6f} {b[3]:.6f} {b[4]:.6f}\n")

def draw_boxes(img_path, boxes, selected_idx):
    img = cv2.imread(str(img_path))
    if img is None:
        return None

    h, w, _ = img.shape
    for i, (cls, x, y, bw, bh) in enumerate(boxes):
        x, y, bw, bh = x*w, y*h, bw*w, bh*h
        x1, y1 = int(x-bw/2), int(y-bh/2)
        x2, y2 = int(x+bw/2), int(y+bh/2)

        color = (0,0,255) if i == selected_idx else (0,255,0)
        thick = 3 if i == selected_idx else 2

        cv2.rectangle(img, (x1,y1), (x2,y2), color, thick)
        label = class_names[cls] if cls < len(class_names) else f"id:{cls}"
        cv2.putText(img, label, (x1, y1-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img)

def crop_and_zoom(img_path, box, size=(400,400), padding=0.25):
    img = cv2.imread(str(img_path))
    if img is None:
        return None

    h, w, _ = img.shape
    cls, x, y, bw, bh = box
    x, y, bw, bh = x*w, y*h, bw*w, bh*h

    pad_w = bw * padding
    pad_h = bh * padding

    x1 = int(max(0, x-bw/2-pad_w))
    y1 = int(max(0, y-bh/2-pad_h))
    x2 = int(min(w, x+bw/2+pad_w))
    y2 = int(min(h, y+bh/2+pad_h))

    crop = img[y1:y2, x1:x2]
    if crop.size == 0:
        return None

    crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(crop)
    pil = pil.resize(size, Image.LANCZOS)
    return pil

# ==============================
# GUI Update
# ==============================
def update_image():
    global photo, zoom_photo, index, box_index

    if not dataset:
        info_label.config(text="Kein Datensatz vorhanden.")
        return

    img, label = dataset[index]
    boxes = load_boxes(label)
    if not boxes:
        return

    box_index = min(box_index, len(boxes)-1)

    main_img = draw_boxes(img, boxes, box_index)
    main_img.thumbnail((900, 600))
    photo = ImageTk.PhotoImage(main_img)
    canvas.config(image=photo)

    zoom_img = crop_and_zoom(img, boxes[box_index])
    if zoom_img:
        zoom_photo = ImageTk.PhotoImage(zoom_img)
        zoom_canvas.config(image=zoom_photo)
        zoom_canvas.image = zoom_photo

    info_label.config(
        text=f"Bild {index+1}/{len(dataset)} – Objekt {box_index+1}/{len(boxes)}"
    )

    cls = boxes[box_index][0]
    class_label.config(text=f"Aktuelle Klasse: {class_names[cls]}")
    class_dropdown.current(cls)

# ==============================
# Navigation
# ==============================
def prev_image(e=None):
    global index, box_index
    index = max(0, index-1)
    box_index = 0
    update_image()

def next_image(e=None):
    global index, box_index
    index = min(len(dataset)-1, index+1)
    box_index = 0
    update_image()

def prev_box(e=None):
    global box_index
    box_index = max(0, box_index-1)
    update_image()

def next_box(e=None):
    global box_index
    box_index += 1
    update_image()

def accept(e=None):
    img, lbl = dataset[index]
    shutil.copy(img, finished_folder / img.name)
    shutil.copy(lbl, finished_folder / lbl.name)
    dataset.pop(index)
    update_image()

def delete_box(e=None):
    global box_index
    img, lbl = dataset[index]
    boxes = load_boxes(lbl)
    boxes.pop(box_index)

    if not boxes:
        os.remove(img)
        os.remove(lbl)
        dataset.pop(index)
        box_index = 0
    else:
        save_boxes(lbl, boxes)
        box_index = max(0, box_index-1)

    update_image()

def change_class(e=None):
    img, lbl = dataset[index]
    boxes = load_boxes(lbl)
    boxes[box_index][0] = class_dropdown.current()
    save_boxes(lbl, boxes)
    update_image()

# ==============================
# GUI
# ==============================
root = tk.Tk()
root.title("ASFINAG Verkehrszeichen Review Tool")

info_label = tk.Label(root)
info_label.pack(pady=4)

image_frame = tk.Frame(root)
image_frame.pack(pady=6)

zoom_frame = tk.Frame(image_frame)
zoom_frame.pack(side=tk.LEFT, padx=10)

tk.Label(zoom_frame, text="🔍 Objekt-Zoom", font=("Arial", 10, "bold")).pack()
zoom_canvas = tk.Label(zoom_frame)
zoom_canvas.pack()

main_frame = tk.Frame(image_frame)
main_frame.pack(side=tk.LEFT, padx=10)

tk.Label(main_frame, text="🖼 Gesamtbild", font=("Arial", 10, "bold")).pack()
canvas = tk.Label(main_frame)
canvas.pack()

class_label = tk.Label(root)
class_label.pack(pady=4)

class_dropdown = ttk.Combobox(root, values=class_names, state="readonly")
class_dropdown.pack()
class_dropdown.bind("<<ComboboxSelected>>", change_class)

frame = tk.Frame(root)
frame.pack(pady=6)

tk.Button(frame, text="← Bild", command=prev_image).pack(side=tk.LEFT, padx=3)
tk.Button(frame, text="→ Bild", command=next_image).pack(side=tk.LEFT, padx=3)
tk.Button(frame, text="↑ Objekt", command=prev_box).pack(side=tk.LEFT, padx=3)
tk.Button(frame, text="↓ Objekt", command=next_box).pack(side=tk.LEFT, padx=3)
tk.Button(frame, text="✅ Akzeptieren", command=accept).pack(side=tk.LEFT, padx=6)
tk.Button(frame, text="🗑 Objekt löschen", command=delete_box).pack(side=tk.LEFT, padx=6)

root.bind("<Left>", prev_image)
root.bind("<Right>", next_image)
root.bind("<Up>", prev_box)
root.bind("<Down>", next_box)
root.bind("k", accept)
root.bind("l", delete_box)

update_image()
root.mainloop()
