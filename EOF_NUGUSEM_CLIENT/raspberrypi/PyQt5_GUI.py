import cv2
import time
import serial
import json
from os import getcwd
from os.path import join
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import client
import face_detector

# 전역 인스턴스
serial_instance = serial.Serial('/dev/ttyACM0', 9600)
client_instance = client.ClientCommunication("10.10.15.58", 8888)
client_instance_temp = client.ClientCommunication("10.10.15.58", 8889) # 포트 다름. 8889임.
face_detector_instance = face_detector.FaceDetector()


class WebcamThread(QThread):
    global client_instance
    change_pixmap_signal = pyqtSignal(QImage)
    update_information = pyqtSignal(str)

    def __init__(self, serial_port): 
        super().__init__()
        self.running = False
        self.information = ""
        with open(join(getcwd(), "model/label_name.json"), 'r') as json_file:
            self.label_name = json.load(json_file)

    def run(self):
        cap = cv2.VideoCapture(0)

        while self.running:
            ret, frame = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb_image = face_detector_instance.verify_face(rgb_image)

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
                        ri_id_confidence = int(100*(1-(ri_id_)/300))
                        ci_id_confidence = int(100*(1-(ci_id_)/300))

                        if ci_id_ == ri_id_ and \
                            ri_id_confidence > 75 and \
                                  ci_id_confidence > 75:
                            self.information = "인증완료. 입장 가능합니다."
                            self.update_information.emit(self.information)
                            print("동일인") 
                            
                            # 서보모터 문 열기
                            command = "A180\n" # ex: A180\n
                            serial_instance.write(command.encode())

                            name = self.label_name[str(ci_id_)] #ID를 이용하여 이름 가져오기
                            client_instance.authentication_log = name + " Enter Complete!!!"
                            client_instance.authentication_flag = True
                            client_instance.Manager_flag=True
                        else:
                            self.information = "인증실패! 입장 불가능합니다!"
                            self.update_information.emit(self.information)
                            print("다른 사람")

                            # 서보모터 문 닫기
                            command = "A0\n" # ex: A0\n
                            serial_instance.write(command.encode())

                            client_instance.authentication_log = "Enter Fail..."
                            client_instance.authentication_flag = True

                        #################################################################################
                
                        client_instance.img_rcv_flag = False
                        client_instance.rfid_tag_flag = False

        cap.release() 
        # 웹캠 정지 상태에는 IDLE이미지 출력
        idle_frame = cv2.imread("resources/idle_frame.png")
        idle_frame = cv2.cvtColor(idle_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = idle_frame.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QImage(idle_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_qt_format.scaled(640, 480, Qt.KeepAspectRatio)
        self.change_pixmap_signal.emit(p)

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


class ManagerCommThread(QThread):
    global client_instance_temp
    data_received_signal = pyqtSignal(str)
    
    def __init__(self, serial_port):
        super().__init__()
        self.request_flag = 0
        print("관리자 통신 스레드 생성")


    def run(self):
        while True:
            if self.request_flag == 1:
                print("클릭 한번으로 여기까지 들어오긴 함")
                client_instance_temp.send_communicate_manager()
                self.request_flag = 2

            elif self.request_flag == 2:
                client_instance_temp.receive_communicate_manager()
                if client_instance_temp.Manager_flag == True:
                    self.request_flag = 0
                    client_instance_temp.Manager_flag = False
            else:
                pass
                
                

    def request(self):
        self.request_flag = 1


class ArduinoThread(QThread):
    global client_instance

    
    def __init__(self, serial_port):
        super().__init__()
        print("RFID 스레드 생성완료")
        # self.ser = serial.Serial('/dev/ttyACM0', 9600)

    """
    def __del__(self, serial_port):
        self.ser.close()
    
    def set_servo_angle(self,angle):
        command = f'A{client_instance.angle}\n' # ex: A180\n
        serial_instance.write(command.encode())
    def open_servo_motor(self):
        set_servo_angle(180)
    def close_servo_motor(self):
        set_servo_angle(0)

    """
        
    def run(self):
        print("RFID 스레드 동작시작")
        while True:    
            data = serial_instance.readline().decode('utf-8').strip()
            print("RFID 1회 읽기")
            if data and data.startswith("U"):
                uid_ = data[1:]  # 헤더 "U"를 제외한 부분이 UID
                client_instance.uid = uid_
                client_instance.arduino_rfid_flag = True




            if client_instance_temp.arduino_servo_flag==1:
                # 서보모터 문 열기
                command = "A180\n" # ex: A180\n
                serial_instance.write(command.encode())
                client_instance_temp.arduino_servo_flag=0
            elif client_instance_temp.arduino_servo_flag==2 :
                # 서보모터 문 열기
                command = "A0\n" # ex: A180\n
                serial_instance.write(command.encode())
                client_instance_temp.arduino_servo_flag=0
            else :
                pass


            # if client_instance.Manager_flag:
            #     self.set_servo_angle(client_instance.angle)
            #     client_instance.Manager_flag=False
            #     #servo motor to arduino


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
        self.timer.start(4000)
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

        # TCP IP 통신 스레드 생성
        self.comm_thread = CommThread(self.serial_port)
        self.comm_thread.data_received_signal.connect(self.update_data)
        self.comm_thread.start()

        # 관리실 통신 스레드 생성
        self.manager_comm_thread = ManagerCommThread(self.serial_port)
        # self.manager_comm_thread.data_received_signal.connect(self.update_data)
        self.manager_comm_thread.start()

        # 아두이노 시리얼 통신 스레드 생성
        self.arduino_thread = ArduinoThread(self.serial_port)
        self.arduino_thread.start()
        
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
        btn3.clicked.connect(self.manager_request)


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

    
    def manager_request(self):
        self.manager_comm_thread.request()


    # 각종 정보 출력 슬롯
    @pyqtSlot(str)
    def print_info_to_edit1(self, information):
        if information == "인증완료. 입장 가능합니다.":
            self.edit1.setStyleSheet("background-color : green")
            self.edit1.setText(information)
            self.timer.start(4000)
        elif information == "인증실패! 입장 불가능합니다!":
            self.edit1.setStyleSheet("background-color : red")
            self.edit1.setText(information)
            self.timer.start(4000)

    # 주기적으로 정보창 초기화
    def refresh_edit1(self):
        self.edit1.setStyleSheet("background-color : gray")
        self.edit1.setText("")

