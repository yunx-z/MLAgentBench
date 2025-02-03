import json
import os
import re
import difflib
import inspect
import ast
from pprint import pprint

from MLAgentBench.LLM import complete_text
from MLAgentBench.LLM_as_a_Judge import llm_evaluate_method
# from MLAgentBench.llm_test_cases import test_cases_evaluation 
# from MLAgentBench.schema import EnvException

from MLAgentBench.constants import *

def calculate_complexity(code):
    tree = ast.parse(code)
    LLOC = sum(isinstance(node, ast.stmt) for node in ast.walk(tree))
    return LLOC

def sanitize_json_string(s):
    """ Try to sanitize a string to be a valid JSON string."""
    s = s.strip("```json").strip("```").strip()
    s = s.replace('\\', '\\\\')  # Escape backslashes first
    # s = s.replace('/', '\\/')  # Escape forward slashes
    s = s.replace('\b', '\\b')  # Escape backspaces
    s = s.replace('\f', '\\f')  # Escape form feeds
    s = s.replace('\r', '\\r')  # Escape carriage returns
    s = s.replace('\t', '\\t')  # Escape horizontal tabs
    # triple quotes are a problem
    return re.sub(r'"([^"]*)"', lambda m: '"' + m.group(1).replace('\n', '\\n').replace('\"', '\\"') + '"', s)

def summarize_code(code):
    FEEDBACK_MODEL = os.getenv("FEEDBACK_MODEL", "o1")
    FEEDBACK_MAX_TOKENS = int(os.getenv("FEEDBACK_MAX_TOKENS", "4000"))
    MAX_RETRYS = 3

    prompt = f"""
    Analyze the following Python code with comments and generate a high-level idea proposal summarizing:
    1. The main goal or purpose of the method or algorithm implemented.
    2. The general approach or methodology used to achieve the goal.
    3. Any core assumptions or requirements underlying the implementation.

    Focus on providing a conceptual overview rather than implementation details.

    Code:
    ```python
    {code}
    ```
    Provide the summary as an idea proposal, avoiding references to the code itself. Focus on describing the approach and methodology as a standalone concept.
    """ 
    completion = complete_text(prompt, log_file=os.path.join(os.getenv("LOG_DIR", "logs/"), "env_log", "summarize_code.txt"), model=FEEDBACK_MODEL, max_tokens_to_sample=FEEDBACK_MAX_TOKENS) 
    return completion

# def get_llm_feedback(idea, code):
#     try:
#         test_cases_eval_result = test_cases_evaluation(idea, code)
#     except Exception as e:
#         raise EnvException("test_cases_evaluation failed:\n" + str(e))
#     feedback_result = {}
#     if test_cases_eval_result:
#         feedback_result["test_case_pass_rate"] = test_cases_eval_result["test_case_pass_rate"]
#         feedback_result["test_case_message"] = test_cases_eval_result["test_case_message"]
#     return feedback_result
# 
# def get_llm_feedback_deprecated(idea, code):
#     prompt = f"""You have a research idea proposal and the corresponding code generated by AI. Your task is to evaluate how faithfully the code implements the proposed idea. Specifically, you should:
# 
#     1. Identify the Method: Identify the core portion of the proposal that describes the methodology, ignoring the other parts such as abstract, motivation, impact, etc.
#     2. Identify the Code: Identify the core portion of code that implements the method, ignoring the other parts such as class initialization, loading dataset/model/tokenizer, setting hyperparameters, etc. 
#     3. Segment the Text and Code: Break down both the method text and the code into minimal, meaningful units.
#     4. Match Units: For each unit of text, find the corresponding unit of code that is relevant to it.
#     5. Judgement of Relevance: For each matched pair, provide a judgement of relevance, categorizing it as "high", "medium", "low", or "unsure", and include your rationale for that judgement.
# 
#     Format your output in JSON: The output should be a list of dictionaries, where each dictionary contains the following entries:
#     - "text": The text unit from the method.
#     - "code": The corresponding code unit.
#     - "rationale": Your reasoning for the relevance judgement.
#     - "relevance": Your relevance judgement.
# 
#     If a unit of text does not have a corresponding code unit or vice versa, create a dictionary entry in the output that leaves the unmatched field blank.
# 
#     # Idea Proposal
# 
#     {idea}
# 
#     # Code
# 
#     ```python
#     {code}
#     ```"""
#     i = 0
#     items = None
#     while i < MAX_RETRYS: 
#         i += 1
#         completion = complete_text(prompt, log_file=os.path.join(LOG_DIR, "env_log", "relevance_feedback.txt"), model=FEEDBACK_MODEL, max_tokens_to_sample=FEEDBACK_MAX_TOKENS) 
#         completion = sanitize_json_string(completion)
# 
#         try:
#             items = json.loads(completion)
#             feedback = ""
#             relevance_score, total_units = 0, 0 
#             for item in items:
#                 if item['relevance'] == "high":
#                     relevance_score += 1
#                     total_units += 1
#                 elif item['relevance'] == "medium":
#                     relevance_score += 0.5
#                     total_units += 1
#                 elif item['relevance'] == "low":
#                     relevance_score += 0
#                     total_units += 1
# 
#                 if item['relevance'] in ["low"]:
#                     # check if all pairs are relevant, then feedback is empty string
#                     method = item['text'] if item['text'] else "None"
#                     code_snippet = f"```python\n{item['code']}\n```" if item['code'] else "None"
#                     feedback += f"Method Description: {method}\n"
#                     feedback += f"Code Implementation:\n{code_snippet}\n"
#                     feedback += f"Feedback: The relevance between this code snippet and the described method is {item['relevance']}. {item['rationale']}\n\n"
#             if feedback:
#                 feedback_prefix = "\nHere is the feedback for how some parts of your code may not faithfully reflect the proposed method from another AI. Please improve your code based on the feedback.\n\n"
#                 feedback = feedback_prefix + feedback
#             else:
#                 feedback = "Your code looks relevant to the proposed method from another AI."
#             if total_units:
#                 relevance_score = relevance_score / total_units
#             else:
#                 relevance_score = None
# 
#             try:
#                 test_cases_eval_result = test_cases_evaluation(idea, code)
#             except Exception as e:
#                 raise EnvException("test_cases_evaluation failed:\n" + e)
#             feedback_result = {
#                     "relevance_feedback" : feedback,
#                     "relevance_score" : relevance_score,
#                     }
#             if test_cases_eval_result:
#                 feedback_result["test_case_pass_rate"] = test_cases_eval_result["test_case_pass_rate"]
#                 feedback_result["test_case_message"] = test_cases_eval_result["test_case_message"]
#             return feedback_result
#         except Exception as e:
#             # print(f"DEBUG: error parsing -- {e}\n", completion)
#             continue
# 
#     return None

