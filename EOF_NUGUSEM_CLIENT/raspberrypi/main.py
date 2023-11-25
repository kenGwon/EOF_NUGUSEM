import sys
import PyQt5_GUI

if __name__ == "__main__":
    serial_port = "/dev/ttyACM0"  # 아두이노의 시리얼 포트에 맞게 수정
    app = PyQt5_GUI.QApplication(sys.argv)
    window = PyQt5_GUI.App(serial_port)
    window.show()
    sys.exit(app.exec_())
