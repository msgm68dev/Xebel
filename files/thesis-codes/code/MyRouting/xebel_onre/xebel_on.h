#include <iostream>
#include <string>
#include <vector>
#include "xebel_common.h"
using namespace std;
// class equation
//     string left_key
//     string * right_keys
//     operator
// class xono
//     xon * Xon
//     equation* equations
//     function go_equatino(operator)
//     functino run

class equation
{
private:
public:
    way *left;
    vector<way *> rights;
    int id = -1, worker_id = -1, cost;

    equation(way *left, vector<way *> rights)
    {
        this->left = left;
        this->rights = rights;
        this->cost = this->rights.size() - 1;
    };
    equation(way *left, vector<way *> rights, int id, int worker_id) : equation(left, rights)
    {
        this->id = id;
        this->worker_id = worker_id;
    }

    string to_str()
    {
        char str[2000];
        sprintf(str, "eq%d|w%d|c%d|%s = ",
                this->id, this->worker_id, this->cost,
                this->left->tuple_dashed.c_str());
        for (size_t i = 0; i < this->rights.size(); i++)
        {
            way *rw = this->rights[i];
            sprintf(str + strlen(str), "%s %s ", rw->tuple_dashed.c_str(), i == this->rights.size() - 1 ? "" : "&");
        }
        // for (auto &&rw : this->rights)
        // {
        // }
        sprintf(str + strlen(str), "\n");
        return string(str);
    }
    void print()
    {
        cout << this->to_str();
    }

    ~equation(){};
};
vector<equation *> Equations;

void do_equation_add(equation *eq, int metric_idx)
{
    float result = 0;
    for (size_t i = 0; i < eq->rights.size(); i++)
    {
        result += eq->rights[i]->get_metric_value(metric_idx);
    }
    eq->left->set_metric_value(metric_idx, result);
}
void do_equation_multiply(equation *eq, int metric_idx)
{
    float result = 1;
    for (size_t i = 0; i < eq->rights.size(); i++)
    {
        result *= eq->rights[i]->get_metric_value(metric_idx);
    }
    eq->left->set_metric_value(metric_idx, result);
}
void do_equation_min(equation *eq, int metric_idx)
{
    float result = Metrics[metric_idx]->max_theoric_val;
    for (size_t i = 0; i < eq->rights.size(); i++)
    {
        result = min(result, eq->rights[i]->get_metric_value(metric_idx));
    }
    eq->left->set_metric_value(metric_idx, result);
}
void do_equation_max(equation *eq, int metric_idx)
{
    float result = Metrics[metric_idx]->min_theoric_val;
    for (size_t i = 0; i < eq->rights.size(); i++)
    {
        result = max(result, eq->rights[i]->get_metric_value(metric_idx));
    }
    eq->left->set_metric_value(metric_idx, result);
}

class xono
{
private:
    int metric_id;
    function<void(equation *eq)> do_equation;
    string log_file;

public:
    int id;
    string name;
    metric *Metric;
    vector<equation *> equations;
    function<void(string logstr)> logger;
    xono(int id, int metric_id, string log_dir)
    {
        this->metric_id = metric_id;
        this->Metric = Metrics[this->metric_id];
        this->id = id;
        ostringstream oss, oss2;
        oss << "xono_" << this->id << "_" << this->Metric->name;
        this->name = oss.str();
        oss2 << this->name << ".log";
        this->log_file = join_paths(log_dir, oss2.str());
        make_dirs_and_file(this->log_file);
        this->logger = std::bind(append_to_file, this->log_file, false, std::placeholders::_1);
        if (this->Metric->operator_str == "min")
            this->do_equation = std::bind(do_equation_min, std::placeholders::_1, this->metric_id);
        else if (this->Metric->operator_str == "max")
            this->do_equation = std::bind(do_equation_max, std::placeholders::_1, this->metric_id);
        else if (this->Metric->operator_str == "add")
            this->do_equation = std::bind(do_equation_add, std::placeholders::_1, this->metric_id);
        else if (this->Metric->operator_str == "multiply")
            this->do_equation = std::bind(do_equation_multiply, std::placeholders::_1, this->metric_id);
    };
    void run()
    {
        // string test = "14-17-18-21-20-19-11-4-1-3-12-2-6-13-15-16";
        // string test = "1-3-12";
        for (auto &&eq : this->equations)
        {
            // if (eq->left->tuple_dashed == test)
            // {
            // cout << "before " << test  << " : " << Ways[test]->get_metric_value(0) << endl;
            // float f1 = Ways["1-3"]->get_metric_value(0);
            // float f2 = Ways["3-12"]->get_metric_value(0);
            // cout << "    " << "1-3"  << " : " << f1 << endl;
            // cout << "    " << "3-12"  << " : " << f2 << endl;
            //  Ways[test]->set_metric_value(0, f1 + f2);
            // cout << "after0 " << test  << " : " << Ways[test]->get_metric_value(0) << endl;
            // }
            this->do_equation(eq);
        }
    }
    ~xono(){};
};
void xono_runner(xono *x, int sleep_MS, bool log)
{
    float sum_time = 0;
    int iter = 0;
    float avg_time;
    ostringstream oss;
    while (true)
    {
        start_timer();
        x->run();
        float duration = elapsed_time();
        sum_time += duration;
        iter++;
        if (log)
        {
            avg_time = sum_time / iter;
            oss << " . " << x->name << " iter " << iter << " done. avg time: " << avg_time << endl;
            x->logger(oss.str());
        }
        sleep_milliseconds(sleep_MS);
    }
}
class xon
{
private:
    int n_workers;
    function<void(string logstr)> logger;
    string log_file;

public:
    vector<xono *> workers;
    xon(int n_xono, string log_dir)
    {
        this->n_workers = n_xono;
        // int sum_cost_total = 0;
        // for (auto &&eq : Equations)
        // {
        //     sum_cost_total += eq->cost;
        // }
        // int per_worker_cost = sum_cost_total / this->n_workers;
        // vector<equation *> *sublists = new vector<equation *>[this->n_workers];
        // int sublist_idx = 0;
        // int sublist_sum = 0;
        // for (size_t i = 0; i < Equations.size(); i++)
        // {
        //     equation *e = Equations[i];
        //     if (sublist_sum < per_worker_cost)
        //     {
        //         sublist_sum += e->cost;
        //         sublists[sublist_idx].push_back(e);
        //     }
        //     else{
        //         sublist_sum = 0;
        //         sublist_idx++;
        //     }
        // }
        for (size_t j = 0; j < Metrics.size(); j++)
        {
            for (size_t i = 0; i < this->n_workers; i++)
            {
                xono *w = new xono(i, j, log_dir);

                this->workers.push_back(w);
            }
        }
        for (auto &&eq : Equations)
        {
            for (size_t i = 0; i < N_METRICS; i++)
            {
                this->workers[eq->worker_id + (i * n_xono)]->equations.push_back(eq);
            }
        }
        ostringstream oss;
        oss << "xebel_on.log";
        this->log_file = oss.str();
        this->logger = std::bind(append_to_file, this->log_file, false, std::placeholders::_1);
    };
    ~xon(){};
};
xon *Xon;
