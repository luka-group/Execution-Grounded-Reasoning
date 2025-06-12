from vllm import LLM, SamplingParams
import pickle
import argparse
from tqdm import tqdm
from transformers import AutoTokenizer
import re
import random
random.seed(123)

def filter_trace(lines):
    filtered_lines = []
    for line in lines:
        if re.search(r' at 0x[0-9a-fA-F]+', line):
            line = line.replace(re.search(r' at 0x[0-9a-fA-F]+', line).group(), "")
        filtered_lines.append(line) 
    filtered_trace = '\n'.join(filtered_lines)
    return filtered_trace

    return prompt

def get_translation_prompt(question, input, code, trace):
    prompt = f"""Given a question, an input to the question, solution code of the question, and an execution trace of the soluction code, your job is to translate the execution trace into a step-by-step solution to solve the question. Here are some rules for translation:

- Use the exact values from the execution trace during the thought process to ensure the correctness of the thought process.
- Do not write code in your thinking process.
- Pretend you are not given the execution trace and you are solving the question by tracing the code by yourself. So, you should not mention that you are following the execution trace even when you are thinking. 

**Question**

{question}
Given the input, {input}, predict the output of the question by thinking step by step to reach the final output.
Here is a solution code that solves the question:
```
{code}
```

**Execution Trace**

```
{trace}
```
"""
    return prompt

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Execution Trace Translation')
    parser.add_argument('--data_dir', type=str, default="data/")
    parser.add_argument('--input_file', type=str, default="pyedu_executed_filtered.pkl")
    parser.add_argument('--output_file', type=str, default="pyedu_executed_translated.pkl")
    parser.add_argument('--translator_model', type=str, default='Qwen/Qwen3-32B', help='translator model name') 
    parser.add_argument('--num_gpus', type=int, default=8)
    args = parser.parse_args()
    
    tokenizer = AutoTokenizer.from_pretrained(args.translator_model)
    sampling_params = SamplingParams(max_tokens=16384, temperature=0.6, top_p=0.95, top_k=20, min_p=0)

    with open(args.data_dir+args.input_file, "rb") as f:
        total_data = pickle.load(f)
    print(f"Total data: {len(total_data)}")

    answer_prefix = "<<< Return value from main_solution: "
    messages_list = []
    for data in tqdm(total_data):
        question = (data['problem_description']+'\n'+data['io_requirements']).replace("\n\n", "\n")
        if isinstance(data['input'], str):
            data['input'] = data['input'].strip()
        trace_lines = data['trace'].strip().split('\n')
        trace = filter_trace(trace_lines)
        answer = trace_lines[-1].split(answer_prefix, 1)[1].strip()
        data['answer'] = answer
        prompt = get_translation_prompt(question=question, input=data['input'], code=data['refcode'], trace=trace)
        messages_list.append([{'role': 'user', 'content': prompt}])
        
    assert len(messages_list) == len(total_data)
    
    inputs = tokenizer.apply_chat_template(
        messages_list,
        tokenize=False,
        add_generation_prompt=True,
        enabled_thinking=True,
    )

    # filter out prompts longer than 40960 tokens which the max length for Qwen3-32B
    org_count = len(inputs)
    total_data = [data for i, data in enumerate(total_data) if len(inputs[i]) <= 40960]
    inputs = [input for input in inputs if len(input) <= 40960]
    print(f"Filtered {org_count - len(inputs)} inputs longer than 40960 tokens")
    print(f"Filtered {org_count - len(total_data)} data accordingly")

    llm = LLM(model=args.translator_model, tensor_parallel_size=args.num_gpus, gpu_memory_utilization=0.9, disable_custom_all_reduce=True, distributed_executor_backend="mp")
    outputs = llm.generate(inputs, sampling_params)
    
    assert len(outputs) == len(total_data)
    
    for output, data in zip(outputs, total_data):
        data['nl_trace'] = output.outputs[0].text.strip()

    with open(args.data_dir+args.output_file, "wb") as f:
        pickle.dump(total_data, f)

    

  