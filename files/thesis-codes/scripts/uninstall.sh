#!/bin/bash

# Import install tools:
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )
TOOLS="$DIR/tools/install-tools"
if [ -f "$TOOLS" ]; then . $TOOLS; else echo "Error! Can not find $TOOLS"; exit 1; fi

check_root_user
rm_from_bashrc "THESIS"
rm_from_bashrc "$DIR"

# BKUP="/usr/local/share/thesis/backup"

echo After next reboot, the program will be removed from \$PATH and \$PYTHONPATH 

echo Uninstalled