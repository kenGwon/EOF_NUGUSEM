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
    def verify_face(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        face_area_info = self.face_classifier.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)

        if len(face_area_info):
            largest_ROI_idx = 0
            max_width, max_height = 0, 0
            
            for i, (x, y, width, height) in enumerate(face_area_info):
                if width > max_width and height > max_height:
                    largest_ROI_idx = i
            
            largest_ROI_x = face_area_info[largest_ROI_idx][0]
            largest_ROI_y = face_area_info[largest_ROI_idx][1]
            largest_ROI_width = face_area_info[largest_ROI_idx][2]
            largest_ROI_height = face_area_info[largest_ROI_idx][3]

            return img[largest_ROI_y:largest_ROI_y+largest_ROI_height,\
                       largest_ROI_x:largest_ROI_x+largest_ROI_width]

        else:
            return None

        """
        for (x, y, width, height) in face_area_info:
            roi_gray = gray[y:y+height, x:x+width]
            id_, conf = self.model.predict(roi_gray)
            print(id_, conf) # 실시간 얼굴 모델 일치율 출력
            try:
                if conf < 500:
                    confidence = int(100*(1-(conf)/300))
                    display_string = str(confidence)+'% Confidence it is user'
                cv2.putText(img,display_string,(100,120), cv2.FONT_HERSHEY_COMPLEX,1,(250,120,255),2)


                if confidence > 75:
                    name = self.label_name[str(id_)] #ID를 이용하여 이름 가져오기
                    cv2.putText(img, name, (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                else:
                    cv2.putText(img, "OutSider!", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
            except:
                cv2.putText(img, "Face Not Found", (400,500), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0),2)
                print("Face Not Found!")
                pass
            finally:
                pass
        return img
        """
