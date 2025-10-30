#include <iostream>
#include <fstream>
#include <nlohmann/json.hpp> // Include your preferred JSON library (e.g., nlohmann::json)
using namespace std;
using json = nlohmann::json; // Example using nlohmann library

typedef map<string, json> my_map_type;

int main()
{
    ifstream file("data.json");
    json data;
    file >> data;
    my_map_type my_map;

    // Iterate over JSON object and add key-value pairs to the map
    for (auto it = data.begin(); it != data.end(); ++it)
    {
        my_map[it.key()] = it.value();
    }
    /*
    if (my_map["key1"].type() == json::value_t::null) {
    // key1 is null
} else if (my_map["key1"].type() == json::value_t::number_integer) {
    // key1 is an integer
} else if (my_map["key1"].type() == json::value_t::number_unsigned) {
    // key1 is an unsigned integer
} else if (my_map["key1"].type() == json::value_t::number_float) {
    // key1 is a floating-point number
} else if (my_map["key1"].type() == json::value_t::boolean) {
    // key1 is a boolean
} else if (my_map["key1"].type() == json::value_t::string) {
    // key1 is a string
} else if (my_map["key1"].type() == json::value_t::array) {
    // key1 is an array
} else if (my_map["key1"].type() == json::value_t::object) {
    // key1 is an object
} else {
    // Other possible types (binary, byte array)
}
    */
 
 /*
if (my_map["key1"].is_null()) {
    // key1 is null
} else if (my_map["key1"].is_number()) {
    // key1 is a number (check further with is_number_integer, is_number_unsigned, ...)
} else if (my_map["key1"].is_boolean()) {
    // key1 is a boolean
} else if (my_map["key1"].is_string()) {
    // key1 is a string
} else if (my_map["key1"].is_array()) {
    // key1 is an array
} else if (my_map["key1"].is_object()) {
    // key1 is an object
} else {
    // Other possible types (binary, byte array)
} 
 */
    cout << "Value for key1: " << my_map["key1"] << " type: " << my_map["key1"].type_name() << endl;
    cout << "Value for key2: " << my_map["key2"] << " type: " << my_map["key2"].type_name() << endl;
    cout << "Value for key3: " << my_map["key3"] << " type: " << my_map["key3"].type_name() << endl;
}