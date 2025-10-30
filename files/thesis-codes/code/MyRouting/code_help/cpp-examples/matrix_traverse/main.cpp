#include <iostream>
#include <string>

using namespace std;
// A function that creates a string 2D array 7 * 4 and fills each element of row i and column j as "ij"

string **create_string_array(int rows, int cols)
{
    string **array = new string *[rows];
    for (int i = 0; i < rows; i++)
    {
        array[i] = new std::string[cols];
    }
    for (int i = 0; i < rows; i++)
    {
        for (int j = 0; j < cols; j++)
        {
            array[i][j] = std::to_string(i) + std::to_string(j);
        }
    }
    return array;
}

void print_array(string **array, int n_rows, int n_cols)
{
    for (size_t i = 0; i < n_rows; i++)
    {
        for (size_t j = 0; j < n_cols; j++)
        {
            cout << array[i][j] << " ";
        }
        cout << endl;
    }
}
void traverse2_to_00(string **array, int n_rows, int n_cols, int I, int J)
{
    for (int k = 0; k <= I + J; k++)
    {
        cout << "k" << k << "\t";
        for (int i = I, j = J - k; i >= 0 && j <= J; i--, j++)
        {
            if (j < 0)
                continue;
            cout << array[i][j] << " ";
        }
        cout << endl;
    }
}
void traverse2_to_0N(string **array, int n_rows, int n_cols, int I, int J)
{
    for (int k = 0; k <= I + (n_cols - 1 - J); k++)
    {
        cout << "k" << k << "\t";
        for (int i = I, j = J + k; i >= 0 && j >= J; i--, j--)
        {
            if (i < 0 || j > n_cols - 1)
                continue;
            cout << array[i][j] << " ";
        }
        cout << endl;
    }
}
void traverse2_to_MN(string **array, int n_rows, int n_cols, int I, int J)
{
    for (int k = 0; k <= (n_rows - 1- I) + (n_cols - 1- J); k++)
    {
        cout << "k" << k << "\t";
        for (int i = I, j = J + k; i <= n_rows && j >= J; i++, j--)
        {
            if (i > n_rows - 1 || j > n_cols - 1)
                continue;
            cout << array[i][j] << " ";
        }
        cout << endl;
    }
}
void traverse2_to_M0(string **array, int n_rows, int n_cols, int I, int J)
{
    for (int k = 0; k <= (n_rows - 1 - I) + J; k++)
    {
        cout << "k" << k << "\t";
        for (int i = I, j = J - k; i <= n_rows && j <= J; i++, j++)
        {
            if (i > n_rows - 1 || j < 0)
                continue;
            cout << array[i][j] << " ";
        }
        cout << endl;
    }
}
void traverse_to_00(string **array, int n_rows, int n_cols, int I, int J)
{
    for (int k = 0; k <= I + J; k++)
    {
        cout << "k" << k << "\t";
        for (int i = I, j = J - k; i >= 0 && j <= J; i--, j++)
        {
            if (i < 0 || i > I || j < 0 || j > J)
                continue;
            cout << array[i][j] << " ";
        }
        cout << endl;
    }
}
void traverse_to_0N(string **array, int n_rows, int n_cols, int I, int J)
{
    for (int k = 0; k <= I + (n_cols - 1 - J); k++)
    {
        cout << "k" << k << "\t";
        for (int i = I, j = J + k; i >= 0 && j >= 0; i--, j--)
        {
            if (i < 0 || i > I  || j < J || j >= n_cols)
                continue;
            cout << array[i][j] << " ";
        }
        cout << endl;
    }
}
void traverse_to_MN(string **array, int n_rows, int n_cols, int I, int J)
{
    for (int k = 0; k <= (n_rows - 1- I) + (n_cols - 1- J); k++)
    {
        cout << "k" << k << "\t";
        for (int i = I, j = J + k; i <= n_rows && j >= 0; i++, j--)
        {
            if (i < I || i >= n_rows || j < J || j >= n_cols)
                continue;
            cout << array[i][j] << " ";
        }
        cout << endl;
    }
}
void traverse_to_M0(string **array, int n_rows, int n_cols, int I, int J)
{
    for (int k = 0; k <= (n_rows - 1 - I) + J; k++)
    {
        cout << "k" << k << "\t";
        for (int i = I, j = J - k; i <= n_rows && j <= J; i++, j++)
        {
            if (i < I || i >= n_rows || j < 0 || j > J)
                continue;
            cout << array[i][j] << " ";
        }
        cout << endl;
    }
}
int main()
{
    int n_rows, n_cols, I, J;
    cout << "Number of rows: ";
    cin >> n_rows;
    cout << "Number of columns: ";
    cin >> n_cols;
    string **M = create_string_array(n_rows, n_cols);
    printf("Matrix: row=%d, cols=%d\n", n_rows, n_cols);
    print_array(M, n_rows, n_cols);
    cout << "row index: ";
    cin >> I;
    cout << "column index: ";
    cin >> J;
    printf("Traverse from %d %d to %d %d\n", I, J, 0, 0);
    traverse_to_00(M, n_rows, n_cols, I, J);
    traverse2_to_00(M, n_rows, n_cols, I, J);
    printf("Traverse from %d %d to %d %d\n", I, J, 0, n_cols - 1);
    traverse_to_0N(M, n_rows, n_cols, I, J);
    traverse2_to_0N(M, n_rows, n_cols, I, J);
    printf("Traverse from %d %d to %d %d\n", I, J, n_rows - 1, 0);
    traverse_to_M0(M, n_rows, n_cols, I, J);
    traverse2_to_M0(M, n_rows, n_cols, I, J);
    printf("Traverse from %d %d to %d %d\n", I, J, n_rows - 1, n_cols - 1);
    traverse_to_MN(M, n_rows, n_cols, I, J);
    traverse2_to_MN(M, n_rows, n_cols, I, J);
    return 0;
}