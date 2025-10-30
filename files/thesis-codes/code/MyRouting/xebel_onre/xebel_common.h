#ifndef XEBEL_CPP_ONLINE
#define XEBEL_CPP_ONLINE
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include "utils.h"
using namespace std;
/*--------------------------------------------------------------*/
#define N_METRICS 2
vector<int> Nodes;
function<void(string logstr)> common_logger;
class metric
{
private:
    void set_neutral_value()
    {
        if (this->operator_str == "min")
            this->neutral_val = this->max_theoric_val;
        if (this->operator_str == "max")
            this->neutral_val = this->min_theoric_val;
        if (this->operator_str == "add")
            this->neutral_val = 0;
        if (this->operator_str == "multiply")
            this->neutral_val = 1;
    }

public:
    string name;
    bool reverse;
    string optimum;
    float min_theoric_val;
    float max_theoric_val;
    float neutral_val;
    string operator_str;
    metric(string name, string optimum, string operator_str)
    {
        this->name = name;
        this->optimum = optimum;
        this->operator_str = operator_str;
        this->min_theoric_val = -999999999;
        this->max_theoric_val = +999999999;
        string opti = str_to_lower(this->optimum);
        this->reverse = opti == "maximum" || opti == "max";
        this->set_neutral_value();
    };
    metric(string name, string optimum, string operator_str, float min_theoric_val, float max_theoric_val) : metric(name, optimum, operator_str)
    {
        this->min_theoric_val = min_theoric_val;
        this->max_theoric_val = max_theoric_val;
    }
    ~metric(){};
    string to_str()
    {
        ostringstream oss;
        oss << "Metric " << this->name << ":: optimum: " << this->optimum << ", operation: " << this->operator_str;
        oss << ", in (" << this->min_theoric_val << ", " << this->max_theoric_val << ")";
        oss << endl;
        return oss.str();
    }
};
vector<metric *> Metrics;
class way
{
private:
    float metric_values[N_METRICS];
    bool locked = false;

public:
    int src, dst;
    bool is_path, is_edge, is_mid, is_midonly;
    string tuple_dashed, key, role = "way";
    vector<unsigned short> tuple;
    vector<way *> parents;
    map<string, string> OPTS;
    // string metric_keys[N_METRICS];
    way()
    {
        this->src = -1;
        this->dst = -1;
        this->is_path = false;
        this->is_edge = false;
        this->is_mid = false;
        this->is_midonly = false;
        this->tuple_dashed = "";
        this->key = "";
        for (size_t i = 0; i < N_METRICS; i++)
        {
            // this->metric_values[i] = 14;
            this->metric_values[i] = Metrics[i]->neutral_val;
        }
    }
    way(const string &tuple_dashed) : way()
    {
        this->tuple_dashed = tuple_dashed;
        this->tuple = parse_tuple_str_dashed(tuple_dashed);
        this->src = this->tuple[0];
        this->dst = this->tuple[this->tuple.size() - 1];
        this->is_edge = this->tuple.size() == 2;
        if (this->is_edge)
        {
            this->role = "edge";
        }
    }
    way(const string &tuple_dashed, bool is_path, bool is_mid, bool is_mid_only) : way(tuple_dashed)
    {
        this->is_path = is_path;
        this->is_mid = is_mid;
        this->is_midonly = is_mid_only;
        if (this->is_path && !this->is_edge)
            this->role = "path";
        if (is_mid_only)
            this->role = "mido";
    }
    way(const string &tuple_dashed, bool is_path, bool is_mid, bool is_mid_only, string key) : way(tuple_dashed, is_path, is_mid, is_mid_only)
    {
        this->key = key;
    }
    float get_metric_value(int metric_idx)
    {
        if (metric_idx < 0 || metric_idx >= N_METRICS)
        {
            cerr << "Error in get_metric_value: wrong metric index: " << metric_idx << endl;
            exit(-1);
        }
        while (this->locked)
            ;
        return this->metric_values[metric_idx];
    }
    void set_metric_value(int metric_idx, float value)
    {
        if (metric_idx < 0 || metric_idx >= N_METRICS)
        {
            cerr << "Error in get_metric_value: wrong metric index: " << metric_idx << endl;
            exit(-1);
        }
        while (this->locked)
            ;
        this->locked = true;
        this->metric_values[metric_idx] = value;
        this->locked = false;
    }
    vector<string> get_edge_keys()
    {
        vector<string> edges;
        for (size_t i = 0; i < this->tuple.size() - 1; i++)
        {
            ostringstream oss;
            oss << this->tuple[i] << "-" << this->tuple[i + 1];
            edges.push_back(oss.str());
        }
        return edges;
    }
    string to_str()
    {
        ostringstream oss;
        oss << this->role << "|";
        oss << this->tuple_dashed << "|";
        for (size_t i = 0; i < N_METRICS; i++)
        {
            oss << Metrics[i]->name << ": " << this->get_metric_value(i) << ", ";
        }
        if (this->OPTS.size() > 0)
        {
            oss << "opts: ";
            for (auto &&opt : this->OPTS)
            {
                oss << opt.first << "=" << opt.second << " ";
            }
        }
        oss << endl;
        return oss.str();
    }
    void print()
    {
        cout << this->to_str();
    }
    ~way(){};
};
map<string, way *> Ways;
class path
{
private:

public:
    int row = -1, col = -1;
    way *W;
    path(way *w)
    {
        this->W = w;
    }
    path(way *w, int row, int col) : path(w)
    {
        this->row = row;
        this->col = col;
    }
    string to_str()
    {
        ostringstream oss;
        oss << "row:" << this->row << ",col:" << this->col << "|" << this->W->to_str() ;
        return oss.str();
    }
};
map<string, path *> Paths;
class edge
{
private:
public:
    way *W;
    string metric_files[N_METRICS];
    edge(way *w)
    {
        this->W = w;
    }
    edge(way *w, string metric1_filename, string metric2_filename) : edge(w)
    {
        this->metric_files[0] = metric1_filename;
        this->metric_files[1] = metric2_filename;
    }
    int fetch_metric(int metric_idx)
    {
        float val;
        bool success = read_float_value_from_file(this->metric_files[metric_idx], &val);
        if (success)
        {
            this->W->set_metric_value(metric_idx, val);
            // Ways[this->W->tuple_dashed]->set_metric_value(metric_idx, val);
            return 0;
        }
        else
            return -1;
    }
    int fetch_metrics()
    {
        int fails = 0;
        for (size_t i = 0; i < N_METRICS; i++)
        {
            fails += this->fetch_metric(i);
        }
        if (fails < 0)
        {
            cerr << "fetch_metrics: failed to update metrics" << fails << endl;
        }
        return fails;
    }
    string to_str()
    {
        ostringstream oss;
        oss << this->W->to_str();
        for (size_t i = 0; i < N_METRICS; i++)
        {
            oss << "\t" << this->metric_files[i] << endl;
        }
        return oss.str();
    }
};
map<string, edge *> Edges;
float verify_way(way *w, float &way_value, float &total_edges_value)
{
    // returns error
    ostringstream oss;
    return 999999999;
}
int edges_updater()
{
    int errors = 0;
    for (auto &&elem : Edges)
    {
        edge *e = elem.second;
        errors += e->fetch_metrics();
    }
    return errors;
}
void edges_updater_thread(int sleep_MS, bool log)
{
    while (true)
    {
        start_timer();
        int errs = edges_updater();
        float duration = elapsed_time();
        if (log)
        {
            ostringstream oss;
            oss << "+ All edges updated in " << duration << " seconds, errors: " << abs(errs) << endl;
            common_logger(oss.str());
        }
        sleep_milliseconds(sleep_MS);
    }
}
void fill_nodes()
{
    vector_insert_if_not_exist(Nodes, 0);
    for (auto &&elem : Edges)
    {
        edge *p = elem.second;
        vector_insert_if_not_exist(Nodes, p->W->src);
        vector_insert_if_not_exist(Nodes, p->W->dst);
    }
}
#endif