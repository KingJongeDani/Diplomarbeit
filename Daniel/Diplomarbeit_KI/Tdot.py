import cv2
import os

video_path = r"Dataset\Predictes_Tdot_Video.mp4"

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Video konnte nicht geöffnet werden.")
    exit()

# FPS auslesen
fps = cap.get(cv2.CAP_PROP_FPS)
delay = 15


#Slow-Motion aktivieren
# slow_factor = 2   # 2 = halb so schnell
# delay = delay * slow_factor


print(f"FPS: {fps}, Delay: {delay} ms")

# Vollbild
cv2.namedWindow("Video", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    ret, frame = cap.read()

    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    cv2.imshow("Video", frame)

    key = cv2.waitKey(delay) & 0xFF
    if key in (ord('x'), ord('X')):
        break

cap.release()
cv2.destroyAllWindows()
