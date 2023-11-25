import cv2
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import client
import face_detector

client_instance = client.ClientCommunication("10.10.15.58", 8888)
face_detector_instance = face_detector.FaceDetector()

class WebcamThread(QThread):
    global client_instance
    change_pixmap_signal = pyqtSignal(QImage)
    update_information = pyqtSignal(str)

    def __init__(self, serial_port): 
        super().__init__()
        self.running = True
        self.information = ""

    def run(self):
        cap = cv2.VideoCapture(0)

        while self.running:
            ret, frame = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb_image = face_detector_instance.verify_face(rgb_image) #########
                # 박스가 적용된 이미지

                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                p = convert_to_qt_format.scaled(640, 480, Qt.KeepAspectRatio)
                self.change_pixmap_signal.emit(p)
                
                gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_area_info = face_detector_instance.face_classifier.detectMultiScale(gray_image, scaleFactor=1.5, minNeighbors=5)
                
                if len(face_area_info):
                    x = face_area_info[0][0]
                    y = face_area_info[0][1]
                    width = face_area_info[0][2]
                    height = face_area_info[0][3]
                
                    face_gray_image = gray_image[y:y+height, x:x+width]
                    image_filename = "resources/face_on_captured_image.jpg"
                    cv2.imwrite(image_filename, face_gray_image)                     


                if client_instance.rfid_tag_flag:
                    image_filename = "resources/captured_image.png"
                    cv2.imwrite(image_filename, frame) # client.py 127번재 라인이 참조하는 실제파일 저장 타이밍
                    time.sleep(0.25)

                    if client_instance.img_rcv_flag:                    
                        captured_image_path = "resources/face_on_captured_image.jpg"
                        received_image_path = "resources/received_image.jpg"

                        received_image_mat = cv2.cvtColor(cv2.imread(received_image_path), cv2.COLOR_BGR2GRAY)
                        captured_image_gray = cv2.cvtColor(cv2.imread(captured_image_path), cv2.COLOR_BGR2GRAY)
                    
                        ri_id_, ri_conf = face_detector_instance.model.predict(received_image_mat)
                        ci_id_, ci_conf = face_detector_instance.model.predict(captured_image_gray)
                        
                        ##################### 다양한 플로우 다루기 위한 조건 추가 될 부분 #####################
                        print(f"ri_id_: {ri_id_}")
                        print(f"ci_id_: {ci_id_}")

                        if ci_id_ == ri_id_:
                            print("동일인") 
                            self.information = "인증완료. 입장 가능합니다."
                            self.update_information.emit(self.information)
                            

                        else:
                            print("다른 사람")
                            self.information = "인증실패! 입장 불가능합니다!"
                            self.update_information.emit(self.information)

                        #################################################################################
                
                        client_instance.img_rcv_flag = False
                        client_instance.rfid_tag_flag = False

        cap.release() # 나중에 카메라 on / off 기능이 추가될 경우, 위 while True가 깨지면서 진입 가능해짐.

    def resume(self):
        self.running = True

    def pause(self):
        self.running = False

class CommThread(QThread):
    global client_instance
    data_received_signal = pyqtSignal(str)

    def __init__(self, serial_port):
        super().__init__()

    def run(self):
        client_instance.communicate()


class App(QMainWindow):
    def __init__(self, serial_port):
        super().__init__()

        self.serial_port = serial_port
        self.title = "EOF NUGU:SEM"
        self.top = 100
        self.left = 100
        self.width = 640
        self.height = 580

        # 3초에 한번씩 Edit Control 초기화
        self.timer = QTimer(self)
        self.timer.start(3000)
        self.timer.timeout.connect(self.refresh_edit1)

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)

        # 웹캠 시작/정지 버튼생성
        btn1 = QPushButton("웹캠 시작")
        layout.addWidget(btn1)
        btn2 = QPushButton("웹캠 정지")
        layout.addWidget(btn2)

        # 웹캠 시작/정지 시그널-슬롯 연결하기
        btn1.clicked.connect(self.resume)
        btn2.clicked.connect(self.pause)

        
        # 웹캠 영상 출력 라벨 생성
        self.label = QLabel(self)
        layout.addWidget(self.label)

        # 웹캠 스레드 생성
        self.webcam_thread = WebcamThread(self)
        self.webcam_thread.change_pixmap_signal.connect(self.update_image)
        self.webcam_thread.update_information.connect(self.print_info_to_edit1) # 라인 에디트 시그널 슬롯 연결
        self.webcam_thread.start()

        # 아두이노 시리얼 통신 스레드 생성
        self.comm_thread = CommThread(self.serial_port)
        self.comm_thread.data_received_signal.connect(self.update_data)
        self.comm_thread.start()

        
        # 각종 정보 출력 라인 에디트 생성
        self.edit1 = QLineEdit(self)
        self.edit1.setAlignment(Qt.AlignCenter)
        self.edit1.setReadOnly(True)
        self.edit1.setStyleSheet("background-color : gray")
        self.edit1.setPlaceholderText("여기에 각종 정보가 출력됩니다.")
        layout.addWidget(self.edit1)


        # 관리실 문 열기 요청 버튼 생성
        btn3 = QPushButton("관리실 인증 요청")
        layout.addWidget(btn3)
        # btn3.clicked.connect(self.함수명)


    # 웹캠 동영상 프레임 갱신 슬롯
    def update_image(self, img):
        self.label.setPixmap(QPixmap.fromImage(img))

    def update_data(self, data):
        print(f"Data received from Arduino: {data}")

    # 웹캠 시작 슬롯
    def resume(self):
        self.webcam_thread.resume()
        self.webcam_thread.start()

    # 웹캠 정지 슬롯
    def pause(self):
        self.webcam_thread.pause()
        
        idle_frame = cv2.imread("resources/idle_frame.png")
        idle_frame = cv2.cvtColor(idle_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = idle_frame.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QImage(idle_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_qt_format.scaled(640, 480, Qt.KeepAspectRatio)
        self.update_image(p)

    # 각종 정보 출력 슬롯
    @pyqtSlot(str)
    def print_info_to_edit1(self, information):
        if information == "인증완료. 입장 가능합니다.":
            self.edit1.setStyleSheet("background-color : green")
            self.edit1.setText(information)
            self.timer.start(3000)
        elif information == "인증실패! 입장 불가능합니다!":
            self.edit1.setStyleSheet("background-color : red")
            self.edit1.setText(information)
            self.timer.start(3000)

    # 주기적으로 정보창 초기화
    def refresh_edit1(self):
        self.edit1.setStyleSheet("background-color : gray")
        self.edit1.setText("")

