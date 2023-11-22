
// server.cpp

#include "pch.h"
#include "Server.h"

Server::Server() {
    Rflag = -1;//no input

    WSAStartup(MAKEWORD(2, 2), &wsaData);

    serverSocket = socket(AF_INET, SOCK_STREAM, 0);

    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(PORT);

    bind(serverSocket, (struct sockaddr*)&serverAddr, sizeof(serverAddr));
    listen(serverSocket, 5);
    std::cout << "Server listening on port " << PORT << "..." << std::endl;
}

Server::~Server() {
    closesocket(serverSocket);
    WSACleanup();
}

void Server::run(CString& received_string) {
    sockaddr_in clientAddr;
    int clientAddrLen = sizeof(clientAddr);
    SOCKET clientSocket = accept(serverSocket, (struct sockaddr*)&clientAddr, &clientAddrLen);

    DataType dataType;
    int headerBytesRead = recv(clientSocket, reinterpret_cast<char*>(&dataType), sizeof(DataType), 0);

    if (headerBytesRead != sizeof(DataType)) {
        std::cerr << "Error reading data type header" << std::endl;
        closesocket(clientSocket);
    }

    switch (dataType) {
    case IMAGE:
        receiveImage(clientSocket);
        set_Rflag(0);
        break;
    case STRING:
        received_string = receiveString(clientSocket);
        set_Rflag(1);
        break;
    case RFID_UID:
        received_string = receiveRFID_UID(clientSocket);
        set_Rflag(2);
        break;
    default:
        std::cerr << "Unknown data type received" << std::endl;
    }

    closesocket(clientSocket);
}

void Server::set_Rflag(int Rflag) {
    this->Rflag = Rflag;
}

int Server::get_Rflag() {
    return this->Rflag;
}
SOCKET Server::get_serverSocket() {
    return this->serverSocket;
}

void Server::receiveImage(SOCKET clientSocket) {
    std::ofstream receivedFile("received_image.png", std::ios::binary);
    char buffer[BUFFER_SIZE];
    int bytesRead;

    while ((bytesRead = recv(clientSocket, buffer, BUFFER_SIZE, 0)) > 0) {
        receivedFile.write(buffer, bytesRead);
        std::cout << "Received " << bytesRead << " bytes of image data from client" << std::endl;
    }

    receivedFile.close();
    set_Rflag(0);//image flag
    std::cout << "Image received and saved as received_image.png" << std::endl;
}

CString Server::receiveString(SOCKET clientSocket) {
    char stringBuffer[BUFFER_SIZE];
    int stringBytesRead = recv(clientSocket, stringBuffer, BUFFER_SIZE, 0);

    if (stringBytesRead > 0) {
        stringBuffer[stringBytesRead] = '\0';
        std::cout << "Received string from client: " << stringBuffer << std::endl;
    }
    else {
        std::cerr << "Error receiving string data" << std::endl;
    }

    CStringW receivedString(stringBuffer);
    set_Rflag(1);//1:string for log
    return receivedString;
}

CString Server::receiveRFID_UID(SOCKET clientSocket) {
    char uidBuffer[BUFFER_SIZE];
    int uidBytesRead = recv(clientSocket, uidBuffer, BUFFER_SIZE, 0);

    if (uidBytesRead > 0) {
        uidBuffer[uidBytesRead] = '\0';
        std::cout << "Received RFID UID from client: " << uidBuffer << std::endl;
    }
    else {
        std::cerr << "Error receiving RFID UID data" << std::endl;
    }

    CStringW receivedUID(uidBuffer);
    set_Rflag(2);//2:RFID_UID
    return receivedUID;
}
