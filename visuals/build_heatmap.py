import pandas as pd
import numpy as np
import sys
import pickle

#########################################################################################
# This script builds a heatmap (represented as a square numpy array) of the values of one
# of the metrics for binned data in the class BinnedDataMetrics in bracket_comp.py.  The
# values will be arranged using indices generated in the function make_index, which
# arrange the values in such a way that the worst (largest) values of the metric are
# clustered in the bottom right corner of the array, and the best (smallest) values are
# along the left and top edges.
#########################################################################################
def main(metrics_df, which_metric, square_dim, algorithm='spiral'):
    if square_dim**2 != metrics_df.shape[0]:
        raise RuntimeError('Square dimensions do not match number of rows...')

    # make_index returns a square array with indices increasing bottom-right to top-left: e.g.
    # make_index(4)
    # array([[15., 13., 11.,  9.],
    #        [14.,  8.,  6.,  4.],
    #        [12.,  7.,  3.,  1.],
    #        [10.,  5.,  2.,  0.]])
    # We do the flipping outside to preserve the tail recursion.
    index_array = -1*make_index(square_dim) + square_dim**2 - 1

    # metric_array holds the actual values of the metric in the desired order and shape
    # in case they are needed. However, quintile_array will be used for the colormap in
    # the jupyter notebook.
    metric_array = np.zeros((square_dim, square_dim))
    quintile_array = np.zeros((square_dim, square_dim))

    num_cells = square_dim**2
    current_quintile = 0
    for i in range(num_cells):
        if i > (current_quintile + 1) * 0.2 * num_cells:
            current_quintile += 1
        r, c = np.unravel_index((index_array == i).argmax(), (square_dim, square_dim))
        metric_array[r, c] = metrics_df[which_metric].values[i]
        quintile_array[r, c] = current_quintile
    return metric_array, quintile_array

# Deprecated.  Saving because it's neat.
def make_sqiral(dim):
    def loop(acc, to_add):
        if to_add == 0:
            return acc
        else:
            N = acc.shape[0]
            if acc.shape[1] != N:
                raise RecusionError('Error in recursion.')
            new_acc = np.zeros((N+1, N+1))
            new_acc[1:, 1:] = acc
            entry = N**2
            for i in range(N, -1, -1):
                new_acc[i, 0] = entry
                entry += 1
            for i in range(1, N+1):
                new_acc[0, i] = entry
                entry += 1
            return loop(new_acc, to_add - 1)
    return loop(np.zeros((0, 0)), dim)

def make_index(dim):
    def loop(acc, to_add):
        if to_add == 0:
            return acc
        else:
            N = acc.shape[0]
            if acc.shape[1] != N:
                raise RecusionError('Error in recursion.')
            new_acc = np.zeros((N+1, N+1))
            new_acc[1:, 1:] = acc
            entry = N**2
            for i in range(N, -1, -1):
                new_acc[0, i] = entry
                entry += 2
            entry = N**2 + 1
            for i in range(N, 0, -1):
                new_acc[i, 0] = entry
                entry += 2
            return loop(new_acc, to_add - 1)
    if dim == 0:
        return np.zeros((0, 0))
    else:
        return loop(np.zeros((1, 1)), dim - 1)

# Putting all of the bookkeeping junk here.
if __name__ == '__main__':
    # Out output will be used by a jupyter notebook in the following directory.
    OUTPATH = '../../jupyter/demo_validation_notebook/out/'

    if len(sys.argv) < 3:
        raise KeyError('Not enough arguments.')

    which_data = sys.argv[1]
    which_metric = sys.argv[2]
    if which_data not in ['income', 'education', 'tenure']:
        raise KeyError('I don\'t understand what ' + which_data + ' means.  Please pass one of \'income\', \'education\', or \'tenure\'.')

    print('Loading dataframes...')
    join_df = pd.read_csv(OUTPATH + 'join_df.csv', dtype={'geo_id' : str})
    metrics_df = pd.read_csv(OUTPATH + which_data + '_metrics_df.csv', dtype={'geo_id' : str})

    if which_metric not in list(metrics_df.columns[1:]):
        raise KeyError('I don\'t understand what \'' + which_metric + '\' means.  Please pass one of \'income\', \'education\', or \'tenure\'.')

    # Filter only tracts where charter subs count for at least half of the census population.
    print('Joining...')
    join_df['charter_saturation'] = join_df['population lower bound'] / join_df['Total Population']
    metrics_df = metrics_df.merge(
        join_df[['geo_id', 'charter_saturation']],
        how='left',
        left_on='geo_id',
        right_on='geo_id'
    )
    print('Filtering...')
    metrics_df = metrics_df.loc[
        metrics_df['charter_saturation'] >= 0.5,
        ['geo_id', 'charter_saturation', which_metric]
    ].sort_values(by='charter_saturation')
    metrics_df = metrics_df[metrics_df['charter_saturation'] != np.inf] # Drop bad values.  Should only be a few.

    # Depending on the metric, there may be an unreasonable number of cells with trivial values.
    if which_metric in ['abs. overest. metric', 'rel. overest. metric']:
        print('Dropping zeros...')
        metrics_df = metrics_df[metrics_df[which_metric] > 0]

    # Trim to make sure the number of rows is a square.
    num_tracts = metrics_df.shape[0]
    square_dim = int(np.sqrt(num_tracts))
    metrics_df = metrics_df.iloc[-square_dim**2:].sort_values(by=which_metric, ascending=True)

    metric_array, quintile_array = main(metrics_df, which_metric, square_dim)
    print('Saving output...')
    with open(OUTPATH + which_data + '_(' + which_metric + ')_metric.out', 'wb') as f:
        pickle.dump(metric_array, f)
    with open(OUTPATH + which_data + '_(' + which_metric + ')_quintile.out', 'wb') as f:
        pickle.dump(quintile_array, f)
