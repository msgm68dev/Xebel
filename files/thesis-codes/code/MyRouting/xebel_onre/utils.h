#ifndef XEBEL_CPP_UTILS
#define XEBEL_CPP_UTILS
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <algorithm> // for remove_spaces
#include <iostream>
#include <experimental/filesystem>
#include <boost/algorithm/string.hpp>
#include <chrono>
#include <ctime>
#include <iomanip>
#include <chrono>
#include <thread> // Not used directly, but needed for high_resolution timestamps
using namespace std;
namespace bal = boost::algorithm;
namespace fs = experimental::filesystem;

chrono::high_resolution_clock::time_point start_time; // Global variable to store start time
/* ---------- TIME ----------    */
string get_now()
{
    auto now = chrono::system_clock::now();
    time_t now_t = chrono::system_clock::to_time_t(now);
    stringstream ss;
    ss << put_time(localtime(&now_t), "%Y-%m-%d %H:%M:%S");
    return ss.str();
}
void start_timer()
{
    // Get high-resolution clock start time
    start_time = chrono::high_resolution_clock::now();
}
void sleep_milliseconds(int milliseconds)
{
    using namespace std::chrono_literals;
    std::this_thread::sleep_for(milliseconds * 1ms);
}
float elapsed_time()
{
    // Get high-resolution clock end time
    auto end_time = chrono::high_resolution_clock::now();
    // Calculate elapsed time in nanoseconds
    auto duration = chrono::duration_cast<chrono::nanoseconds>(end_time - start_time);
    // Convert to seconds and set precision
    float seconds = chrono::duration<float>(duration).count();
    return seconds;
}

/* ---------- STRING ---------- */
string str_to_lower(string S)
{
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
vector<unsigned short> parse_tuple_str_dashed(string tuple_dashed)
{
    vector<unsigned short> tuple;
    stringstream ss2(tuple_dashed);
    string number_str;
    try
    {
        while (getline(ss2, number_str, '-'))
        {
            // cout << " ** " << number_str << endl;
            tuple.push_back(stoi(number_str));
        }
    }
    catch (const std::exception &e)
    {
        std::cerr << "Error"
                  << " parse_tuple_str_dashed" << tuple_dashed << e.what() << '\n';
    }
    return tuple;
}
/* ----------  FILE content ----------   */
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
bool read_float_value_from_file(const string &filename, float *value_ptr)
{
    std::ifstream file(filename);

    if (!file.is_open())
    {
        std::cerr << "Error read_float_value_from_file. cannot open the file: " << filename << std::endl;
        return false;
    }
    file >> *value_ptr;
    if (file.fail())
    {
        std::cerr << "Error read_float_value_from_file. cannot read float value from file: " << filename << std::endl;
        return false;
    }
    return true;
}
vector<vector<string>> file_to_table(const string &filename, const string &field_delimeter)
{
    vector<vector<string>> Table;

    ifstream file(filename);
    if (!file.is_open())
    {
        cerr << "Error: file_to_table: cannot open the file" << endl;
        exit(-1);
    }
    // read each line from the file
    string line_raw;
    while (getline(file, line_raw))
    {
        string line = remove_spaces(line_raw);
        if (line.empty())
            continue;
        if (line[0] == '#')
            continue;
        vector<string> record = split(line, field_delimeter);
        Table.push_back(record);
    }
    return Table;
}

/* --------------- File & Directory ---------------*/
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
void create_file_with_path(const fs::path &file_path)
{
    make_dirs_and_file(file_path);
}
string join_paths(string first_part, string second_part)
{
    fs::path dir(first_part);
    fs::path file(second_part);
    fs::path full_path = dir / file;
    return string(full_path);
}

/* --------------- STL Containers ---------------*/
template <typename T>
bool vector_contains(const std::vector<T> &vec, const T &element)
{
    // return std::find(vec.begin(), vec.end(), element,
    //                  [](const T &a, const T &b) { return a == b; }) != vec.end();
    return std::find(vec.begin(), vec.end(), element) != vec.end();
}

template <typename T>
bool vector_insert_if_not_exist(vector<T> &vec, const T &element)
{
    bool contains = vector_contains(vec, element);
    if (!contains)
    {
        vec.push_back(element);
    }
    return contains;
}
/* ---------- MISC ----------    */
bool is_yes(string answer)
{
    string ans = bal::to_lower_copy(answer);
    if (ans == "y" || ans == "yes" || ans == "true" || ans == "ok")
    {
        return true;
    }
    else
        return false;
}

string get_switch_if_entered(std::string switch_str, int argc, char *argv[])
{
    string switch_value = "";
    for (int i = 1; i < argc; ++i)
    {
        string arg = argv[i];
        if (arg == switch_str)
        {
            if (i + 1 < argc)
            {
                switch_value = argv[++i];
                std::cout << switch_str << " provided: " << switch_value << std::endl;
            }
            else
            {
                std::cerr << switch_str << " option requires one argument." << std::endl;
                exit(-1);
            }
        }
    }
    return switch_value;
}
#endif