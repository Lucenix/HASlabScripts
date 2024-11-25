
import re
import pandas as pd
from datetime import datetime

"""
"""
def parse_csv_output(file, skiprows=0, delimiter=',', skipfooter=0, ignore_string={}, index=None, dtypes={}, drop_col=[], names=None):
    for string in ignore_string:
        with open(file, "r") as fd:
            data = fd.read()
        with open(file, "w") as fd:
            data = data.replace(string, ignore_string[string])
            fd.write(data)
    
    df = pd.read_csv(file, skiprows=skiprows, skipfooter=skipfooter, names=names, delimiter=delimiter, index_col=False, engine="python")
    if len(df) <= 1:
        return pd.DataFrame()

    for dtype in dtypes:
        df[dtype] = df[dtype].astype(dtypes[dtype])

    if index and index != "":
        df = df.set_index(index)

    for col in drop_col:
        df = df.drop(col, axis=1)

    return df

"""
    Parse simple histogram bpftrace output file, with or without time
"""
def parse_histogram_output(file, pattern_text, key_group, count_group, mark="[", reverse=False, agg=[]):
    data = {}
    current_time = None
    pattern = re.compile(pattern_text)
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                time_match = re.match(r'(\d{2}:\d{2}:\d{2})', line)
                if time_match:
                    current_time = datetime.strptime(time_match.group(1), "%H:%M:%S").time()
                    data[current_time] = {}
                    continue

                if line.startswith(mark):
                    match = pattern.search(line)
                    if match:
                        key = match.group(key_group)
                        count = int(match.group(count_group))

                        
                        if current_time:
                            if agg:
                                for agg_word in agg:
                                    if key.startswith(agg_word):
                                        data[current_time][agg_word + "_" + str(count)] = count
                                        break
                            else:
                                data[current_time][key] = count
                        else:
                            if agg:
                                if None not in data:
                                    data[None] = {}
                                for agg_word in agg:
                                    if key.startswith(agg_word):
                                        data[None][agg_word + "_" + str(count)] = count
                                        break
                            else:
                                if None not in data:
                                    data[None] = {}
                                data[None][key] = count
    except FileNotFoundError:
        return data
    
    if reverse:
        data = dict(reversed(data[None].items())) if None in data else {}

    return data


def parse_multiple_histogram_output(file, histogram_pattern_text, pattern_text, title_group_list, key_group, count_group):
    data = {}
    histogram_pattern = re.compile(histogram_pattern_text)
    pattern = re.compile(pattern_text)
    current_time = None

    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                time_match = re.match(r'(\d{2}:\d{2}:\d{2})', line)
                if time_match:
                    current_time = datetime.strptime(time_match.group(1), "%H:%M:%S").time()
                    continue

                if line.startswith('@'):
                    match = histogram_pattern.search(line)

                    title = match.group(title_group_list[0])
                    for title_group in title_group_list[1:]:
                        title += ' ' + match.group(title_group)

                    if title not in data:
                        data[title] = {}
                    histogram_data = {}
                    data[title][current_time] = histogram_data
                elif line.startswith('['):
                    match = pattern.search(line)
                    if match:
                        key = match.group(key_group)
                        count = int(match.group(count_group))
                        histogram_data[key] = count

    except FileNotFoundError:
        return {}
    
    return data

def parse_time_series_output(file, pattern_text, start, key_group, count_group, filter_labels=[]):
    all_data = {}
    all_data["time"] = []
    if len(filter_labels) > 0:
        print(f"--- Filter for syscalls: {filter_labels}")
    current_time = ""
    
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if re.search(r'\d\d:\d\d:\d\d', line):
                    time_match = re.search(r'\d\d:\d\d:\d\d', line)
                    if time_match:
                        current_time = time_match.group(0)
                        all_data["time"].append(current_time)
                
                elif line.startswith(start):
                    syscall_match = re.search(pattern_text, line)
                    if syscall_match:
                        label = syscall_match.group(key_group)
                        count = int(syscall_match.group(count_group))
                        
                        if filter_labels and label not in filter_labels:
                            continue

                        time_index = all_data["time"].index(current_time)
                        
                        if label not in all_data:
                            all_data[label] = []
                        
                        while len(all_data[label]) <= time_index:
                            all_data[label].append(0)
                        
                        all_data[label][time_index] += count
                        
        size = len(all_data["time"])
        for label in all_data.keys():
            if label != "time":
                while len(all_data[label]) < size:
                    all_data[label].append(0)
    
    except FileNotFoundError:
        print("File not found.")
        return {}
    
    df = pd.DataFrame(all_data).set_index('time')
    return df

import pandas as pd
import re

def parse_2_args_time_series_output(file, pattern_text, start, name_group, label_group, count_group):
    grouped_data = {}
    current_time = ""

    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if re.search(r'\d\d:\d\d:\d\d', line):
                    time_match = re.search(r'\d\d:\d\d:\d\d', line)
                    if time_match:
                        current_time = time_match.group(0)
                
                elif line.startswith(start):
                    match = re.search(pattern_text, line)
                    if match:
                        name = match.group(name_group)
                        label = match.group(label_group)
                        count = int(match.group(count_group))
                        
                        if name not in grouped_data:
                            grouped_data[name] = {
                                "time": [],
                                "counts": {}
                            }
                        
                        name_data = grouped_data[name]
                        
                        if not name_data["time"] or name_data["time"][-1] != current_time:
                            name_data["time"].append(current_time)

                        if label not in name_data["counts"]:
                            name_data["counts"][label] = []

                        time_index = len(name_data["time"]) - 1
                        while len(name_data["counts"][label]) <= time_index:
                            name_data["counts"][label].append(0)

                        name_data["counts"][label][time_index] += count

            for name, data in grouped_data.items():
                time_series_length = len(data["time"])
                for label, counts in data["counts"].items():
                    while len(counts) < time_series_length:
                        counts.append(0)

    except FileNotFoundError:
        print("File not found.")
        return {}

    grouped_dfs = {}
    for name, data in grouped_data.items():
        df_data = {"time": data["time"]}
        for label, counts in data["counts"].items():
            df_data[label] = counts
        
        df = pd.DataFrame(df_data).set_index("time")
        grouped_dfs[name] = df
        

    return grouped_dfs



