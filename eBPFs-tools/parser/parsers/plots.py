import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.validators.scatter.marker import SymbolValidator
from plotly.subplots import make_subplots
import parsers.utils as utils
import matplotlib.pyplot as plt
import seaborn as sb
import subprocess
import os

"""
    Generate a histogram
    @param setup: the setup name
    @param test: the test name
    @param df: the data to plot (DataFrame)
    @param xlabel: the x-axis label
    @param ylabel: the y-axis label
    @param show: show the plot
"""
def gen_histogram(setup, test, df, xlabel="", ylabel="Count", show=False):
    print("  -- Generating histogram")

    fig = px.bar(df, barmode='group')

    # Update layout
    plot_title = setup + " " + test
    fig.update_xaxes(tickangle= -90)
    fig.update_layout(title=plot_title,
                      title_x=0.5,
                      xaxis_title=xlabel,
                      yaxis_title=ylabel,
                      legend_title_text='Legend')

    # Save the plot
    utils.save_plot(fig, setup, test)
    # output_file = utils.gen_output_file_name(setup, test)
    # fig.write_image(output_file, width=1080, height=720)
    # print("  -- Saved to %s" % output_file)

    if show:
        fig.show()


"""
    Generate a time series plot
    @param df: the data to plot (DataFrame)
    @param setup: the setup name
    @param test: the test name
    @param mode: the mode of the data (secure or unsecure)
    @param xlabel: the x-axis label
    @param ylabel: the y-axis label
    @param show: show the plot
"""
def gen_time_series(df, setup, test, mode="", xlabel="", ylabel="Count", show=False):

    print("  -- Generating time series...")

    # Add data to the plot
    fig = px.scatter(df, x=df.index, y=df.columns).update_traces(
        mode="lines+markers"
    )

    # Assign symbols to traces
    i = 0
    raw_symbols = SymbolValidator().values
    for t in fig.data:
        if i >= len(raw_symbols):
            i = 0
        t.update(marker_symbol=raw_symbols[i])
        i += 3

    # Update layout
    plot_title=setup + " " + test + " " + mode
    fig.update_layout(title=plot_title,
                      title_x=0.5,
                      xaxis_title=xlabel,
                      yaxis_title=ylabel,
                      legend_title_text='Legend',
    )

    fig.update_xaxes(tickangle=-45)

    # Save the plot
    utils.save_plot(fig, setup, test)

    if show:
        fig.show()


def gen_time_series_stacked(grouped_dfs, setup, test, mode="", xlabel="", ylabel="Count", show=False):
    print("  -- Generating stacked time series...")

    names_len = len(grouped_dfs)

    fig = make_subplots(
        rows=names_len, 
        cols=1, 
        shared_xaxes=False, 
        shared_yaxes=True, 
        vertical_spacing=0.02, 
        row_titles=["( " + name + " )" for name in grouped_dfs.keys()], 
    )

    for i, (_, df) in enumerate(grouped_dfs.items(), start=1):
        for label in df.columns:
            fig.append_trace(go.Scatter(
                x=df.index,
                y=df[label],
                mode="lines+markers",
                name=label
            ), row=i, col=1)

    plot_title = f"{setup} {test} {mode}"
    fig.update_layout(
        title=plot_title,
        title_x=0.5,
        legend_title_text=xlabel,
        showlegend=True,
        legend=dict(
            orientation="v", 
            x=1.05, 
            y=1, 
            xanchor="left", 
            yanchor="top"
        ),
        margin=dict(t=50, b=100, l=70, r=150), 
        height=names_len * 300 
    )

    for i in range(1, names_len + 1):
        fig.update_xaxes(
            title_text="Time", 
            tickangle=-45, 
            showticklabels=True, 
            row=i, col=1
        )

    fig.update_yaxes(showticklabels=True, tickangle=0)

    # save the plot
    utils.save_plot(fig, setup, test, False)

    if show:
        fig.show()




"""
    Generate a clustered stacked bar plot
    @param data: the data to plot
    @param setup: the setup name
    @param test: the test name
    @param mode: the mode of the data (secure or unsecure)
    @param xlabel: the x-axis label
    @param ylabel: the y-axis label
    @param show: show the plot
"""
def gen_clustered_stacked_bar(data, setup, test, xlabel="", ylabel="Count", show=False):

    print("  -- Generating clustered stacked bar...")

    # Prepare data
    index = data.index.values
    levels = list(data.columns.levels)
    columns = list(data.columns.levels[1])

    # Prepare x-axis
    x = []
    x1 = []
    x2 = []
    levels = list(data.columns.levels[0])
    for l in levels:
        for c in index:
            x1.append(l)
            x2.append(c)
    x.append(x1)
    x.append(x2)


    # Create the plot
    fig = go.Figure()

    # Add bars
    for col in columns:
        vals = []
        for l in levels:
            if col not in data[l]:
                vals += [0] * len(index)
            else:
                vals += list(data[l][col].values)
        fig.add_bar(x=x, y=vals, name=col, text=vals, textposition='auto')

    # Update layout
    plot_title = setup + " " + test
    fig.update_layout(barmode='relative',
                      title=plot_title,
                      title_x=0.5,
                      xaxis_title=xlabel,
                      yaxis_title=ylabel)

    # Save the plot
    utils.save_plot(fig, setup, test)

    if show:
        fig.show()

def gen_heatmap(setup, test, data, xlabel="Time", ylabel="Interval", show=False):

    print("  -- Generating Heatmap...")

    plot_title=setup + " " + test

    fig = plt.figure(figsize=(12, 8))
    sb.heatmap(data, cmap="YlGnBu", annot=True, fmt="g")
    plt.title(plot_title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Save the plot
    utils.save_plot(fig, setup, test)


    if show:
        plt.show()

    plt.close()

def gen_flamegraph(setup, test, data, xlabel=""):
    print("  -- Generating Flamegraph...")

    plot_title = setup + " " + test

    temp_file_path = "FlameGraph/flamegraph.temp"

    with open(temp_file_path, "w") as temp_file:
        temp_file.write(data)

    program = ["./FlameGraph/flamegraph.pl", temp_file_path, "--title", plot_title, "--subtitle", xlabel]

    # Save the plot
    output_file = utils.gen_output_file_name(setup, test, format=".svg")
    with open(output_file, "w") as out_file:
        try:
            subprocess.run(program, stdout=out_file, check=True)
            print(f"  -- Saved to %s" % output_file)
        except subprocess.CalledProcessError as e:
            print(f"  -- Failed to save to %s : %s" % (output_file,e))

    os.remove(temp_file_path)

def gen_plot(setup, test, df, x, Y, xlabel, ylabel, show=False):

    plot_title = setup + " " + test
    # plots action with time
    fig = plt.figure()
    for y in Y:
        plt.plot(df[x], df[y], label=Y[y], marker = "+")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(plot_title)
    plt.legend()
    
    utils.save_plot(fig, setup, test)
    if show:
        plt.show()
    plt.close(fig)

def gen_complete_bar(setup, test, x, y, xlabel, ylabel, show=False):
    plot_title = setup + " " + test
    plt.figure()
    fig = px.bar(x=x, y=y)

    # update layout
    plot_title = setup + " " + test
    fig.update_layout(title=plot_title,
                      title_x=0.5,
                      xaxis_title=xlabel,
                      yaxis_title=ylabel,
                      legend_title_text='Legend')

    # Save the plot
    utils.save_plot(fig, setup, test)

    if show:
        plt.show()

    plt.close()
