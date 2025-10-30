import os
from utils import *
FUNCTION =  get_env_var('FUNCTION')
flowset_dir = os.path.join(thesis_dir, "data/flowset/")
if FUNCTION == "linkutil":
    ALGORITHM = get_env_var('ALGORITHM')
    FLOWSET = os.path.join(flowset_dir, get_env_var('FLOWSET'))
    check_file_exist(FLOWSET)
elif FUNCTION == "tgen":
    N_FLOWS = int(get_env_var('N_FLOWS'))







'''
Read flowset file,
First non-comment row is header
skip comments,
skip empty lines, 
skip heading/leading spaces/tabs
First row can be header or not
output: a dictionary with keys = headers & values = columns
'''
def read_flowset(filename, comment_char = '#', no_header = False):
    output = {}
    f = open(filename, 'r')
    lines = f.readlines()
    headers = []
    n_columns = 0
    i = 0
    for line in lines:
        s = line.strip()
        if not s or s == [''] or s[0] == '#':
            continue
        cells = s.split()
        i = i+1
        if not headers:
            n_columns = len(cells)
            if no_header:
                headers = [str(x+1) for x in range(n_columns)]
            else:
                headers = cells
            for header in headers:
                output[header] = []
        else:
            if len(cells) != n_columns:
                raise Exception('Record {} has not {} fields as headers: {}'.format(i, n_columns, cells))
                return
            for j in range(n_columns):
                output[headers[j]].append(cells[j])
    return output   
