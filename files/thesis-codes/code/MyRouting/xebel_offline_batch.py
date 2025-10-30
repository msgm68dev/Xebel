#!/usr/bin/python3
# import sys
import os, sys, gc, time, argparse
from utils import *


def Batch_Xoff(CONF = None, stage = 0):
    # raise Exception("Sorry. DONT USE BATCH MODE: this way results in OUT OF MEMORY problem .....")
    Offline_batch_conf = CONF['offlineBatch']
    batch_acep = Offline_batch_conf['batch_acep']
    batch_aps = Offline_batch_conf['batch_aps']
    batch_make_method = Offline_batch_conf['batch_make_methods']
    batch_logfile = Offline_batch_conf['batch_logfile']
    logger = lambda log_str, ts = False : log_into(log_str, batch_logfile, timestamp = ts, print_it = True)
    aceps = comma_separated_str_to_str_tuple(batch_acep)
    apss = comma_separated_str_to_str_tuple(batch_aps)
    make_methods = comma_separated_str_to_str_tuple(batch_make_method.replace('\n', ''))
    # print(f"Make methods = {make_methods}")
    # input()
    n_modes = len(aceps) * len(apss)
    create_file_with_path(batch_logfile, clear_it=False)
    logger(f"xoff-batch: ", True)
    logger(f" n_acep: {len(aceps)}")
    logger(f" n_aps: {len(apss)}")
    logger(f" n_modes: {n_modes}")
    m = 0
    for acep in aceps:
        for aps in apss:
            for maker in make_methods:
                m += 1
                logger(f"### START mode: {m} acep {acep} aps {aps} stage {stage}")
                start = time.time()
                params = f"{acep}-{aps}"
                logger(f"\tparams: {params}")
                main_conf = CONF
                main_conf['offline'].update({"acep" : acep, "aps" : aps})
                off_conf = main_conf['offline']
                # logger(f"\toff_conf: {off_conf}")
                # input()
                # Xoff_1(off_conf)
                os.system(f"xebel-offline --acep {acep} --aps {aps} --maker {maker} --stage {stage}")
                # time.sleep(3)
                print(f"{gc.collect()} garbages collected")
                et = elapsed_time(start)
                logger(f"### END mode: {m}, time: {et}")

            

def main():
    argc = len(sys.argv)
    argv = sys.argv
    # Define command-line switches:
    parser = argparse.ArgumentParser()
    # Define the --config-file switch
    parser.add_argument("--config-file", help="specify the configuration file")
    parser.add_argument("--stage", help="specify the stage of offline phase (default is 0 to run all stages in order)")
    parser.add_argument("--acep", type=float, help="specify ACEP parameter to be used (instead of the value in config file)")
    parser.add_argument("--aps", type=float, help="specify APS parameter to be used (instead of the value in config file)")
    parser.add_argument("batch", nargs="?", help="run batch mode (generate outputs for several aceps and aps)")
    # parser.add_argument("args", nargs="*", help="any arguments without switches")
    args = parser.parse_args()
    Stage = args.stage or "0"
    # Batch = args.batch or False
    # Acep = args.acep or -1
    # Aps = args.aps or -1
    current_dir = os.getcwd()
    print(f"Here: {current_dir}")
    Config_file = args.config_file
    if not Config_file:
        if os.path.exists(current_dir + "/xebel.conf"):
            Config_file = os.path.join(current_dir, "xebel.conf")
        elif os.path.exists("/root/configs/xebel.conf"):
            Config_file = "/root/configs/xebel.conf"
        else:
            print("No config file (xebel.conf) found!")
    print(f"Using config file: {Config_file}")
    CONF = load_configs(Config_file)
    Batch_Xoff(CONF, Stage)
if __name__ == "__main__":
    main()