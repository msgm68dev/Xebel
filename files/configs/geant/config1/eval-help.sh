#!/bin/bash
n_flows=50
delay_init=1.0001
delay_grow_pcnt=1
freecap_init_x=0.5
per_flow_log=no
debug_reject=no
#delay_thresholds="0, 2, 4, 6, 8, 10, 12, 14, 18, 22"
#bw_thresholds="0, 1, 2, 3, 5, 10, 15, 20, 25, 100 "
xoff_param="0.85-5.0"
ways="./data/offline/xoff_3/$xoff_param/ways.txt"
equations="./data/offline/xoff_3/$xoff_param/equations.txt"
routing_method="        simple_mcp      "; sleep_between_flows_ms=0; description="simple"
#routing_method="xebel_mcp 127.0.0.1 2369"; sleep_between_flows_ms=100; description="xebel-$xoff_param"
xebel-eval \
 --function linkutil \
 --freecap_init_x "$freecap_init_x" \
 --delay_grow_pcnt "$delay_grow_pcnt" \
 --delay_init "$delay_init" \
 --debug_reject "$debug_reject" \
 --n_flows "$n_flows" \
 --per_flow_log "$per_flow_log" \
 --sleep_between_flows_ms "$sleep_between_flows_ms" \
 --routing_method "$routing_method" \
 --metric1_thresholds "$delay_thresholds" \
 --metric2_thresholds "$bw_thresholds" \
 --ways_file "$ways" \
 --equations_file "$equations" \
 --description "$description"

tail ./data/eval/result.txt
