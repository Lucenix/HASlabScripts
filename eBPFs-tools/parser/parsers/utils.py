import os
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib
import plotly
import pickle as pkl

"""
"""
def save_plot(fig, setup, test):
    output_file_name_pdf = gen_output_file_name(setup, test, format=".pdf")
    output_file_name_html = gen_output_file_name(setup, test, format=".html")
    output_file_name_pkl = gen_output_file_name(setup, test, format=".pkl")

    if type(fig) is plotly.graph_objs._figure.Figure:

        fig.write_image(output_file_name_pdf, width=1080, height=720)
        fig.write_html(output_file_name_html)
    elif type(fig) is matplotlib.figure.Figure:
        fig.savefig(output_file_name_pdf, dpi=300, bbox_inches='tight')
        with open(output_file_name_pkl, "bw+") as fd:
            pkl.dump(fig, fd)
    print("  -- Saved to %s" % output_file_name_pdf)


"""
    Generates the output file name for the plot
    @param setup: the setup name
    @param test: the test name
    @param mode: the mode of the data (secure or unsecure)
"""
def gen_output_file_name(setup, test, mode="", format=".pdf"):
    output_folder = "plots/" + setup
    os.makedirs(output_folder, exist_ok=True)
    output_file = output_folder+"/"

    if mode == "":
        output_file += test + format
    else:
        output_file += test + "_" + mode + format
    return output_file.replace(" ", "_")
