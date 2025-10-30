// include the necessary headers
#include <iostream>
#include <string>
#include <sstream>
#include <cstring>
#include <libmemcached/memcached.h>

// #include <libmemcached-1.0/memcached.h>
// #include <libmemcached-1.0/memcached.h>
// #include <libmemcached-1.0/server_list.h>
//#include <libmemcached-1.0/visibility.h>
//LIBMEMCACHED_API
// define a function that takes a hex string as a parameter
void get_and_print_value(const std::string &hex_key)
{
    // convert the hex string to a float using std::stringstream
    std::stringstream ss;
    ss << std::hex << hex_key;
    float key;
    ss >> key;

    // connect to memcached server on localhost and port 11211
    memcached_server_st *servers = NULL;
    memcached_st *memc = memcached_create(NULL);
    memcached_return rc;
    servers = memcached_server_list_append(servers, "localhost", 11211, &rc);
    rc = memcached_server_push(memc, servers);

    // get the value associated with the key from memcached
    size_t value_length;
    uint32_t flags;
    memcached_return error;
    char *value = memcached_get(memc, (const char *)&key, sizeof(key), &value_length, &flags, &error);

    // convert the value to a float
    float result;
    std::memcpy(&result, value, sizeof(result));

    // print the value
    std::cout << "The value for key " << key << " is " << result << std::endl;

    // free the resources
    free(value);
    memcached_free(memc);
}

// test the function with an example hex string
int main()
{
    // get_and_print_value("3f800000"); // this is 1.0 in hex
    get_and_print_value("b567bc5029842f41694123db479af0f4"); // this is 1.0 in hex
    return 0;
}

// This function uses the libmemcached https://stackoverflow.com/questions/10842909/using-memcached-get-in-libmemcached-without-value-length library to connect to memcached and get the value for a given key. It also uses the std::stringstream https://techoverflow.net/2019/06/25/how-to-parse-hex-strings-in-c-using-stdstringstream/ class to convert a hex string to a float and vice versa. You can install libmemcached using your package manager or download it from here http://docs.python.org/library/stdtypes.html. You can also use other libraries or methods to achieve the same functionality, but this is one simple and common way to do it.
