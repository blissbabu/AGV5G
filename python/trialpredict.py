from ultralytics import YOLO
from ultralytics.models.yolo.detect.predict import DetectionPredictor

import cv2
import os

model_path = os.path.join('.', 'runs', 'detect', 'train16', 'weights', 'best.pt')
# Load a model
model = YOLO(model_path)  # load a custom model


# model = YOLO("yolov8s.pt")


results = model.predict(source = 0, show=True)



 