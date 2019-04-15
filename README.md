# Census

## Generating the dataset
I would imagine I can find better ways of getting a census dataset indexed by GEOID, but I settled on using the 2015 ACS, which has a web API.  This survey has thousands of fields available, all indexed by GEOID.

### How to build the dataset.
1. Make the directories `./data/` and `./data/json/`.  These will not be synced by the repo.
2. Go [here](https://api.census.gov/data/key_signup.html) and get an API key for the census API.  Check your email and copy the key.
3. Go to `./build_census_table/` and run the command `python query_acs.py <API key> population income household tenure marriage education`, where `<API key>` is the key you received from the census bureau.  Go get coffee while this runs (It should take a few minutes).
4. Run the command `python build_table.py population income household tenure marriage education` to build the table.  This will not take as much time.
5. Boot up the jupyter notebook `Rename Columns.ipynb` and execute it.  This renames the columns to something sensible.

#### Shape files
Shape files for every census tract in the US can be found [here](https://www.census.gov/geo/maps-data/data/cbf/cbf_tracts.html).  I added a script in `./data/shapefiles` to scrape this page for you - all you should have to do is run `python get_shapefiles.py`.  It is written for mac, but could easily be changed to work on linux.  I plan to use the shapefiles for some fun visuals, but I havenn't planned out anything yet.

## Glossary of Terms
1. GEOID.  See [here](https://www.census.gov/geo/reference/geoidentifiers.html)
2. ACS.  The American Community Survey.  See [here](https://en.wikipedia.org/wiki/American_Community_Survey).  We are using the 2015 5 year estimates to build our dataset.
