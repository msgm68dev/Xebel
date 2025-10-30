#include <iostream>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <cstring>

using namespace std;

// Shared memory name
const char *SHM_NAME = "my_shared_memory";

// Keys and their sizes
const char *KEY_P = "keyp";
const char *KEY_C = "keyc";
const int KEY_SIZE = 4; // Size of float in bytes
// Define functions to read and write values
void * mem;
float read_float(const char *key)
{
    memcpy(mem, key, strlen(key));
    return *((float *)(mem + KEY_SIZE + strlen(key)));
}

void write_float(const char *key, float value)
{
    memcpy(mem, key, strlen(key));
    *((float *)(mem + KEY_SIZE + strlen(key))) = value;
}
int main()
{
    // Open shared memory
    int shm_fd = shm_open(SHM_NAME, O_RDWR | O_CREAT, S_IRUSR | S_IWUSR);
    if (shm_fd == -1)
    {
        perror("shm_open failed");
        return 1;
    }

    // Set shared memory size
    ftruncate(shm_fd, 2 * KEY_SIZE + strlen(KEY_P) + strlen(KEY_C));

    // Map shared memory
    mem = mmap(NULL, 2 * KEY_SIZE + strlen(KEY_P) + strlen(KEY_C), PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
    if (mem == MAP_FAILED)
    {
        perror("mmap failed");
        return 1;
    }

    // Write test value
    write_float(KEY_C, 2.71);

    // Read value from other program
    cout << "Read value of keyp: " << read_float(KEY_P) << endl;

    // Unmap shared memory
    munmap(mem, 2 * KEY_SIZE + strlen(KEY_P) + strlen(KEY_C));

    // Close shared memory
    close(shm_fd);

    return 0;
}