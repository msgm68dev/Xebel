class Mcell
{
public:
    // Constructor
    Mcell(int val = 0) : Mcval(val) {}

    // Getter and setter for Mcval
    int getMcval() const { return Mcval; }
    void setMcval(int val) { Mcval = val; }

private:
    // The value of the cell
    int Mcval;
};
