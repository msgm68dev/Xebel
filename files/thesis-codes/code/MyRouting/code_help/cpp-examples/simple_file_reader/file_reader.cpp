#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <sstream>
#include <algorithm> // for remove_spaces 


class path
{
public:
    // data members
    std::string Role;
    std::vector<unsigned short> Tuple;
    std::string MKey;
    // float value =

    // constructor
    path(std::string role, std::vector<unsigned short> tuple, std::string mkey)
    {
        Role = role;
        Tuple = tuple;
        MKey = mkey;
    }

    // print function
    void print()
    {
        std::cout << "Role: " << Role << std::endl;
        std::cout << "Tuple: ";
        for (auto x : Tuple)
        {
            std::cout << x << " ";
        }
        std::cout << std::endl;
        std::cout << "MKey: " << MKey << std::endl;
    }
};
// define a function that takes a string and removes all spaces from it
std::string remove_spaces(const std::string &str)
{
    // copy the string to a new variable
    std::string result = str;
    // use std::remove to move all non-space characters to the front
    // and get an iterator to the new end of the string
    auto end = std::remove(result.begin(), result.end(), ' ');
    // use erase to remove the trailing spaces
    result.erase(end, result.end());
    // return the modified string
    return result;
}
// main function
int main()
{
    // open the file
    std::ifstream file("data.txt");
    // check if the file is opened
    if (!file.is_open())
    {
        std::cerr << "Error: cannot open the file" << std::endl;
        return 1;
    }

    // create a vector of objects
    std::vector<path> records;

    // read each line from the file
    std::string line_raw;
    while (std::getline(file, line_raw))
    {
        std::string line = remove_spaces(line_raw);
        if (line.empty())
            continue;
        if (line[0] == '#')
            continue;
        // split the line into tokens using '|' as the delimiter
        std::vector<std::string> tokens;
        std::stringstream ss(line);
        std::string token;
        while (std::getline(ss, token, '|'))
        {
            tokens.push_back(token);
        }

        // create an object using the tokens as arguments
        std::string role = tokens[0];
        std::string tuple_str = tokens[1];
        std::stringstream ss2(tuple_str);
        std::string number_str;
        std::vector<unsigned short> tuple;

        while (std::getline(ss2, number_str, '-'))
        {
            tuple.push_back(std::stoi(number_str));
        }
        std::string mkey = tokens[2];
        path record(role, tuple, mkey);
        // store the object in the vector
        records.push_back(record);
    }
    // close the file
    file.close();
    // print the vector of objects
    for (auto r : records)
    {
        r.print();
    }
    return 0;
}

// Output:

// Role: path
// Tuple: 11 18 9 7 3
// MKey: 96df1126b1ae9ec54541dcb8d589877e
