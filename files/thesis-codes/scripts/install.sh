#!/bin/bash

# Import install tools:
SCRIPTS_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )
TOOLS="$SCRIPTS_DIR/tools/install-tools"
if [ -f "$TOOLS" ]; then . $TOOLS; else echo "Error! Can not find $TOOLS"; exit 1; fi

# check_root_user
check_required_packages || exit 1

mkdir -p $THESIS_BKUP
mkdir -p $THESIS_TMP

# Get thesis-codes folder:
cd $SCRIPTS_DIR/..; THESIS_CODES_DIR="$PWD"; cd - 
BIN_DIR="$SCRIPTS_DIR/bin"

# Enable python tab autocompletion
function python_auto_tab_completion(){
    sudo bash -c 'cat > ~/.pythonrc' <<EOF
# enable syntax completion
try:
    import readline
except ImportError:
    print("Module readline not available.")
else:
    import rlcompleter
    readline.parse_and_bind("tab: complete")
EOF
    export="export PYTHONSTARTUP=~/.pythonrc"
    grep -qxF "$export" ~/.bashrc || echo "$export" >> ~/.bashrc
    echo "restart bash to apply python tab autocompletion!"
    echo 
}
python_auto_tab_completion

# Add scripts directory to PATH in ~/.profile
export="export PATH=$PATH:\"$BIN_DIR/\" "
grep -qxF "$export" ~/.bashrc || echo "$export" >> ~/.bashrc

# Add project folder to bashrc
export="export THESIS=\"$THESIS_CODES_DIR\""
grep -qxF "$export" ~/.bashrc || echo "$export" >> ~/.bashrc

# Add code directory to PYTHONPATH in ~/.bashrc
PPath="$THESIS_CODES_DIR/code/"
export="export PYTHONPATH=$PYTHONPATH:\"$PPath\" "
grep -qxF "$export" ~/.bashrc || echo "$export" >> ~/.bashrc

# echo "restart bash:"
echo "  bash"
echo 
for file in $(ls $BIN_DIR)
do
    echo $file
done