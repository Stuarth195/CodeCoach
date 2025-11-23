// OutputNormalizer.cpp
#include "OutputNormalizer.h"
#include <algorithm>
#include <sstream>

std::string OutputNormalizer::cleanString(const std::string &s)
{
    size_t first = s.find_first_not_of(" \t\r\n");
    if (std::string::npos == first)
        return "";
    size_t last = s.find_last_not_of(" \t\r\n");
    return s.substr(first, (last - first + 1));
}

std::vector<std::string> OutputNormalizer::splitArray(const std::string &arrayStr)
{
    std::vector<std::string> elements;
    if (arrayStr.empty() || arrayStr == "[]")
        return elements;

    std::string clean = arrayStr.substr(1, arrayStr.length() - 2);
    std::stringstream ss(clean);
    std::string element;

    while (std::getline(ss, element, ','))
    {
        elements.push_back(cleanString(element));
    }

    return elements;
}

std::string OutputNormalizer::normalizeBool(const std::string &output)
{
    std::string clean = cleanString(output);
    std::string lower = clean;
    std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);

    if (lower == "true" || lower == "1" || clean == "1")
        return "1";
    if (lower == "false" || lower == "0" || clean == "0")
        return "0";

    return clean;
}

std::string OutputNormalizer::normalizeArray(const std::string &output)
{
    std::string clean = cleanString(output);

    if (clean[0] == '[' && clean[clean.length() - 1] == ']')
    {
        auto elements = splitArray(clean);
        std::string result = "[";
        for (size_t i = 0; i < elements.size(); i++)
        {
            result += elements[i];
            if (i < elements.size() - 1)
                result += ",";
        }
        result += "]";
        return result;
    }

    return clean;
}

std::string OutputNormalizer::normalizeNumber(const std::string &output)
{
    return cleanString(output);
}

std::string OutputNormalizer::normalizeString(const std::string &output)
{
    return cleanString(output);
}

std::string OutputNormalizer::normalize(const std::string &output, const std::string &function_type)
{
    if (function_type == "bool")
    {
        return normalizeBool(output);
    }
    else if (function_type == "array")
    {
        return normalizeArray(output);
    }
    else if (function_type == "int" || function_type == "double")
    {
        return normalizeNumber(output);
    }
    else
    {
        return normalizeString(output);
    }
}

bool OutputNormalizer::compare(const std::string &expected, const std::string &obtained, const std::string &function_type)
{
    std::string norm_expected = normalize(expected, function_type);
    std::string norm_obtained = normalize(obtained, function_type);
    return norm_expected == norm_obtained;
}