import sys
import cv2
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget
import serial
import time
import TCPIP


myTCPIP = TCPIP.TcpClient("10.10.15.58", 8888)


class WebcamThread(QThread):
    global myTCPIP
    change_pixmap_signal = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                p = convert_to_qt_format.scaled(640, 480, Qt.KeepAspectRatio)
                self.change_pixmap_signal.emit(p)
                
                if myTCPIP.rfid_tag_flag:
                    print("웹캠 이미지 캡쳐")
					# 현재의 이미지를 저장하고, 서버로 

        cap.release()


class ArduinoThread(QThread):
    global myTCPIP
    data_received_signal = pyqtSignal(str)

    def __init__(self, serial_port):
        super().__init__()
        # self.serial_port = serial_port

    def run(self):
        # ser = serial.Serial(self.serial_port, 9600, timeout=1)

        
        while True:
            
            myTCPIP.receive_uid_and_send_image()
            
                
            # self.data_received_signal.emit(uid)
                
                
                
                
            time.sleep(0.1)


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
        self.arduino_thread = ArduinoThread(self.serial_port)
        self.arduino_thread.data_received_signal.connect(self.update_data)
        self.arduino_thread.start()

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
