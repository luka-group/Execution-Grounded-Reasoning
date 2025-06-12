from snoop.formatting import DefaultFormatter
import os
import json
import re
from pympler import asizeof
from string import Template

class MyFormatter(DefaultFormatter):
    def __init__(self, prefix, columns, color):
        super().__init__(prefix, columns, color)
        
    def format_start(self, event):
        if event.frame_info.is_ipython_cell:
            return []
        if event.comprehension_type:
            return [u'{type}:'.format(type=event.comprehension_type)]
        else:
            if event.event == 'enter':
                description = 'Enter with block in'
            else:
                assert event.event == 'call'
                if event.frame_info.is_generator:
                    if event.is_yield_value:
                        description = 'Re-enter generator'
                    else:
                        description = 'Start generator'
                else:
                    description = 'Call to'
            return [
                u'{c.cyan}>>> {description} {name}'.format(
                    name=event.code_qualname(),
                    c=self.c,
                    description=description,
                )]

func_arg_template = Template("""from pathlib import Path
import snoop
from snoop.formatting import DefaultFormatter
snoop.tracer.internal_directories += tuple(
    map(str, Path(snoop.tracer.internal_directories[0]).parent.glob("*"))
)
class MyFormatter(DefaultFormatter):
    def __init__(self, prefix, columns, color):
        super().__init__(prefix, columns, color)
        
    def format_start(self, event):
        if event.frame_info.is_ipython_cell:
            return []
        if event.comprehension_type:
            return [u'{type}:'.format(type=event.comprehension_type)]
        else:
            if event.event == 'enter':
                description = 'Enter with block in'
            else:
                assert event.event == 'call'
                if event.frame_info.is_generator:
                    if event.is_yield_value:
                        description = 'Re-enter generator'
                    else:
                        description = 'Start generator'
                else:
                    description = 'Call to'
            return [
                u'{c.cyan}>>> {description} {name}'.format(
                    name=event.code_qualname(),
                    c=self.c,
                    description=description,
                )]
snoop.install(columns='', replace_watch_extras=(), formatter_class=MyFormatter)

$refcode

if __name__ == "__main__":
    main_solution($args)""")

def strict_check_size(obj):
    if asizeof.asizeof(obj) >= 1024: 
        return False

    if isinstance(obj, dict):
        if len(obj) >= 20:  
            return False
        for k, v in obj.items():
            if not strict_check_size(k) or not strict_check_size(v):
                return False

    elif isinstance(obj, (list, tuple, set)):
        if len(obj) >= 20:  
            return False
        for item in obj:
            if not strict_check_size(item):
                return False

    elif isinstance(obj, str):
        if len(obj) >= 100: 
            return False
    else:
        if asizeof.asizeof(obj) >= 128:  
            return False

    return True

def deduplicate_io_pairs(io_pairs):
    seen = set()
    unique = []
    for item in io_pairs:
        # Convert unhashable objects to a hashable string representation
        try:
            key = json.dumps(item[0], sort_keys=True)
        except TypeError:
            key = str(item[0])  # fallback for unserializable objects

        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique

def count_functions(code):
    # Use regex to find all function definitions
    functions = re.findall(r'\bdef\s+\w+\s*\(.*?\)', code)
    return len(functions)

def read_jsonl(jsonl_file_path):
    s = []
    with open(jsonl_file_path, "r") as f:
        lines = f.readlines()
    for line in lines:
        linex = line.strip()
        if linex == "":
            continue
        s.append(json.loads(linex))
    return s

def write_jsonl(data, jsonl_file_path, mode="w"):
    # data is a list, each of the item is json-serilizable
    assert isinstance(data, list)
    if len(data) == 0:
        return
    with open(jsonl_file_path, mode) as f:
        for item in data:
            try:
                f.write(json.dumps(item, ensure_ascii=False)+"\n")
            except Exception as e:
                print(item)