"""
    Parse fsrwstat output file
    @param file: the file to parse
    @param filter_fs: the list of filesystems to filter
    @return: a DataFrame with the data
"""
def parse_fsrwstat_output(file, filter_fs=[]):
    all_data = {}
    all_data["time"] = []
    if (len(filter_fs) > 0):
        print("--- Filter for filesystems: %s" % filter_fs)
    time = ""
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if re.match(r'\d\d:\d\d:\d\d', line):
                    time = re.search(r'\d\d:\d\d:\d\d', line)
                    if time:
                        time = time.group(0)
                        all_data["time"].append(time)
                    else:
                        print("--- Error parsing time")
                        continue
                elif line.startswith("@["):
                    pattern_text = r'@\[(?P<fs>[a-z1-9_]+)\,\s+vfs_(?P<syscall>[a-z]+)\]:\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        fs = match.group('fs')
                        syscall = match.group('syscall')
                        count = match.group('count')

                        if len(filter_fs)>0 and fs not in filter_fs:
                            continue

                        label=fs#+"-"+syscall
                        time_index = all_data["time"].index(time)
                        if label not in all_data:
                            all_data[label] = []

                        if len(all_data[label]) <= time_index:
                            for i in range(len(all_data[label]), time_index+1):
                                all_data[label].append(0)
                        all_data[label][time_index] += int(count)

        size = len(all_data["time"])
        for label in all_data.keys():
            if label != "time":
                if len(all_data[label]) < size:
                    for i in range(len(all_data[label]), size):
                        all_data[label].append(0)

    except FileNotFoundError:
        return {}

    df = pd.DataFrame(all_data).set_index('time')
    return df

"""
    Parse signals output file and return a DataFrame with the data
    @param file: the file to parse
    @param mode: the mode of the data (secure or unsecure)
    @return: a DataFrame with the data
"""
def parse_signals_output(file, mode):
    data={}
    df = pd.DataFrame()
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('@['):
                    pattern_text = r'@\[(?P<signal>[A-Z]+),\s+(?P<pid>[0-9]+),\s+(?P<comm>[a-z0-9]+)\]:\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        signal = match.group('signal')
                        pid = match.group('pid')
                        comm = match.group('comm')
                        count = match.group('count')

                        if signal not in data:
                            data[signal] = {}
                        if comm not in data[signal]:
                            data[signal][comm] = int(count)
                        else:
                            data[signal][comm] += int(count)

    except FileNotFoundError:
        return df

    df = pd.DataFrame(data)
    df = df.reindex(sorted(df.columns), axis=1)
    df = df.sort_index()

    return df

"""
"""
def parse_pidpersec_output(file, filter_labels=[]):
    all_data = {}
    all_data["time"] = []
    
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            current_time = ""

            for line in lines:
                if re.match(r'\d\d:\d\d:\d\d', line):
                    current_time = re.search(r'\d\d:\d\d:\d\d', line).group(0)
                    all_data["time"].append(current_time)

                pattern_text = r'@\[(?P<label>[^]]+)\]:\s+(?P<count>\d+)'
                pattern = re.compile(pattern_text)
                match = pattern.search(line)
                if match:
                    label = match.group('label')
                    count = int(match.group('count'))

                    if filter_labels and label not in filter_labels:
                        continue

                    if label not in all_data:
                        all_data[label] = []

                    time_index = all_data["time"].index(current_time)
                    while len(all_data[label]) <= time_index:
                        all_data[label].append(0)

                    all_data[label][time_index] += count

        size = len(all_data["time"])
        for label in all_data.keys():
            if label != "time":
                while len(all_data[label]) < size:
                    all_data[label].append(0)

    except FileNotFoundError:
        return {}

    df = pd.DataFrame(all_data).set_index('time')
    return df

def parse_flamegraph_output(file, pattern_text, key_group, count_group, reverse=False):
    data = []
    try:
        with open(file, 'r') as f:
            for line in f:
                match = re.search(pattern_text, line.strip())
                if match:
                    components = match.group(key_group).split(", ")
                    if reverse:
                        components = components[::-1]
                    stack_trace = ";".join(components)
            
                    count = match.group(count_group)
                    data.append(f"{stack_trace} {count}")
    except FileNotFoundError:
        print("File not found.")
        return {}

    return "\n".join(data)

def parse_flamegraph_collapse_output(file):

    stack = []
    in_stack = False
    data = []

    try:
        with open(file) as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if not in_stack:
                    if re.match(r"^@\[$", line):
                        in_stack = True
                    elif match := re.match(r"^@\[,\s(.*)\]: (\d+)", line):
                        data.append(f"{match.group(1)} {match.group(2)}")
                else:
                    if match := re.match(r",?\s?(.*)\]: (\d+)", line):
                        if match.group(1):
                            stack.append(match.group(1))
                        data.append(f"{';'.join(reversed(stack))} {match.group(2)}")
                        in_stack = False
                        stack.clear()
                    else:
                        stack.append(line.lstrip())
                        
    except FileNotFoundError:
        print("File not found")
        return {}

    return "\n".join(data)