
import itertools
import re
import pandas as pd
from datetime import datetime

"""
    Parse simple histogram bpftrace output file, with or without time
"""
def parse_histogram_output(file, pattern_text, key_group, count_group, mark="[", reverse=False, map_key=[]):
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
                        if(len(map_key)!=0):
                            key = map_key[int(key)]
                        count = int(match.group(count_group))

                        if current_time:
                            data[current_time][key] = count
                        else:
                            if None not in data:
                                data[None] = {}
                            data[None][key] = count
    except FileNotFoundError:
        return data
    
    if reverse:
        data = dict(reversed(data[None].items()))

    return data


def parse_multiple_histogram_output(file, histogram_pattern_text, pattern_text, key_group, count_group):
    datas = {}
    histogram_pattern = re.compile(histogram_pattern_text)
    pattern = re.compile(pattern_text)
    #histogram_pattern_text = r'\[(?P<name>[^,]*), (?P<type>[^]]*)\]'
    #pattern_text = r'(?P<size>\[\d+[A-Za-z]?(\]|\,\s\d+[A-Za-z]?\)))\s+(?P<count>\d+)'

    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                time_match = re.match(r'(\d{2}:\d{2}:\d{2})', line)
                if time_match:
                    current_time = datetime.strptime(time_match.group(1), "%H:%M:%S").time()
                    data[current_time] = {}
                    continue


                if line.startswith('@'):
                    data = {}
                    match = histogram_pattern.search(line)
                    datas[match.group('name') + ' ' + match.group('type')] = data
                elif line.startswith('['):
                    match = pattern.search(line)
                    if match:
                        key = match.group(key_group)
                        count = int(match.group(count_group))
                        data[key] = count
    except FileNotFoundError:
        return {}
    
    return datas

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
    Parse vfssize output file
    @param file: the file to parse
    @return: a dictionary with the data
"""
def parse_vfssize_output(file):
    datas = {}
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('@'):
                    data = {}
                    pattern_text = r'\[(?P<name>[^,]*), (?P<type>[^]]*)\]'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    datas[match.group('name') + ' ' + match.group('type')] = data
                elif line.startswith('['):
                    pattern_text = r'(?P<size>\[\d+[A-Za-z]?(\]|\,\s\d+[A-Za-z]?\)))\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        size = match.group('size')
                        count = match.group('count')
                        data[size] = int(count)
    except FileNotFoundError:
        return {}
    
    return datas

"""
    Parse ext4dist output file
    @param file: the file to parse
    @return: a dictionary with the data
"""
def parse_ext4dist_output(file):
    datas = {}
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('@'):
                    data = {}
                    pattern_text = r'\[ext4\_(?P<operation>[^]]*)\]'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    datas[match.group('operation')] = data
                elif line.startswith('['):
                    pattern_text = r'(?P<usecs>\[\d+[A-Za-z]?(\]|\,\s\d+[A-Za-z]?\)))\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        usecs = match.group('usecs')
                        count = match.group('count')
                        data[usecs] = int(count)
    except FileNotFoundError:
        return {}
    
    return datas


"""
    Parse bitesize output file
    @param file: the file to parse
    @return: a dictionary with the data
"""
def parse_bitesize_output(file):
    datas = {}
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('@'):
                    data = {}
                    pattern_text = r'\[(?P<process_name>[^]]*)\]'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    datas[match.group('process_name')] = data
                elif line.startswith('['):
                    pattern_text = r'(?P<size>\[\d+[A-Za-z]?(\]|\,\s\d+[A-Za-z]?\)))\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        size = match.group('size')
                        count = match.group('count')
                        data[size] = int(count)
    except FileNotFoundError:
        return {}
    
    return datas

"""
    Parse netsize output file
    @param file: the file to parse
    @return: a dictionary with the data
"""
def parse_netsize_output(file):
    datas = {}
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('@'):
                    data = {}
                    pattern_text = r'@(?P<size_type>[^:]*):'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    datas[match.group('size_type')] = data
                elif line.startswith('['):
                    pattern_text = r'(?P<size>\[\d+[A-Za-z]?(\]|\,\s\d+[A-Za-z]?\)))\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        size = match.group('size')
                        count = match.group('count')
                        data[size] = int(count)
    except FileNotFoundError:
        return {}
    
    return datas

"""
"""
def parse_xfsdist_output(file):
    datas = {}
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('@'):
                    data = {}
                    pattern_text = r'\[(?P<function>[^]]*)\]'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    datas[match.group('function')] = data                                                                                                                                                                                                                                                                                   
                elif line.startswith('['):
                    pattern_text = r'(?P<usecs>\[\d+[A-Za-z]?(\]|\,\s\d+[A-Za-z]?\)))\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        usecs = match.group('usecs')
                        count = match.group('count')
                        data[usecs] = int(count)
    except FileNotFoundError:
        return {}
    
    return datas

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

"""
"""
def parse_ffaults_output(file, top=0):
    data={}
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("@"):
                    pattern_text = r'@\[(?P<filename>.*)\]:\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        filename = match.group('filename')
                        if filename == "":
                            filename = "$anonymous mappings$"
                        count = match.group('count')
                        data[filename] = int(count)
        data = dict(reversed(data.items()))
    except FileNotFoundError:
        return {}

    if top > 0:
        data = dict(itertools.islice(data.items(), top))

    return data

"""
"""
def parse_hfaults_output(file, top=0):
    data={}
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("@"):
                    pattern_text = r'@\[[^,], (?P<process>.*)\]:\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        process = match.group('process')
                        count = match.group('count')
                        data[process] = int(count)
        data = dict(reversed(data.items()))
    except FileNotFoundError:
        return {}

    if top > 0:
        data = dict(itertools.islice(data.items(), top))

    return data

"""
"""
def parse_netsize_output(file):
    datas = {}
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('@'):
                    data = {}
                    pattern_text = r'(?P<operation>[^]]*)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    datas[match.group('operation')] = data
                elif line.startswith('['):
                    pattern_text = r'(?P<size>\[\d+[A-Za-z]?(\]|\,\s\d+[A-Za-z]?\)))\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        size = match.group('size')
                        count = match.group('count')
                        data[size] = int(count)
    except FileNotFoundError:
        return {}
    
    return datas


"""
"""
def parse_socksize_output(file):
    datas = {}
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('@'):
                    data = {}
                    pattern_text = r'@(?P<operation>[^:]*)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    datas[match.group('operation')] = data
                elif line.startswith('['):
                    pattern_text = r'(?P<size>\[\d+[A-Za-z]?(\]|\,\s\d+[A-Za-z]?\)))\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        size = match.group('size')
                        count = match.group('count')
                        data[size] = int(count)
    except FileNotFoundError:
        return {}
    
    return datas