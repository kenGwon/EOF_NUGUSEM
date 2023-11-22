import cv2
from os import getcwd
from os.path import join
import os
os.chdir(os.path.dirname(__file__)) # vscode에서 현재 path 잘못 잡는 문제해결용
import json

# db_UID_image
def verify_face():
    with open(join(getcwd(), "model/label_name.json"), 'r') as json_file:
        label_name = json.load(json_file)

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

            # if conf >= 50:
            #     font = cv2.FONT_HERSHEY_SIMPLEX #폰트 지정
            #     name = labels[id_] #ID를 이용하여 이름 가져오기
            #     cv2.putText(img, name, (x,y), font, 1, (0,0,255), 2)
            #     cv2.rectangle(img,(x,y),(x+width,y+height),(0,255,0),2)

            # cv2.imshow('Preview',img) #이미지 보여주기

            ###################

            try:
                if conf < 500:
                    confidence = int(100*(1-(conf)/300))
                    display_string = str(confidence)+'% Confidence it is user'
                cv2.putText(img,display_string,(100,120), cv2.FONT_HERSHEY_COMPLEX,1,(250,120,255),2)

                if confidence > 80:
                    name = label_name[str(id_)] #ID를 이용하여 이름 가져오기
                    cv2.putText(img, name, (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.imshow('Face Cropper', img)
                else:
                    cv2.putText(img, "OutSider!", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                    cv2.imshow('Face Cropper', img)
            except:
                cv2.putText(img, "Face Not Found", (400,500), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0),2)
                print("Face Not Found!")
                #cv2.imshow('Fail Face Cropper',image)
                pass

            ################### 

            

        if cv2.waitKey(1) == 27: # 27: ESC
            break 
    
    #전체 종료
    cap.release()
    cv2.destroyAllWindows()
