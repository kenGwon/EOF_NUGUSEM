import cv2 
from os import mkdir, getcwd
from os.path import isdir, join
import os
os.chdir(os.path.dirname(__file__)) # vscode에서 현재 path 잘못 잡는 문제해결용

face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# desc: BGR이미지 한장을 GrayScale로 변환한 후 CascadeClassifier를 활용하여 얼굴 영역 행렬을 리턴한다.
def face_extractor(src): 
    src_gray = cv2.cvtColor(src,cv2.COLOR_BGR2GRAY) 
    faces_area_info = face_classifier.detectMultiScale(src_gray, 1.3, 5) 

    if faces_area_info is (): 
        return None 

    for(x, y, width, height) in faces_area_info: 
        face_area_matrix = src[y : y + height, x : x + width] 

    return face_area_matrix 

# desc: 웹캠으로 이미지 100장을 읽어들여, 얼굴 영역을 딴 뒤 폴더에 저장한다.
def collect_data(person):
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
        
        if face_extractor(frame) is not None: 
            count += 1 
            face = cv2.resize(face_extractor(frame),(200,200))         
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