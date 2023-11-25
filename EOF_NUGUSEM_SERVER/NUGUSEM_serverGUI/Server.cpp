
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

    if (dataType == IMAGE_REC) //0
    {
        receiveImage(clientSocket);
        set_Rflag(0);


        
    }
    else if (dataType == STRING)// 1 
    {
        received_string = receiveString(clientSocket);
        set_Rflag(1);

    }
    else if (dataType == AUTH_LOG)// 4
    {
        received_string = receiveString(clientSocket);
        set_Rflag(4);
    }






    else {
        std::cerr << "Unknown data type received" << std::endl;
        closesocket(clientSocket);
        return;
    }

    closesocket(clientSocket);
}

void Server::set_Rflag(int Rflag) {
    this->Rflag = Rflag;
}

int Server::get_Rflag() {
    return this->Rflag;
}




// 이미지 데이터를 수신했는지 확인하는 함수
bool Server::isLastPacket(const char* buffer, int bytesRead) {
    // 마지막 패킷을 확인할 수 있는 조건을 추가
    // 여기서는 buffer의 마지막 4바이트가 END_OF_IMAGE_MARKER인지 확인

    if (bytesRead >= sizeof(int)) {
        int marker;
        memcpy(&marker, buffer + bytesRead - sizeof(int), sizeof(int));

        return marker == END_OF_IMAGE_MARKER;
    }

    return bytesRead == 0; // 마지막 패킷이 아니라면 false 반환
}



void Server::receiveImage(SOCKET clientSocket) {
    std::ofstream receivedFile("received_image.png", std::ios::binary);
    char buffer[BUFFER_SIZE];
    int bytesRead;

    while ((bytesRead = recv(clientSocket, buffer, BUFFER_SIZE, 0)) > 0) {
        receivedFile.write(buffer, bytesRead);
        std::cout << "Received " << bytesRead << " bytes of image data from client" << std::endl;

        // 마지막 패킷인지 확인
        if (isLastPacket(buffer, bytesRead)) {
            set_Rflag(0); // 이미지 flag
            std::cout << "Image received and saved as received_image.png" << std::endl;
            
            break;
        }
    }

    receivedFile.close();
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

    CStringA receivedString(stringBuffer);
    //set_Rflag(1);//1:string for log
    return receivedString;
}



void Server::sendImageToClient(CString image_Path) {
    sockaddr_in clientAddr;
    int clientAddrLen = sizeof(clientAddr);
    SOCKET clientSocket = accept(serverSocket, (struct sockaddr*)&clientAddr, &clientAddrLen);
    std::ifstream imageFile(image_Path, std::ios::binary);

    if (!imageFile.is_open()) {
        std::cerr << "Error opening image file: " << image_Path << std::endl;
        closesocket(clientSocket);
        return;
    }

    // 이미지 파일의 크기를 가져옴
    std::ifstream imageFileSize(image_Path, std::ios::binary | std::ios::ate);
    int imageSize = static_cast<int>(imageFileSize.tellg());
    imageFileSize.close();

    DataType img_size_Transmission = IMAGE_SIZE;//3
    send(clientSocket, reinterpret_cast<char*>(&img_size_Transmission), sizeof(DataType), 0);

    char buffer[BUFFER_SIZE];
    int bytesRead;

    try {
        while ((bytesRead = imageFile.read(buffer, BUFFER_SIZE).gcount()) > 0) {
            int bytesSent = send(clientSocket, buffer, bytesRead, 0);

            if (bytesSent == SOCKET_ERROR) {
                std::cerr << "Error sending image data: " << WSAGetLastError() << std::endl;
                break;
            }

            std::cout << "Sent " << bytesSent << " bytes of image data to client" << std::endl;
        }
    }
    catch (const std::exception& e) {
        std::cerr << "Error reading image file: " << e.what() << std::endl;
    }
    imageFile.close();
    std::cout << "Image sent to client" << std::endl;
    closesocket(clientSocket); // 이미지를 전송한 후에 소켓을 닫습니다.
    std::cout << "client Socket Off" << std::endl;
}

void Server::sendImageToClientAsync(CString image_Path) {
    // 이미지를 전송하는 스레드 생성
    std::thread([this, image_Path]() {
        // imagePathA는 이 스레드에서만 사용될 것이므로 복사본을 사용
        sockaddr_in clientAddr;
        int clientAddrLen = sizeof(clientAddr);
        SOCKET clientSocket = accept(serverSocket, (struct sockaddr*)&clientAddr, &clientAddrLen);
       
        if (clientSocket == INVALID_SOCKET) {
            std::cerr << "Error accepting client connection: " << WSAGetLastError() << std::endl;
            return;
        }

        std::ifstream imageFile(image_Path, std::ios::binary);

        if (!imageFile.is_open()) {
            std::cerr << "Error opening image file: " << image_Path << std::endl;
            closesocket(clientSocket);
            return;
        }

        char buffer[BUFFER_SIZE];
        int bytesRead;

        try {
            while ((bytesRead = imageFile.read(buffer, BUFFER_SIZE).gcount()) > 0) {
                int bytesSent = send(clientSocket, buffer, bytesRead, 0);

                if (bytesSent == SOCKET_ERROR) {
                    std::cerr << "Error sending image data: " << WSAGetLastError() << std::endl;
                    break;
                }

                std::cout << "Sent " << bytesSent << " bytes of image data to client" << std::endl;
            }

            // 클라이언트에게 이미지 전송이 완료되었음을 알리는 메시지 전송
            DataType endTransmission = STRING;
            send(clientSocket, reinterpret_cast<char*>(&endTransmission), sizeof(DataType), 0);
        }
        catch (const std::exception& e) {
            std::cerr << "Error reading image file: " << e.what() << std::endl;
        }

        imageFile.close();
        std::cout << "Image sent to client" << std::endl;

        // 이미지 전송이 완료된 후에 소켓을 닫습니다.
        closesocket(clientSocket);
        std::cout << "client Socket Off" << std::endl;

        // 이미지 전송이 완료된 후에 추가 작업을 수행할 수 있습니다.
        handleImageTransmissionCompleteMessage();
        }).detach();
}

void Server::handleImageTransmissionCompleteMessage() {
    std::cout << "Image transmission complete message received from client" << std::endl;
    // 이미지 전송 완료 후의 추가 작업을 여기에 추가합니다.


}

void Server::sendAck(SOCKET clientSocket) {
    DataType ackType = ACK;//9를 보내주는거임.
    send(clientSocket, reinterpret_cast<char*>(&ackType), sizeof(DataType), 0);
}