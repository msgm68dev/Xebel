#ifndef XEBEL_CPP_REALTIME
#define XEBEL_CPP_REALTIME
#include <iostream>
#include <string>
#include <vector>
#include <list>
#include "utils.h"
#include "xebel_common.h"
using namespace std;
class metric_range
{
private:
public:
    metric *M;
    float low, high;
    metric_range(metric *M, float low, float high)
    {
        this->M = M;
        this->low = low;
        this->high = high;
    }
    ~metric_range(){};
};

class metric_box
{
private:
public:
    int row, col;
    metric_range *mr1;
    metric_range *mr2;
    list<path *> paths;
    metric_box() {}
    metric_box(metric_range *mr1, metric_range *mr2)
    {
        this->mr1 = mr1;
        this->mr2 = mr2;
    };
    metric_box(metric_range *mr1, metric_range *mr2, int row, int col) : metric_box(mr1, mr2)
    {
        this->row = row;
        this->col = col;
    }
    ~metric_box(){};
    string to_str()
    {
        ostringstream oss;
        oss << "mbox [" << this->row << ", " << this->col << "]: ";
        oss << this->mr1->M->name << " (" << this->mr1->low << ", " << this->mr1->high << ") ";
        oss << this->mr2->M->name << " (" << this->mr2->low << ", " << this->mr2->high << ")";
        oss << "#paths: " << this->paths.size() << endl;
        return oss.str();
    }
    void print()
    {
        cout << this->to_str();
    }
};
path *retrieve_path(metric_box *m)
{
    // m->print();
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
path *tr_worstfirst_diagonal(vector<vector<metric_box>> **Metrixes, int n_rows, int n_cols, int src, int dst, int I, int J)
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
path *tr_worstfirst_diagonal_m1_reverse(vector<vector<metric_box>> **Metrixes, int n_rows, int n_cols, int src, int dst, int I, int J)
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
path *tr_worstfirst_diagonal_m2_reverse(vector<vector<metric_box>> **Metrixes, int n_rows, int n_cols, int src, int dst, int I, int J)
{
    path *p;
    for (int k = 0; k <= I + (n_cols - 1 - J); k++)
    {

        for (int i = I, j = J + k; i >= 0 && j >= J; i--, j--)
        {
            if (i < 0 || j > n_cols - 1)
                continue;
            p = retrieve_path(&(Metrixes[src][dst])[i][j]);
            if (p)
                return p;
        }
    }
    return nullptr;
}
path *tr_worstfirst_diagonal_m1_m2_reverse(vector<vector<metric_box>> **Metrixes, int n_rows, int n_cols, int src, int dst, int I, int J)
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
path *tr_bestfirst_simple(vector<vector<metric_box>> **Metrixes, int n_rows, int n_cols, int src, int dst, int I, int J)
{
    int m1_low = 0;
    int m1_high = I;
    int m2_low = 0;
    int m2_high = J;
    path *p;
    for (size_t i = m1_low; i <= m1_high; i++)
    {
        for (size_t j = m2_low; j <= m2_high; j++)
        {
            p = retrieve_path(&(Metrixes[src][dst])[i][j]);
            if (p)
                return p;
        }
    }
    return nullptr;
}
path *tr_bestfirst_simple_m1_reverse(vector<vector<metric_box>> **Metrixes, int n_rows, int n_cols, int src, int dst, int I, int J)
{
    int m1_low = I;
    int m1_high = n_rows - 1;
    int m2_low = 0;
    int m2_high = J;
    path *p;
    for (size_t i = m1_low; i <= m1_high; i++)
    {
        for (size_t j = m2_low; j <= m2_high; j++)
        {
            p = retrieve_path(&(Metrixes[src][dst])[i][j]);
            if (p)
                return p;
        }
    }
    return nullptr;
}
path *tr_bestfirst_simple_m2_reverse(vector<vector<metric_box>> **Metrixes, int n_rows, int n_cols, int src, int dst, int I, int J)
{
    int m1_low = 0;
    int m1_high = I;
    int m2_low = J;
    int m2_high = n_cols - 1;
    path *p;
    for (size_t i = m1_low; i <= m1_high; i++)
    {
        for (size_t j = m2_low; j <= m2_high; j++)
        {
            p = retrieve_path(&(Metrixes[src][dst])[i][j]);
            if (p)
                return p;
        }
    }
    return nullptr;
}
path *tr_bestfirst_simple_m1_m2_reverse(vector<vector<metric_box>> **Metrixes, int n_rows, int n_cols, int src, int dst, int I, int J)
{
    int m1_low = I;
    int m1_high = n_rows - 1;
    int m2_low = J;
    int m2_high = n_cols - 1;
    path *p;
    for (size_t i = m1_low; i <= m1_high; i++)
    {
        for (size_t j = m2_low; j <= m2_high; j++)
        {
            p = retrieve_path(&(Metrixes[src][dst])[i][j]);
            if (p)
                return p;
        }
    }
    return nullptr;
}
path *tr_bestfirst_diagonal(vector<vector<metric_box>> **Metrixes, int n_rows, int n_cols, int src, int dst, int I, int J)
{

    path *p;
    for (int k = I + J; k >= 0; k--)
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
path *tr_bestfirst_diagonal_m1_reverse(vector<vector<metric_box>> **Metrixes, int n_rows, int n_cols, int src, int dst, int I, int J)
{
    path *p;
    for (int k = (n_rows - 1 - I) + J; k >= 0 ; k--)
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
path *tr_bestfirst_diagonal_m2_reverse(vector<vector<metric_box>> **Metrixes, int n_rows, int n_cols, int src, int dst, int I, int J)
{
    path *p;
    for (int k = I + (n_cols - 1 - J); k >= 0 ; k--)
    {

        for (int i = I, j = J + k; i >= 0 && j >= J; i--, j--)
        {
            if (i < 0 || j > n_cols - 1)
                continue;
            p = retrieve_path(&(Metrixes[src][dst])[i][j]);
            if (p)
                return p;
        }
    }
    return nullptr;
}
path *tr_bestfirst_diagonal_m1_m2_reverse(vector<vector<metric_box>> **Metrixes, int n_rows, int n_cols, int src, int dst, int I, int J)
{
    path *p;
    for (int k = (n_rows - 1 - I) + (n_cols - 1 - J); k >= 0; k--)
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
    string log_file;

public:
    function<void(string logstr)> logger;
    vector<vector<metric_box>> **Metrixes;
    vector<float> m1_thresholds;
    vector<float> m2_thresholds;
    string metric1_name;
    string metric2_name;
    bool metric1_reverse;
    bool metric2_reverse;
    bool from_best_traverse;
    int n_rows, n_cols, n_nodes;
    function<path *(int src, int dst, int M1, int M2)> traverse;
    MetricMatrix(metric *metric1, metric *metric2,
                 string metric1_thresholds_str,
                 string metric2_thresholds_str,
                 string log_dir,
                 bool from_best_traverse = true)
    {
        // cout << "dbg|1-MetricMatrix" << endl;
        this->from_best_traverse = from_best_traverse;
        string m1ths = str_replace(metric1_thresholds_str, " ", "");
        vector<float> metric1_thresholds;
        metric1_thresholds.push_back(metric1->min_theoric_val);
        vector<float> metric2_thresholds;
        metric2_thresholds.push_back(metric2->min_theoric_val);
        stringstream ss1(m1ths);
        string token;
        // cout << "dbg|2-MetricMatrix" << endl;
        while (getline(ss1, token, ','))
        {
            metric1_thresholds.push_back(stof(token));
        }
        // cout << "dbg|3-MetricMatrix" << endl;
        string m2ths = str_replace(metric2_thresholds_str, " ", "");
        stringstream ss2(m2ths);
        while (getline(ss1, token, ','))
        {
            metric1_thresholds.push_back(stof(token));
        }
        // cout << "dbg|4-MetricMatrix" << endl;
        while (getline(ss2, token, ','))
        {
            metric2_thresholds.push_back(stof(token));
        }
        for (size_t i = 0; i < metric1_thresholds.size() - 1; i++)
            if (metric1_thresholds[i] >= metric1_thresholds[i + 1])
                throw runtime_error("Xebel realtime error: Invalid threshold order for " + metric1->name);
        for (size_t i = 0; i < metric2_thresholds.size() - 1; i++)
            if (metric1_thresholds[i] >= metric1_thresholds[i + 1])
                throw runtime_error("Xebel realtime error: Invalid threshold order for " + metric2->name);
        int n_rows = metric1_thresholds.size();
        int n_cols = metric2_thresholds.size();

        // MetricMatrix(n_rows, n_cols, Nodes.size(), metric1, metric2, log_dir);
        this->n_rows = n_rows;
        this->n_cols = n_cols;
        int n_nodes = Nodes.size();
        this->n_nodes = n_nodes;
        this->m1_thresholds.resize(n_rows);
        this->m2_thresholds.resize(n_cols);
        this->Metrixes = new vector<vector<metric_box>> *[n_nodes];
        for (size_t i = 0; i < n_nodes; i++)
        {
            this->Metrixes[i] = new vector<vector<metric_box>>[n_nodes];
            for (size_t j = 0; j < n_nodes; j++)
            {
                vector<vector<metric_box>> temp(n_rows, vector<metric_box>(n_cols));
                this->Metrixes[i][j] = temp;
                // // cout << "dbg| Metrixes[" << i << "][" << j << "] = "
                //                      << "vector " << temp.size() << "*" << temp[0].size() << endl;
            }
        }
        this->metric1_name = metric1->name;
        this->metric2_name = metric2->name;
        this->metric1_reverse = metric1->reverse;
        this->metric2_reverse = metric2->reverse;
        if (this->from_best_traverse)
        {
            if (this->metric1_reverse && this->metric2_reverse)
                // this->traverse = bind(tr_bestfirst_simple_m1_m2_reverse, this->Metrixes, this->n_rows, this->n_cols, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
                this->traverse = bind(tr_bestfirst_diagonal_m1_m2_reverse, this->Metrixes, this->n_rows, this->n_cols, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
            else if (this->metric1_reverse)
                // this->traverse = bind(tr_bestfirst_simple_m1_reverse, this->Metrixes, this->n_rows, this->n_cols, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
                this->traverse = bind(tr_bestfirst_diagonal_m1_reverse, this->Metrixes, this->n_rows, this->n_cols, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
            else if (this->metric2_reverse)
                // this->traverse = bind(tr_bestfirst_simple_m2_reverse, this->Metrixes, this->n_rows, this->n_cols, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
                this->traverse = bind(tr_bestfirst_diagonal_m2_reverse, this->Metrixes, this->n_rows, this->n_cols, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
            else
                // this->traverse = bind(tr_bestfirst_simple, this->Metrixes, this->n_rows, this->n_cols, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
                this->traverse = bind(tr_bestfirst_diagonal, this->Metrixes, this->n_rows, this->n_cols, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
        }
        else
        {
            if (this->metric1_reverse && this->metric2_reverse)
                this->traverse = bind(tr_worstfirst_diagonal_m1_m2_reverse, this->Metrixes, this->n_rows, this->n_cols, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
            else if (this->metric1_reverse)
                this->traverse = bind(tr_worstfirst_diagonal_m1_reverse, this->Metrixes, this->n_rows, this->n_cols, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
            else if (this->metric2_reverse)
                this->traverse = bind(tr_worstfirst_diagonal_m2_reverse, this->Metrixes, this->n_rows, this->n_cols, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
            else
                this->traverse = bind(tr_worstfirst_diagonal, this->Metrixes, this->n_rows, this->n_cols, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
        }

        this->log_file = join_paths(log_dir, "xebel_re.log");
        make_dirs_and_file(this->log_file);
        this->logger = bind(append_to_file, log_file, false, std::placeholders::_1);

        // cout << "dbg|6-MetricMatrix created" << endl;

        metric1_thresholds.push_back(metric1->max_theoric_val);
        metric2_thresholds.push_back(metric2->max_theoric_val);
        this->m1_thresholds = metric1_thresholds;
        this->m2_thresholds = metric2_thresholds;
        for (size_t i = 0; i < n_rows; i++)
        {
            for (size_t j = 0; j < n_cols; j++)
            {
                int row = i;
                int col = j;
                metric_range *m1 = new metric_range(metric1, this->m1_thresholds[i + 1], this->m1_thresholds[i]);
                metric_range *m2 = new metric_range(metric2, this->m2_thresholds[j + 1], this->m2_thresholds[j]);
                for (size_t src = 0; src < this->n_nodes; src++)
                {
                    for (size_t dst = 0; dst < this->n_nodes; dst++)
                    {
                        metric_box *mb = new metric_box(m1, m2, row, col);
                        (this->Metrixes[src][dst])[i][j] = *mb;
                    }
                }
            }
        }
    }
    /*
    path *tr_worstfirst_diagonal_m2_reverse(vector<vector<metric_box>> **Metrixes, int n_rows, int n_cols, int src, int dst, int I, int J)

{
    path *p;
    for (int k = 0; k <= I + (n_cols - 1 - J); k++)
    {

        for (int i = I, j = J + k; i >= 0 && j >= J; i--, j--)
        {
            if (i < 0 || j > n_cols - 1)
                continue;
            p = retrieve_path(&(Metrixes[src][dst])[i][j]);
            if (p)
                return p;
        }
    }
    return nullptr;
}
            this->traverse = bind(tr_worstfirst_diagonal_m2_reverse, this->Metrixes, this->n_rows, this->n_cols, placeholders::_1, placeholders::_2, placeholders::_3, placeholders::_4);
    */
    path *traverse_best_to_worst(int src, int dst, int I, int J)
    {
        // metric_box *mb = this->find(src, dst, metric1, metric2);
        int m1_low, m1_high, m2_low, m2_high;
        if (this->metric1_reverse)
        {
            m1_low = I;
            m1_high = this->n_rows - 1;
        }
        else
        {
            m1_low = 0;
            m1_high = I;
        }
        if (this->metric2_reverse)
        {
            m2_low = J;
            m2_high = this->n_cols - 1;
        }
        else
        {
            m2_low = 0;
            m2_high = J;
        }
        path *p;
        for (size_t i = m1_low; i <= m1_high; i++)
        {
            for (size_t j = m2_low; j <= m2_high; j++)
            {
                p = retrieve_path(&(this->Metrixes[src][dst])[i][j]);
                if (p)
                    return p;
            }
        }
        return nullptr;
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

// MetricMatrix *MM_from_config_file(metric *metric1, metric *metric2,
//                                   string metric1_thresholds_str,
//                                   string metric2_thresholds_str,
//                                   string log_dir)
// {
//     string m1ths = str_replace(metric1_thresholds_str, " ", "");
//     vector<float> metric1_thresholds;
//     metric1_thresholds.push_back(metric1->min_theoric_val);
//     vector<float> metric2_thresholds;
//     metric2_thresholds.push_back(metric2->min_theoric_val);
//     stringstream ss1(m1ths);
//     string token;
//     while (getline(ss1, token, ','))
//     {
//         metric1_thresholds.push_back(stof(token));
//     }
//     string m2ths = str_replace(metric2_thresholds_str, " ", "");
//     stringstream ss2(m2ths);
//     while (getline(ss1, token, ','))
//     {
//         metric1_thresholds.push_back(stof(token));
//     }
//     while (getline(ss2, token, ','))
//     {
//         metric2_thresholds.push_back(stof(token));
//     }
//     for (size_t i = 0; i < metric1_thresholds.size() - 1; i++)
//         if (metric1_thresholds[i] >= metric1_thresholds[i + 1])
//             throw runtime_error("Xebel realtime error: Invalid threshold order for " + metric1->name);
//     for (size_t i = 0; i < metric2_thresholds.size() - 1; i++)
//         if (metric1_thresholds[i] >= metric1_thresholds[i + 1])
//             throw runtime_error("Xebel realtime error: Invalid threshold order for " + metric2->name);
//     int n_rows = metric1_thresholds.size();
//     int n_cols = metric2_thresholds.size();
//     // // cout << "DBG|1" << endl;
//     MM = new MetricMatrix(n_rows, n_cols, Nodes.size(), metric1, metric2, log_dir);
//     metric1_thresholds.push_back(metric1->max_theoric_val);
//     metric2_thresholds.push_back(metric2->max_theoric_val);
//     MM->m1_thresholds = metric1_thresholds;
//     MM->m2_thresholds = metric2_thresholds;
//     for (size_t i = 0; i < n_rows; i++)
//     {
//         for (size_t j = 0; j < n_cols; j++)
//         {
//             int row = i;
//             int col = j;
//             metric_range *m1 = new metric_range(metric1, MM->m1_thresholds[i + 1], MM->m1_thresholds[i]);
//             metric_range *m2 = new metric_range(metric2, MM->m2_thresholds[j + 1], MM->m2_thresholds[j]);
//             for (size_t src = 0; src < MM->n_nodes; src++)
//             {
//                 for (size_t dst = 0; dst < MM->n_nodes; dst++)
//                 {
//                     (MM->Metrixes[src][dst])[i][j] = metric_box(m1, m2, row, col);
//                 }
//             }
//         }
//     }
// }
void xero_fill(int Sleep_msec, bool log)
{
    int SleepSecs = Sleep_msec / 1000;
    ostringstream oss;
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
        // oss << "dbg|" << "before for paths: " << Paths.size() << endl; MM->logger(oss.str()); oss.clear();
        for (const auto &entry : Paths)
        {
            path *P = entry.second;
            float val1 = P->W->get_metric_value(0);
            float val2 = P->W->get_metric_value(1);
            sum_metric1 += val1;
            sum_metric2 += val2;
            metric_box *mb = MM->find(P->W->src, P->W->dst, val1, val2);
            if (mb->row != P->row || mb->col != P->col)
            {
                if (P->col >= 0 && P->row >= 0)
                    (MM->Metrixes[P->W->src][P->W->dst])[P->row][P->col].paths.remove(P);
                P->row = mb->row;
                P->col = mb->col;
                mb->paths.push_back(P);
            }
        }
        time(&end);
        double time_taken = double(end - start);
        if (log)
        {
            char report[2000];
            sprintf(report, "  + xero_fill %d) errors: %d, time: %f, #%s:%d avg %f, #%s:%d avg %f",
                    iter, errors, time_taken, Metrics[0]->name.c_str(), n1, sum_metric1 / n1, Metrics[1]->name.c_str(), n2, sum_metric2 / n2);
            MM->logger(report);
        }
        errors = 0;
        this_thread::sleep_for(chrono::seconds(SleepSecs));
    }
}
#endif