import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class Worker(QThread):
    timeout = pyqtSignal(int)    # 사용자 정의 시그널

    def __init__(self):
        super().__init__()
        self.num = 0             # 초깃값 설정

    def run(self):
        while True:
            self.timeout.emit(self.num)     # 방출
            self.num += 1
            self.sleep(1)


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.worker = Worker()
        self.worker.start()
        self.worker.timeout.connect(self.timeout)   # 시그널 슬롯 등록

        self.edit = QLineEdit(self)
        self.edit.move(10, 10)

    @pyqtSlot(int)
    def timeout(self, num):
        self.edit.setText(str(num))


app = QApplication(sys.argv)
mywindow = MyWindow()
mywindow.show()
app.exec_()
