import cv2 
import numpy as np 
from os import listdir, mkdir
from os.path import isdir, isfile, join 

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


# desc: BGR이미지 한장을 GrayScale로 변환한 후 CascadeClassifier를 활용하여 얼굴 영역 행렬을 리턴한다.
def face_detector(src): 
    src_gray = cv2.cvtColor(src,cv2.COLOR_BGR2GRAY) 
    faces_area_info = face_classifier.detectMultiScale(src_gray, 1.3, 5) 

    if faces_area_info is(): 
        return src, []
    
    for(x, y, width, height) in faces_area_info: 
        cv2.rectangle(src, (x, y), (x + width, y + height), (0, 255, 255), 2) 
        roi = src[y : y + height, x : x + width] 
        roi = cv2.resize(roi, (200, 200)) 

    return src, roi # 원본 영상(src)와 ROI영역 부분행렬(roi) 리턴


# desc: 웹캠으로 이미지 100장을 읽어들여, 얼굴 영역을 딴 뒤 폴더에 저장한다.
def collect_data(person):
    save_path = "C:/EOF_NUGUSEM/EOF_NUGUSEM_CLIENT/faces/"
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


# desc: 폴더에 저장된 이미지를 가지고 모델 생성 후 학습
def train_data(person):
    save_path = "C:/EOF_NUGUSEM/EOF_NUGUSEM_CLIENT/faces/" + person + "/"

    # 디렉토리에 있는 파일들을 리스트에 담기
    files = []
    for file in listdir(save_path):
        if isfile(join(save_path, file)):
            files.append(file)
    
    # 학습에 필요한 "데이터 - 라벨" 준비
    Training_Data, Labels = [], [] 
    for i, file in enumerate(files):
        file_path = save_path + files[i]
        face_gray = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
        
        if face_gray is None:
            continue
        else:
            Training_Data.append(np.asarray(face_gray, dtype=np.uint8))
            Labels.append(person)

    Labels = np.asarray(Labels, dtype=np.int32) # 라벨값을 4바이트 integer로 형 변환
    model = cv2.face.LBPHFaceRecognizer_create() # 모델 생성
    model.train(np.asarray(Training_Data), np.asarray(Labels))
    print("모델 학습 완료")
    return model
    

def do_face_verification(model):
    cap = cv2.VideoCapture(0) 

    while True: 
        ret, frame = cap.read() 
        image, face = face_detector(frame) 
        
        try: 
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY) 
            id_, confidence = model.predict(face) 
            print(confidence)

            if confidence < 500: 
                confidence = int(100 * (1 - (confidence) / 300)) 
                display_string = str(confidence)+'% Confidence it is user' 
            cv2.putText(image, display_string, (100,120), cv2.FONT_HERSHEY_COMPLEX,1,(250,120,255),2) 
            
            # 유사도 75% 초과이면 동일인으로 간주
            if confidence > 75: 
                cv2.putText(image, str(id_) + "OK!!!", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2) 
                cv2.imshow('Face Cropper', image) 
            # 유사도 75% 이하이면 타인으로 간주
            else: 
                cv2.putText(image, str(id_) + "NO!!!", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2) 
                cv2.imshow('Face Cropper', image) 
        except: 
            #얼굴 검출 안됨  
            cv2.putText(image, "Face Not Found", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2) 
            cv2.imshow('Face Cropper', image) 
            pass 

        if cv2.waitKey(1) == 27: # 27: ESC
            break 

    cap.release() 
    cv2.destroyAllWindows()


collect_data("Ganghyeon")
model = train_data("Ganghyeon")
do_face_verification(model)
