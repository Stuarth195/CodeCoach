// OutputNormalizer.h
#pragma once
#include <string>
#include <vector>
#include <sstream>
#include <algorithm>

class OutputNormalizer
{
public:
    static std::string normalize(const std::string &output, const std::string &function_type);
    static bool compare(const std::string &expected, const std::string &obtained, const std::string &function_type);

private:
    static std::string normalizeBool(const std::string &output);
    static std::string normalizeArray(const std::string &output);
    static std::string normalizeNumber(const std::string &output);
    static std::string normalizeString(const std::string &output);

    static std::string cleanString(const std::string &s);
    static std::vector<std::string> splitArray(const std::string &arrayStr);
};