CXX = g++
CXXFLAGS = -Wall -std=c++11
all: shared_memory_cpp
shared_memory_cpp.o: shared_memory_cpp.cpp
	$(CXX) $(CXXFLAGS) -c shared_memory_cpp.cpp
shared_memory_cpp: shared_memory_cpp.o
	$(CXX) $(CXXFLAGS) -o shared_memory_cpp shared_memory_cpp.o -lrt
clean:
	rm -f shared_memory_cpp shared_memory_cpp.o
