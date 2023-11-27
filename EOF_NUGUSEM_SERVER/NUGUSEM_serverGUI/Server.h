// server.h

#pragma once
#pragma comment(lib, "Ws2_32.lib")

#include <iostream>
#include <fstream>
#include <winsock2.h>
#include <ws2ipdef.h>
#include <atlstr.h>
#include <mutex> // 추가된 헤더

enum DataType {
    IMAGE_REC = 0,
    STRING = 1,
    IMAGE_SEND = 2,
    IMAGE_SIZE = 3,
    AUTH_LOG = 4,
    ACK = 9,
};

enum ManagerDataType {
    M_IMAGE_REC = 0,
    M_STRING = 1,
    REQUEST = 2,
    OPEN = 3,
    CLOSE = 4,
    
};

constexpr int PORT = 8888;
constexpr int MPORT = 8889;
constexpr int BUFFER_SIZE = 1024;
#define END_OF_IMAGE_MARKER 9

class Server {
public:
    Server();
    Server(const int _port);
    ~Server();

    /*일반 상황 통신용 쓰레드 port:8888 */
    void run(CString& received_string);

    void receiveImage(SOCKET clientSocket);
    CString receiveString(SOCKET clientSocket);
    void sendImageToClient(CString image_Path);
    bool isLastPacket(const char* buffer, int bytesRead);
    //void sendAck(SOCKET clientSocket); // ACK 송신

    int get_Rflag();
    void set_Rflag(int Rflag/*receieve flag*/);


    /*매니저 호출 상황 통신용 쓰레드 port:8889 */
    void run_manager();

    void send_comm_manager(SOCKET clientSocket);

    int get_Manager_Req_flag();
    void set_Manager_Req_flag(int Rflag/*receieve flag*/);
    
    int get_Manager_com_flag();
    void set_Manager_com_flag(int Rflag/*receieve flag*/);

    BOOL get_image_upload_flag();
    void set_image_upload_flag(BOOL image_upload_flag/*receieve flag*/);

    
private:
    WSADATA wsaData; //Windows 소켓 프로그래밍에서 Winsock 라이브러리를 초기화에 사용
    SOCKET serverSocket;
    sockaddr_in serverAddr;

    int Rflag; /*receieve flag 0: image 1:string for log 2:RFID_UID*/ 
    int Manager_Req_flag; //manager Request flag  0: 평소 listening 1: req 수신 및 MFC 메시지 박스 2: 메시지 박스 입력 기반 동작 후 0으로 복귀
    int Manager_com_flag; //manager command flag -1: 평소 0: CLOSE   1:OPEN
    BOOL image_upload_flag;// true : img rcv 완료 false: img not rcv

};
