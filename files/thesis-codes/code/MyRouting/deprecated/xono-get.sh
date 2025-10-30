#!/bin/bash

function helpstr {
echo "
Usage:
    $0 \"CMD\"
    CMD:
      * stats
      * keys
      * get|<tuple>
      * verify|<tuple>
      * key|<tuple>
"
}

if [ "$1" == "" ] || [ "$1" == "-h" ] || [ "$1" == "--help" ] || [ "$2" != "" ]
then
  helpstr
else
  echo "$1" | nc localhost 11311
  exit 0
fi
