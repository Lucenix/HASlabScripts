import os
import matplotlib
import plotly
import pickle as pkl

"""
"""
def save_plot(fig, setup, test):
    output_file_name = gen_output_file_name(setup, test, format="")

    if type(fig) is plotly.graph_objs._figure.Figure:

        fig.write_image(f'{output_file_name}.pdf', width=1080, height=720)
        fig.write_html(f'{output_file_name}.html')
        print("  -- Saved to %s" % f'{output_file_name}.pdf/html')

    elif type(fig) is matplotlib.figure.Figure:
        fig.savefig(f'{output_file_name}.pdf', dpi=300, bbox_inches='tight')
        with open(f'{output_file_name}.pkl', "bw+") as fd:
            pkl.dump(fig, fd)
        print("  -- Saved to %s" % f'{output_file_name}.pdf/pkl')
    
    else:
        raise Exception("Invalid figure type") 


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
