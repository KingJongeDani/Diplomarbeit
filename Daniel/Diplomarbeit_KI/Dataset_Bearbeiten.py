import os, cv2, shutil, yaml
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# ==============================
# CONFIG
# ==============================
dataset_folder = Path("Dataset\Videos_Pictures\Videos_Pictures_03")
yaml_file = Path("data.yaml")
finished_folder = Path("Dataset/Videos_Pictures_finished")
finished_folder.mkdir(exist_ok=True)

# Klassen-Namen aus YAML laden
with open(yaml_file, "r") as f:
    data = yaml.safe_load(f)
class_names = data["names"]

# Dataset laden (alle Unterordner!)
dataset = []
for root_dir, dirs, files in os.walk(dataset_folder):
    img_dir = Path(root_dir)
    if "images" in img_dir.parts:  # nur images-Ordner
        label_dir = Path(str(img_dir).replace("images", "labels"))
        for img_file in files:
            if img_file.endswith(".jpg"):
                img_path = img_dir / img_file
                label_path = Path(label_dir) / img_file.replace(".jpg", ".txt")

                # Prüfen ob Bild schon im finished_folder liegt
                finished_img = finished_folder / img_file
                finished_label = finished_folder / img_file.replace(".jpg", ".txt")
                if finished_img.exists() or finished_label.exists():
                    continue  # überspringen, wenn schon akzeptiert

                if label_path.exists():
                    dataset.append((img_path, label_path))

index = 0
box_index = 0  # welches Objekt (Box) im aktuellen Bild ausgewählt ist

# ==============================
# Hilfsfunktionen
# ==============================
def load_boxes(label_path):
    with open(label_path) as f:
        lines = [line.strip() for line in f if len(line.strip().split()) == 5]
    boxes = []
    for line in lines:
        parts = line.split()
        cls = int(parts[0])
        x, y, w, h = map(float, parts[1:])
        boxes.append([cls, x, y, w, h])
    return boxes

def save_boxes(label_path, boxes):
    with open(label_path, "w") as f:
        for box in boxes:
            cls, x, y, w, h = box
            f.write(f"{cls} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")

