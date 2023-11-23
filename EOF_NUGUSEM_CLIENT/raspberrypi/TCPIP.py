
import socket
import struct
import threading
import serial
import time
class TcpClient:
    def __init__(self, server_ip, port):
        self.server_ip = server_ip
        self.port = port
        self.client_socket = None

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.server_ip, self.port))
            print("서버에 연결되었습니다.")
        except ConnectionRefusedError:
            print("서버에 연결할 수 없습니다.")
            self.client_socket = None  # 연결 실패 시 client_socket을 None으로 설정
    def wait_for_ACK(self):
        ACK = 9
        ack_type_header = self.client_socket.recv(4)

        # Check if received data is empty
        if not ack_type_header:
            print("Error: No data received.")
            return

        ack_type = struct.unpack("I", ack_type_header)[0]
        if ack_type == ACK:
            print("ACK received")
        else:
            print("ACK reception failed")


    def send_data_type(self, data_type):
        if self.client_socket is not None:  # client_socket이 None이 아닌지 확인
            try:
                data_type_header = struct.pack("I", data_type)
                self.client_socket.sendall(data_type_header)
            except AttributeError:
                print("데이터 유형을 보낼 수 없습니다.")
        else:
            print("클라이언트 소켓이 초기화되지 않았습니다. 연결이 실패했을 수 있습니다.")

    def send_image(self, image_path):
        self.connect_to_server()
        self.send_data_type(0)  # 이미지

        # 이미지 전송
        with open(image_path, "rb") as image_file:
            while True:
                image_data = image_file.read(1024)
                if not image_data:
                    last_packet=struct.pack("I",9)
                    self.client_socket.sendall(last_packet)
                    break
                self.client_socket.sendall(image_data)
        print("이미지를 서버로 보냈습니다.")

    def receive_data_type(self):
        # 데이터 유형 수신
        data_type_header = self.client_socket.recv(4)

        # 데이터 언팩에 충분한 데이터가 있는지 확인
        if len(data_type_header) < 4:
            print("오류: 데이터 언팩에 충분한 데이터가 없습니다.")
            return -1

        data_type = struct.unpack("I", data_type_header)[0]
        return data_type

    def close_connection(self):
        self.client_socket.close()

def receive_uid_and_send_image():
    # Arduino에서 UID 수신 및 서버로 전송
    ser = serial.Serial('/dev/ttyACM0', 9600)

    try:
        while True:
            data = ser.readline().decode('utf-8').strip()
            if data and data.startswith("U"):
                uid = data[1:]  # 헤더 "U"를 제외한 부분이 UID
                print("받은 UID:", uid)

                # RFID UID를 서버로 전송
                tcp_client = TcpClient("10.10.15.58", 8888)
                try:
                    tcp_client.connect_to_server()
                    
                    
                    #tcp_client.send_data_type(2)  # RFID_UID
                    #tcp_client.client_socket.sendall(uid.encode("utf-8"))
                    #print("RFID UID를 서버로 보냈습니다.")
                    #tcp_client.wait_for_ACK()
                    
                    
                    tcp_client.send_data_type(1)  # Log string
                    Log = uid + "@" + "Log Test"
                    
                    tcp_client.client_socket.sendall(Log.encode("utf-8"))
                    print("Log를 서버로 보냈습니다.")
                    tcp_client.wait_for_ACK()
                    
                    
                    
                    tcp_client.send_data_type(0)  # image
                    tcp_client.send_image("gcc_version.png")# 이미지를 서버로 송신
                    tcp_client.wait_for_ACK()
                    time.sleep(1)
                    

                    # 대기: 이미지 전송이 시작됨을 확인
                    #tcp_client.receive_data_type()

                except Exception as e:
                    print(f"통신 오류: {e}")
                finally:
                    tcp_client.close_connection()
    except KeyboardInterrupt:
        print("KeyboardInterrupt: 데이터 수신을 중지합니다.")
    finally:
        ser.close()

if __name__ == "__main__":
    receive_uid_and_send_image()

