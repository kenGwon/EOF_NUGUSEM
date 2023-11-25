// server.h

#pragma once

#include <iostream>
#include <fstream>
#include <winsock2.h>
#include <ws2ipdef.h>
#include <atlstr.h>
#include <mutex> // 추가된 헤더
#pragma comment(lib, "Ws2_32.lib")

constexpr int PORT = 8888;
constexpr int BUFFER_SIZE = 1024;
#define END_OF_IMAGE_MARKER 9
enum DataType {
    IMAGE_REC = 0,
    STRING = 1,
    IMAGE_SEND =2,
    IMAGE_SIZE=3,
    AUTH_LOG=4,
    ACK = 9, 
};


enum ManagerDataType {
    REQUEST = 0,
    OPEN = 1,
    CLOSE = 2,
};


class Server {
public:
    Server();
    Server(const int _port);
    ~Server();
    void run(CString& received_string);
    void set_Rflag(int Rflag/*receieve flag*/);
    int get_Rflag();
    void set_Manager_Req_flag(int Rflag/*receieve flag*/);
    int get_Manager_Req_flag();
    void set_Manager_com_flag(int Rflag/*receieve flag*/);
    int get_Manager_com_flag();
    void receiveImage(SOCKET clientSocket);
    CString receiveString(SOCKET clientSocket);
    void sendImageToClient(CString image_Path);
    void sendImageToClientAsync(CString image_Path); // 비동기적으로 이미지를 클라이언트로 보내는 함수
    void handleImageTransmissionCompleteMessage();
    void sendAck(SOCKET clientSocket); // ACK 송신
    bool isLastPacket(const char* buffer, int bytesRead);



    void run_manager();
    void send_comm_manager(SOCKET clientSocket);


private:
    WSADATA wsaData;
    SOCKET serverSocket;
    sockaddr_in serverAddr;
    int Rflag; /*receieve flag 0: image 1:string for log 2:RFID_UID*/ 
    int Manager_Req_flag; //manager Request flag 
    int Manager_com_flag=-1; //manager command flag 

};
