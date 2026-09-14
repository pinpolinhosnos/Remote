#pragma once
#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <iostream>
#include <string>
#include <thread>
#include <atomic>
#include <vector>
#include <functional>
#include <map>

#pragma comment(lib, "ws2_32.lib")

class RemoteAgent {
private:
    SOCKET clientSocket;
    std::atomic<bool> running;
    std::thread connectionThread;
    std::string serverIP;
    int serverPort;
    
    // Command handlers
    std::map<std::string, std::function<std::string(const std::string&)>> commandHandlers;
    
    void setupCommandHandlers() {
        commandHandlers["ping"] = [this](const std::string& params) { return "pong"; };
        commandHandlers["inject"] = [this](const std::string& params) { return handleInject(params); };
        commandHandlers["clean"] = [this](const std::string& params) { return handleClean(params); };
        commandHandlers["status"] = [this](const std::string& params) { return handleStatus(params); };
    }
    
    std::string handleInject(const std::string& params) {
        // Integração com injectSK.hpp
        return "Inject command received - integration with local inject system";
    }
    
    std::string handleClean(const std::string& params) {
        // Integração com Cleaner.hpp
        return "Clean command received - integration with local cleaner system";
    }
    
    std::string handleStatus(const std::string& params) {
        return "Agent running - Ready for remote commands";
    }
    
    bool connectToServer() {
        WSADATA wsaData;
        if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
            return false;
        }
        
        clientSocket = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        if (clientSocket == INVALID_SOCKET) {
            WSACleanup();
            return false;
        }
        
        sockaddr_in serverAddr;
        serverAddr.sin_family = AF_INET;
        serverAddr.sin_port = htons(serverPort);
        inet_pton(AF_INET, serverIP.c_str(), &serverAddr.sin_addr);
        
        if (connect(clientSocket, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
            closesocket(clientSocket);
            WSACleanup();
            return false;
        }
        
        return true;
    }
    
    void connectionLoop() {
        char buffer[4096];
        
        while (running) {
            int bytesReceived = recv(clientSocket, buffer, sizeof(buffer) - 1, 0);
            if (bytesReceived > 0) {
                buffer[bytesReceived] = '\0';
                std::string command(buffer);
                
                // Parse command
                size_t spacePos = command.find(' ');
                std::string cmdName, params;
                if (spacePos != std::string::npos) {
                    cmdName = command.substr(0, spacePos);
                    params = command.substr(spacePos + 1);
                } else {
                    cmdName = command;
                }
                
                // Execute command
                std::string response;
                if (commandHandlers.find(cmdName) != commandHandlers.end()) {
                    response = commandHandlers[cmdName](params);
                } else {
                    response = "ERROR: Unknown command";
                }
                
                // Send response
                send(clientSocket, response.c_str(), response.length(), 0);
            } else if (bytesReceived == 0) {
                // Connection closed
                break;
            } else {
                // Error
                break;
            }
        }
        
        closesocket(clientSocket);
        WSACleanup();
    }
    
public:
    RemoteAgent(const std::string& ip = "127.0.0.1", int port = 8080) 
        : serverIP(ip), serverPort(port), clientSocket(INVALID_SOCKET), running(false) {
        setupCommandHandlers();
    }
    
    ~RemoteAgent() {
        stop();
    }
    
    bool start() {
        if (!connectToServer()) {
            return false;
        }
        
        running = true;
        connectionThread = std::thread(&RemoteAgent::connectionLoop, this);
        
        // Send initial registration
        std::string initMsg = "AGENT_CONNECTED";
        send(clientSocket, initMsg.c_str(), initMsg.length(), 0);
        
        return true;
    }
    
    void stop() {
        running = false;
        if (connectionThread.joinable()) {
            connectionThread.join();
        }
        
        if (clientSocket != INVALID_SOCKET) {
            closesocket(clientSocket);
            clientSocket = INVALID_SOCKET;
        }
    }
    
    bool isRunning() const {
        return running;
    }
};