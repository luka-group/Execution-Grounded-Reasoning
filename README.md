# Code Execution as Grounded Supervision for LLM Reasoning

## Installation
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Released Resources 

### Dataset

You can download our dataset from [huggingface](https://huggingface.co/datasets/dongwonj/Execution-Grounded-Reasoning)

### Models

|Base Model|Link|
|-|-|
|Qwen3-4B|[🤗](https://huggingface.co/dongwonj/Qwen3-4B_code_execution_trace)|
|Qwen3-8B|[🤗](https://huggingface.co/dongwonj/Qwen3-8B_code_execution_trace)|


## Data Generation 🔧
Execute the following Python scripts to generate an execution trace for each coding problem and filter out unsuccessful executions. We employ a Python debugging tool called [Snoop](https://github.com/alexmojaki/snoop) to record detailed line-by-line execution signals, which will serve as a basis for grounded supervision for enhanced reasoning.
```bash
python src/filter_raw_data.py
python src/generate_exeuction_trace.py
python src/filter_execution_trace.py
```
Then, use a Translator model to translate the execution traces to be a more natural form of reasoning. The `nl_trace` field in the resulting file will contain the translated execution trace. 
```bash
python src/execution_trace_translation.py
python src/data_construction.py 
```
Run the following script to convert the final data into training data compatible with [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory).
```bash
python src/data_construction.py 
```

## Acknowledgments 🏆
Our work builds upon and is inspired by the following projects. We sincerely appreciate their contributions to the community:

- [Snoop](https://github.com/alexmojaki/snoop)
- [CodeIO](https://github.com/hkust-nlp/CodeIO)
- [LLaMA Factory](https://github.com/hiyouga/LLaMA-Factory)
