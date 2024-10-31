import plotly.graph_objects as go
import plotly.express as px
from plotly.validators.scatter.marker import SymbolValidator
import parsers.utils as utils

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
    output_file = utils.gen_output_file_name(setup, test)
    fig.write_image(output_file, width=1080, height=720)
    print("  -- Saved to %s" % output_file)
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
    output_file = utils.gen_output_file_name(setup, test+"_"+mode)
    fig.write_image(output_file, width=1080, height=720, scale=1)



    print("  -- Saved to %s" % output_file)
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
    output_file = utils.gen_output_file_name(setup, test)
    fig.write_image(output_file, width=1080, height=720)
    print("  -- Saved to %s" % output_file)
    if show:
        fig.show()