def draw_boxes(img_path, boxes, selected_box_idx):
    image = cv2.imread(os.path.normpath(str(img_path)))
    if image is None:
        print(f"⚠️ Konnte Bild nicht laden, überspringe: {img_path}")
        return None
    h, w, _ = image.shape
    for i, box in enumerate(boxes):
        cls, x, y, bw, bh = box
        cls = int(cls)
        x, y, bw, bh = x*w, y*h, bw*w, bh*h
        x1, y1 = int(x - bw/2), int(y - bh/2)
        x2, y2 = int(x + bw/2), int(y + bh/2)
        color = (0, 0, 255) if i == selected_box_idx else (0, 255, 0)
        thickness = 3 if i == selected_box_idx else 2
        cv2.rectangle(image, (x1,y1), (x2,y2), color, thickness)
        cv2.putText(image, class_names[cls], (x1, y1-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(image_rgb)

def update_image():
    global photo, index, box_index
    while 0 <= index < len(dataset):
        img, label = dataset[index]
        boxes = load_boxes(label)
        if len(boxes) == 0:
            index += 1
            box_index = 0
            continue
        if box_index >= len(boxes):
            box_index = 0
        pil_img = draw_boxes(img, boxes, box_index)
        if pil_img is None:
            index += 1
            box_index = 0
            continue
        pil_img.thumbnail((800, 600))
        photo = ImageTk.PhotoImage(pil_img)
        canvas.config(image=photo)

        # NEU: Anzahl der Objekte anzeigen
        total_objects = len(boxes)
        info_label.config(
            text=f"Bild {index+1}/{len(dataset)}: {img.name}  "
                 f"(Objekt {box_index+1}/{total_objects}, insgesamt {total_objects})"
        )

        cls_id = int(boxes[box_index][0])
        if cls_id is not None and cls_id < len(class_names):
            class_label.config(text=f"Aktuelle Klasse: {class_names[cls_id]}")
            class_dropdown.current(cls_id)
        break


def prev_image(event=None):
    global index, box_index
    index = max(0, index-1)
    box_index = 0
    update_image()

def next_image(event=None):
    global index, box_index
    index = min(len(dataset)-1, index+1)
    box_index = 0
    update_image()

def prev_box(event=None):
    global box_index
    box_index = max(0, box_index-1)
    update_image()

def next_box(event=None):
    global box_index, index
    img, label = dataset[index]
    boxes = load_boxes(label)
    box_index = min(len(boxes)-1, box_index+1)
    update_image()

def accept(event=None):
    global index, box_index
    img, label = dataset[index]
    shutil.copy(img, finished_folder / img.name)
    shutil.copy(label, finished_folder / label.name)
    status_label.config(text="✅ akzeptiert")
    index += 1
    box_index = 0
    update_image()

def delete_box(event=None):
    global index, box_index
    img, label = dataset[index]
    boxes = load_boxes(label)
    if len(boxes) == 0:
        # Sollte nie vorkommen, aber sicherheitshalber
        return
    # Lösche die aktuell ausgewählte Box
    boxes.pop(box_index)
    if len(boxes) == 0:
        # Keine Boxen mehr → Bild + Label löschen
        os.remove(img)
        os.remove(label)
        status_label.config(text="🗑️ Bild+Label komplett gelöscht (keine Objekte mehr)")
        dataset.pop(index)
        # index bleibt, evtl. anpassen wenn out of range
        if index >= len(dataset):
            index = len(dataset)-1
        box_index = 0
    else:
        # Nur Label speichern
        save_boxes(label, boxes)
        status_label.config(text="🗑️ Objekt gelöscht")
        if box_index >= len(boxes):
            box_index = len(boxes)-1
    update_image()

def change_class(event=None):
    global index, box_index
    new_cls = class_dropdown.current()
    img, label = dataset[index]
    boxes = load_boxes(label)
    if len(boxes) == 0:
        return
    boxes[box_index][0] = new_cls
    save_boxes(label, boxes)
    status_label.config(text=f"✏️ Klasse geändert zu {class_names[new_cls]}")
    update_image()

def rename_class(event=None):
    new_name = rename_entry.get().strip()
    if new_name:
        cls_id = class_dropdown.current()
        class_names[cls_id] = new_name
        class_dropdown["values"] = class_names
        status_label.config(text=f"🔤 Klasse {cls_id} umbenannt zu {new_name}")
        data["names"] = class_names
        with open(yaml_file, "w") as f:
            yaml.safe_dump(data, f)

def open_legend():
    legend_win = tk.Toplevel(root)
    legend_win.title("Legende / Bedienung")
    tk.Label(legend_win, text="Legende / Bedienung", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
    tk.Label(legend_win, text="← / → : Navigation zwischen Bildern").pack(anchor="w")
    tk.Label(legend_win, text="↑ / ↓ : Navigation zwischen Objekten im Bild").pack(anchor="w")
    tk.Label(legend_win, text="l : Löschen (aktuelles Objekt)").pack(anchor="w")
    tk.Label(legend_win, text="k : Akzeptieren (Bild+Label ins Finished-Ordner)").pack(anchor="w")
    tk.Label(legend_win, text="c : Klasse ändern (Dropdown übernehmen)").pack(anchor="w")
    tk.Label(legend_win, text="r : Klassennamen umbenennen (Textfeld übernehmen)").pack(anchor="w")

# ==============================
# Tkinter GUI
# ==============================
root = tk.Tk()
root.title("Verkehrszeichen Review Tool")

info_label = tk.Label(root, text="")
info_label.pack()

canvas = tk.Label(root)
canvas.pack()

class_label = tk.Label(root, text="")
class_label.pack()

frame = tk.Frame(root)
frame.pack()

btn_prev = tk.Button(frame, text="← Vorheriges Bild", command=prev_image)
btn_prev.pack(side=tk.LEFT)

btn_next = tk.Button(frame, text="→ Nächstes Bild", command=next_image)
btn_next.pack(side=tk.LEFT)

btn_prev_box = tk.Button(frame, text="↑ Vorheriges Objekt", command=prev_box)
btn_prev_box.pack(side=tk.LEFT)

btn_next_box = tk.Button(frame, text="↓ Nächstes Objekt", command=next_box)
btn_next_box.pack(side=tk.LEFT)

btn_accept = tk.Button(frame, text="✅ Akzeptieren", command=accept)
btn_accept.pack(side=tk.LEFT)

btn_delete = tk.Button(frame, text="🗑️ Löschen (Objekt)", command=delete_box)
btn_delete.pack(side=tk.LEFT)

tk.Label(root, text="Klasse ändern:").pack()
class_dropdown = ttk.Combobox(root, values=class_names, state="readonly")
class_dropdown.bind("<<ComboboxSelected>>", change_class)
class_dropdown.pack()

tk.Label(root, text="Klassenname umbenennen:").pack()
rename_entry = tk.Entry(root)
rename_entry.pack()
rename_btn = tk.Button(root, text="Umbenennen", command=rename_class)
rename_btn.pack()

status_label = tk.Label(root, text="")
status_label.pack()

legend_btn = tk.Button(root, text="📖 Legende anzeigen", command=open_legend)
legend_btn.pack(pady=10)

# ==============================
# Tastenkürzel binden
# ==============================
root.bind("<Left>", prev_image)       # Pfeil links = vorheriges Bild
root.bind("<Right>", next_image)      # Pfeil rechts = nächstes Bild
root.bind("<Up>", prev_box)            # Pfeil hoch = vorheriges Objekt
root.bind("<Down>", next_box)          # Pfeil runter = nächstes Objekt
root.bind("l", delete_box)             # l = aktuelles Objekt löschen
root.bind("k", accept)                 # k = Bild akzeptieren (Bild+Label kopieren)
root.bind("c", change_class)           # c = Klasse ändern (Dropdown übernehmen)
root.bind("r", rename_class)           # r = Klassennamen umbenennen

update_image()
root.mainloop()
