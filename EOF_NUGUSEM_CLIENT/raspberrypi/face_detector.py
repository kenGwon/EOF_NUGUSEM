import cv2 
from os import walk, mkdir, getcwd
from os.path import isdir, join, basename
import os
os.chdir(os.path.dirname(__file__)) # vscode에서 현재 path 잘못 잡는 문제해결용
import numpy as np 
import json

class FaceDetector():
    def __init__(self):
        self.face_classifier = cv2.CascadeClassifier("model/haarcascade_frontalface_default.xml")
        self.model = cv2.face.LBPHFaceRecognizer_create()

    # desc: BGR이미지 한장을 GrayScale로 변환한 후 CascadeClassifier를 활용하여 얼굴 영역 행렬을 리턴한다.
    def face_extractor(self, src): 
        src_gray = cv2.cvtColor(src,cv2.COLOR_BGR2GRAY) 
        faces_area_info = self.face_classifier.detectMultiScale(src_gray, 1.3, 5) 

        if faces_area_info is (): 
            return None 

        for(x, y, width, height) in faces_area_info: 
            face_area_matrix = src[y : y + height, x : x + width] 

        return face_area_matrix     

    # desc: 웹캠으로 이미지 100장을 읽어들여, 얼굴 영역을 딴 뒤 폴더에 저장한다.
    def collect_data(self, person):
        save_path = join(getcwd(), "faces/")
        print(save_path)
        if isdir(save_path + person):
            save_path = save_path + person
        else:
            mkdir(save_path + person)
            save_path = save_path + person

        cap = cv2.VideoCapture(0) 
        count = 0 
        while True: 
            ret, frame = cap.read() 
            
            if self.face_extractor(frame) is not None: 
                count += 1 
                face = cv2.resize(self.face_extractor(frame),(200,200))         
                face_gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY) 

                file_path = save_path + "/" + str(count) +".jpg"
                cv2.imwrite(file_path, face_gray)

                cv2.putText(face_gray, str(count), (50,50), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
                cv2.imshow("얼굴 수집", face_gray) 

            if cv2.waitKey(1) == 27 or count == 100: # 27: ESC
                break 

        cap.release() 
        cv2.destroyAllWindows() 
        print("이미지 수집 완료")

    # desc: 이미지를 바탕으로 모델을 학습한다.
    def train_model(self):
        person_id = -1
        prev_name = ""
        label, data = [], []
        label_name_dic = {} # json 파일 생성을 위한 딕셔너리
        
        directory_path = join(getcwd(), "faces")

        for root, dir, files in walk(directory_path):
            print(root)
            print(dir)
            for file in files:
                if file.endswith("jpeg") or file.endswith("jpg") or file.endswith("png") :
                    file_path = join(root, file)
                    current_name = basename(root)

                    if prev_name != current_name:
                        person_id += 1
                        prev_name = current_name
                        label_name_dic[str(person_id)] = current_name # json 파일용 딕셔너리 값 추가

                    src_gray = cv2.cvtColor(cv2.imread(file_path), cv2.COLOR_BGR2GRAY)
                    face_area_info = self.face_classifier.detectMultiScale(src_gray, 1.3, 5)

                    for (x, y, width, height) in face_area_info:
                        roi = src_gray[x:x+width, y:y+height]
                        data.append(roi)
                        label.append(person_id)

        
        self.model.train(data, np.array(label))
        self.model.save(join(getcwd(), "model/face_recognizer_model.yml"))
        
        with open(join(getcwd(), "model/label_name.json"), 'w', encoding='utf-8') as outfile:
            json.dump(label_name_dic, outfile, indent="\t")        

    # desc: 
    def verify_face(self):
        with open(join(getcwd(), "model/label_name.json"), 'r') as json_file:
            label_name = json.load(json_file)

        self.model.read(join(getcwd(), "model/face_recognizer_model.yml"))

        cap = cv2.VideoCapture(0)

        if cap.isOpened() == False:
            exit()

        while True:
            ret, img = cap.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_area_info = self.face_classifier.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)

            for (x, y, width, height) in face_area_info:
                roi_gray = gray[y:y+height, x:x+width]
                id_, conf = self.model.predict(roi_gray) #얼마나 유사한지 확인
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

