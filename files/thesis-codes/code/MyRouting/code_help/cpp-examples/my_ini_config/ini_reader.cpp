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
#include <sstream>
#include <vector>
#include <algorithm>
#include <stdexcept>
using namespace std;

class path
{
private:
public:
    string way;
    char *mkey;
    path *next;
    path *prev;
    path(string way, char *mkey)
    {
        this->way = way;
        this->mkey = mkey;
        this->next = nullptr;
        this->prev = nullptr;
    }
    path() : path("*-*", nullptr) {}
    ~path() {};
};
class metric_range
{
public:
    float low;
    float high;
    string name;
    metric_range(string name, float value_max, float value_min)
    {
        this->name = name;
        this->high = value_max;
        this->low = value_min;
    }
    metric_range(string name) : metric_range(name, -100, -99) {}
    metric_range() : metric_range("noname") {}
};
class metric_box
{
private:
public:
    int row, col;
    metric_range m1;
    metric_range m2;
    metric_box(string m1_name, string m2_name)
    {
        this->m1 = metric_range(m1_name);
        this->m2 = metric_range(m2_name);
        this->row = -1;
        this->col = -1;
    }
    metric_box() : metric_box("fake_matric_1", "fake_matric_2") {}
    metric_box(metric_range m1, metric_range m2, int row, int col)
    {
        this->m1 = m1;
        this->m2 = m2;
        this->row = row;
        this->col = col;
    }

