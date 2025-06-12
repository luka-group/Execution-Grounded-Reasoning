import argparse
from collections import defaultdict
import json
import pickle
import random

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default="data/")
    parser.add_argument('--input_file', type=str, default="pyedu_executed.jsonl")
    parser.add_argument('--output_file', type=str, default="pyedu_executed_filtered.pkl")
    parser.add_argument('--num_samples', type=int, default=1, help="Number of samples per problem")
    args = parser.parse_args()

    with open(args.data_dir+args.input_file, 'r') as f:
        lines = f.readlines()

    idx_data = defaultdict(list)
    for line in lines:
        line = json.loads(line)
        if line['trace'].startswith("ERROR: ") or "!!!" in line['trace']:
            continue
        trace_lines = line['trace'].strip().split('\n')
        if not trace_lines[-1].strip().startswith('<<< Return value from main_solution:'):
            continue
        num_trace_lines = len(trace_lines)
        if num_trace_lines < 300: 
            idx_data[line['problem_description']].append(line)

    total_data = []
    num_samples = args.num_samples
    for _, items in idx_data.items():
        if len(items) > num_samples:
            items = random.sample(items, num_samples)
        total_data.extend(items)
            
    print("Total data count:", len(total_data))
    with open(args.data_dir+args.output_file, 'wb') as f:
        pickle.dump(total_data, f)