import socket
import struct
import serial
import time
from datetime import datetime

class ClientCommunication:
    def __init__(self, server_ip, port):
        self.server_ip = server_ip
        self.port = port
        self.uid = ""
        self.client_socket = None
        self.rfid_tag_flag = False
        self.img_rcv_flag = False
        self.arduino_rfid_flag = False
        self.arduino_servo_flag = 0
        self.authentication_flag = False
        self.authentication_log = ""
        self.angle=0
        self.Manager_flag=False

    def connect_to_server(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.server_ip, self.port))
            print("서버에 연결되었습니다.")
        except ConnectionRefusedError:
            print("서버에 연결할 수 없습니다.")
            self.client_socket = None  # 연결 실패 시 client_socket을 None으로 설정

    def close_connection(self):
        self.client_socket.close()
    

    def send_data_type(self, data_type):
        if self.client_socket is not None:  # client_socket이 None이 아닌지 확인
            try:
                data_type_header = struct.pack("I", data_type)
                self.client_socket.sendall(data_type_header)
            except AttributeError:
                print("데이터 유형을 보낼 수 없습니다.")
        else:
            print("클라이언트 소켓이 초기화되지 않았습니다. 연결이 실패했을 수 있습니다.")

    def receive_data_type(self):
        # 데이터 유형 수신
        data_type_header = self.client_socket.recv(4)

        # 데이터 언팩에 충분한 데이터가 있는지 확인
        if len(data_type_header) < 4:
            print("오류: 데이터 언팩에 충분한 데이터가 없습니다.")
            return -1

        data_type = struct.unpack("I", data_type_header)[0]
        return data_type
    

    def send_image_to_server(self, image_path):
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

    def receive_image_from_server(self, save_path="resources/received_image.jpg"):
        try:
            # 데이터 형식 식별자 및 이미지 파일의 크기 수신
            data_type_header = self.client_socket.recv(4)
            image_size_header = self.client_socket.recv(4)
            print("image_size_header:", image_size_header)
            # 데이터 형식 식별자 확인
            data_type = struct.unpack("I", data_type_header)[0]
            if data_type == 3:  # 이미지 데이터 수신 시작
                image_size = struct.unpack("I", image_size_header)[0]
                print("Image size:", image_size)
                #self.client_socket.recv(4)  # 4바이트 데이터 읽어오기만 하고 사용하지 않음
                # 이미지 데이터 수신 및 저장
                received_data = image_size_header
                remaining_size = image_size
                while remaining_size > 0:
                    data = self.client_socket.recv(min(1024, remaining_size))
                    if not data:
                        break
                    received_data += data
                    remaining_size -= len(data)
                # print(received_data)#
                with open(save_path, "wb") as image_file:
                    image_file.write(received_data)

                print("Image received and saved")
            else:
                print("Error: Image header does not contain '3'")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            pass

        
    def receive_manager_command(self):
        # receive_data_type()
        self.Manager_flag=True

    def communicate(self):
        try:
            while True:
                               
                # 인증 완료후 로그 재전송 로직
                if self.authentication_flag:
                    try:
                        self.connect_to_server()
                        
                        self.send_data_type(4) # string
                        self.client_socket.sendall(self.authentication_log.encode("utf-8"))
                        print("입장승인여부 로그를 서버로 보냈습니다.")
                    except Exception as e:
                        print(f"통신 오류: {e}")
                    finally:
                        self.close_connection()
                        self.authentication_flag = False
                        
               
                
                # 아두이노에서 RFID가 읽힌 경우, 로그 및 이미지 전송 처리 로직
                if self.arduino_rfid_flag:
                    
                    print("받은 UID:", self.uid)
                    self.rfid_tag_flag = True # 플래그 처리는 여기 있어야 함                  

                    try:
                        # 송신용 소켓 오픈
                        self.connect_to_server()
                        
                        self.send_data_type(1) # string
                        log = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        send_data = self.uid + "@" + log + " try to enter"
                        self.client_socket.sendall(send_data.encode("utf-8"))
                        print("UID + Log를 서버로 보냈습니다.")
                        #tcp_client.wait_for_ACK()
                        time.sleep(0.25)  
                                               
                        self.send_data_type(0) # image binary
                        self.send_image_to_server("resources/captured_image.png")
                        # tcp_client.wait_for_ACK()
                        
                        self.close_connection()
                        

                        # 수신용 소켓 오픈
                        self.connect_to_server()
                        self.receive_image_from_server()
                        self.close_connection()
                    except Exception as e:
                        print(f"통신 오류: {e}")
                    finally:
                        self.close_connection()
                        self.img_rcv_flag = True # 플래그 처리는 여기 있어야 함
                        self.arduino_rfid_flag = False
                

        except KeyboardInterrupt:
            print("KeyboardInterrupt: 데이터 수신을 중지합니다.")
        finally:
            pass
            

    """
    def wait_for_ACK(self):
        ACK = 9
        ack_type_header = self.client_socket.recv(4)

        # 수신된 데이터가 비어 있는지 확인
        if not ack_type_header:
            print("오류: 데이터를 수신하지 못했습니다.")
            return

        ack_type = struct.unpack("I", ack_type_header)[0]
        if ack_type == ACK:
            print("ACK를 받았습니다.")
        else:
            print("오류: 예상치 않은 ACK 유형입니다.")
    """

    def send_communicate_manager(self):
        try:
            self.connect_to_server()
            self.send_data_type(0) # REQUEST
            print("매니저 리퀘스트 메세지를 서버로 보냈습니다.")

        except Exception as e:
            print(f"통신 오류: {e}")
        finally:
            print("여기까지 들어왔다")
            self.close_connection()


    def receive_communicate_manager(self):
        try:
            self.connect_to_server()
            print("위")
            ack_type_header = self.client_socket.recv(4)
            print("아래")

            # 수신된 데이터가 비어 있는지 확인
            if not ack_type_header:
                print("오류: 데이터를 수신하지 못했습니다.")
                self.Manager_flag = False
                return
            else:
                ack_type = struct.unpack("I", ack_type_header)[0]
                if ack_type == 1:
                    print("MFC로부터 Open ACK를 받음")
                    self.arduino_servo_flag = 1
                elif ack_type == 2:
                    print("MFC로부터 Close ACK를 받음")
                    self.arduino_servo_flag = 2
                else:
                    print("오류: 예상치 않은 ACK 유형입니다.")
                self.Manager_flag = True

        except Exception as e:
            print(f"통신 오류: {e}")
        finally:
            print("여기까지 들어왔다")
            self.close_connection()