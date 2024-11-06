import sys
import pandas as pd

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
    tool_name_list = [target.removesuffix(".bt") for target in os.listdir(args.path) if os.path.isfile(os.path.join(args.path, target))]

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
