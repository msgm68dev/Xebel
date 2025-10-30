
// Include the necessary headers
#include <iostream>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <string.h>
#include <arpa/inet.h>
// #include <format>
#include <sstream>

// Define the server port as a macro
#define SERVER_PORT 12345

// Use the std namespace
using namespace std;

// Define the main function
int main()
{
    // Declare a buffer array
    std::cout << "C++ version: " << __cplusplus << "\n";

    // Declare an integer variable for the number of bytes
    int n;

    // Create a TCP socket object
    int serverSock = socket(AF_INET, SOCK_STREAM, 0);

    // Declare a sockaddr_in struct for the server address
    sockaddr_in serverAddr;

    // Set the address family to AF_INET
    serverAddr.sin_family = AF_INET;

    // Set the port number to the defined value
    serverAddr.sin_port = htons(SERVER_PORT);

    // Set the IP address to any interface
    serverAddr.sin_addr.s_addr = INADDR_ANY;

    // Bind the socket to the server address
    bind(serverSock, (struct sockaddr *)&serverAddr, sizeof(serverAddr));
    while (true)
    {
        char buffer[1024] = "";
        char buffer2[1024] = "";
        // Listen for incoming connections
        listen(serverSock, 1);

        // Declare a sockaddr_in struct for the client address
        sockaddr_in clientAddr;

        // Declare a socklen_t variable for the address size
        socklen_t addrSize = sizeof(clientAddr);
        std::cout << "before accept" << std::endl;
        // Accept a connection from a client
        int clientSock = accept(serverSock, (struct sockaddr *)&clientAddr, &addrSize);
        std::cout << "after accept before recv" << std::endl;

        // Receive a message from the client
        n = recv(clientSock, buffer, 1024, 0);

        // Print the number of bytes received
        cout << "Received " << n << " bytes" << endl;

        // Print the message received
        cout << "Message: " << buffer << endl;

        // Define the response to be sent as a string
        std::stringstream ss;
        ss << "Hello " << buffer << std::endl;
        std::string response = ss.str();

        // std::snprintf(response, 100, "Hello  %s", buffer);
        // string response = std::format("Hello {}\n", buffer);

        // Copy the response to the buffer array
        strcpy(buffer2, response.c_str());

        // Send the response to the client
        n = send(clientSock, buffer2, response.length(), 0);

        // Print the number of bytes sent
        cout << "Sent " << n << " bytes" << endl;

        // Close the client socket
        close(clientSock);
    }
    // Close the server socket
    close(serverSock);

    // Return 0 to indicate success
    return 0;
}
