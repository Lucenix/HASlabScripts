from heapq import merge
import sys
from typing import final
import pandas as pd

import parsers.plots as pl
import parsers.parser as pr
import os
import os.path
import argparse

def parse_histogram(tool_name, xlabel, parser_function, *args):
    print(f"> Parsing {tool_name} results into a histogram")
    parsed_output = parser_function(*args)

    df = pd.Series(parsed_output).to_frame()

    if (len(df) == 0):
        print("No data to plot")
        return

    pl.gen_histogram(setup, tool_name, df, xlabel=xlabel)

def parse_multiple_histogram(tool_name, xlabel, parser_function, *args):
    print(f"> Parsing {tool_name} results into multiple histograms")
    parsed_output = parser_function(*args)

    for title in set(parsed_output.keys()):
        df_series = pd.Series(parsed_output[title]).to_frame()

        if (len(df_series) == 0):
            print("No data to plot")
            return

        df = pd.DataFrame(df_series)
        title = title.replace("/", "_").replace(":", "_")

        pl.gen_histogram(setup, tool_name + title, df, xlabel=xlabel)

def parse_time_series(tool_name, xlabel, parser_function, *args):
    print(f"> Parsing {tool_name} results into a time series")
    df = parser_function(*args)
    if len(df) > 0:
        pl.gen_time_series(df, setup, tool_name, "", xlabel=xlabel)

def clustered_stacked_bar(tool_name, xlabel, parser_function, *args):
    print(f"> Parsing {tool_name} results into a stacked bar")
    parsed_output = parser_function(*args)

    if len(parsed_output) == 0:
        print("No data to plot")
        return
    
    pl.gen_clustered_stacked_bar(all, setup, tool_name, xlabel=xlabel)

tool_map = {
    "biolatency" : [(parse_histogram, pr.parse_biolatency_output, [], "Time interval (usecs)")],
    "syscount"   : [(parse_histogram, pr.parse_syscount_output_syscalls, [0], "Syscall"),
                    (parse_histogram, pr.parse_syscount_output_processes, [0], "Process")],
    "fsrwstat"   : [(parse_time_series, pr.parse_fsrwstat_output, [[], False], "Time")],
    "runqlat"    : [(parse_histogram, pr.parse_runqlat_output, [], "Time interval (usecs)")],
    "signals"    : [(clustered_stacked_bar, pr.parse_signals_output, [], "Command")],
    "vfscount"   : [(parse_histogram, pr.parse_vfscount_output, [], "vfs function")],
    "vfssize"    : [(parse_multiple_histogram, pr.parse_vfssize_output, [], "Size (bytes)")],
    "ext4dist"   : [(parse_multiple_histogram, pr.parse_ext4dist_output, [], "Time interval (usecs)")],
    "bitesize"   : [(parse_multiple_histogram, pr.parse_bitesize_output, [], "Size (bytes)")],
    "netsize"    : [(parse_multiple_histogram, pr.parse_netsize_output, [], "Size (bytes)")],
    "funccount"  : [(parse_histogram, pr.parse_funccount_output_functions, [], "Function")],
}

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

    tool_name_list = [target for target in os.listdir(args.path) if os.path.isfile(os.path.join(args.path, target))]

    for tool_name in tool_name_list:
        if tool_name in tool_map:
            for (parse_plotter, parse_function, parse_function_args, xlabel) in tool_map[tool_name]:
                parse_function_args.insert(0, os.path.join(args.path, tool_name))
                parse_plotter(tool_name, xlabel, parse_function, *parse_function_args)
        else:
            print(f"No available parser for tool: {tool_name}")


if __name__ == "__main__":
    main()
