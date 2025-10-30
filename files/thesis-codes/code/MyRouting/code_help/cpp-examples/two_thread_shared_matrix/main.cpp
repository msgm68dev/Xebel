#include <thread>
#include <sstream>
#include <string.h>
#include <cstring>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include "Matrix.h"

const int speak_PORT = 1369;
void xerop(Matrix *mat, int S)
{
    // Get the size of the matrix
    int m = mat->getSize().first;
    int n = mat->getSize().second;

    // Initialize the random seed
    srand(time(NULL));

    // Loop forever
    while (true)
    {
        // Fill the matrix with random integers
        for (int i = 0; i < m; i++)
        {
            for (int j = 0; j < n; j++)
            {
                // Generate a random integer between 0 and 99
                int val = rand() % 100;
                // Set the value of the cell
                (*mat)[i][j].setMcval(val);
            }
        }

        // Sleep for S seconds

        // std::cout << "xerop done. sleeping " << S << std::endl;
        std::this_thread::sleep_for(std::chrono::seconds(S));
    }
}

// The function xeror takes a pointer to a Matrix object and a port number as parameters. It opens a raw socket that listens on the given port, and responds to requests of the form "GET NUMBER x y" by reading the value of the cell at row x and column y in the matrix, and sending back a response of the form "GIVE x y v", where v is the value of the cell. It also prints the request and the response on the standard output.

using namespace std;

void xeror(Matrix *mat, int port)
{
    // Create a raw socket
    // int sock = socket(AF_INET, SOCK_RAW, IPPROTO_RAW);
    int sock = socket(AF_INET, SOCK_STREAM, 0); // create a TCP socket

    if (sock == -1)
    {
        std::cerr << "Error creating socket" << std::endl;
        return;
    }
    // Bind the socket to the given port
    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port); // use a different port number

    addr.sin_addr.s_addr = INADDR_ANY;
    // addr.sin_addr.s_addr = inet_addr("127.0.0.1"); // use a specific IPv4 address
    if (bind(sock, (struct sockaddr *)&addr, sizeof(addr)) == -1)
    {
        std::cerr << "Error binding socket" << std::endl;
        return;
    }
    else
    {
        std::cout << "binding socket successfully to " << port << std::endl;
    }

    // Loop forever
    while (true)
    {

        std::cout << "xeroR start: " << std::endl;
        // std::this_thread::sleep_for(std::chrono::seconds(1));
        char buffer[1024] = "";
        listen(sock, 1);
        struct sockaddr_in src;
        socklen_t len = sizeof(src);
        std::cout << "xeroR 2 " << std::endl;
        int clientSock = accept(sock, (struct sockaddr *)&src, &len);
        int bytes = recv(clientSock, buffer, 1024, 0);
        if (bytes == -1)
        {
            std::cerr << "Error receiving from socket" << std::endl;
            continue;
        }
        // Convert the request to a string
        std::string request(buffer, bytes);
        std::cout << "Received request: " << request << std::endl;
        // Parse the request
        std::istringstream iss(request);
        std::string cmd, x, y, z;
        iss >> cmd >> x >> y >> z;
        std::cout << "xeroR 4.4) cmd " << cmd << ", x " << x << ", y " << y << ", z " << z << std::endl;

        // Check if the request is valid
        if (cmd == "GET" && x == "NUMBER")
        {
            std::cout << "xeroR if 1 " << std::endl;
            // Convert the row and column indices to integers
            int i = std::stoi(y);
            std::cout << "xeroR if 2 " << std::endl;
            int j = std::stoi(z);
            std::cout << "xeroR if 3 " << std::endl;
            // Get the value of the cell
            int v = (*mat)[i][j].getMcval();
            std::cout << "MAT[" << i << "][" << j << "] = " << v << std::endl;
            // Format the response
            std::ostringstream oss;
            oss << "GIVE " << y << " " << z << " " << v;
            std::string response = oss.str();

            // Print the response
            std::cout << "Sending response: " << response << std::endl;

            int n = send(clientSock, response.c_str(), response.size(), 0);
            std::cout << n << " bytes responded: " << response << std::endl;
            close(clientSock);
        }
        if (cmd == "GET" && x == "MKEY")
        {
            std::cout << "xeroR if x1 " << std::endl;
            // Convert the row and column indices to integers
            int i = std::stoi(y);
            std::cout << "xeroR if x2 " << std::endl;
            int j = std::stoi(z);
            std::cout << "xeroR if x3 " << std::endl;
            // Get the value of the cell
            int v = (*mat)[i][j].getMcval();
            std::cout << "MAT[" << i << "][" << j << "] = " << v << std::endl;
            // Format the response
            std::ostringstream oss;
            oss << "GIVE " << y << " " << z << " " << v;
            std::string response = oss.str();

            // Print the response
            std::cout << "Sending response: " << response << std::endl;

            int n = send(clientSock, response.c_str(), response.size(), 0);
            std::cout << n << " bytes responded: " << response << std::endl;
            close(clientSock);
        }
        else
        {
            // Invalid request
            std::cerr << "Invalid request format" << std::endl;
        }
    }
    close(sock);
}

// Define the main function
int main()
{
    std::cout << "C++ version: " << __cplusplus << "\n";
    // Create a matrix object
    Matrix mat(10, 10);

    // Create a thread for xerop function
    std::thread t1(xerop, &mat, 5);

    // Create a thread for xeror function
    std::thread t2(xeror, &mat, speak_PORT);

    // Wait for the threads to finish
    t1.join();
    t2.join();

    // Return 0 on success
    return 0;
}