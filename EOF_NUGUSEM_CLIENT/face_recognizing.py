import cv2
from os import getcwd
from os.path import join
import os
os.chdir(os.path.dirname(__file__)) # vscode에서 현재 path 잘못 잡는 문제해결용

# db_UID_image
def verify_face():
    labels = ["changmin", "ganghyeon", "yongguen"] #라벨 지정

    face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    model = cv2.face.LBPHFaceRecognizer_create() 
    model.read(join(getcwd(), "model/face_recognizer_model.yml"))

    cap = cv2.VideoCapture(0)

    if cap.isOpened() == False:
        exit()

    while True:
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_area_info = face_classifier.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)

        for (x, y, width, height) in face_area_info:
            roi_gray = gray[y:y+height, x:x+width]
            id_, conf = model.predict(roi_gray) #얼마나 유사한지 확인
            print(id_, conf)

            if conf >= 50:
                font = cv2.FONT_HERSHEY_SIMPLEX #폰트 지정
                name = labels[id_] #ID를 이용하여 이름 가져오기
                cv2.putText(img, name, (x,y), font, 1, (0,0,255), 2)
                cv2.rectangle(img,(x,y),(x+width,y+height),(0,255,0),2)

            cv2.imshow('Preview',img) #이미지 보여주기

        if cv2.waitKey(1) == 27: # 27: ESC
            break 
    
    #전체 종료
    cap.release()
    cv2.destroyAllWindows()

    
    