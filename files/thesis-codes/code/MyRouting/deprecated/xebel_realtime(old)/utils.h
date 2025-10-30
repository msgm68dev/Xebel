#include <string>
#include <vector>
#include <fstream>
#include <algorithm> // for remove_spaces
#include <iostream>
#include <experimental/filesystem>
#include <boost/algorithm/string.hpp>
#include <chrono>
#include <ctime>
#include <iomanip>
using namespace std;
namespace bal = boost::algorithm;
namespace fs = experimental::filesystem;

/* ---------- MISC ----------    */
string get_now()
{
    auto now = chrono::system_clock::now();
    time_t now_t = chrono::system_clock::to_time_t(now);
    stringstream ss;
    ss << put_time(localtime(&now_t), "%Y-%m-%d %H:%M:%S");
    return ss.str();
}
bool is_yes(string response){
    string resp = bal::to_lower_copy(response);
    if (resp == "true")
        return true;
    if (resp == "yes")
        return true;
    if (resp == "y")
        return true;
    return false;    
}
/* ---------- STRING ---------- */
string str_to_lower(string S){
    // Note:  bal::to_lower(S); edits S itself
    return bal::to_lower_copy(S); //
}
string remove_spaces(const string &str)
{
    // copy the string to a new variable
    string result = str;
    // use remove to move all non-space characters to the front
    // and get an iterator to the new end of the string
    auto end = remove(result.begin(), result.end(), ' ');
    // use erase to remove the trailing spaces
    result.erase(end, result.end());
    return result;
}
// str_replace Usage:
//          cout << str_replace(string("Number Of Beans"), string(" "), string("_")) << endl;
//          cout << str_replace(string("ghghjghugtghty"), string("gh"), string("X")) << endl;
// Output:
//          Number_Of_Beans
//          XXjXugtXty
string str_replace(string str, const string &from, const string &to)
{
    size_t start_pos = 0;
    while ((start_pos = str.find(from, start_pos)) != string::npos)
    {
        str.replace(start_pos, from.length(), to);
        start_pos += to.length(); // Handles case where 'to' is a substring of 'from'
    }
    return str;
}
vector<string> split(const string &STR, const string &DELIMITER)
{
    vector<string> WORDS; // a vector to store the tokens
    size_t pos = 0;       // the current position in the string
    size_t found;         // the position of the delimiter
    string sub;
    while ((found = STR.find(DELIMITER, pos)) != string::npos)
    {
        // extract the substring between pos and found and add it to the vector
        sub = STR.substr(pos, found - pos);
        if (!sub.empty())
            WORDS.push_back(sub);
        // move pos to the next position after the delimiter
        pos = found + DELIMITER.length();
    }
    sub = STR.substr(pos);
    if (!sub.empty())
        WORDS.push_back(sub);
    return WORDS;
}

/* ----------  FILE ----------   */
void append_to_file(const string &filename, bool timestamp, const string &str)
{
    // Open the file for output and append
    ofstream file(filename, ios::app);
    // Check if the file is opened successfully
    if (file.is_open())
    {
        if (timestamp)
        {
            file << get_now() << " | " << str << endl;
        }
        else
        {
            file << str << endl;
        }
        file.close();
    }
    else
    {
        // Handle the error
        cerr << "Error in logger: Failed to open the logfile: " << filename << endl;
    }
}
void make_dirs_and_file(const fs::path &file_path)
{
    // Check if the file path is valid
    if (file_path.empty())
    {
        cerr << "Invalid file path\n";
        return;
    }
    // Create the parent directory of the file if it does not exist
    fs::path dir_path = file_path.parent_path();
    if (!dir_path.empty() && !fs::exists(dir_path))
    {
        fs::create_directories(dir_path);
    }
    // Create the file as empty if it does not exist
    if (!fs::exists(file_path))
    {
        ofstream ofs(file_path);
        ofs.close();
    }
}

