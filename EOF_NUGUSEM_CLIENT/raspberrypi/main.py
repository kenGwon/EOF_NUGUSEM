import sys
from PyQt5_GUI import *

if __name__ == "__main__":
    serial_port = "/dev/ttyACM0"  # 아두이노의 시리얼 포트에 맞게 수정
    app = QApplication(sys.argv)
    window = App(serial_port)
    window.show()
    sys.exit(app.exec_())
