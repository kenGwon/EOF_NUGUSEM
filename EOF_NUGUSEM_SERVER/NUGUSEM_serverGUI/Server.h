// server.h

#pragma once

#include <iostream>
#include <fstream>
#include <winsock2.h>
#include <ws2ipdef.h>
#include <atlstr.h>
#pragma comment(lib, "Ws2_32.lib")

constexpr int PORT = 8888;
constexpr int BUFFER_SIZE = 2048;

enum DataType {
    IMAGE = 0,
    STRING = 1,
    RFID_UID = 2,
};

class Server {
public:
    Server();
    ~Server();

    void run(CString& received_string);
    void set_Rflag(int Rflag/*receieve flag*/);
    int get_Rflag();
    void receiveImage(SOCKET clientSocket);
    CString receiveString(SOCKET clientSocket);
    CString receiveRFID_UID(SOCKET clientSocket);
    SOCKET get_serverSocket(); // 새로 추가한 함수

private:
    WSADATA wsaData;
    SOCKET serverSocket;
    sockaddr_in serverAddr;
    int Rflag; /*receieve flag 0: image 1:string for log 2:RFID_UID*/ 
};
