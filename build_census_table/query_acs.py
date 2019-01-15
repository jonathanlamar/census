import sys
import os
import pickle
import pandas as pd

def run_queries(categories):
    # Grabbing state names for readability.
    state_df = pd.read_csv(DATAPATH + 'states.txt', dtype=str)
    # Curling the jsons
    for i in state_df.index:
        state_name = state_df.iloc[i].loc['Name']
        state_fips = state_df.iloc[i].loc['FIPS']
        state_abbr = state_df.iloc[i].loc['USPS']
        print('Curling json for ' + state_name + '...')
        for category in categories:
            print(category + '...')
            query = get_query(category)
            os.system(
                'curl "'
                + query
                + state_fips
                + KEYSTRING
                + '" > '
                + DATAPATH
                + 'json/'
                + category
                + '_'
                + state_abbr
                + '.json'
            )

def get_query(category):
    query_vars = QUERY_VARS[category]
    the_query = URL_PREFIX
    for var in query_vars:
        the_query += (var + ',')
    the_query = the_query[:-1]
    the_query += URL_SUFFIX
    return the_query

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise KeyError('Not enough arguments.  You must at least pass an API key.')

    # Change this if you want to store data somewhere else.
    DATAPATH = '../data/'

    # We need to query the census API for the following data fields.
    # I found these column names by searching https://api.census.gov/data/2015/acs5/variables.html
    # I started using 2015 data because it was the only year that I could get queries from without
    # bouncing.  TODO: Update to 2017 (or 2018 if available) ACS 5 year survey.  Some or all variables
    # will need to be renamed.  That will take a bit of time to adjust the query, but the basic format
    # should be the same.

    print('Prepping API queries...')

    # These queries are time consuming, but they only need to be run once.
    QUERY_VARS = {
        'population' : ['B01001_00' + str(n) + 'E' for n in range(1, 10)] 
            + ['B01001_0' + str(n) + 'E' for n in range(10, 50)],
        'income' : ['B19001_00' + str(n) + 'E' for n in range(2, 10)]
            + ['B19001_0' + str(n) + 'E' for n in range(10, 18)],
        'household' : ['B11011_00' + str(n) + 'E' for n in range(1, 10)]
            + ['B11011_0' + str(n) + 'E' for n in range(10, 20)]
            + ['B25003_002E', 'B25003_003E'],
        'tenure' : ['B25026_00' + str(n) + 'E' for n in range(2, 10)]
            + ['B25026_0' + str(n) + 'E' for n in range(10, 16)],
        'marriage' : ['B12001_00' + str(n) + 'E' for n in [3, 4, 9]]
            + ['B12001_0' + str(n) + 'E' for n in [10, 12, 13, 18, 19]],
        'education' : ['B15003_00' + str(n) + 'E' for n in range(2, 10)]
            + ['B15003_0' + str(n) + 'E' for n in range(10, 26)],
        'race' : ['B01001' + letter + '_001E' for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']]
    }

    # Make sure you get one of these first.
    api_key = sys.argv[1]
    categories = sys.argv[2:]

    URL_PREFIX = 'https://api.census.gov/data/2015/acs5?get=' # prefix for all curl statements
    URL_SUFFIX = '&for=tract:*&in=state:' # suffix (+ state code + API key)
    KEYSTRING = '&key=' + api_key

    run_queries(categories)
