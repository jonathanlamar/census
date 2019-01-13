import os
import pandas as pd

state_df = pd.read_csv('../states.txt', dtype=str)

for i in state_df.index:
    state_FIPS = state_df['FIPS'].iloc[i]
    state_abbr = state_df['USPS'].iloc[i]

    # Download the shape files, unzip, and remove the .zip file
    os.system(
        'wget http://www2.census.gov/geo/tiger/GENZ2017/shp/cb_2017_'
        + state_FIPS
        + '_tract_500k.zip -P ./'
        + state_abbr
        + '/'
    )
    os.system(
        'unzip ./'
        + state_abbr
        + '/cb_2017_'
        + state_FIPS
        + '_tract_500k.zip -d ./'
        + state_abbr
        + '/'
    )
    os.system(
        'rm ./'
        + state_abbr
        + '/cb_2017_'
        + state_FIPS
        + '_tract_500k.zip'
    )
