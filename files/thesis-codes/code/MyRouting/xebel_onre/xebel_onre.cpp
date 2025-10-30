#include <iostream>
#include <string>
#include <experimental/filesystem>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/ini_parser.hpp>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include "utils.h"
#include "xebel_common.h"
#include "xebel_on.h"
#include "xebel_re.h"
using namespace std;
string xonre_response(string request)
{
    vector<string> words = split(request, " ");
    ostringstream oss;
    if (words.size() == 0)
    {
        return "";
    }
    else if (words[0] == "healthcheck")
    {
        oss << "OK";
        // oss << endl;
    }
    else if (words[0] == "stats")
    {
        oss << "#ways: " << Ways.size() << ", ";
        oss << "#paths: " << Paths.size() << ", ";
        oss << "#edges: " << Edges.size() << endl;
        oss << "#equations: " << Equations.size() << ", ";
        oss << "#workers: " << Xon->workers.size();
        oss << endl;
    }
    else if (words[0] == "paths")
    {
        oss << "Total " << Paths.size() << " " << words[0] << ": " << endl;
        for (auto &&elem : Paths)
        {
            path *p = elem.second;
            oss << p->W->to_str();
        }
    }
    else if (words[0] == "ways")
    {
        oss << "Total " << Ways.size() << " " << words[0] << ": " << endl;
        for (auto &&elem : Ways)
        {
            way *p = elem.second;
            oss << p->to_str();
        }
    }
    else if (words[0] == "edges")
    {
        oss << "Total " << Edges.size() << " " << words[0] << ": " << endl;
        for (auto &&elem : Edges)
        {
            edge *e = elem.second;
            oss << e->W->to_str();
        }
    }
    else if (words[0] == "nodes")
    {
        oss << "Nodes: ";
        oss << "Total " << Nodes.size() << " " << words[0] << ": " << endl;
        for (auto &&i : Nodes)
        {
            oss << i << " ";
        }
        oss << endl;
    }
    else if (words[0] == "metrics")
    {
        oss << "Total " << Metrics.size() << " " << words[0] << ": " << endl;
        for (auto &&m : Metrics)
        {
            oss << m->to_str();
        }
        oss << "Used metrics: " << endl;
        oss << "  " << MM->metric1_name << ": " << endl;
        for (auto &&i : MM->m1_thresholds)
        {
            oss << i << " ";
        }
        oss << endl;
        oss << "  " << MM->metric2_name << ": " << endl;
        for (auto &&i : MM->m2_thresholds)
        {
            oss << i << " ";
        }
        oss << endl;
    }
    else if (words[0] == "equations")
    {
        oss << "Total " << Equations.size() << " " << words[0] << ": " << endl;
        for (auto &&e : Equations)
        {
            oss << e->to_str();
        }
    }
    else if (words[0] == "way")
    {
        string tuple_dashed = words[1];
        try
        {
            if (Ways.find(tuple_dashed) != Ways.end())
                oss << Ways[tuple_dashed]->to_str();
            else
                oss << "No such way found: " << tuple_dashed << endl;
        }
        catch (const std::exception &e)
        {
            oss << "Error fetching way " << tuple_dashed << endl;
            std::cerr << e.what() << '\n';
        }
    }
    else if (words[0] == "path")
    {
        string tuple_dashed = words[1];
        try
        {
            if (Paths.find(tuple_dashed) != Paths.end())
                oss << Paths[tuple_dashed]->to_str();
            else
                oss << "No such path found: " << tuple_dashed << endl;
        }
        catch (const std::exception &e)
        {
            oss << "Error fetching path " << tuple_dashed << endl;
            std::cerr << e.what() << '\n';
        }
    }
    else if (words[0] == "edge")
    {
        string tuple_dashed = words[1];
        try
        {
            if (Edges.find(tuple_dashed) != Edges.end())
                oss << Edges[tuple_dashed]->to_str();
            else
                oss << "No such edge found: " << tuple_dashed << endl;
        }
        catch (const std::exception &e)
        {
            oss << "Error fetching edge " << tuple_dashed << endl;
            std::cerr << e.what() << '\n';
        }
    }
    else if (words[0] == "equation")
    {
        int id = stoi(words[1]);
        equation *eq = Equations[id - 1];
        oss << eq->to_str();
        oss << "  Workers: ";
        for (auto &&w : Xon->workers)
            if (w->id == eq->worker_id)
                oss << w->name << " ";
        oss << endl;
    }
    else if (words[0] == "verify")
    {
        string key = words[1];
        way *w = Ways[key];
        oss << w->to_str();
        float sum_parents = 0, sum_edges = 0;
        for (auto &&p : w->parents)
        {
            oss << " parent: " << p->to_str();
            sum_parents += p->get_metric_value(0);
        }
        oss << " + sum_parent: " << sum_parents << endl;
        for (auto &&p : w->get_edge_keys())
        {
            oss << "  " << Ways[p]->to_str();
            sum_edges += Ways[p]->get_metric_value(0);
        }
        oss << "  + sum_edges: " << sum_edges << endl;
    }
    else if (words[0] == "traverse")
    {
        int src = stoi(words[1]);
        int dst = stoi(words[2]);
        int i = stoi(words[3]);
        int j = stoi(words[4]);
        if (src >= MM->n_nodes || src < 1 || dst >= MM->n_nodes || dst < 1 || i < 0 || i >= MM->n_rows || j < 0 || j >= MM->n_cols)
        {
            oss << "Wrong parameters" << endl;
        }
        else
        {

            path *p = MM->traverse(src, dst, i, j);
            if (p)
            {
                oss << p->W->to_str();
            }
            else
            {
                oss << "NoPath";
            }
        }
    }
    else if (words[0] == "traverse1")
    {
        oss << "not implemented yet"
            << "" << endl;
    }
    else if (words[0] == "route" || words[0] == "route_show")
    {
        int src = stoi(words[1]);
        int dst = stoi(words[2]);
        float m1 = stof(words[3]);
        float m2 = stof(words[4]);
        if (src >= MM->n_nodes || src < 1 || dst >= MM->n_nodes || dst < 1)
        {
            oss << "Wrong parameters" << endl;
        }
        else
        {
            metric_box *mb = MM->find(src, dst, m1, m2);
            path *p = MM->traverse(src, dst, mb->row, mb->col);
            if (p)
            {
                if (words[0] == "route")
                {
                    oss << p->W->tuple_dashed;
                }
                else if (words[0] == "route_show")
                {
                    oss << p->to_str();
                }
            }
            else
            {
                oss << "";
            }
        }
        // oss << ""
        // << "" << endl;
    }
    else if (words[0] == "route_old" || words[0] == "route_old_show")
    {
        int src = stoi(words[1]);
        int dst = stoi(words[2]);
        float m1 = stof(words[3]);
        float m2 = stof(words[4]);
        if (src >= MM->n_nodes || src < 1 || dst >= MM->n_nodes || dst < 1)
        {
            oss << "Wrong parameters" << endl;
        }
        else
        {
            metric_box *mb = MM->find(src, dst, m1, m2);

            path *p = MM->traverse(src, dst, mb->row, mb->col);
            if (p)
            {
                if (words[0] == "route")
                {
                    oss << p->W->tuple_dashed;
                }
                else if (words[0] == "route_show")
                {
                    oss << p->to_str();
                }
            }
            else
            {
                oss << "";
            }
        }
        // oss << ""
        // << "" << endl;
    }
    else if (words[0] == "routes")
    {
        int src = stoi(words[1]);
        int dst = stoi(words[2]);
        if (src >= MM->n_nodes || src < 1 || dst >= MM->n_nodes || dst < 1)
        {
            oss << "Wrong parameters" << endl;
        }
        else
        {
            vector<vector<metric_box>> mbs = MM->Metrixes[src][dst];
            for (auto &&vec : mbs)
            {
                for (auto &&mb : vec)
                {
                    for (auto &&path : mb.paths)
                    {
                        oss << "\t" << path->to_str() << endl;
                    }
                }
            }
            oss << endl;
        }
    }
    else
    {
        cerr << "Invalid request format" << endl;
        oss << "Invalid command: " << words[0] << endl;
    }
    return oss.str();
}
void xonre_server(int port)
{
    int sock = socket(AF_INET, SOCK_STREAM, 0); // create a TCP socket
    if (sock < 0)
    {
        cerr << "Error creating socket" << endl;
        return;
    }
    int yes = 1;
    if (setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes)) == -1)
    {
        cerr << "Error setting socket options" << endl;
        return;
    }
    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port); // use a different port number
    addr.sin_addr.s_addr = INADDR_ANY;
    if (bind(sock, (struct sockaddr *)&addr, sizeof(addr)) == -1)
    {
        cerr << "Error binding socket to port " << port << endl;
        exit(-1);
    }
    else
    {
        cout << "binding socket successfully to " << port << endl;
    }
    while (true)
    {
        // this_thread::sleep_for(chrono::seconds(1));
        char buffer[1024] = "";
        listen(sock, 1);
        struct sockaddr_in src;
        socklen_t len = sizeof(src);
        int clientSock = accept(sock, (struct sockaddr *)&src, &len);
        int bytes = recv(clientSock, buffer, 1024, 0);
        if (bytes == -1)
        {
            cerr << "xonre_server Error receiving from socket" << endl;
            continue;
        }
        // cout << "DBG|xero_r start: " << endl;
        // Convert the request to a string
        string request(buffer, bytes);
        string response = xonre_response(request);
        int n = send(clientSock, response.c_str(), response.size(), 0);
        // cout << "    " << n << " bytes responded." << endl;
        close(clientSock);
    }
    close(sock);
}
int main(int argc, char *argv[])
{
    char report[5000];
    int counter = 0;
    boost::property_tree::ptree pt;
    string metric1_name, metric2_name, metric1_thresholds_str, metric2_thresholds_str,
        metric1_optimum, metric2_optimum, metric1_operator, metric2_operator,
        metric1_edges_directory, metric2_edges_directory;
    bool from_best_traverse, metric1_reverse, metric2_reverse, edge_updater_log, xono_log, xero_fill_log;
    string configfile, ways_file, equations_file, log_dir, log_file;
    int online_workers, xonre_server_port,
        xono_run_sleep_ms, edge_updater_sleep_ms, xero_fill_sleep_ms;
    vector<thread *> Threads;

    // Initial things ------------------------------------------
    {
        std::cout << "C++ version: " << __cplusplus << "\n";
    }
    // Determin config file ------------------------------------------
    {
        cout << "Determin config file:";
        string config_switch = get_switch_if_entered("--config-file", argc, argv);
        if (config_switch != "")
        {
            configfile = config_switch;
        }
        else
        {
            experimental::filesystem::path current = experimental::filesystem::current_path();
            current /= "xebel.conf";
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
        }
        cout << " " << configfile << endl;
    }
    // Reading configurations ------------------------------------------
    {
        cout << "Reading configurations:";
        boost::property_tree::ini_parser::read_ini(configfile, pt);
        metric1_name = pt.get<string>("onre.metric1");
        metric2_name = pt.get<string>("onre.metric2");
        metric1_thresholds_str = pt.get<string>("onre.metric1_thresholds");
        metric2_thresholds_str = pt.get<string>("onre.metric2_thresholds");
        metric1_optimum = pt.get<string>("onre.metric1_optimum");
        metric2_optimum = pt.get<string>("onre.metric2_optimum");
        metric1_operator = pt.get<string>("onre.metric1_operator");
        metric2_operator = pt.get<string>("onre.metric2_operator");
        metric1_reverse = str_to_lower(metric1_optimum) == "maximum" ? true : false;
        metric2_reverse = str_to_lower(metric2_optimum) == "maximum" ? true : false;
        from_best_traverse = is_yes(pt.get<string>("onre.from_best_traverse"));
        edge_updater_log = is_yes(pt.get<string>("onre.edge_updater_log"));
        xono_log = is_yes(pt.get<string>("onre.xono_log"));
        xero_fill_log = is_yes(pt.get<string>("onre.xero_fill_log"));
        ways_file = pt.get<string>("onre.ways_file");
        equations_file = pt.get<string>("onre.equations_file");
        log_dir = pt.get<string>("onre.log_dir");
        log_file = pt.get<string>("onre.log_file");
        metric1_edges_directory = pt.get<string>("onre.metric1_edges_directory");
        metric2_edges_directory = pt.get<string>("onre.metric2_edges_directory");
        online_workers = atoi(pt.get<string>("onre.online_workers").c_str());
        xonre_server_port = atoi(pt.get<string>("onre.xonre_server_port").c_str());
        xono_run_sleep_ms = atoi(pt.get<string>("onre.xono_run_sleep_ms").c_str());
        edge_updater_sleep_ms = atoi(pt.get<string>("onre.edge_updater_sleep_ms").c_str());
        xero_fill_sleep_ms = atoi(pt.get<string>("onre.xero_fill_sleep_ms").c_str());
        cout << " done" << endl;
    }
    // Declare metrics ------------------------------------------------------
    {
        cout << "Declare metrics:";
        metric *m1 = new metric(metric1_name, metric1_optimum, metric1_operator);
        metric *m2 = new metric(metric2_name, metric2_optimum, metric2_operator);
        Metrics.push_back(m1);
        Metrics.push_back(m2);
        cout << " done" << endl;
    }
    // READ ways_file ------------------------------------------------------
    //      key|tuple-dashed|edge?|path?|mid?|midonly?
    //      key = <src>_<dst>_<digest>
    {
        cout << "Reading ways file:";
        vector<vector<string>> way_records = file_to_table(ways_file, "|");
        int mid_onlyes = 0;
        // string key, tuple_dashed;
        bool is_edge, is_path, is_mid, is_mid_only;
        counter = 0;
        for (auto &&way_record : way_records)
        {
            string key = way_record[0];
            string tuple_dashed = way_record[1];
            is_edge = way_record[2] == "1";
            is_path = way_record[3] == "1";
            is_mid = way_record[4] == "1";
            is_mid_only = way_record[5] == "1";
            way *w = new way(tuple_dashed, is_path, is_mid, is_mid_only, key);
            // Ways[key] = w;
            Ways[tuple_dashed] = w;
            if (is_edge)
            {
                string metric1_file = join_paths(metric1_edges_directory, w->tuple_dashed);
                string metric2_file = join_paths(metric2_edges_directory, w->tuple_dashed);
                edge *e = new edge(w, metric1_file, metric2_file);
                Edges[e->W->tuple_dashed] = e;
            }
            // if (is_path && !is_edge)
            if (is_path)
            {
                path *p = new path(w);
                Paths[w->tuple_dashed] = p;
            }
            if (is_mid_only)
                mid_onlyes++;
            counter += 1;
        }
        fill_nodes();
        cout << " done" << endl;
        sprintf(report, "\t%d nodes. %d ways = %d paths + %d mid_onlys + %d edges imported.\n",
                int(Nodes.size()), int(Ways.size()), int(Paths.size()), mid_onlyes, int(Edges.size()));
        std::cout << report;
    }
    // READ equations_file ------------------------------------------------------
    {
        cout << "Reading equations file:";
        //      id|worker|cost|left_key|right_key_1#right_key_2#...
        int id, worker_id, cost;
        string left_key, right_keys_str;
        vector<string> right_keys;
        vector<vector<string>> equation_records = file_to_table(equations_file, "|");
        way *left;
        equation *e;
        int total_cost = 0;
        for (auto &&eq_record : equation_records)
        {
            id = atoi(eq_record[0].c_str());
            worker_id = atoi(eq_record[1].c_str());
            cost = atoi(eq_record[2].c_str());
            left_key = eq_record[3];
            right_keys_str = eq_record[4];
            right_keys = split(right_keys_str, "#");
            left = Ways[left_key];
            vector<way *> rights;
            for (auto &&rk : right_keys)
            {
                rights.push_back(Ways[rk]);
            }
            left->parents = rights;
            e = new equation(left, rights, id, worker_id);
            left->OPTS["eqid"] = to_string(id);
            Equations.push_back(e);
            total_cost += e->cost;
        }
        cout << " done" << endl;
        sprintf(report, "\tTotal %d equations with cost %d read from %s\n", int(Equations.size()), total_cost, equations_file.c_str());
        std::cout << report;
    }
    // Creating main objects
    {
        // metric *m1 = new metric(metric1_name, metric1_optimum, metric1_operator);
        // metric *m2 = new metric(metric2_name, metric2_optimum, metric2_operator);
        // Metrics.push_back(m1);
        // Metrics.push_back(m2);
        cout << "Creating main objects:";
        make_dirs_and_file(log_file);
        common_logger = bind(append_to_file, log_file, false, std::placeholders::_1);
        Xon = new xon(online_workers, log_dir);
        MM = new MetricMatrix(Metrics[0], Metrics[1],
                              metric1_thresholds_str,
                              metric2_thresholds_str,
                              log_dir,
                              from_best_traverse);
        cout << " done" << endl;
    }
    // Creating threads
    {
        cout << "Creating threads:";
        Threads.push_back(new thread(edges_updater_thread, edge_updater_sleep_ms, edge_updater_log));
        Threads.push_back(new thread(xero_fill, xero_fill_sleep_ms, xero_fill_log));
        Threads.push_back(new thread(xonre_server, xonre_server_port));
        for (auto &&worker : Xon->workers)
        {
            Threads.push_back(new thread(xono_runner, worker, xono_run_sleep_ms, xono_log));
        }
        cout << " done" << endl;
    }
    // Print help
    {
        ostringstream oss;
        oss << "See logs: " << endl;
        oss << "  ls " << log_dir << endl;
        oss << "  tail -f " << log_file << endl;
        oss << "Kill app: " << endl;
        oss << "  pkill xebel-onre" << endl;

        std::cout << oss.str();
    }
    // Running threads
    {
        cout << "Running threads..." << endl;
        for (auto &&tr : Threads)
        {
            tr->join();
        }
    }
}