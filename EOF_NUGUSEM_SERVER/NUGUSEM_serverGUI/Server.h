#pragma once

#include <iostream>
#include <fstream>
#include <winsock2.h>
#include <ws2ipdef.h>
#include <atlstr.h>
#pragma comment(lib, "Ws2_32.lib")

constexpr int PORT = 8888;
constexpr int BUFFER_SIZE = 1024;

enum DataType {
    IMAGE = 0,
    STRING = 1,
};

class Server {
public:
    Server();
    ~Server();

    void run(CString& receieved_string);
    void set_image_flag(bool image_flag);
    bool get_image_flag();


private:
    WSADATA wsaData;
    SOCKET serverSocket;
    sockaddr_in serverAddr;
    bool image_flag;
    void receiveImage(SOCKET clientSocket);
    CString receiveString(SOCKET clientSocket);
};
