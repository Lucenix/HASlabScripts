import sys
import pandas as pd

import pickle as pkl

import parsers.plots as pl
import parsers.parser as pr
import os
import os.path
import argparse

from dataclasses import dataclass
from typing import Callable, List, Optional
import json

@dataclass
class ToolConfig:
    parse_plotter: Callable
    parse_function: Callable
    parse_function_args: List
    xlabel: str

def parse_dstat_plots(tool_name, xlabel, parser_function, *args):
    print(f"> Parsing {tool_name} results")
    df = parser_function(*args)

    if (len(df) == 0):
        print("No data to plot")
        return
    
    # data treatment
    df.rename(columns={
    'read':'read_io_total_nops',
    'writ':'write_io_total_nops',
    'time':'system_time',
    'usr':'usr_cpu_usage',
    'sys':'sys_cpu_usage',
    'idl':'idl_cpu_usage',
    'wai':'wai_cpu_usage',
    'stl':'stl_cpu_usage',
    'read.1':'read_dsk_total_bytes',
    'writ.1':'writ_dsk_total_bytes',
    'used':'used_memory',
    'free':'free_memory',
    'buff':'buff_memory',
    'cach':'cach_memory',
    'recv':'recv_net_total',
    'send':'send_net_total',
    'in':'in_paging',
    'out':'out_paging'}, inplace=True)
    df['system_time'] = pd.to_datetime(df['system_time'], format='%d-%m %H:%M:%S')

    # generate read/write ops timeline
    pl.gen_plot(setup, 'IO Ops Timeline', df, 'system_time', {'read_io_total_nops': 'Reads', 'write_io_total_nops' : 'Writes'}, 
                'System Time', 'Number of Operations')
    
    # generate read/write disk bytes timeline
    pl.gen_plot(setup, 'IO Disk Timeline', df, 'system_time', {'read_dsk_total_bytes': 'Reads', 'writ_dsk_total_bytes' : 'Writes'}, 
                'System Time', 'Disk Operations (Bytes)')
    
    # generate memory usage timeline
    pl.gen_plot(setup, 'Memory Usage Timeline', df, 'system_time', 
                {'used_memory': 'Used Memory', 'free_memory' : 'Free Memory', 'buff_memory': 'Buffer Memory', 'cach_memory': 'Cache Memory'}, 
                'System Time', 'Memory (Bytes)')
    
    # generate network usage timeline
    pl.gen_plot(setup, 'Network Usage Timeline', df, 'system_time', 
                {'recv_net_total': 'Received Net', 'send_net_total' : 'Send Net'}, 
                'System Time', 'Network (Bytes)')
    
    # generate cpu usage timeline
    pl.gen_plot(setup, 'CPU Usage Timeline', df, 'system_time', 
                {'usr_cpu_usage': 'usr CPU usage', 'sys_cpu_usage' : 'sys CPU usage', 'idl_cpu_usage': 'idl CPU usage', 'wai_cpu_usage': 'wai CPU usage'}, 
                'System Time', 'CPU (%)')


