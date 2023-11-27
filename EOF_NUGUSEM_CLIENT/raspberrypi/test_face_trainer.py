import cv2
from os import walk, mkdir, getcwd, chdir
from os.path import isdir, join, basename, dirname
import numpy as np
import json
import dlib


chdir(dirname(__file__))


class FaceTrainer():
    def __init__(self):
        self.face_detector = dlib.get_frontal_face_detector()
        self.model = self.initialize_face_recognizer()
        self.model.read(join(getcwd(), "model/face_recognizer_model.yml"))
        self.cap = cv2.VideoCapture(0)
        with open(join(getcwd(), "model/label_name.json"), 'r') as json_file:
            self.label_name = json.load(json_file)


    def initialize_face_recognizer(self):
        try:
            return cv2.face.LBPHFaceRecognizer_create()
        except AttributeError:
            return cv2.face.LBPH_create()
       
    def face_extractor(self, src):
        src_gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        faces_area_info = self.face_detector(src_gray)


        if len(faces_area_info) == 0:
            return None


        for face in faces_area_info:
            x, y, width, height = face.left(), face.top(), face.width(), face.height()
            face_area_matrix = src[y: y + height, x: x + width]


        return face_area_matrix


    def collect_data(self, person):
        save_path = join(getcwd(), "faces/")
        if isdir(join(save_path, person)):
            save_path = join(save_path, person)
        else:
            mkdir(join(save_path, person))
            save_path = join(save_path, person)


        cap = cv2.VideoCapture(0)
        count = 0
        while True:
            ret, frame = cap.read()


            if self.face_extractor(frame) is not None:
                count += 1
                face = cv2.resize(self.face_extractor(frame), (200, 200))
                face_gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)


                file_path = join(save_path, str(count) + ".jpg")
                cv2.imwrite(file_path, face_gray)


                cv2.putText(face_gray, str(count), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow("얼굴 수집", face_gray)


            if cv2.waitKey(1) == 27 or count == 500:
                break


        cap.release()
        cv2.destroyAllWindows()
        print("이미지 수집 완료")


    def train_model(self):
        person_id = -1
        prev_name = ""
        label, data = [], []
        label_name_dic = {}


        directory_path = join(getcwd(), "faces")


        for root, dir, files in walk(directory_path):
            for file in files:
                if file.endswith("jpeg") or file.endswith("jpg") or file.endswith("png"):
                    file_path = join(root, file)
                    current_name = basename(root)


                    if prev_name != current_name:
                        person_id += 1
                        prev_name = current_name
                        label_name_dic[str(person_id)] = current_name


                    src_gray = cv2.cvtColor(cv2.imread(file_path), cv2.COLOR_BGR2GRAY)
                    faces_area_info = self.face_detector(src_gray)


                    for face in faces_area_info:
                        x, y, width, height = face.left(), face.top(), face.width(), face.height()
                        roi = src_gray[y:y + height, x:x + width]
                        data.append(roi)
                        label.append(person_id)


        self.model.train(data, np.array(label))
        self.model.save(join(getcwd(), "model/face_recognizer_model.yml"))


        with open(join(getcwd(), "model/label_name.json"), 'w', encoding='utf-8') as outfile:
            json.dump(label_name_dic, outfile, indent="\t")


if __name__ == "__main__":
    myFaceTrainer = FaceTrainer()
    myFaceTrainer.collect_data("Dohyeon_test")
    myFaceTrainer.train_model()