#!/usr/bin/python3
import os, sys, gc, time, argparse
from utils import *
# from time import sleep as sleep
# import traceback
# print("Hello")
# from multiprocessing import Pool
# from utils import *
# from Network import Network, Path
# from Traffic import Flow_property, Flow, Traffic
# from Topology import Topology, Link, Switch
# from mc_router import MC_Router
import Traffic

from xebel_eval import flow_properties_list, load_global_variables_from_config


def Batch_Xeval(CONF = None):

    # raise Exception("Sorry. DONT USE BATCH MODE: this way results in OUT OF MEMORY problem .....")
    results_file = CONF['link_utilization']['result']
    delay_grow_pcnt = float(CONF['link_utilization']['delay_grow_pcnt'])
    metric2_thresholds = CONF['onre']['metric2_thresholds']
    xonre_server_port = CONF['onre']['xonre_server_port']
    # description = CONF['link_utilization']['description']
    evalBatch_conf = CONF['evalBatch']
    flowset = evalBatch_conf['flowset']
    batch_xoff_param = evalBatch_conf['batch_xoff_param']
    batch_n_flows = evalBatch_conf['batch_n_flows']
    batch_logfile = evalBatch_conf['batch_logfile']
    # batch_flowset_dir = evalBatch_conf['batch_flowset_dir']
    freecap_init_x = float(evalBatch_conf['freecap_init_x'])
    generate_traffic = evalBatch_conf['generate_traffic'].lower() in ("y", "yes", "true")
    logger = lambda log_str, ts = False : log_into(log_str, batch_logfile, timestamp = ts, print_it = True)
    xoff_params = comma_separated_str_to_str_tuple(batch_xoff_param)
    xoff_params += ("simple", )
    n_flowss = comma_separated_str_to_str_tuple(batch_n_flows)
    n_modes = len(xoff_params) * len(n_flowss)
    create_file_with_path(batch_logfile, clear_it=False)
    create_file_with_path(results_file, clear_it=False)
    logstr = f"### Batch_eval_start: {now_str()} ###"
    log_into(logstr, results_file, timestamp=False, print_it=False)
    log_into(logstr, batch_logfile, timestamp=False, print_it=False)
    m = 0
    n_flows_val = [int(nf) for nf in n_flowss]
    if generate_traffic:
        system_str = f"xebel-eval --function tgen --n_flows {max(max(n_flows_val), 50000)} --flowset {flowset} "
        os.system(system_str)
    for nf in n_flows_val:
        # Freecap_init calculation:
        #  load traffic and calculate avg flow rate:
        # t = Traffic.Traffic(flowset, flow_properties_list, n_flows=nf)
        # flow_rates = [f.property['rate'] for f in t.flows]
        # flow_delays = [f.property['delay'] for f in t.flows]
        # avg_flow_rate = sum(flow_rates) / len(flow_rates)
        #\ load traffic and calculate avg flow rate:
        # freecap_init = avg_flow_rate * nf * freecap_init_x
        freecap_init = 0 # Auto calculate by xebel-eval
        #\ Freecap_init calculation
        
        # flowset = os.path.join(batch_flowset_dir, f"{n_flows}")
        for xoff_param in xoff_params:
            m += 1
            if xoff_param == "simple":
                routing_method = "simple_mcp"
                sleep_between_flows_ms = "1"
                description = f"simple"
            else:
                routing_method = f"xebel_mcp 127.0.0.1 {xonre_server_port}"
                sleep_between_flows_ms = "100"
                ways = f"./data/offline/xoff_3/{xoff_param}/ways.txt"
                equations = f"./data/offline/xoff_3/{xoff_param}/equations.txt"
                description = f"xebel-{xoff_param}"
            check_file_exist(ways)
            check_file_exist(equations)
            logger(f"### START mode: {m},  param= {xoff_params} ")
            system_str = f"xebel-eval "
            system_str += " " + f"--function linkutil"
            system_str += " " + f"--freecap_init_x {freecap_init_x}"
            # system_str += " " + f"--delay_grow_pcnt {delay_grow_pcnt}"
            # system_str += " " + f"--delay_init {delay_init}"
            system_str += " " + f"--debug_reject no"
            system_str += " " + f"--n_flows {nf}"
            system_str += " " + f"--per_flow_log no"
            system_str += " " + f"--per_flow_log_detail no"
            system_str += " " + f"--sleep_between_flows_ms {sleep_between_flows_ms}"
            system_str += " " + f"--routing_method \"{routing_method}\""
            # system_str += " " + f"--metric1_thresholds \"{delay_thresholds}\""
            # system_str += " " + f"--metric2_thresholds \"{bw_thresholds}\""
            system_str += " " + f"--ways_file {ways}"
            system_str += " " + f"--equations_file {equations}"
            system_str += " " + f"--description {description}"
            logger(f"{system_str}")
            start = time.time()
            
            os.system(system_str)
            et = elapsed_time(start)
            if xoff_param == "simple":
                et -= nf * 0.001
            else:
                et -= nf * 0.1
            gc.collect()
            logger(f"### END mode: {m}, time: {et}")
            # log_into(f"### END mode: {m}, time: {et}", results_file)
    # log_into(f"freecap_init_x {freecap_init_x},  delay_grow_pcnt = {delay_grow_pcnt}", results_file, timestamp=False, print_it=False)
    log_into(f"###end", results_file, timestamp=False, print_it=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", help="specify the configuration file")
    args = parser.parse_args()
    current_dir = os.getcwd()
    print(f"Here: {current_dir}")
    Config_file = args.config_file
    if not Config_file:
        if os.path.exists(current_dir + "/xebel-eval.conf"):
            Config_file = os.path.join(current_dir, "xebel-eval.conf")
        elif os.path.exists("/root/configs/xebel-eval.conf"):
            Config_file = "/root/configs/xebel-eval.conf"
        else:
            print("No config file (xebel-eval.conf) found!")
    print(f"Using config file: {Config_file}")
    CONF = load_configs(Config_file)
    load_global_variables_from_config(CONF)
    Batch_Xeval(CONF)
if __name__ == "__main__":
    main()

