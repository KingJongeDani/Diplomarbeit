import os, cv2, shutil, yaml
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# ==============================
# CONFIG
# ==============================
dataset_folder = Path("Dataset/Videos_Pictures")
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

# ==============================
# Hilfsfunktionen
# ==============================
def draw_boxes(img_path, label_path):
    image = cv2.imread(os.path.normpath(str(img_path)))
    if image is None:
        print(f"⚠️ Konnte Bild nicht laden, überspringe: {img_path}")
        return None  # Signal: Bild defekt
    h, w, _ = image.shape
    with open(label_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 5:
                continue
            cls, x, y, bw, bh = map(float, parts)
            cls = int(cls)
            x, y, bw, bh = x*w, y*h, bw*w, bh*h
            x1, y1 = int(x - bw/2), int(y - bh/2)
            x2, y2 = int(x + bw/2), int(y + bh/2)
            cv2.rectangle(image, (x1,y1),(x2,y2),(0,255,0),2)
            cv2.putText(image, class_names[cls], (x1,y1-5),
                        cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,0),2)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(image_rgb)

def get_current_class(label_path):
    with open(label_path) as f:
        line = f.readline().strip()
        if line:
            return int(line.split()[0])
    return None

def update_image():
    global photo, index
    while 0 <= index < len(dataset):
        img, label = dataset[index]
        pil_img = draw_boxes(img, label)
        if pil_img is None:
            # defektes Bild -> überspringen
            index += 1
            continue
        # Bildgröße begrenzen
        pil_img.thumbnail((800, 600))
        photo = ImageTk.PhotoImage(pil_img)
        canvas.config(image=photo)
        info_label.config(text=f"Bild {index+1}/{len(dataset)}: {img.name}")
        cls_id = get_current_class(label)
        if cls_id is not None and cls_id < len(class_names):
            class_label.config(text=f"Aktuelle Klasse: {class_names[cls_id]}")
            class_dropdown.current(cls_id)
        break

def prev(event=None):
    global index
    index = max(0, index-1)
    update_image()

def nxt(event=None):
    global index
    index = min(len(dataset)-1, index+1)
    update_image()

def accept(event=None):
    global index
    img, label = dataset[index]
    shutil.copy(img, finished_folder / img.name)
    shutil.copy(label, finished_folder / label.name)
    status_label.config(text="✅ akzeptiert")
    index += 1
    update_image()

def delete(event=None):
    global index
    img, label = dataset[index]
    os.remove(img); os.remove(label)
    status_label.config(text="🗑️ gelöscht")
    dataset.pop(index)
    update_image()

def change_class(event=None):
    global index
    new_cls = class_dropdown.current()
    img, label = dataset[index]
    with open(label) as f: lines = f.readlines()
    with open(label, "w") as f:
        for line in lines:
            parts = line.split()
            if len(parts)==5:
                parts[0] = str(new_cls)
                f.write(" ".join(parts)+"\n")
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
    tk.Label(legend_win, text="l : Löschen (Bild+Label entfernen)").pack(anchor="w")
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

btn_prev = tk.Button(frame, text="← Vorheriges", command=prev)
btn_prev.pack(side=tk.LEFT)

btn_next = tk.Button(frame, text="→ Nächstes", command=nxt)
btn_next.pack(side=tk.LEFT)

btn_accept = tk.Button(frame, text="✅ Akzeptieren", command=accept)
btn_accept.pack(side=tk.LEFT)

btn_delete = tk.Button(frame, text="🗑️ Löschen", command=delete)
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
root.bind("<Left>", prev)       # Pfeil links = vorheriges Bild
root.bind("<Right>", nxt)       # Pfeil rechts = nächstes Bild
root.bind("l", delete)          # Taste l = löschen
root.bind("k", accept)          # Taste k = akzeptieren/speichern
root.bind("c", change_class)    # Taste c = Klasse ändern (Dropdown übernehmen)
root.bind("r", rename_class)    # Taste r = Klassennamen umbenennen (Textfeld übernehmen)

update_image()
root.mainloop()
