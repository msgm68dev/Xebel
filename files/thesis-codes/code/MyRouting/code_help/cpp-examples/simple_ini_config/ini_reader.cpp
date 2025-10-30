// An ini file is a text file that contains configuration settings in the form of sections and key-value pairs. For example, an ini file might look like this:
// [General]
// name = Alice
// age = 25
// [Network]
// ip = 192.168.1.1
// port = 8080
// To read configs from an ini file in C++, you can use one of the following methods:
// •  Use a library that can parse ini files, such as Boost.PropertyTree https://stackoverflow.com/questions/1417765/parse-config-file-in-c-c, minIni https://stackoverflow.com/questions/146795/how-to-read-config-file-entries-from-an-ini-file, or iniParser https://stackoverflow.com/questions/12633/what-is-the-easiest-way-to-parse-an-ini-file-in-c. These libraries provide functions and classes to read and write ini files, and access the settings as data structures. For example, using Boost.PropertyTree, you can write code like this:
#include <iostream>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/ini_parser.hpp>
// create a property tree object
boost::property_tree::ptree pt;
void read_by_boost()
{
    // read the ini file
    boost::property_tree::ini_parser::read_ini("config.ini", pt);

    // access the settings
    std::string name = pt.get<std::string>("General.name");
    int age = pt.get<int>("General.age");
    std::string ip = pt.get<std::string>("Network.ip");
    int port = pt.get<int>("Network.port");

    // print the settings
    std::cout << "Name: " << name << std::endl;
    std::cout << "Age: " << age << std::endl;
    std::cout << "IP: " << ip << std::endl;
    std::cout << "Port: " << port << std::endl;

    // Output:

    // Name: Alice
    // Age: 25
    // IP: 192.168.1.1
    // Port: 8080
}
// •  Write your own parser using standard C++ streams and strings. You can read each line from the file using std::getline, and split the line into tokens using a delimiter (such as '=' or '[') using std::stringstream and std::getline. You can also use std::stod, std::stoi, or std::stol to convert the string tokens to numeric values if needed. For example, you can write code like this:
#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <map>
#include <vector>
// create a map to store the settings
std::map<std::string, std::string> settings;
int read_by_map()
{
    // open the ini file
    std::ifstream file("config.ini");

    // check if the file is opened
    if (!file.is_open())
    {
        std::cerr << "Error: cannot open the file" << std::endl;
        return 1;
    }

    // read each line from the file
    std::string line;
    while (std::getline(file, line))
    {
        // skip empty or comment lines
        if (line.empty() || line[0] == '#')
            continue;

        // split the line into tokens using '=' as the delimiter
        std::vector<std::string> tokens;
        std::stringstream ss(line);
        std::string token;
        while (std::getline(ss, token, '='))
        {
            tokens.push_back(token);
        }

        // check if the tokens are valid
        if (tokens.size() != 2)
        {
            std::cerr << "Error: invalid line format: " << line << std::endl;
            return 1;
        }

        // store the key-value pair in the map
        settings[tokens[0]] = tokens[1];
    }

    // close the file
    file.close();

    // access the settings
    std::string name = settings["name"];
    int age = std::stoi(settings["age"]);
    std::string ip = settings["ip"];
    int port = std::stoi(settings["port"]);

    // print the settings
    std::cout << "Name: " << name << std::endl;
    std::cout << "Age: " << age << std::endl;
    std::cout << "IP: " << ip << std::endl;
    std::cout << "Port: " << port << std::endl;

    // Output:

    // Name: Alice
    // Age: 25
    // IP: 192.168.1.1
    // Port: 8080
}

int main(){
    read_by_boost();

    read_by_map();
    return 0;
}