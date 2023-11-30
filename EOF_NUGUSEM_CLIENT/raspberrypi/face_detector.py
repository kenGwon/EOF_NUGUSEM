import cv2
from os import getcwd, chdir
from os.path import join, dirname
import numpy as np
import json
chdir(dirname(__file__)) # vscode에서 현재 path 잘못 잡는 문제해결용

class FaceDetector():
    def __init__(self):
        self.face_classifier = cv2.CascadeClassifier("model/haarcascade_frontalface_default.xml")
        self.model = cv2.face.LBPHFaceRecognizer_create()
        self.model.read(join(getcwd(), "model/face_recognizer_model.yml"))
        self.verify_flag = False

        with open(join(getcwd(), "model/label_name.json"), 'r') as json_file:
            self.label_name = json.load(json_file)

    # desc:
    def get_faceROI(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        face_area_info = self.face_classifier.detectMultiScale(img_gray, scaleFactor=1.5, minNeighbors=5)

        if len(face_area_info):
            largest_ROI_idx = 0
            max_width = 0
            max_height = 0
            
            for i, (x, y, width, height) in enumerate(face_area_info):
                if width > max_width and height > max_height:
                    max_width = width
                    max_height = height
                    largest_ROI_idx = i
            
            largest_ROI_x = face_area_info[largest_ROI_idx][0]
            largest_ROI_y = face_area_info[largest_ROI_idx][1]
            largest_ROI_width = face_area_info[largest_ROI_idx][2]
            largest_ROI_height = face_area_info[largest_ROI_idx][3]

            return img_gray[largest_ROI_y:largest_ROI_y+largest_ROI_height,\
                       largest_ROI_x:largest_ROI_x+largest_ROI_width]

        else:
            return None
