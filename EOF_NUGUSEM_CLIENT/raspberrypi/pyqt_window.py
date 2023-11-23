from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QWidget

class CameraInput(QThread):
    def __init__(self):
        super().__init__()
        self.running = True


    def run(self):
        while self.running:
            print("안녕하세요")

    def resume(self):
        self.running = True
    
    def pause(self):
        self.running = False



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.cameraInput = CameraInput()
        self.cameraInput.start() # 쓰레드 시작... 쓰레드 클래스 내부의 run()함수 시작




if __name__ == "__main__":
    app = QApplication(sys.argv)
    mywindow = MainWindow()
    mywindow.show()
    app.exec_()

