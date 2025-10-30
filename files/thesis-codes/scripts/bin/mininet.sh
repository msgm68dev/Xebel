#!/bin/bash

HERE=$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
#if [[ $USER != root ]]; then echo "Run as root!"; echo "    sudo ${BASH_SOURCE[0]}"; exit;
#else echo "Mininet topology runner!";fi


case "$2" in
    "-h"|"--help"|"help")
      echo "
mininet.sh clear|-c : Do sudo mn -c before running
"
      ;;
    "-c"|"clear")
      echo "Clearing: sudo mn -c" && sudo mn -c >/dev/null 2>&1 && echo "" && echo "CLEARED"
      ;;
    *)
      ;;
esac


cd $HERE/../../simulations/
topos=$(find . -type f -iname "*.py"  -printf "%f " | sed 's/.py//g')

if [ -z $1 ]
then
	echo please specify topology:
	echo "	"
	echo "	$topos"
	exit 1
else
	TOPO=$1
fi

sudo mn --custom $THESIS/simulations/$TOPO.py --topo mytopo --mac --switch ovsk --controller remote
