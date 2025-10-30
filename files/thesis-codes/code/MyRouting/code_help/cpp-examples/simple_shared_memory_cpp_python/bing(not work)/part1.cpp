
// This is a code block
#include <boost/interprocess/file_mapping.hpp>
#include <boost/interprocess/mapped_region.hpp>
#include <boost/interprocess/sync/scoped_lock.hpp>
#include <boost/interprocess/sync/named_mutex.hpp>
#include <iostream>
#include <random>

using namespace boost::interprocess;

int main()
{
    // create a file mapping object for the shared memory
    file_mapping fm("shared_memory", read_write);

    // map the whole file with read-write permissions
    mapped_region region(fm, read_write);

    // get the address of the mapped region
    char *addr = static_cast<char *>(region.get_address());

    // create a named mutex to synchronize the access
    named_mutex mutex(open_or_create, "shared_mutex");

    // lock the mutex
    scoped_lock<named_mutex> lock(mutex);

    // read a float value from keyp (the first 8 bytes)
    float keyp;
    std::memcpy(&keyp, addr, sizeof(float));
    std::cout << "C++ read " << keyp << " from keyp" << std::endl;

    // write a float value to keyc (the next 8 bytes)
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<float> dis(0, 100);
    float keyc = dis(gen);
    std::memcpy(addr + sizeof(float), &keyc, sizeof(float));
    std::cout << "C++ wrote " << keyc << " to keyc" << std::endl;

    // unlock the mutex
    lock.unlock();

    // remove the named mutex
    named_mutex::remove("shared_mutex");

    return 0;
}