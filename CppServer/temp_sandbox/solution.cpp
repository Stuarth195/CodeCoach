#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <list>
#include <algorithm>
#include <exception>
using namespace std;

// --- User Code ---
bool Igual_A_Dos(int n) {
    
    return n ==2 
}
// -----------------

// Helper para convertir string a vector<int>
vector<int> stringToVector(const string& str) {
    vector<int> result;
    if (str.empty() || str == "[]") return result;
    string clean_str = str.substr(1, str.length() - 2);
    stringstream ss(clean_str);
    string token;
    while (getline(ss, token, ',')) {
        result.push_back(stoi(token));
    }
    return result;
}

// Helper para convertir vector<int> a string
string vectorToString(const vector<int>& vec) {
    string result = "[";
    for (size_t i = 0; i < vec.size(); i++) {
        result += to_string(vec[i]);
        if (i < vec.size() - 1) result += ",";
    }
    result += "]";
    return result;
}

// Helper para convertir string a list<int>
list<int> stringToList(const string& str) {
    list<int> result;
    if (str.empty() || str == "[]") return result;
    string clean_str = str.substr(1, str.length() - 2);
    stringstream ss(clean_str);
    string token;
    while (getline(ss, token, ',')) {
        result.push_back(stoi(token));
    }
    return result;
}

// Helper para convertir list<int> a string
string listToString(const list<int>& lst) {
    string result = "[";
    string valStr;
    bool first = true;
    for (int val : lst) {
        if (!first) result += ",";
        result += to_string(val);
        first = false;
    }
    result += "]";
    return result;
}

int main() {
    
    // Test 1: 1
    try {
        int input_val = 1;
        bool result = IgualUno(input_val);
        cout << (result ? "1" : "0") << endl;
    } catch(const exception& e) { 
        cout << "ERROR_RUNTIME: " << e.what() << endl; 
    } catch(...) { 
        cout << "ERROR_RUNTIME_UNKNOWN" << endl; 
    }
    
    // Test 2: 2
    try {
        int input_val = 2;
        bool result = IgualUno(input_val);
        cout << (result ? "1" : "0") << endl;
    } catch(const exception& e) { 
        cout << "ERROR_RUNTIME: " << e.what() << endl; 
    } catch(...) { 
        cout << "ERROR_RUNTIME_UNKNOWN" << endl; 
    }
    
    // Test 3: 3
    try {
        int input_val = 3;
        bool result = IgualUno(input_val);
        cout << (result ? "1" : "0") << endl;
    } catch(const exception& e) { 
        cout << "ERROR_RUNTIME: " << e.what() << endl; 
    } catch(...) { 
        cout << "ERROR_RUNTIME_UNKNOWN" << endl; 
    }
    return 0;
}
