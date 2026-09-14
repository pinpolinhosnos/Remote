#include "remote_agent.hpp"
#include <iostream>
#include <string>
#include <thread>
#include <chrono>

int main(int argc, char* argv[]) {
    std::string serverIP = "127.0.0.1";
    int serverPort = 8080;
    
    // Parse command line arguments
    if (argc >= 3) {
        serverIP = argv[1];
        serverPort = std::stoi(argv[2]);
    } else if (argc == 2) {
        serverIP = argv[1];
    }
    
    std::cout << "Starting Remote Agent..." << std::endl;
    std::cout << "Connecting to server: " << serverIP << ":" << serverPort << std::endl;
    
    RemoteAgent agent(serverIP, serverPort);
    
    if (!agent.start()) {
        std::cerr << "Failed to connect to server" << std::endl;
        return 1;
    }
    
    std::cout << "Agent connected successfully" << std::endl;
    std::cout << "Agent is running. Press Ctrl+C to exit." << std::endl;
    
    // Keep the agent running
    while (agent.isRunning()) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    
    std::cout << "Agent stopped" << std::endl;
    return 0;
}