#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <list>
#include <map>
#include <sstream>
#include <experimental/filesystem>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/ini_parser.hpp>
#include <algorithm>
#include <stdexcept>
#include <thread>
#include <cstring>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstdlib>
#include <ctime>
#include "memcache_utils.h"
#include "utils.h"
#include <functional>
using namespace std;

/* Globals */
function<void(string logstr)> logger;
string Metric1, Metric2;
map<string, string> CONF;
bool read_float_from_memcached(char *key, int keylen, float &value)
{
    memcached_return rc;
    size_t len;
    uint32_t flags = 0;
    char *res = memcached_get(mcd, key, keylen, &len, &flags, &rc);
    if (rc == MEMCACHED_SUCCESS)
    {
        memcpy(&value, res, len);
        free(res);
        return true;
    }
    else
    {
        // cout << "Error in read_float_from_memcached: cannot read key \"" << key << "\" from memcached." << endl;
        return false;
    }
}

/* Classes */
class path
{
private:
    vector<unsigned short> get_Tuple()
    {
        stringstream ss2(this->way);
        string number_str;
        vector<unsigned short> tuple;
        while (getline(ss2, number_str, '-'))
        {
            tuple.push_back(stoi(number_str));
        }
        return tuple;
    }

public:
    // data members
    string role = "-";
    string way = "-";
    vector<unsigned short> tuple;
    int src = -1, dst = -1;
    char metric1_key[50] = "";
    int metric1_key_len = -1, metric2_key_len = -1;
    char metric2_key[50] = "";
    float m1_value = -1, m2_value = -1;
    int row = -1, col = -1;
    path *next = nullptr;
    path *prev = nullptr;
    path(string role, string way, string mkey_str)
    {
        this->role = role;
        this->way = way;
        char metric[10];
        int src, dst;
        char hash[10];
        sscanf(mkey_str.c_str(), "%[^_]_%d_%d_%s", metric, &src, &dst, hash);
        this->tuple = this->get_Tuple();
        this->src = src;
        this->dst = dst;
        if (string(metric) == Metric1)
        {
            strcpy(this->metric1_key, mkey_str.c_str());
            this->metric1_key_len = mkey_str.length();
        }
        else if (string(metric) == Metric2)
        {
            strcpy(this->metric2_key, mkey_str.c_str());
            this->metric2_key_len = mkey_str.length();
        }
        else
        {
            throw runtime_error("Xebel realtime error: metric name:" + string(metric));
        }
    }
    string to_str()
    {
        char str[500];
        sprintf(str, "%s|%s|%s=%f|%s=%f|r%d,c%d", this->role.c_str(), this->way.c_str(),
                this->metric1_key, this->m1_value,
                this->metric2_key, this->m2_value,
                this->row, this->col);
        return str;
    }
    void print()
    {
        cout << this->to_str();
        // cout << "role " << this->role;
        // cout << ", tup ";
        // for (auto x : this->tuple)
        //     cout << x << ",";
        // cout << " key " << this->metric1_key;
        // cout << ", " << Metric1 << " " << this->m1_value;
        // cout << ", " << Metric2 << " " << this->m2_value;
        // cout << endl;
    }
    bool metric1_update()
    {
        bool stat = read_float_from_memcached(this->metric1_key, this->metric1_key_len, this->m1_value);
        return stat;
    }
    bool metric2_update()
    {
        bool stat = read_float_from_memcached(this->metric2_key, this->metric2_key_len, this->m2_value);
        return stat;
    }
};
map<string, path *> Paths;
int N_NODES;
class metric_range
{
public:
    float low;
    float high;
    string name;
    // string optimum;
    // bool reverse;
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
    // string name;
    int row, col;
    metric_range m1;
    metric_range m2;
    list<path *> paths;
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
    string to_str()
    {
        char str[1000];
        sprintf(str, "box [%d, %d]: %s(%f, %f) %s(%f, %f) paths %d\n", this->row, this->col,
                this->m1.name.c_str(), this->m1.low, this->m1.high,
                this->m2.name.c_str(), this->m2.low, this->m2.high,
                int(this->paths.size()));
        return string(str);
    }
    void print()
    {
        // cout << this->m1.name << " " << this->row << ": (" << this->m1.value_min << ", " << this->m1.value_max << ") | ";
        // cout << this->m2.name << " " << this->col << ": (" << this->m2.value_min << ", " << this->m2.value_max << ")" << endl;
        // cout << "[" << this->row << ", " << this->col << "]: " << this->m1.value_min << " < " << this->m1.name << " <= " << this->m1.value_max;
        // cout << " & " << this->m2.value_min << " < " << this->m2.name << " <= " << this->m2.value_max << endl;
        cout << this->to_str();
    }
    string paths_to_str()
    {
        char str[2000] = "";
        for (auto &&p : this->paths)
        {
            sprintf(str + strlen(str), "\t%s\n", p->to_str().c_str());
        }
    }
    ~metric_box(){};
};
path *retrieve_path(metric_box *m)
{
    m->print();
    if (m->paths.size() > 0)
    {
        path *first = m->paths.front();
        // Move the first element to the end of the list
        m->paths.pop_front();
        m->paths.push_back(first);
        return first;
    }
    return nullptr;
}
path *traverse_to_00(vector<vector<metric_box>> **Metrixes, int n_rows, int n_cols, int src, int dst, int I, int J)
{

    path *p;
    for (int k = 0; k <= I + J; k++)
        for (int i = I, j = J - k; i >= 0 && j <= J; i--, j++)
        {
            if (j < 0)
                continue;
            p = retrieve_path(&(Metrixes[src][dst])[i][j]);
            if (p)
                return p;
        }
    return nullptr;
}
path *traverse_to_M0(vector<vector<metric_box>> **Metrixes, int n_rows, int n_cols, int src, int dst, int I, int J)
{
    path *p;
    for (int k = 0; k <= (n_rows - 1 - I) + J; k++)
        for (int i = I, j = J - k; i <= n_rows && j <= J; i++, j++)
        {
            if (i > n_rows - 1 || j < 0)
                continue;
            p = retrieve_path(&(Metrixes[src][dst])[i][j]);
            if (p)
                return p;
        }
    return nullptr;
}
path *traverse_to_0N(vector<vector<metric_box>> **Metrixes, int n_rows, int n_cols, int src, int dst, int I, int J)
{
    path *p;
    for (int k = 0; k <= I + (n_cols - 1 - J); k++)
        for (int i = I, j = J + k; i >= 0 && j >= J; i--, j--)
        {
            if (i < 0 || j > n_cols - 1)
                continue;
            p = retrieve_path(&(Metrixes[src][dst])[i][j]);
            if (p)
                return p;
        }
    return nullptr;
}
path *traverse_to_MN(vector<vector<metric_box>> **Metrixes, int n_rows, int n_cols, int src, int dst, int I, int J)
{
    path *p;
    for (int k = 0; k <= (n_rows - 1 - I) + (n_cols - 1 - J); k++)
        for (int i = I, j = J + k; i <= n_rows && j >= J; i++, j--)
        {
            if (i > n_rows - 1 || j > n_cols - 1)
                continue;
            p = retrieve_path(&(Metrixes[src][dst])[i][j]);
            if (p)
                return p;
        }
    return nullptr;
}
class MetricMatrix
{
private:
public:
    // vector<vector<metric_box>> Metrix;
    vector<vector<metric_box>> **Metrixes;
    vector<float> m1_thresholds;
    vector<float> m2_thresholds;
    string metric1_name;
    string metric2_name;
    bool metric1_reverse;
    bool metric2_reverse;
    int n_rows, n_cols, n_nodes;
    // path *(*traverse)(int, int);
    function<path *(int src, int dst, int M1, int M2)> traverse;
    // std::function<path *(int, int, int, int)> traverse;
    MetricMatrix(int n_rows, int n_cols, int n_nodes)
    {
        this->n_rows = n_rows;
        this->n_cols = n_cols;
        this->n_nodes = n_nodes;
        this->m1_thresholds.resize(n_rows);
        this->m2_thresholds.resize(n_cols);
        // vector<vector<metric_box>> temp(n_rows, vector<metric_box>(n_cols));
        // this->Metrix = temp;
        this->Metrixes = new vector<vector<metric_box>> *[n_nodes];
        for (size_t i = 0; i < n_nodes; i++)
        {
            this->Metrixes[i] = new vector<vector<metric_box>>[n_nodes];
            for (size_t j = 0; j < n_nodes; j++)
            {
                vector<vector<metric_box>> temp(n_rows, vector<metric_box>(n_cols));
                this->Metrixes[i][j] = temp;
            }
        }
    };
    MetricMatrix(int n_rows, int n_cols, int n_nodes,
                 string metric1_name, string metric2_name,
                 bool metric1_reverse, bool metric2_reverse) : MetricMatrix(n_rows, n_cols, n_nodes)
    {
        this->metric1_name = metric1_name;
        this->metric2_name = metric2_name;
        this->metric1_reverse = metric1_reverse;
        this->metric2_reverse = metric2_reverse;
        if (metric1_reverse && metric2_reverse)
            this->traverse = bind(traverse_to_MN, this->Metrixes, this->n_rows, this->n_cols, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
        else if (metric1_reverse)
            this->traverse = bind(traverse_to_M0, this->Metrixes, this->n_rows, this->n_cols, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
        else if (metric2_reverse)
            this->traverse = bind(traverse_to_0N, this->Metrixes, this->n_rows, this->n_cols, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
        else
            this->traverse = bind(traverse_to_00, this->Metrixes, this->n_rows, this->n_cols, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
    }
    void print()
    {
        cout << " *** MetricMatrix with " << this->n_rows << " " << this->metric1_name << "s & " << this->n_cols << " " << this->metric2_name << "s: " << endl;
        for (auto &&i : this->Metrixes[0][0])
            for (auto &&j : i)
                j.print();
        cout << " ***" << endl;
    }
    metric_box *find(int src, int dst, float m1_val, float m2_val)
    {
        auto it = lower_bound(this->m1_thresholds.begin(), this->m1_thresholds.end(), m1_val);
        int row = it - this->m1_thresholds.begin() - 1;
        it = lower_bound(this->m2_thresholds.begin(), this->m2_thresholds.end(), m2_val);
        int col = it - this->m2_thresholds.begin() - 1;
        return &(this->Metrixes[src][dst])[row][col];
    }
    ~MetricMatrix(){};
};
MetricMatrix *MM;
// class Source_Dest{
// public:
//     MetricMatrix * MM;
//     map<string, path *> Paths;
//     int src, dst;
//     Source_Dest(int src, int dst){
//         this->src = src;
//         this->dst = dst;
//     }
//     Source_Dest(int src, int dst, MetricMatrix * M, map<string, path *> P) : Source_Dest(src, dst) {
//         this->MM = M;
//         this->Paths = P;
//     }
// };
// map<vector<int, vector<int>>, Source_Dest*> SrcDsts;

/* Functions */
void read_xon_file(string filename)
{
    // map<string, path> Paths;
    ifstream file(filename);
    if (!file.is_open())
    {
        cerr << "Error: cannot open the file" << endl;
        return;
    }
    // read each line from the file
    string line_raw;
    int max_node_id = -1;
    while (getline(file, line_raw))
    {
        string line = remove_spaces(line_raw);
        if (line.empty())
            continue;
        if (line[0] == '#')
            continue;
        // split the line into tokens using '|' as the delimiter
        vector<string> tokens;
        stringstream ss(line);
        string token;
        while (getline(ss, token, '|'))
        {
            tokens.push_back(token);
        }
        string role = tokens[0];
        string way = tokens[1];
        string mkey = tokens[2];
        path *p;
        auto it = Paths.find(way); // find the key in the map
        if (it != Paths.end())
        {
            p = it->second; // get the value
            char metric[10];
            int src, dst;
            char hash[10];
            sscanf(mkey.c_str(), "%[^_]_%d_%d_%s", metric, &src, &dst, hash);
            if (string(metric) == Metric1)
            {
                strcpy(p->metric1_key, mkey.c_str());
                p->metric1_key_len = mkey.length();
            }
            else if (string(metric) == Metric2)
            {
                strcpy(p->metric2_key, mkey.c_str());
                p->metric2_key_len = mkey.length();
            }
            else
            {
                throw runtime_error("Xebel realtime error: metric name:" + string(metric));
            }
        }
        else
        {
            p = new path(role, way, mkey);
            Paths[way] = p; // insert the new entry in the map
        }
        max_node_id = max(max_node_id, p->src);
        max_node_id = max(max_node_id, p->dst);
    }
    N_NODES = max_node_id + 1;
    file.close();
    // return paths;
}
void read_config_file(string filename)
{
    boost::property_tree::ptree pt;
    boost::property_tree::ini_parser::read_ini(filename, pt);
    // map<string, string> CONF;
    CONF["metric1_name"] = pt.get<string>("realtime.metric1_name");
    CONF["metric2_name"] = pt.get<string>("realtime.metric2_name");
    CONF["metric1_thresholds"] = pt.get<string>("realtime.metric1_thresholds");
    CONF["metric2_thresholds"] = pt.get<string>("realtime.metric2_thresholds");
    CONF["metric1_optimum"] = pt.get<string>("realtime.metric1_optimum");
    CONF["metric2_optimum"] = pt.get<string>("realtime.metric2_optimum");
    CONF["nodes_cache_keys_file"] = pt.get<string>("online.nodes_cache_keys_file");
    CONF["memcached_ip"] = pt.get<string>("realtime.memcached_ip");
    CONF["memcached_port"] = pt.get<string>("realtime.memcached_port");
    CONF["xerclient_speak_port"] = pt.get<string>("realtime.xerclient_speak_port");
    CONF["xerclient_speak_port"] = pt.get<string>("realtime.xerclient_speak_port");
    CONF["log_file"] = pt.get<string>("realtime.log_file");
    CONF["log_dir"] = pt.get<string>("realtime.log_dir");

    // return CONF;
}
MetricMatrix *MM_from_config_file(string metric1_name, string metric2_name,
                                  string metric1_thresholds_str,
                                  string metric2_thresholds_str,
                                  bool metric1_reverse,
                                  bool metric2_reverse)
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
    // // cout << "DBG|1" << endl;
    MM = new MetricMatrix(n_rows, n_cols, N_NODES, metric1_name, metric2_name, metric1_reverse, metric2_reverse);
    metric1_thresholds.push_back(999999);
    metric2_thresholds.push_back(999999);
    MM->m1_thresholds = metric1_thresholds;
    MM->m2_thresholds = metric2_thresholds;
    for (size_t i = 0; i < n_rows; i++)
    {
        for (size_t j = 0; j < n_cols; j++)
        {
            int row = i;
            int col = j;
            metric_range m1 = metric_range(metric1_name, MM->m1_thresholds[i + 1], MM->m1_thresholds[i]);
            metric_range m2 = metric_range(metric2_name, MM->m2_thresholds[j + 1], MM->m2_thresholds[j]);
            // metric_box mb = metric_box(m1, m2, row, col);
            // MM->Metrix[i][j] = mb;
            for (size_t src = 0; src < MM->n_nodes; src++)
            {
                for (size_t dst = 0; dst < MM->n_nodes; dst++)
                {
                    (MM->Metrixes[src][dst])[i][j] = metric_box(m1, m2, row, col);
                }
            }
        }
    }
}
/* Threads */
void xero_fill(int SleepSecs)
{
    // Update all paths values.
    bool stat1 = false, stat2 = false;
    int n1, n2;
    float sum_metric1, sum_metric2;
    int errors = 0;
    int iter = 0;
    time_t start, end;
    while (true)
    {
        n1 = 0;
        n2 = 0;
        sum_metric1 = 0;
        sum_metric2 = 0;
        iter++;
        time(&start);
        for (const auto &entry : Paths)
        {
            path *P = entry.second;
            stat1 = P->metric1_update();
            stat2 = P->metric2_update();
            if (!stat1 || !stat2)
            {
                errors++;
                cerr << "  -err xero_fill: " << P->to_str() << endl;
            }
            if (stat1)
            {
                n1++;
                sum_metric1 += P->m1_value;
            }
            if (stat2)
            {
                n2++;
                sum_metric2 += P->m2_value;
            }

            metric_box *mb = MM->find(P->src, P->dst, P->m1_value, P->m2_value);

            if (mb->row != P->row || mb->col != P->col)
            {
                if (P->col >= 0 && P->row >= 0)
                    (MM->Metrixes[P->src][P->dst])[P->row][P->col].paths.remove(P);
                P->row = mb->row;
                P->col = mb->col;
                mb->paths.push_back(P);
            }
            // printf("DBG786| %s \n mbox: %s\n", P->to_str().c_str(), mb->to_str().c_str());
        }
        time(&end);
        double time_taken = double(end - start);
        char report[2000];
        sprintf(report, "  + xero_fill %d) errors: %d, time: %f, #%s:%d avg %f, #%s:%d avg %f",
                iter, errors, time_taken, Metric1.c_str(), n1, sum_metric1 / n1, Metric2.c_str(), n2, sum_metric2 / n2);
        // cout << "  + xero_fill iter " << iter << " done. errors: " << errors << " in " << time_taken << " seconds" << endl;
        // cout << "    + average " << n1 << " " << Metric1 << ": " << sum_metric1 / n1 << ", average " << n2 << " " << Metric2 << ": " << sum_metric2 / n2 << endl;
        logger(report);
        errors = 0;
        this_thread::sleep_for(chrono::seconds(SleepSecs));
    }
}
void xero_route(int speak_PORT = 1369)
{
    int sock = socket(AF_INET, SOCK_STREAM, 0); // create a TCP socket
    if (sock == -1)
    {
        cerr << "Error creating socket" << endl;
        return;
    }
    int port = speak_PORT;
    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port); // use a different port number
    addr.sin_addr.s_addr = INADDR_ANY;
    if (bind(sock, (struct sockaddr *)&addr, sizeof(addr)) == -1)
    {
        cerr << "Error binding socket" << endl;
        return;
    }
    else
    {
        cout << "binding socket successfully to " << port << endl;
    }
    vector<string> words;
    while (true)
    {
        // this_thread::sleep_for(chrono::seconds(1));
        char buffer[1024] = "";
        listen(sock, 1);
        struct sockaddr_in src;
        socklen_t len = sizeof(src);
        // cout << "xeroR 2 " << endl;
        int clientSock = accept(sock, (struct sockaddr *)&src, &len);
        int bytes = recv(clientSock, buffer, 1024, 0);
        if (bytes == -1)
        {
            cerr << "Error receiving from socket" << endl;
            continue;
        }
        // cout << "DBG|xero_r start: " << endl;
        // Convert the request to a string
        string request(buffer, bytes);
        string response = "";
        cout << "Received request: " << request << endl;
        words = split(request, " ");
        if (words.size() == 0)
        {
            cerr << "Invalid request format" << endl;
        }
        else if (words[0] == "get-metrix")
        {
            response = "";
            if (words.size() < 3)
            {
                response = "malformed command\n";
            }
            else
                try
                {
                    int src = atoi(words.at(1).c_str());
                    int dst = atoi(words.at(2).c_str());
                    for (int i = 0; i < MM->n_rows; i++)
                    {
                        for (size_t j = 0; j < MM->n_cols; j++)
                        {
                            response += (MM->Metrixes[src][dst])[i][j].to_str();
                        }
                    }
                }
                catch (const std::exception &e)
                {
                    std::cerr << "MostafaError: " << e.what() << '\n';
                }
        }
        else if (words[0] == "get-metrix-paths")
        {
            response = "aleyke salam. Use \'get-mbox-paths <i> <j>\' instead!";
        }
        else if (words[0] == "get-mbox")
        {
            response = "aleyke " + words[0];
            if (words.size() < 5)
            {
                response = "malformed command\n";
            }
            else
                try
                {
                    int src = atoi(words[1].c_str());
                    int dst = atoi(words[2].c_str());
                    int i = atoi(words[3].c_str());
                    int j = atoi(words[4].c_str());
                    metric_box *mb = &(MM->Metrixes[src][dst])[i][j];
                    response = mb->to_str();
                }
                catch (const std::exception &e)
                {
                    std::cerr << e.what() << '\n';
                }
        }
        else if (words[0] == "get-mbox-paths")
        {
            response = "";
            if (words.size() < 5)
            {
                response = "malformed command\n";
            }
            else
                try
                {
                    int src = atoi(words[1].c_str());
                    int dst = atoi(words[2].c_str());
                    int i = atoi(words[3].c_str());
                    int j = atoi(words[4].c_str());
                    metric_box *mb = &(MM->Metrixes[src][dst])[i][j];
                    response = mb->to_str();
                    for (auto &&P : mb->paths)
                    {
                        response += "\n\t" + P->to_str();
                    }
                }
                catch (const std::exception &e)
                {
                    std::cerr << e.what() << '\n';
                }
        }
        else if (words[0] == "traverse")
        {
            response = "";
            if (words.size() < 5)
            {
                response = "malformed command\n";
            }
            else
                try
                {
                    int src = atoi(words[1].c_str());
                    int dst = atoi(words[2].c_str());
                    int i = atoi(words[3].c_str());
                    int j = atoi(words[4].c_str());
                    path *p = MM->traverse(src, dst, i, j);
                    if (p)
                    {
                        response = p->to_str();
                    }
                    else
                    {
                        response = "NoPath";
                    }
                }
                catch (const std::exception &e)
                {
                    std::cerr << e.what() << '\n';
                }
        }
        else
        {
            cerr << "Invalid request format" << endl;
            response = ":( aleyke " + words[0];
        }
        // Print the response
        int n = send(clientSock, response.c_str(), response.size(), 0);
        cout << "    " << n << " bytes responded: " << response << endl;
        close(clientSock);
    }
    close(sock);
}
/* Main */
int main(int argc, char **argv)
{
    experimental::filesystem::path current = experimental::filesystem::current_path();
    current /= "xebel.conf";
    string configfile;
    if (experimental::filesystem::exists(current))
        configfile = current.c_str();
    else
    {
        experimental::filesystem::path root = "/root/configs/xebel.conf";
        if (experimental::filesystem::exists(root))
            configfile = root.c_str();
        else
        {
            cerr << "no xebel.conf found at " << current.c_str() << " nor " << root.c_str() << endl;
            exit(-1);
        }
    }
    // m.salari: Deleteme

    //\ m.salari
    read_config_file(configfile);
    string metric1_name = CONF["metric1_name"];
    string metric2_name = CONF["metric2_name"];
    string metric1_thresholds_str = CONF["metric1_thresholds"];
    string metric2_thresholds_str = CONF["metric2_thresholds"];
    bool metric1_reverse = str_to_lower(CONF["metric1_optimum"]) == "max" ? true : false;
    bool metric2_reverse = str_to_lower(CONF["metric2_optimum"]) == "max" ? true : false;
    string nodes_file = CONF["nodes_cache_keys_file"];
    string memcached_ip = CONF["memcached_ip"];
    int memcached_port = atoi(CONF["memcached_port"].c_str());
    int xerclient_speak_port = atoi(CONF["xerclient_speak_port"].c_str());
    int xero_fill_sleep_ms = atoi(CONF["xero_fill_sleep_ms"].c_str());
    Metric1 = metric1_name;
    Metric2 = metric2_name;
    string log_file = CONF["log_file"];
    string log_dir = CONF["log_dir"];
    // Preparation *****************************
    make_dirs_and_file(log_file);
    logger = std::bind(append_to_file, log_file, false, std::placeholders::_1);
    // auto logger_time = std::bind(append_to_file, log_file, true, std::placeholders::_1);
    logger("Xebel realtime start ");
    // Read Xon record file: **********************************
    read_xon_file(nodes_file);
    if (Paths.empty())
    {
        cout << "Error. No path is provided!!!" << endl;
        return -1;
    }
    else
        cout << "Total " << Paths.size() << " paths loaded from " << nodes_file << endl;
    // Create Metric Matrix: **********************************
    MM_from_config_file(metric1_name, metric2_name, metric1_thresholds_str, metric2_thresholds_str, metric1_reverse, metric2_reverse);
    cout << "MetricMatrix " << MM->n_rows << "x" << MM->n_cols << " created!" << endl;
    MM->print();
    // Initial read from memcached:  **********************************
    mcd_connect(memcached_ip, memcached_port);
    int counter = 0;
    int errors = 0;
    float sum_metric1 = 0;
    float sum_metric2 = 0;
    int n1 = 0;
    int n2 = 0;
    bool stat1 = false, stat2 = false;
    for (const auto &P : Paths)
    {
        path *p = P.second; // get the value
        stat1 = p->metric1_update();
        stat2 = p->metric2_update();
        counter++;
        if (!stat1 || !stat2)
        {
            errors++;
            cout << "- err read path: " << p->to_str() << endl;
        }
        if (stat1)
        {
            n1++;
            sum_metric1 += p->m1_value;
        }
        if (stat2)
        {
            n2++;
            sum_metric2 += p->m2_value;
        }
        if (counter % 1000 == 0)
        {
            cout << counter << " path updates " << errors << " failures." << endl;
        }
    }
    cout << "average of " << n1 << " " << Metric1 << ": " << sum_metric1 / n1 << ", average of " << n2 << " " << Metric2 << ": " << sum_metric2 / n2 << endl;
    // Create reader & writer threads: **********************************
    cout << "C++ version: " << __cplusplus << "\n";
    thread t1(xero_fill, xero_fill_sleep_ms);
    thread t2(xero_route, xerclient_speak_port);
    // Wait for the threads to finish
    cout << "Logfile: " << log_file << endl;
    t1.join();
    t2.join();
    mcd_shutdown();
    return 0;
}
