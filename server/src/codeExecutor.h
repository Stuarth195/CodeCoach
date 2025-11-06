#ifndef CODEEXECUTOR_H
#define CODEEXECUTOR_H

#include <string>
#include <vector>
#include <map>

struct TestCase
{
    std::string input_raw;
    std::string expected_output_raw;
};

struct EvaluationRequest
{
    std::string problem_title;
    std::string user_code;
    std::vector<TestCase> test_cases;
};

struct TestResult
{
    std::string input_raw;
    std::string expected_output_raw;
    std::string actual_output;
    bool passed;
    std::string status_message;
};

struct EvaluationResponse
{
    std::string problem_title;
    std::string user_code;
    std::vector<TestResult> test_results;
    std::string summary;
    int total_cases;
    int passed_cases;
    int failed_cases;
};

class CodeExecutor
{
public:
    CodeExecutor();
    ~CodeExecutor();

    EvaluationResponse evaluateCode(const EvaluationRequest &request);

private:
    std::string generateSourceFile(const std::string &code);
    bool compileCode(const std::string &sourcePath, const std::string &executablePath);
    std::string executeCode(const std::string &executablePath, const std::string &input);
    std::string cleanOutput(const std::string &output);
    TestResult runTestCase(const std::string &executablePath, const TestCase &testCase);

    std::string tempDirectory;
};

#endif // CODEEXECUTOR_H