#RFID가 리더기에 읽히면 아두이노 측에서 라즈베리파이로 UID 송신하고 수신받은 #라즈베리파이는 윈도우 서버로 송신하는 코드
import serial
import socket
import struct

class TcpClient:
    def __init__(self, server_ip, port):
        self.server_ip = server_ip
        self.port = port

    def connect_to_server(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server_ip, self.port))
        print("Connected to the server")
        return client_socket

    def send_data_type(self, client_socket, data_type):
        data_type_header = struct.pack("I", data_type)
        client_socket.sendall(data_type_header)

    def send_string(self, message):
        client_socket = self.connect_to_server()
        self.send_data_type(client_socket, 1)  # STRING
        client_socket.sendall(message.encode("utf-8"))
        print("String sent to server")
        client_socket.close()

    def send_image(self, image_path):
        client_socket = self.connect_to_server()
        self.send_data_type(client_socket, 0)  # IMAGE
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            client_socket.sendall(image_data)
        print("Image sent to server")
        client_socket.close()

    def send_rfid_uid(self, uid):
        client_socket = self.connect_to_server()
        self.send_data_type(client_socket, 2)  # RFID_UID
        client_socket.sendall(uid.encode("utf-8"))
        print("RFID UID sent to server")
        client_socket.close()



if __name__ == "__main__":
    tcp_client = TcpClient("10.10.15.58", 8888)

    # Arduino에서 UID 수신 및 서버로 전송
    ser = serial.Serial('/dev/ttyACM0', 9600)
    while True:
        data = ser.readline().decode('utf-8').strip()
        if data and data.startswith("U"):
            uid = data[1:]  # 헤더 "U"를 제외한 부분이 UID
            print("Received UID:", uid)

            # 여기에 UID를 사용하여 원하는 동작 수행
            # 예: 데이터베이스 조회, 특정 동작 수행 등

            # RFID UID를 서버로 전송
            tcp_client.send_rfid_uid(uid)
