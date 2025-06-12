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


## Data Generation
Execute the following Python programs in order.
```bash
python src/filter_raw_data.py
python src/generate_exeuction_trace.py
python src/filter_raw_execution_trace.py
python src/execution_trace_generation.py
```
