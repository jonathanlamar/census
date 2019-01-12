import sys
import pandas as pd
import numpy as np
from bracket_comp import BinnedDataMetrics # Our methods for comparing Binned data

###########################################################################
# This script applies various metrics defined in class BinnedDataMetrics in
# bracket_comp.py to the binned data (e.g. income, education, tenure).
###########################################################################
def main(which_data, **kwargs):
    p = kwargs['p']
    # Force the geo_id column to load as string to preserve leading zeros.
    join_df = pd.read_csv(OUTPATH + 'join_df.csv', dtype={'geo_id' : str})
    if which_data == 'income':
        # Get the columns and midpoitns, etc. for just income information.
        print('Setting midpoints and getting columns.')
        midpoints = np.array([7500, 17500, 25000, 35000, 45000, 62500, 87500, 112500, 132500, 175000, 200000])
        cols = join_df.columns
        census_cols = [c for c in cols if c.find('census HH income') == 0]
        demo_cols = [c for c in cols if c.find('demo HH income') == 0]
    else:
        raise NotImplementedError('The keyword \'' + which_data + '\' is not understood.  Some are under construction.')

    # Get just the columns we need, with the index we need.
    tmp_df = join_df[
        ['geo_id'] + census_cols + demo_cols
    ].copy()


    # The data we collect will be stored here.
    data_dict = {'geo_id' : tmp_df['geo_id']}

    # Compute Brock's metric, both in absolute and relative terms.
    for abs_or_rel, norm_first in zip(['abs. overest. metric', 'rel. overest. metric'], [False, True]):
        print('Computing ' + abs_or_rel + '...')
        data_dict[abs_or_rel] = tmp_df.apply(
            lambda row:
            BinnedDataMetrics.overestimate_expectation(
                row[census_cols].values,
                row[demo_cols].values,
                midpoints,
                normalize_first=norm_first
            ),
            axis=1,
            result_type='reduce'
        )

    print('Computing avg. abs. error...')
    data_dict['avg. abs. error'] = tmp_df.apply(
        lambda row:
        BinnedDataMetrics.avg_abs_err(
            row[census_cols].values,
            midpoints
        ),
        axis=1,
        result_type='reduce'
    )

    for rel_or_not, norm_Lp in zip(['relative', 'absolute'], [True, False]):
        print('Computing ' + rel_or_not + ' L' + str(p) + ' error...')
        data_dict[rel_or_not + ' L' + str(p) + ' error'] = tmp_df.apply(
            lambda row:
            BinnedDataMetrics.lebesgue(
                row[census_cols].values,
                row[demo_cols].values,
                p=p,
                normalize_first=norm_Lp
            ),
            axis=1,
            result_type='reduce'
        )

    # Save output for jupyter notebook.
    print('Saving output.')
    metrics_df = pd.DataFrame(data=data_dict)
    metrics_df.to_csv(OUTPATH + which_data + '_metrics_df.csv', index=False)

if __name__ == '__main__':
    # Out output will be used by a jupyter notebook in the following directory.
    OUTPATH = '../../jupyter/demo_validation_notebook/out/'
    if len(sys.argv) < 2:
        raise KeyError('Not enough arguments.')
    else:
        which_data = sys.argv[1]
        if which_data not in ['income', 'education', 'tenure']:
            raise KeyError('I don\'t understand what ' + which_data + ' means.  Please pass one of \'income\', \'education\', or \'tenure\'.')
        else:
            # The parameter should be uniform across the different sets of binned variables.
            main(which_data, p=1)
