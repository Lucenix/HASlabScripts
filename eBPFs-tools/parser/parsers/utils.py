import os

"""
    Generates the output file name for the plot
    @param setup: the setup name
    @param test: the test name
    @param mode: the mode of the data (secure or unsecure)
"""
def gen_output_file_name(setup, test, mode=""):
    output_folder = "plots/" + setup
    os.makedirs(output_folder, exist_ok=True)
    output_file = output_folder+"/"
    if mode == "":
        output_file += test + ".pdf"
    else:
        output_file += test + "_" + mode + ".pdf"
    return output_file.replace(" ", "_")