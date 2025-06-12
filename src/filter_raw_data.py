import argparse
import pickle
import json
from tqdm import tqdm
from utils import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default="data/")
    parser.add_argument('--input_file', type=str, default="pyedu_toy.jsonl")
    parser.add_argument('--output_file', type=str, default="pyedu_filtered.pkl")
    args = parser.parse_args()

    with open(args.data_dir+args.input_file, 'r') as f:
        raw_data = [json.loads(line) for line in f]
    
    random_included = 0
    no_ios = 0
    deduplicated_ios = 0
    exceed_size = 0
    filtered_data = []
    for data in tqdm(raw_data):
        if "import random" in data['refcode'] or "from random" in data['refcode'] or "import rand" in data['refcode']:
            random_included += 1
            continue
        if data['ios'] is None or len(data['ios']) == 0:
            no_ios += 1
            continue
        
        data['id'] = data['meta']['msgidx']
        io_pairs = deduplicate_io_pairs([(ios['input'], ios['output']) for ios in data['ios']])
        if len(data['ios']) != len(io_pairs):
            deduplicated_ios += 1
        data['input_output'] = []
        for io_pair in io_pairs:
            input = io_pair[0]
            output = io_pair[1]
            if strict_check_size(input):
                data['input_output'].append({'input': input, 'output': output})
            else:
                exceed_size += 1
        del data['ios']
        
        filtered_data.append(data)
    
    print("Random included count:", random_included)
    print("No ios count:", no_ios)
    print("Deduplicated input and output pairs", deduplicated_ios)
    print("Input exceed size", exceed_size)
    print("Total filtered data count:", len(filtered_data))
    
    with open(args.data_dir+args.output_file, 'wb') as f:
        pickle.dump(filtered_data, f)