    void print()
    {
        // cout << this->m1.name << " " << this->row << ": (" << this->m1.value_min << ", " << this->m1.value_max << ") | ";
        // cout << this->m2.name << " " << this->col << ": (" << this->m2.value_min << ", " << this->m2.value_max << ")" << endl;
        cout << "[" << this->row << ", " << this->col << "]: " << this->m1.low << " < " << this->m1.name << " <= " << this->m1.high;
        cout << " & " << this->m2.low << " < " << this->m2.name << " <= " << this->m2.high << endl;
    }
    ~metric_box(){};
};
class MetricMatrix
{
private:
public:
    vector<vector<metric_box>> Metrix;
    vector<float> m1_thresholds;
    vector<float> m2_thresholds;
    string metric1_name;
    string metric2_name;
    int n_rows, n_cols;
    MetricMatrix(int n_rows, int n_cols)
    {
        this->n_rows = n_rows;
        this->n_cols = n_cols;
        this->m1_thresholds.resize(n_rows);
        this->m2_thresholds.resize(n_cols);
        vector<vector<metric_box>> temp(n_rows, vector<metric_box>(n_cols));
        this->Metrix = temp;
    };
    MetricMatrix(int n_rows, int n_cols, string metric1_name, string metric2_name) : MetricMatrix(n_rows, n_cols)
    {
        this->metric1_name = metric1_name;
        this->metric2_name = metric2_name;
    }
    void print()
    {
        cout << " *** MetricMatrix with " << this->n_rows << " " << this->metric1_name << "s & " << this->n_cols << " " << this->metric2_name << "s: " << endl;
        for (auto &&i : this->Metrix)
            for (auto &&j : i)
                j.print();
        cout << " ***" << endl;
    }
    metric_box find(float m1_val, float m2_val)
    {
        auto it = std::lower_bound(this->m1_thresholds.begin(), this->m1_thresholds.end(), m1_val);
        int row = it - this->m1_thresholds.begin() - 1;
        it = std::lower_bound(this->m2_thresholds.begin(), this->m2_thresholds.end(), m2_val);
        int col = it - this->m2_thresholds.begin() - 1;
        return this->Metrix[row][col];
    }
    ~MetricMatrix(){};
};
// ReplaceAll Usage:
//          cout << ReplaceAll(string("Number Of Beans"), string(" "), string("_")) << endl;
//          cout << ReplaceAll(string("ghghjghugtghty"), string("gh"), string("X")) << endl;
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
MetricMatrix MM_from_config_file(string metric1_name, string metric2_name,
                                 string metric1_thresholds_str,
                                 string metric2_thresholds_str)
{
    string m1ths = str_replace(metric1_thresholds_str, " ", "");
    vector<float> metric1_thresholds;
    metric1_thresholds.push_back(-999999);
    vector<float> metric2_thresholds;
    metric2_thresholds.push_back(-999999);
    stringstream ss1(m1ths);
    string token;
    while (getline(ss1, token, ','))
    {
        metric1_thresholds.push_back(stof(token));
    }
    string m2ths = str_replace(metric2_thresholds_str, " ", "");
    stringstream ss2(m2ths);
    while (getline(ss1, token, ','))
    {
        metric1_thresholds.push_back(stof(token));
    }
    while (getline(ss2, token, ','))
    {
        metric2_thresholds.push_back(stof(token));
    }
    for (size_t i = 0; i < metric1_thresholds.size() - 1; i++)
        if (metric1_thresholds[i] >= metric1_thresholds[i + 1])
            throw runtime_error("Xebel realtime error: Invalid threshold order for " + metric1_name);
    for (size_t i = 0; i < metric2_thresholds.size() - 1; i++)
        if (metric1_thresholds[i] >= metric1_thresholds[i + 1])
            throw runtime_error("Xebel realtime error: Invalid threshold order for " + metric2_name);
    int n_rows = metric1_thresholds.size();
    int n_cols = metric2_thresholds.size();
    // cout << "DBG|1" << endl;
    MetricMatrix MM = MetricMatrix(n_rows, n_cols, metric1_name, metric2_name);
    metric1_thresholds.push_back(999999);
    metric2_thresholds.push_back(999999);
    MM.m1_thresholds = metric1_thresholds;
    MM.m2_thresholds = metric2_thresholds;
    for (size_t i = 0; i < n_rows; i++)
    {
        for (size_t j = 0; j < n_cols; j++)
        {
            int row = i;
            int col = j;
            metric_range m1 = metric_range(metric1_name, MM.m1_thresholds[i + 1], MM.m1_thresholds[i]);
            metric_range m2 = metric_range(metric2_name, MM.m2_thresholds[j + 1], MM.m2_thresholds[j]);
            metric_box mb = metric_box(m1, m2, row, col);
            MM.Metrix[i][j] = mb;
        }
    }
    return MM;
}
int main()
{
    boost::property_tree::ptree pt;
    boost::property_tree::ini_parser::read_ini("config.ini", pt);
    string metric1_name = pt.get<string>("realtime.metric1_name");
    string metric1_thresholds_str = pt.get<string>("realtime.metric1_thresholds");
    string metric2_name = pt.get<string>("realtime.metric2_name");
    string metric2_thresholds_str = pt.get<string>("realtime.metric2_thresholds");
    MetricMatrix MM = MM_from_config_file(metric1_name, metric2_name, metric1_thresholds_str, metric2_thresholds_str);
    MM.print();
    float delay, bw;
    metric_box mb;
    delay = -0.025, bw = 3000;
    cout << "find " << delay << ", " << bw << " = ";
    MM.find(delay, bw).print();
    delay = 0.025, bw = 3000;
    cout << "find " << delay << ", " << bw << " = ";
    MM.find(delay, bw).print();
    delay = 0.025, bw = 10000;
    cout << "find " << delay << ", " << bw << " = ";
    MM.find(delay, bw).print();
    delay = 1, bw = 10000;
    cout << "find " << delay << ", " << bw << " = ";
    MM.find(delay, bw).print();
    delay = 1.1, bw = 10000;
    cout << "find " << delay << ", " << bw << " = ";
    MM.find(delay, bw).print();
    delay = 9, bw = 10001;
    cout << "find " << delay << ", " << bw << " = ";
    MM.find(delay, bw).print();
    return 0;
}