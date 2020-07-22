# %%
import pandas as pd
import numpy as np
import geopandas as gp
import matplotlib.pyplot as plt
import bifurcate as bfc
from shapely import wkt
plt.style.use('classic')

# %%
# Read in the csv and set Hydroseq as the index
test = pd.read_csv("small1019.csv", index_col='Hydroseq',
                    usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                           'Pathlength', 'LENGTHKM', 'StartFlag',
                            'WKT', 'DamID'])

#test = pd.read_csv("small1019.csv", 
#                   usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
#                            'Pathlength', 'LENGTHKM', 'StartFlag',
#                            'WKT', 'DamID'])
# test_i=test.set_index('Hydroseq') #alternate way to set the indes
# after the fact

# add a column to keep track of steps
test.insert(5, "step", np.zeros(len(test)), True)
# fill in the NA's for the dam column with 0s
test['DamID'] = test['DamID'].fillna(0)
# Copying over the dam IDs into a new fragment column
#Making adding this step to the function so its not needed here
#test['Frag'] = test['DamID']
# make a column to indicate if a dam is present or not
test['DamCount'] = np.zeros(len(test))
test.loc[test.DamID>0, 'DamCount'] = 1

# Fix the hydroseq columns, so they are integers
#test['UpHydroseq'] = test['UpHydroseq'].round(decimals=0)
#test['DnHydroseq'] = test['DnHydroseq'].round(decimals=0)
#test['Hydroseq'] = test['Hydroseq'].round(decimals=0)
#test.set_index('Hydroseq')

# %%
# test.rename(columns={'WKT': 'Coordinates'}) #rename column
test2 = test.rename(columns={'WKT': 'Coordinates'})
test2.Coordinates = test2.Coordinates.astype(str)
test2['Coordinates'] = test2['Coordinates'].apply(wkt.loads)
test2Geo = gp.GeoDataFrame(test2, geometry='Coordinates')

segments = test2Geo.copy()

# %%
#reload the Bifucate module --- for testing
import importlib
importlib.reload(bfc)

#%%
# STEP1:  Make Fragments
segments=bfc.make_fragments(segments, exit_id=11)

# STEP 2: Making a fragment data frame and aggregated by fragment
fragments = bfc.agg_by_frag(segments)

# STEP 3: Map Upstream Fragments 
UpDict = bfc.map_up_frag(fragments)

#STEP 4: Aggregate by upstream area
fragments=bfc.agg_by_frag_up(fragments, UpDict)


# %%
# Some plotting
#print(segments.columns)
#segments['Frag'] = segments['Frag'].fillna(0)

fig, ax = plt.subplots(1, 2)
segments.plot(column='DamID', ax=ax[0], legend=True)
segments.plot(column='Frag', ax=ax[1], legend=True)
#segments.plot(column='step', ax=ax[1], legend=True)
plt.show()

# %%
# Doing some summaries to cross check calculations
#print(fragments)
print(segments.loc[segments.Frag == 0]) #check for any segments not covered
temp = segments.pivot_table('LENGTHKM', index='Frag', aggfunc=sum)
print(temp)
print(sum(temp['LENGTHKM']))
print(sum(segments.LENGTHKM))
# alternate approach to pivot tabel
# segments.groupby('Frag')[['LENGTHKM']].sum()


# %%
## Rachel testing the plotting to see what happens with Fragments
## Was testing HUC4 1019
fig, ax = plt.subplots(1, 2)
x = segments[segments['Frag'] <12000]  #this filter value might change 
                                  # depending on the range of vlaues for Frags
x.plot(column='Frag', ax=ax[0], legend=True)
y = segments[segments['Frag'] >12000]  #this filter value might change 
y.plot(column='Frag', ax=ax[1], legend=True)
plt.show()
