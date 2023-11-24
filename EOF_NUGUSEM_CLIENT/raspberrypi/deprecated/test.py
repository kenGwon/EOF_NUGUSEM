import sys
import cv2
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
import serial
import time
import client
import face_detector


myTCPIP = client.TcpClient("10.10.15.58", 8888)
myFACEDETECTOR = face_detector.FaceDetector()

class WebcamThread(QThread):
    global myTCPIP
    change_pixmap_signal = pyqtSignal(QImage)
    

    def run(self):
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb_image = myFACEDETECTOR.verify_face(rgb_image) #########
                # 박스가 적용된 이미지



                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                p = convert_to_qt_format.scaled(640, 480, Qt.KeepAspectRatio)
                self.change_pixmap_signal.emit(p)
                

                gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_area_info = myFACEDETECTOR.face_classifier.detectMultiScale(gray_image, scaleFactor=1.5, minNeighbors=5)
                
                if len(face_area_info):
                    x = face_area_info[0][0]
                    y = face_area_info[0][1]
                    width = face_area_info[0][2]
                    height = face_area_info[0][3]
                
                    face_gray_image = gray_image[y:y+height, x:x+width]
                    image_filename = "face_on_captured_image.jpg"
                    cv2.imwrite(image_filename, face_gray_image)                     


                if myTCPIP.rfid_tag_flag: # and myFACEDETECTOR.verify_flag
                    
                    print("웹캠 이미지 캡쳐")
                    # 현재의 이미지를 저장하고, 서버로 ... 일련의 작업
                    image_filename = "captured_image.png"
                    
                    # 이미지 저장
                    cv2.imwrite(image_filename, frame) #### TCPIP.py 158번재 라인이 참조하는 실제파일 저장 타이밍
                    myTCPIP.rfid_tag_flag = False
                    #myTCPIP.img_save_flag = True


                    if myTCPIP.img_rcv_flag:

                        print("서버 통신 끝")
                       

                        # 이미지 파일 경로
                        captured_image_path = "face_on_captured_image.jpg"
                        received_image_path = "received_image.jpg"

                        # 이미지 읽기
                        received_image_mat = cv2.cvtColor(cv2.imread(received_image_path), cv2.COLOR_BGR2GRAY)
                        captured_image_gray = cv2.cvtColor(cv2.imread(captured_image_path), cv2.COLOR_BGR2GRAY)
                        
                    
                        ri_id_, ri_conf = myFACEDETECTOR.model.predict(received_image_mat)
                        ci_id_, ci_conf = myFACEDETECTOR.model.predict(captured_image_gray)
                        
                        print(f"ri_id_: {ri_id_}")
                        print(f"ci_id_: {ci_id_}")

                        if ci_id_ == ri_id_:
                            print("동일인")
                        else:
                            print("다른 사람")
                
                        


                        #face verify
                        myTCPIP.img_rcv_flag = False 
                        
                    # myFACEDETECTOR.verify_flag = False

        cap.release()


class CommThread(QThread):
    global myTCPIP
    data_received_signal = pyqtSignal(str)

    def __init__(self, serial_port):
        super().__init__()
        # self.serial_port = serial_port

    def run(self):
        # ser = serial.Serial(self.serial_port, 9600, timeout=1)

        myTCPIP.receive_uid_and_send_image()

"""
        while True:
            
            myTCPIP.receive_uid_and_send_image()
            
                
            # self.data_received_signal.emit(uid)
                
                
                
                
            time.sleep(0.1)
"""

class App(QMainWindow):
    def __init__(self, serial_port):
        super().__init__()

        self.title = "Webcam Viewer"
        self.top = 100
        self.left = 100
        self.width = 640
        self.height = 480

        self.initUI()

        self.serial_port = serial_port
        self.comm_thread = CommThread(self.serial_port)
        self.comm_thread.data_received_signal.connect(self.update_data)
        self.comm_thread.start()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)

        self.label = QLabel(self)
        layout.addWidget(self.label)

        self.webcam_thread = WebcamThread(self)
        self.webcam_thread.change_pixmap_signal.connect(self.update_image)
        self.webcam_thread.start()

    def update_image(self, img):
        self.label.setPixmap(QPixmap.fromImage(img))

    def update_data(self, data):
        print(f"Data received from Arduino: {data}")


if __name__ == "__main__":
    serial_port = "/dev/ttyACM0"  # 아두이노의 시리얼 포트에 맞게 수정
    app = QApplication(sys.argv)
    window = App(serial_port)
    window.show()
    sys.exit(app.exec_())
