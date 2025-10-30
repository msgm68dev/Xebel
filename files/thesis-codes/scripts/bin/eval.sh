#!/bin/bash

fname=$(echo "$0" | sed "s/.*\///")

function example {
cat > /tmp/examplestr << EOF
eval.sh linkutil mytopo1 test0.csv "spf"
eval.sh linkutil geant tr_geant_500 "subal <acep> <aps>""
eval.sh linkutil geant tr_geant_50000 "subal 0.85 2.0"
EOF
cat /tmp/examplestr
}

function help {
cat > /tmp/helpstr << EOF
Usage:   
  $fname <evaluation-type>  <dataset> <flowset>  <algorithm [params...]> 
Example
EOF
cat /tmp/helpstr
example
}

case $1 in
  linkutil)
    script=$THESIS/code/evaluation/linkutil.py
    export FUNCTION=linkutil
    if [ -z $2 ]
    then
        echo "Please Specify a dataset (topology)."
        exit 1
    else
      export DATASET=$2
    fi

    if [ -z $3 ]
    then
        echo "Please Specify a flowset (traffic)."
        exit 1
    else
      export FLOWSET=$3
    fi

    if [ -z $4 ]
    then
        echo "Please Specify algorithm."
        exit 1
    else
      export ALGORITHM=$4
    fi
    ;;
  tgen)
    script=$THESIS/code/evaluation/traffic_generate.py
    export FUNCTION=tgen
    if [ -z $2 ]
    then
        echo "Please Specify a dataset (topology)."
        exit 1
    else
      export DATASET=$2
    fi
    if [ -z $3 ]
    then
        echo "Please Specify number of flows."
        exit 1
    else
      export N_FLOWS=$3
    fi

    ;;
  example)
    example
    exit 0
    ;;
  -h|help)
    help
    exit 0
    ;;
  *)
    # echo "Bad input!"
    help
    exit 1
    ;;
esac




exec="exec(open(\"$script\").read())"
python3 -i -c $exec