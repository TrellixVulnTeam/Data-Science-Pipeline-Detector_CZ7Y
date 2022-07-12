"""
This script takes successively larger subsets of the whole numeric data set and compares their histograms to
the histogram generated by the whole data set. We consider a poorly representative sample to be one with alot
of area between its histogram and the histogram of the whole sample. Similarly, a good sample size is one which
generates a histogram whose area differs very little from the histogram of the whole data set.

To do:
** Extend the script so it easily makes this sort of plot for all columns.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def load_df(file, batch_size=10000, skip=1):
    """
    Thanks to Alex Galea
    https://www.kaggle.com/agalea91/bosch-production-line-performance/numerical-feature-density-anomaly-detection
    """
    reader = pd.read_csv(file, chunksize=batch_size, dtype=np.float64, usecols = [1])
    df = pd.concat((chunk for i, chunk in enumerate(reader) if (i % skip) == 0))
    return df

try:
    import sys
    train_numeric_file = sys.argv[1]
except:
    train_numeric_file = "../input/train_numeric.csv"

df1 = load_df(train_numeric_file, batch_size=1000, skip=1)

def make_comparison_plots(plotname, df1, data_file, skip_number):
    n_plots = 4
    f, axarr = plt.subplots(2, 2, figsize=(15, 15))
    area_between_histograms = 0.0
    for i in range(n_plots//2):
        for j in range(n_plots//2):
            df2 = load_df(data_file, batch_size=1000, skip=skip_number)
            n_bins = np.linspace(df1.L0_S0_F0.min(), df1.L0_S0_F0.max(), len(df1.L0_S0_F0.unique()))
            values1, bins1, _ = axarr[i, j].hist(df1.L0_S0_F0, n_bins, range=(n_bins.min(), n_bins.max()), alpha=0.5, normed=True, label="{} rows".format(len(df1)))
            values2, bins2, _ = axarr[i, j].hist(df2.L0_S0_F0, n_bins, range=(n_bins.min(), n_bins.max()), alpha=0.5, normed=True, label="{} rows".format(len(df2)))
            area_between_histograms += sum(np.diff(bins1)*np.abs(values1 - values2))
            axarr[i, j].legend(loc='upper left')
            axarr[i, j].set_xlabel("Bins")
            axarr[i, j].set_ylabel("Normalized Counts")
            axarr[i, j].set_title("Comparison")
    avg_area_between_histograms = area_between_histograms / n_plots
    #axarr[2, 0].axis('off')
    #axarr[2, 1].axis('off')
    #plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
    f.text(0.02, 0.02, "Area between hists: {}".format(avg_area_between_histograms))
    plt.savefig(plotname)

make_comparison_plots("skip10000", df1, train_numeric_file, 10000)
make_comparison_plots("skip1000", df1, train_numeric_file, 1000)
make_comparison_plots("skip100", df1, train_numeric_file, 100)
make_comparison_plots("skip10", df1, train_numeric_file, 10)