def parse_gpu_plots(tool_name, xlabel, parser_function, *args):
    print(f"> Parsing {tool_name} results")
    df = parser_function(*args)

    if (len(df) == 0):
        print("No data to plot")
        return
    
    # data treatment
    df.rename(columns={
        ' temperature.gpu':'temperature_gpu',
        ' utilization.gpu [%]':'utilization_gpu',
        ' utilization.memory [%]':'utilization_memory',
        ' memory.total [MiB]':'memory_total',
        ' memory.free [MiB]':'memory_free',
        ' memory.used [MiB]':'memory_used'}, inplace=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
    df['utilization_gpu'] = df['utilization_gpu'].astype(float)

    # generate gpu temperature timeline
    pl.gen_plot(setup, 'GPU Temperature Timeline', df, 'timestamp',
                {'temperature_gpu': 'Temperature'},
                'System Time', 'Temperature (ºC)')
    
    # generate gpu utilization timeline
    pl.gen_plot(setup, 'GPU Utilization Timeline', df, 'timestamp',
                {'utilization_gpu': 'Utilization'},
                'System Time', 'Utilization (%)')
    
    # generate gpu memory utilization timeline
    pl.gen_plot(setup, 'GPU Memory Utilization Timeline', df, 'timestamp',
                {'memory_total': 'Total Memory', 'memory_free': 'Free Memory', 'memory_used': 'Used Memory'},
                'System Time', 'Memory (MiB)')
    
    
def parse_out_plots(tool_name, xlabel, parser_function, *args):
    print(f"> Parsing {tool_name} results")
    df = parser_function(*args)

    if (len(df) == 0):
        print("No data to plot")
        return
    
    print(f"> Parsing {tool_name} results into pickle")
    os.makedirs(f"plots/{setup}", exist_ok=True)

    with open(f'plots/{setup}/{tool_name}.pkl', "w+b") as fd:
        fd.write(pkl.dumps(df))

    # data treatment
    df = df['system_time'].str.extract(r'[\t\s]*(?P<system_time>[^\t:]*:[^:]*:[^:]*):(?P<action>.*)')
    df = df.dropna()
    df['system_time'] = pd.to_datetime(df['system_time'], format='ISO8601')
    df['duration'] = df['system_time'].shift(-1) - df['system_time']
    df['action'] = df['action'].replace([r'Training epoch.*', r'Trained epoch.*', r'Epoch \d \| Saving.*', r'Epoch \d \| Checkpoint.*', r'Ended.*', r'Start.*'], 
                                    ['Training Epoch', 'Trained Epoch', 'Saving Checkpoint', 'Saved Checkpoint', 'Ended Training Iteration', 'Start Training Iteration'], 
                                    regex=True)
    df = df[~df['action'].str.contains('Accuracy')]
    df['action'] = df['action'].astype(str)

    # generate action timeline
    actions = df.drop(['duration'], axis=1)
    actions = actions.set_index('action')
    #pl.gen_time_series(actions, setup, tool_name, xlabel='Action', ylabel='System Time')
    pl.gen_plot(setup, 'Action Timeline', df, 'system_time',{'action': ''},'System Time', 'Action')

    # generate average time per action histogram
    average_time = df.groupby('action', as_index=False).agg({'duration':'mean'}).sort_values('duration', ascending=False)
    average_time['duration'] = pd.to_datetime(average_time['duration'], unit='ns')
    #pl.gen_clustered_stacked_bar(average_time, setup, tool_name, xlabel='ACtion', ylabel='Average Time Spent', show=True)
    pl.gen_complete_bar(setup, 'Average Time per Action', average_time['action'], average_time['duration'], xlabel='Action', ylabel='Average Time Spent')

    # generate average time per action histogram
    average_time = df.groupby('action', as_index=False).agg({'duration':'sum'}).sort_values('duration', ascending=False)
    average_time['duration'] = pd.to_datetime(average_time['duration'], unit='ns')
    #pl.gen_clustered_stacked_bar(average_time, setup, tool_name, xlabel='ACtion', ylabel='Average Time Spent', show=True)
    pl.gen_complete_bar(setup, 'Total Time per Action', average_time['action'], average_time['duration'], xlabel='Action', ylabel='Total Time Spent')


def parse_histogram(tool_name, xlabel, parser_function, *args):
    print(f"> Parsing {tool_name} results into a histogram")
    parsed_output = parser_function(*args)

    if len(parsed_output.keys())==1 and None in parsed_output:
        parsed_output = parsed_output[None]

    df = pd.Series(parsed_output).to_frame()

    if (len(df) == 0):
        print("No data to plot")
        return
    
    pl.gen_histogram(setup, tool_name, df, xlabel=xlabel)

def parse_multiple_histogram(tool_name, xlabel, parser_function, *args):
    print(f"> Parsing {tool_name} results into multiple histograms")
    parsed_output = parser_function(*args)

    os.makedirs(f"plots/{setup}/{tool_name}", exist_ok=True)

    for title in set(parsed_output.keys()):
        if len(parsed_output[title].keys())==1 and None in parsed_output[title]:
            parsed_output[title] = parsed_output[title][None]

        df_series = pd.Series(parsed_output[title]).to_frame()

        if (len(df_series) == 0):
            print("No data to plot")
            return

        df = pd.DataFrame(df_series)
        title = title.replace("/", "_").replace(":", "_")

        pl.gen_histogram(setup, tool_name + "/" + title, df, xlabel=xlabel)

def parse_pickle(tool_name, xlabel, parser_function, *args):
    print(f"> Parsing {tool_name} results into pickle")
    parsed_output = parser_function(*args)

    os.makedirs(f"plots/{setup}/{tool_name}", exist_ok=True)

    for title in set(parsed_output.keys()):
        if len(parsed_output[title].keys())==1 and None in parsed_output[title]:
            parsed_output[title] = parsed_output[title][None]

        df_series = pd.Series(parsed_output[title]).to_frame()

        if (len(df_series) == 0):
            print("No data to plot")
            return

        df = pd.DataFrame(df_series)
        title = title.replace("/", "_").replace(":", "_").replace(" ", "_")

        with open(f'plots/{setup}/{tool_name}/{title}.pkl', "w+b") as fd:
            fd.write(pkl.dumps(df))
        # pl.gen_histogram(setup, tool_name + "/" + title, df, xlabel=xlabel)

def parse_time_series(tool_name, xlabel, parser_function, *args):
    print(f"> Parsing {tool_name} results into a time series")
    df = parser_function(*args)
    if len(df) > 0:
        pl.gen_time_series(df, setup, tool_name, "", xlabel=xlabel)

def parse_clustered_stacked_bar(tool_name, xlabel, parser_function, *args):
    print(f"> Parsing {tool_name} results into a stacked bar")
    parsed_output = parser_function(*args)

    if len(parsed_output) == 0:
        print("No data to plot")
        return
    
    pl.gen_clustered_stacked_bar(all, setup, tool_name, xlabel=xlabel)


def parse_heatmap(tool_name, xlabel, parser_function, *args):
    print(f"> Parsing {tool_name} results into a heatmap")
    parsed_output = parser_function(*args)

    if len(parsed_output) == 0:
        print("No data to plot")
        return
    
    if len(parsed_output.keys())==1 and None in parsed_output:
        df = pd.DataFrame.from_dict(parsed_output[None], orient='index', columns=['Count'])
        df = df.transpose()
    else:
        df = pd.DataFrame(parsed_output).fillna(0)
    
    pl.gen_heatmap(setup, tool_name, df, ylabel=xlabel)

def parse_multiple_heatmap(tool_name, xlabel, parser_function, *args):
    print(f"> Parsing {tool_name} results into multiple heatmaps")
    parsed_output = parser_function(*args)

    if len(parsed_output) == 0:
        print("No data to plot")
        return

    os.makedirs(f"plots/{setup}/{tool_name}", exist_ok=True)

    for title in parsed_output:
        title_output = parsed_output[title]
        if len(title_output.keys())==1 and None in title_output:
            df = pd.DataFrame.from_dict(title_output[None], orient='index', columns=['Count'])
            df = df.transpose()
        else:
            df = pd.DataFrame(title_output).fillna(0)

        title = title.replace("/", "_").replace(":", "_")
        pl.gen_heatmap(setup, tool_name+"/"+title, df, ylabel=xlabel)

def parse_flamegraph(tool_name, xlabel, parser_function, *args):
    print(f"> Parsing {tool_name} results into a flamegraph")
    parsed_output = parser_function(*args)

    if len(parsed_output) == 0:
        print("No data to plot")
        return
    
    pl.gen_flamegraph(setup, tool_name, parsed_output, xlabel)

### MAIN ###

def load_tool_map(file_path="tool_map.json"):
    with open(file_path, "r") as f:
        config_data = json.load(f)
    
    tool_map = {}
    for tool_name, configs in config_data.items():
        tool_map[tool_name] = []
        for config in configs:
            parse_plotter = getattr(sys.modules[__name__], config["parse_plotter"])
            parse_function = getattr(pr, config["parse_function"])
            tool_map[tool_name].append(
                ToolConfig(
                    parse_plotter=parse_plotter,
                    parse_function=parse_function,
                    parse_function_args=config["parse_function_args"],
                    xlabel=config["xlabel"]
                )
            )
    return tool_map

def process_tool_output(args, tool_map):
    tool_name_list = []

    for target in os.listdir(args.path):
        if os.path.isfile(os.path.join(args.path, target)):
            if target.endswith(".bt"):
                target_path = os.path.join(args.path, target)
                renamed_target_path = os.path.join(args.path, target.removesuffix(".bt"))
                os.rename(target_path, renamed_target_path)
                target = target.removesuffix(".bt")
            
            tool_name_list.append(target)

    for tool_name in tool_name_list:
        if tool_name in tool_map:
            mode = len(tool_map[tool_name]) > 1
            for tool_config in tool_map[tool_name]:
                parse_plotter = tool_config.parse_plotter
                parse_function = tool_config.parse_function
                parse_function_args = tool_config.parse_function_args
                xlabel = tool_config.xlabel

                parse_function_args.insert(0, os.path.join(args.path, tool_name))
                parse_plotter(tool_name+("_" + xlabel if mode else ""), xlabel, parse_function, *parse_function_args)
        else:
            print(f"No available parser for tool: {tool_name}")



def main():
    global setup
    
    args = sys.argv[1:]

    if len(args) != 2:
        print("Incorrect Usage\nUsage: python parse-res [OUTPUT_FOLDER_PATH] [SETUP]")

    parser = argparse.ArgumentParser(description='eBPF\'s parser')
    parser.add_argument('path', nargs='?', default='.')
    parser.add_argument('setup', default="Model")

    args = parser.parse_args()
    setup = args.setup

    tool_map = load_tool_map()
    process_tool_output(args, tool_map)
    

if __name__ == "__main__":
    main()
