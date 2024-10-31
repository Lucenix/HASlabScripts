
import itertools
import re
import pandas as pd

"""
    Parse biolatency output file
    @param file: the file to parse
    @return: a dictionary with the data
"""
def parse_biolatency_output(file):
    data={}
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('['):
                    pattern_text = r'(?P<usecs>\[\d+[A-Za-z]?(\]|\,\s\d+[A-Za-z]?\)))\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        usecs = match.group('usecs')
                        count = match.group('count')
                        data[usecs] = int(count)
    except FileNotFoundError:
        return data

    return data

"""
    Parse syscount output file (syscalls)
    @param file: the file to parse
    @param top: the number of top syscalls to return
    @return: a dictionary with the data
"""
def parse_syscount_output_syscalls(file, top=0):
    data={}
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("@syscall"):
                    pattern_text = r'@syscall\[tracepoint:syscalls:sys_enter_(?P<syscall>.*)\]:\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        syscall = match.group('syscall')
                        count = match.group('count')
                        data[syscall] = int(count)
        data = dict(reversed(data.items()))
    except FileNotFoundError:
        return {}

    if top > 0:
        data = dict(itertools.islice(data.items(), top))

    return data

"""
    Parse syscount output file (processes)
    @param file: the file to parse
    @param top: the number of top processes to return
    @return: a dictionary with the data
"""
def parse_syscount_output_processes(file):
    data={}
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("@process"):
                    pattern_text = r'@process\[(?P<process>.*)\]:\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        process = match.group('process')
                        count = match.group('count')
                        data[process] = int(count)
        data = dict(reversed(data.items()))
    except FileNotFoundError:
        return {}

    return data

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
    Parse runqlat output file
    @param file: the file to parse
    @return: a dictionary with the data
"""
def parse_runqlat_output(file):
    data = {}
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('['):
                    pattern_text = r'(?P<usecs>\[\d+[A-Za-z]?(\]|\,\s\d+[A-Za-z]?\)))\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        usecs = match.group('usecs')
                        count = match.group('count')
                        data[usecs] = int(count)
    except FileNotFoundError:
        return {}

    return data

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
    Parse vfscount output file
    @param file: the file to parse
    @return: a dictionary with the data
"""
def parse_vfscount_output(file):
    data = {}
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("@"):
                    pattern_text = r'@\[vfs_(?P<vfs>.*)\]:\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        vfs_function = match.group('vfs')
                        count = match.group('count')
                        data[vfs_function] = int(count)
        data = dict(reversed(data.items()))
    except FileNotFoundError:
        return {}
    
    return data

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
    Parse funccount (functions) output file
    @param file: the file to parse
    @return: a dictionary with the data
"""
def parse_funccount_output_functions(file, top=0):
    data={}
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("@functions"):
                    pattern_text = r'@functions\[kprobe:(?P<function>.*)\]:\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        function = match.group('function')
                        count = match.group('count')
                        data[function] = int(count)
        data = dict(reversed(data.items()))
    except FileNotFoundError:
        return {}

    if top > 0:
        data = dict(itertools.islice(data.items(), top))

    return data

"""
    Parse funccount (processes) output file
    @param file: the file to parse
    @return: a dictionary with the data
"""
def parse_funccount_output_processes(file):
    data={}
    try:
        with open(file, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("@["):
                    pattern_text = r'@\[(?P<process>.*), (?P<pid>.*)\]:\s+(?P<count>\d+)'
                    pattern = re.compile(pattern_text)
                    match = pattern.search(line)
                    if match:
                        process = match.group('process')
                        pid = match.group('pid')
                        count = match.group('count')
                        data[process] = int(count)
        data = dict(reversed(data.items()))
    except FileNotFoundError:
        return {}

    return data