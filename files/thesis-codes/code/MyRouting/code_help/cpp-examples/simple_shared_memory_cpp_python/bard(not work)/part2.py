#!/usr/bin/python3
from mmap import mmap, ACCESS_READ, ACCESS_WRITE
import struct

# Shared memory name
SHM_NAME = "my_shared_memory"

# Keys and their sizes
KEY_P = "keyp"
KEY_C = "keyc"
KEY_SIZE = 4  # Size of float in bytes

# Open shared memory
# with open(SHM_NAME, 'r+b') as f:
with open(SHM_NAME, 'r+b', 0) as f:
    mem = mmap(f.fileno(), 0, access=ACCESS_READ | ACCESS_WRITE)

# Define functions to read and write values
def write_float(key, value):
    offset = struct.pack("s", key.encode()) + struct.pack("f", value)
    mem.seek(0)
    mem.write(offset)

def read_float(key):
    offset = struct.pack("s", key.encode())
    mem.seek(0)
    mem.write(offset)
    mem.seek(KEY_SIZE + len(offset))
    return struct.unpack("f", mem.read(KEY_SIZE))[0]

# Write test values
write_float(KEY_P, 3.14)

# Read value from other program
print(f"Read value of keyc: {read_float(KEY_C)}")

# Close shared memory
mem.close()