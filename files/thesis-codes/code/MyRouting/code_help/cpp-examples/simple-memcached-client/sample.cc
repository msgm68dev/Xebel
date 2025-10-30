#include <iostream>
#include <string>
#include <unistd.h>
#include <vector>

#include <libmemcached/memcached.h>

// NB: I know that `using namespace std` at global scope is bad form, and that
//     global variables are bad form.  However, they help keep this answer under
//     200 lines.
using namespace std;

/// The connection to memcached
memcached_st *mcd;

/// A global set of key/value pairs that we manufacture for the sake of this
/// example
vector<pair<string, string>> kv_pairs;

/// Put a key/value pair into memcached with expiration 0, no special flags
bool mcd_set(const string &key, const string &val)
{
    auto rc = memcached_set(mcd, key.c_str(), key.length(), val.c_str(),
                            val.length(), (time_t)0, (uint32_t)0);
    if (rc == MEMCACHED_SUCCESS)
        return true;
    cout << "Error in mcd_set(): " << memcached_strerror(mcd, rc) << endl;
    return false;
}

/// Delete a key/value pair from memcached.  return true on success
/// NB: `(time_t)0` is an expiration of `0`, i.e., immediately
bool mcd_delete(const string &key)
{
    auto rc = memcached_delete(mcd, key.c_str(), key.length(), (time_t)0);
    if (rc == MEMCACHED_SUCCESS)
        return true;
    cout << "Error in mcd_delete(): " << memcached_strerror(mcd, rc) << endl;
    return false;
}

/// Get a value from the kv store, using its key to do the lookup.  return
/// true on success.  On success, the by-ref out parameter `val` will be set.
bool mcd_get(const string &key, string &val)
{
    memcached_return rc;
    size_t len;
    uint32_t flags = 0;
    char *res = memcached_get(mcd, key.c_str(), key.length(), &len, &flags, &rc);
    if (rc == MEMCACHED_SUCCESS)
    {
        val = string(res, len);
        free(res);
        return true;
    }
    // NB: skip next line, because we don't want error messages on a failed get:
    //
    // cout << "Error in mcd_get(): " << memcached_strerror(mcd, rc) << endl;
    return false;
}

/// Connect to a single memcached server on the provided port
bool mcd_connect(const string &servername, const int port)
{
    mcd = memcached_create(nullptr);
    memcached_return rc;
    memcached_server_st *servers = nullptr;
    servers =
        memcached_server_list_append(servers, servername.c_str(), port, &rc);
    rc = memcached_server_push(mcd, servers);
    if (rc == MEMCACHED_SUCCESS)
    {
        cout << "  Successfully connected to " << servername << ":" << port << endl;
        return true;
    }
    cout << "Error in mcd_connect(): " << memcached_strerror(mcd, rc) << endl;
    return false;
}

/// Close the connection to memcached
void mcd_shutdown()
{
    memcached_free(mcd);
    cout << "  Successfully disconnected\n";
}

/// Create a bunch of key/value pairs
void build_kv_pairs(int howmany)
{
    for (int i = 0; i < howmany; ++i)
    {
        string key = "key" + to_string(i) + "_______";
        string val = "val" + to_string(i);
        for (int i = 0; i < 100; ++i)
            val += ("_" + to_string(i));
        kv_pairs.push_back({key, val});
    }
}

/// insert a bunch of k/v pairs into memcached
bool put_kv_pairs(int howmany)
{
    for (int i = 0; i < howmany; ++i)
    {
        if (!mcd_set(kv_pairs[i].first, kv_pairs[i].second))
        {
            cout << "Error inserting key `" << kv_pairs[i].first << "`\n";
            return false;
        }
    }
    cout << "  put_kv_pairs(" << howmany << ") completed successfully\n";
    return true;
}

/// Remove a sequence of keys from memcached
///
/// NB: Here and below, we use first/last/stride so that we can vary wich
///     key/value pairs are operated on
bool delete_kv_pairs(int first, int last, int stride)
{
    for (int i = first; i <= last; i += stride)
    {
        if (!mcd_delete(kv_pairs[i].first))
        {
            cout << "Error removing key `" << kv_pairs[i].first << "`\n";
            return false;
        }
    }
    cout << "  delete_kv_pairs(" << first << ", " << last << ", " << stride
         << ") completed successfully\n";
    return true;
}

/// Verify that a sequence of keys is in memcached, with the right expected
/// values
bool check_present_pairs(int first, int last, int stride)
{
    for (int i = first; i <= last; i += stride)
    {
        string value;
        if (!mcd_get(kv_pairs[i].first, value))
        {
            cout << "Error getting key `" << kv_pairs[i].first
                 << "`: key not found\n";
            return false;
        }
        if (value != kv_pairs[i].second)
        {
            cout << "Value error while getting key `" << kv_pairs[i].first << "`\n";
            cout << "  Expected: `" << kv_pairs[i].second << "`\n";
            cout << "  Found: `" << value << "`\n";
            return false;
        }
    }
    cout << "  check_present_pairs(" << first << ", " << last << ", " << stride
         << ") completed successfully\n";
    return true;
}

/// Verify that a sequence of keys is *not* in memcached
bool check_missing_pairs(int first, int last, int stride)
{
    for (int i = first; i <= last; i += stride)
    {
        string value;
        if (mcd_get(kv_pairs[i].first, value))
        {
            cout << "Error getting key `" << kv_pairs[i].first
                 << "`: key unexpectedly found\n";
            return false;
        }
    }
    cout << "  check_missing_pairs(" << first << ", " << last << ", " << stride
         << ") completed successfully\n";
    return true;
}

int main(int argc, char **argv)
{
    // Parse args to get server name (-s) and port (-p)
    string servername = "";
    int port;
    long opt;
    while ((opt = getopt(argc, argv, "s:p:")) != -1)
    {
        switch (opt)
        {
        case 's':
            servername = string(optarg);
            break;
        case 'p':
            port = atoi(optarg);
            break;
        }
    }

    // Create a bunch of key/value pairs to use for the experiments
    int howmany = 50;
    build_kv_pairs(howmany);

    // Connect to memcached
    mcd_connect(servername, port);
    // insert all the pairs, make sure they are all present
    put_kv_pairs(howmany);
    check_present_pairs(0, howmany - 1, 1);
    // Delete the even pairs
    delete_kv_pairs(0, howmany - 2, 2);
    // ensure the odd pairs are present
    check_present_pairs(1, howmany - 1, 2);
    // ensure the even pairs are not present
    check_missing_pairs(0, howmany, 2);

    mcd_shutdown();
}
