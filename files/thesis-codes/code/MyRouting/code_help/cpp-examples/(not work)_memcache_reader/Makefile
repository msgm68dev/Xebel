
# define the compiler
CC = g++

# define the compiler flags
CFLAGS = -g -Wall

# define the linker flags
LDFLAGS = -L/user/cse232/Examples

# define the source files
# SRCS = a3driver.cpp /user/cse232/Examples/example32.sequence.cpp
SRCS = readmemcached.cpp

# define the object files
OBJS = $(SRCS:.cpp=.o)

# define the executable file
MAIN = memctest.exe

# the default rule
all: $(MAIN)

# the rule to create the executable file
$(MAIN): $(OBJS)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $(MAIN) $(OBJS)

# the rule to create the object files
.cpp.o:
	$(CC) $(CFLAGS) -c $< -o $@

# the rule to clean the intermediate files
clean:
	rm -f *.o *~ $(MAIN)