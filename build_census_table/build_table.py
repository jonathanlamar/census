import pandas as pd
import pickle
import os
import sys

def build_table(categories):
    dataframes = {}
    for category in categories.keys():
        if categories[category]:
            print('Loading ' + category + ' data into one dataframe...')
            dataframes[category] = build_factor(category)
            print('Done.')
        else:
            print('Loading pre-computed ' + category + ' ddataframe...')
            eval(category + '_df.to_csv(DATAPATH + \'' + category + '_df.csv\', index=False)')

    print('Checking compatible dimensions...')
    for category in dataframes.keys():
        print(category + ' df has {0} rows.'.format(dataframes[category].shape[0]))

    num_rowcounts = len(set([ df.shape[0] for df in dataframes.values()]))
    if num_rowcounts > 1:
        raise RuntimeError('Incompatible row counts.')
    else:
        print('Done.')

    print('Merging dataframes...')
    census_df = dataframes.pop('population')
    for df in dataframes.values():
        census_df = census_df.merge(
            df.drop(['state','county','tract'], axis=1),
            how='inner',
            left_index=True,
            right_index=True
        )
    print('Done.')

    # There should be a jupyter notebook in this directory with some column names already in it.
    print('Saving dataframe (Don\'t forget to rename columns to something sensible)...')
    census_df.to_csv(DATAPATH + 'census_geoid.csv')
    print('Done.')

def build_factor(category):
    # Load the first state as an accumulator.
    acc_df = read_format_json(category, 'AK')
    for i in STATE_DF.index[1:]:
        state_abbr = STATE_DF.iloc[i].loc['USPS']
        df0 = read_format_json(category, state_abbr)
        acc_df = pd.concat([acc_df, df0], axis=0)

    # We want to have a dataset indexed by GEOID.
    se = (acc_df['state'].astype(str)
     + acc_df['county'].astype(str)
     + acc_df['tract'].astype(str)).rename('geo_id')
    if any(se.apply(lambda x: len(x)) != 11):
        raise RuntimeError('Some of the GEOID strings in ' + category + '_df are the wrong length.')
    acc_df.index = se
    acc_df.to_csv(DATAPATH + category + '_df.csv', index=False)
    return acc_df

def read_format_json(category, state_abbr):
    df0 = pd.read_json(DATAPATH + 'json/' + category + '_' + state_abbr + '.json')
    
    # Partially format column names.  They are initially stored as the first row of df0.
    # We can get the ACS field names from variables.json.  These are ugly and will be
    # changed later, but they are a start.
    df0.iloc[0][:-3] = df0.iloc[0][:-3].apply(lambda x: VARIABLES_DF.loc[x, 'variables']['label'])
    df0.columns = df0.iloc[0]
    return df0.drop(0, axis=0)

# I don't know why I chose to write it this way...
if __name__ == '__main__':
    DATAPATH = '../data/'
    STATE_DF = pd.read_csv(DATAPATH + 'states.txt', dtype=str)

    # For some reason this is super slow.  Better to just save the json from chrome.
    #print('Curling variables json...')
    #os.system('curl "https://api.census.gov/data/2015/acs5/variables.json" > ' + DATAPATH + 'json/variables.json')
    print('Done.\nLoading variables json to df...')
    VARIABLES_DF = pd.read_json(DATAPATH + 'json/variables.json')
    print('Done.')

    categories = {
        'population' : ('population' in sys.argv),
        'income' : ('income' in sys.argv),
        'household' : ('household' in sys.argv),
        'tenure' : ('tenure' in sys.argv),
        'marriage' : ('marriage' in sys.argv),
        'education' : ('education' in sys.argv)
    }

    build_table(categories)
