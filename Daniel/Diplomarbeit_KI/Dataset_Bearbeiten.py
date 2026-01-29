import os, cv2, shutil, yaml
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# ==============================
# CONFIG
# ==============================
dataset_folder = Path(r"Dataset/Videos_Pictures/Videos_Pictures_04")
yaml_file = Path("data.yaml")
finished_folder = Path(r"Dataset/Videos_Pictures_finished")
finished_folder.mkdir(exist_ok=True)

# Klassen-Namen aus YAML laden
with open(yaml_file, "r") as f:
    data = yaml.safe_load(f)
class_names = data["names"]

# ==============================
# DATASET LADEN
# ==============================
dataset = []

for root_dir, dirs, files in os.walk(dataset_folder):
    img_dir = Path(root_dir)

    if img_dir.name == "images":
        label_dir = img_dir.parent / "labels"

        for img_file in files:
            if img_file.lower().endswith(".jpg"):
                img_path = img_dir / img_file
                label_path = label_dir / img_file.replace(".jpg", ".txt")

                finished_img = finished_folder / img_file
                finished_label = finished_folder / img_file.replace(".jpg", ".txt")

                if finished_img.exists() or finished_label.exists():
                    continue

                if label_path.exists():
                    dataset.append((img_path, label_path))

index = 0
box_index = 0

# ==============================
# HILFSFUNKTIONEN
# ==============================
def load_boxes(label_path):
    with open(label_path) as f:
        lines = [line.strip() for line in f if len(line.strip().split()) == 5]
    boxes = []
    for line in lines:
        cls, x, y, w, h = line.split()
        boxes.append([int(cls), float(x), float(y), float(w), float(h)])
    return boxes


def save_boxes(label_path, boxes):
    with open(label_path, "w") as f:
        for cls, x, y, w, h in boxes:
            f.write(f"{cls} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")


def draw_boxes(img_path, boxes, selected_box_idx):
    image = cv2.imread(str(img_path))
    if image is None:
        return None

    h, w, _ = image.shape

    for i, (cls, x, y, bw, bh) in enumerate(boxes):
        x, y, bw, bh = x*w, y*h, bw*w, bh*h
        x1, y1 = int(x - bw/2), int(y - bh/2)
        x2, y2 = int(x + bw/2), int(y + bh/2)

        color = (0, 0, 255) if i == selected_box_idx else (0, 255, 0)
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, class_names[cls], (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


def update_zoom(img_path, box):
    image = cv2.imread(str(img_path))
    if image is None:
        return

    h, w, _ = image.shape
    cls, x, y, bw, bh = box

    x, y, bw, bh = x*w, y*h, bw*w, bh*h
    x1, y1 = int(x - bw/2), int(y - bh/2)
    x2, y2 = int(x + bw/2), int(y + bh/2)

    crop = image[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
    if crop.size == 0:
        return

    crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    crop = cv2.resize(crop, (200, 200), interpolation=cv2.INTER_CUBIC)

    pil_crop = Image.fromarray(crop)
    zoom_photo = ImageTk.PhotoImage(pil_crop)

    zoom_canvas.config(image=zoom_photo)
    zoom_canvas.image = zoom_photo


def update_image():
    global photo, index, box_index

    if len(dataset) == 0:
        info_label.config(text="❌ Keine Bilder gefunden.")
        return

    if index < 0:
        index = 0
    if index >= len(dataset):
        index = len(dataset) - 1

    img, label = dataset[index]
    boxes = load_boxes(label)

    if len(boxes) == 0:
        info_label.config(text=f"⚠️ Keine Boxen in {img.name}")
        return

    if box_index >= len(boxes):
        box_index = 0

    pil_img = draw_boxes(img, boxes, box_index)
    if pil_img is None:
        info_label.config(text=f"⚠️ Fehler beim Laden von {img.name}")
        return

    pil_img.thumbnail((900, 700))
    photo = ImageTk.PhotoImage(pil_img)
    canvas.config(image=photo)

    update_zoom(img, boxes[box_index])

    info_label.config(
        text=f"Bild {index+1}/{len(dataset)} — {img.name} — Objekt {box_index+1}/{len(boxes)}"
    )

    cls_id = boxes[box_index][0]
    class_label.config(text=f"Klasse: {class_names[cls_id]}")
    class_dropdown.current(cls_id)


# ==============================
# NAVIGATION
# ==============================
def prev_image(event=None):
    global index, box_index
    index -= 1
    box_index = 0
    update_image()


def next_image(event=None):
    global index, box_index
    index += 1
    box_index = 0
    update_image()


def prev_box(event=None):
    global box_index
    box_index -= 1
    update_image()


def next_box(event=None):
    global box_index
    box_index += 1
    update_image()


def accept(event=None):
    global index, box_index
    img, label = dataset[index]
    shutil.copy(img, finished_folder / img.name)
    shutil.copy(label, finished_folder / label.name)
    index += 1
    box_index = 0
    update_image()


def delete_box(event=None):
    global index, box_index
    img, label = dataset[index]
    boxes = load_boxes(label)

    if len(boxes) == 0:
        return

    boxes.pop(box_index)

    if len(boxes) == 0:
        os.remove(img)
        os.remove(label)
        dataset.pop(index)
        if index >= len(dataset):
            index = len(dataset) - 1
        box_index = 0
    else:
        save_boxes(label, boxes)
        if box_index >= len(boxes):
            box_index = len(boxes) - 1

    update_image()


def change_class(event=None):
    global index, box_index
    new_cls = class_dropdown.current()
    img, label = dataset[index]
    boxes = load_boxes(label)
    boxes[box_index][0] = new_cls
    save_boxes(label, boxes)
    update_image()


# ==============================
# TKINTER GUI
# ==============================
root = tk.Tk()
root.title("Verkehrszeichen Review Tool")

info_label = tk.Label(root, text="")
info_label.pack()

# ==============================
# Bildbereich (Zoom links, Hauptbild rechts)
# ==============================
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

class_label = tk.Label(root, text="")
class_label.pack()

class_dropdown = ttk.Combobox(root, values=class_names, state="readonly")
class_dropdown.bind("<<ComboboxSelected>>", change_class)
class_dropdown.pack()

frame = tk.Frame(root)
frame.pack()

tk.Button(frame, text="← Bild zurück", command=prev_image).pack(side=tk.LEFT)
tk.Button(frame, text="→ Bild weiter", command=next_image).pack(side=tk.LEFT)
tk.Button(frame, text="↑ Objekt zurück", command=prev_box).pack(side=tk.LEFT)
tk.Button(frame, text="↓ Objekt weiter", command=next_box).pack(side=tk.LEFT)
tk.Button(frame, text="🗑 Objekt löschen", command=delete_box).pack(side=tk.LEFT)
tk.Button(frame, text="✔ Akzeptieren", command=accept).pack(side=tk.LEFT)

# Tastenkürzel
root.bind("<Left>", prev_image)
root.bind("<Right>", next_image)
root.bind("<Up>", prev_box)
root.bind("<Down>", next_box)

update_image()
root.mainloop()
