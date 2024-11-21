#!/usr/bin/python -i

import sys
import argparse
import pickle as pkl
import matplotlib.pyplot as plt

df = None

def plot(df_param: pd.DataFrame, x, y, title):
    dt = df_param
    # plots action with time
    fig = plt.figure()
    plt.plot(dt[x], dt[y], markersize = 5.0, marker = "+")
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(title)
    plt.legend()
    plt.show()
    plt.close(fig)

def plot_actiontimeline():
    plot_title = "Action Timeline"
    # plots action with time
    fig = plt.figure()
    plt.plot(df['system_time'], df['action'], marker = "+")
    plt.xlabel("Action")
    plt.ylabel("Timeline")
    plt.title(plot_title)
    plt.legend()    
    plt.show()
    plt.close(fig)

def plot_actionsimpletimeline():
    plot_title = "Action Simple Timeline"
    # plots action with time
    fig = plt.figure()
    df2 = df[(df['action'] != ' Computing output') & (df['action'] != ' SGD step') & (df['action'] != ' Compute gradient') & (df['action'] != ' Computing Loss') & (df['action'] != ' Moving data to the same device as model')]
    print(df2['action'].unique())
    plt.plot(df2['system_time'], df2['action'], marker = "+")
    plt.xlabel("Action")
    plt.ylabel("Timeline")
    plt.title(plot_title)
    plt.legend()    
    plt.show()
    plt.close(fig)

def main():
    global df
    args = sys.argv[1:]

    if len(args) != 1:
        print("Incorrect Usage\nUsage: python database-parser [DATABASE-FILE-PATH]")

    parser = argparse.ArgumentParser(description='database-file parser')
    parser.add_argument('path', nargs='?', default='.')

    args = parser.parse_args()

    with open(args.path, "rb") as fd:
        df = pkl.load(fd)

if __name__ == "__main__":
    main()
