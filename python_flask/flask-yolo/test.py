# pip install ultralytics cryptography
from ultralytics import YOLO
import cv2
model = YOLO('yolov8n.pt')
img_path = "animal.jpg"
img = cv2.imread(img_path)
frame = cv2.resize(img, (320, 320))
result = model(frame)
annotated_frame = result[0].plot(show=False)
cv2.imwrite('output.JPG', annotated_frame)