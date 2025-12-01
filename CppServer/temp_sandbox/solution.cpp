#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <list>
#include <algorithm>
#include <exception>
using namespace std;

// --- User Code ---
bool es_numero_par(int n) {
    return n % 2 == 0
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
    
    // Test 1: 4
    try {
        int input_val = 4;
        bool result = es_numero_par(input_val);
        cout << (result ? "1" : "0") << endl;
    } catch(const exception& e) { 
        cout << "ERROR_RUNTIME: " << e.what() << endl; 
    } catch(...) { 
        cout << "ERROR_RUNTIME_UNKNOWN" << endl; 
    }
    
    // Test 2: 7
    try {
        int input_val = 7;
        bool result = es_numero_par(input_val);
        cout << (result ? "1" : "0") << endl;
    } catch(const exception& e) { 
        cout << "ERROR_RUNTIME: " << e.what() << endl; 
    } catch(...) { 
        cout << "ERROR_RUNTIME_UNKNOWN" << endl; 
    }
    
    // Test 3: 0
    try {
        int input_val = 0;
        bool result = es_numero_par(input_val);
        cout << (result ? "1" : "0") << endl;
    } catch(const exception& e) { 
        cout << "ERROR_RUNTIME: " << e.what() << endl; 
    } catch(...) { 
        cout << "ERROR_RUNTIME_UNKNOWN" << endl; 
    }
    return 0;
}