def save_evals(task_name, method_name, method_class, base_class, score, phase, runtime, is_debug=False):
    # check whether method_class is a file_name or an actual class (Grant's requests)
    # save idea, method_name, method_code, feedback, score into a file
    if isinstance(method_class, str) and isinstance(base_class, str):  # Check if it's a string
        method_code_file = method_class
        base_method_code_file = base_class
    elif inspect.isclass(method_class) and inspect.isclass(base_class):  # Check if it's a class
        method_code_file = inspect.getfile(method_class)
        base_method_code_file = inspect.getfile(base_class)
    else:
        raise ValueError("check the type of method_class or base_class")

    method_code = open(method_code_file, 'r').read()
    base_method_code = open(base_method_code_file, 'r').read()

    explanation = summarize_code(method_code) if phase in ["test", "debug"] and not is_debug else None
    llm_as_a_judge_eval_result = llm_evaluate_method(explanation, method_code, task_name) if phase == "test" and not is_debug else None

    eval_file = "output/idea_evals.json"
    if os.path.exists(eval_file):
        with open(eval_file, 'r') as reader:
            all_evals = json.load(reader)
    else:
        all_evals = {"implementations" : []}

    method_complexity = calculate_complexity(method_code)
    base_complexity = calculate_complexity(base_method_code)
    BASE_RUNTIME = ALL_BASE_RUNTIME[task_name][phase] 
    BASE_PERFORMANCE = ALL_BASE_PERFORMANCE[task_name][phase]
    eval_result = {
            "task_name" : task_name,
            "method_name" : method_name,
            "phase" : phase,
            "performance" : score,
            "improvement_perc" : 100 * (score - BASE_PERFORMANCE) / BASE_PERFORMANCE,
            "step" : int(os.getenv("CURR_STEP", "-1")),
            # "relevance_score" : relevance_score, 
            # "test_case_pass_rate" : test_case_pass_rate,
            "relative_runtime" : 100 * (runtime - BASE_RUNTIME) / BASE_RUNTIME,
            "relative_complexity" :  100 * (method_complexity - base_complexity) / base_complexity,
            "runtime" : runtime,
            "method_complexity" : method_complexity,
            "base_complexity" : base_complexity,
            "method_code_file" : method_code_file,
            "code" : method_code,
            "explanation" : explanation,
            "llm_eval" : llm_as_a_judge_eval_result,
            # "relevance_feedback" : feedback,
            # "test_case_message" : test_case_message,
            }
    all_evals["implementations"].append(eval_result)
    with open(eval_file, 'w') as writer:
        json.dump(all_evals, writer, indent=2)


# Example Usage
if __name__ == "__main__":
    from pprint import pprint
    # anchor = "dare"
    # idea_proposal_file = f"workspace/llm-merging--{anchor}--o1-preview/o1-preview/latest/llm-merging--{anchor}--o1-preview/idea.txt"
    # full_code_file = f"workspace/llm-merging--{anchor}--o1-preview/o1-preview/latest/llm-merging--{anchor}--o1-preview/llm_merging/merging/IntelligentMerge.py"
    full_code_file = "MLAgentBench/benchmarks/llm-merging/env/methods/MyMethod.py"
    # idea_proposal = open(idea_proposal_file, 'r').read()
    full_code = open(full_code_file, 'r').read()
    # fres = get_llm_feedback(idea_proposal, full_code)
    explanation = summarize_code(full_code)
    llm_eval_result = llm_evaluate_method(explanation, full_code, "llm-merging")
    print("Finished!")
    print(explanation)
    pprint(llm_eval_result)
    # for k in fres:
    #     print(k)
    #     print(fres[k])

