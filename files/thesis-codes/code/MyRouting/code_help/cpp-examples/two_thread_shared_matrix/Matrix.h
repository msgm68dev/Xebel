#include <vector>
#include "Mcell.h"

class Matrix {
public:
// Constructor
Matrix (int m, int n) : size (m, n) {
// Resize the vector of vectors to the given size
data.resize (m);
for (int i = 0; i < m; i++) {
data [i].resize (n);
}
}

// Getter and setter for size
std::pair<int, int> getSize () const { return size; }
void setSize (int m, int n) { size = std::make_pair (m, n); }

// Getter and setter for data
std::vector<std::vector<Mcell>> getData () const { return data; }
void setData (const std::vector<std::vector<Mcell>>& d) { data = d; }

// Operator [] to access the data by index
std::vector<Mcell>& operator [] (int i) { return data [i]; }
const std::vector<Mcell>& operator [] (int i) const { return data [i]; }

private:
// The size of the matrix
std::pair<int, int> size;

// The vector of vectors of Mcell objects
std::vector<std::vector<Mcell>> data;
};
