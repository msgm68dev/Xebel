#!/usr/bin/python3
import mmap
import struct
import time
import random

# create a memory-mapped file of 16 bytes
mm = mmap.mmap(-1, 16, "shared_memory")

# write a float value to keyp (the first 8 bytes)
keyp = random.uniform(0, 100)
mm.seek(0)
mm.write(struct.pack("d", keyp))
print(f"Python wrote {keyp} to keyp")

# read a float value from keyc (the next 8 bytes)
mm.seek(8)
keyc = struct.unpack("d", mm.read(8))[0]
print(f"Python read {keyc} from keyc")

# close the memory-mapped file
mm.close()
