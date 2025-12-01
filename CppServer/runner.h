// runner.h - DEFINICIONES
#pragma once

#include <string>
#include <vector>
#include <cstdint>
#include <chrono>

namespace runner
{
    struct TestResult
    {
        std::string id;
        bool passed = false;
        int exit_code = -1;
        bool timed_out = false;
        std::string stdout_str;
        std::string stderr_str;
    };

    struct EvaluationResult
    {
        std::string status;
        std::string summary;
        int passed_count;
        int total_tests;
        int score;
        bool problem_solved;
        std::string compilation_output;
        std::string execution_output;
        std::vector<std::pair<std::string, std::string>> test_details;
        std::vector<bool> test_passed;
        std::chrono::milliseconds execution_time;
    };

    struct CompileResult
    {
        bool ok = false;
        int exit_code = -1;
        bool timed_out = false;
        std::string stdout_str;
        std::string stderr_str;
    };

    struct EvalRequest
    {
        std::string submission_id;
        std::string user_code;                
        std::string function_name;            
        std::string function_type = "string"; 
        std::string filename;                 

        int compile_timeout_s = 10;
        int run_timeout_s = 2;

        std::vector<std::pair<std::string, std::string>> tests;
    };

    std::string generate_full_source(const EvalRequest &req);
    EvaluationResult evaluate_submission_detailed(const std::string &jsonContent, const std::string &gpp_exe = "g++");
    std::string evaluate_submission(const std::string &jsonContent);
    std::string evaluation_result_to_json(const EvaluationResult &res);
}