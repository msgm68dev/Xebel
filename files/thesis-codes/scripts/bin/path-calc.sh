#!/bin/bash

# script = '$THESIS/code/1.all_paths/allpaths.py'
# exec(open(script).read())

fname=$(echo "$0" | sed "s/.*\///")

function example {
cat > /tmp/examplestr << EOF
path-calc.sh calc mytopo1

g = Graph(TOPOLOGY)
acep = 0.9
aps = 4.0
pathlist = g.get_paths_from_to(acep, aps, sources = [1, 3])
# pathlist_stats(pathlist, verbosity = 2)
DIR = os.path.join(dataset_pkl_dir(), DATASET+"_pathlist.json")
pathlist_export(pathlist, DIR, e = False, as_json = True)

Ctrl + D
-----
path-calc.sh dag mytopo1

DIR = os.path.join(dataset_pkl_dir(), DATASET+"_pathlist.json")
d = dag(DIR)
d.make()
# d.path_nodes[42].sublets_all[45].Tuple
EOF

cat /tmp/examplestr
}

function help {
cat > /tmp/helpstr << EOF
Usage:   
  $fname calc <dataset>     Pathlist calculation 
  $fname dag <dataset>      DAG construcion from pathlist
  $fname shorten|summarize <dataset>      Path calc for conference paper!
     <dataset>: geant | mytopo1
  $fname example            Show full example
  $fname help               Show this message
EOF
cat /tmp/helpstr
}

case $1 in
  calc)
    script=$THESIS/code/allpaths.py
    ;;
  dag)
    script=$THESIS/code/dag.py
    ;;
  summarize|short)
    script=$THESIS/code/summarize-1.py
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
    help
    exit 1
    ;;
esac

if [ -z $2 ]
then
    echo "Please Specify a dataset."
    exit 1
fi

export DATASET=$2
exec="exec(open(\"$script\").read())"
# python -i -c $exec
python3 -i -c $exec

