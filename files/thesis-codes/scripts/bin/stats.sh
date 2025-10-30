#!/bin/bash
MONITOR_DATA_DIR="/dev/shm/mon"
links=$(ls $MONITOR_DATA_DIR/delay)
for link in $links
do
    delay=$(cat $MONITOR_DATA_DIR/delay/$link)
    speed=$(cat $MONITOR_DATA_DIR/speed/$link)
    bw=$(cat $MONITOR_DATA_DIR/bw/$link)
    printf '%-15s' "link $link"
    printf '%-15s' "delay $delay"
    printf '%-15s' "speed $speed"
    printf '%-15s' "bw $bw"
    printf "\n"
done