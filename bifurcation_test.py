# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import geopandas as gp
import matplotlib.pyplot as plt
from shapely import wkt
plt.style.use('classic')

# %%
# Read ub tge csv and set Hydroseq as the index
test = pd.read_csv("small1019.csv", index_col='Hydroseq',
                   usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                            'Pathlength', 'LENGTHKM', 'StartFlag',
                            'WKT', 'DamID'])
# test_i=test.set_index('Hydroseq') #alternate way to set the indes
# after the fact

# add a column to keep track of steps
test.insert(5, "step", np.zeros(len(test)), True)
# fill in the NA's for the dam column with 0s
test['DamID'] = test['DamID'].fillna(0)
# Copying over the dam IDs into a new fragment column
test['Frag'] = test['DamID']


# %%
# test.rename(columns={'WKT': 'Coordinates'}) #rename column
test2 = test.rename(columns={'WKT': 'Coordinates'})
test2.Coordinates = test2.Coordinates.astype(str)
test2['Coordinates'] = test2['Coordinates'].apply(wkt.loads)
test2Geo = gp.GeoDataFrame(test2, geometry='Coordinates')

# %%
segments = test2Geo.copy()

# %%
# make a data frame for the fragments
frag_list = segments.DamID.unique()
flength = np.zeros(len(frag_list))
fragments = pd.DataFrame(data={'flength': flength}, index=frag_list)

# %%
# looping to make fragments
# To do - calculate downtsream fragment
# iterate over this loop by making a second queue
queue = segments.loc[segments.UpHydroseq == 0]
fexit = 0
for ind in range(len(queue)):
    step = 0
    temploc = queue.index[ind]
    templist = []
    templist.append(temploc)
    damflag = segments.loc[temploc, 'Frag']
    print("Satarting headwater #", ind, "SegID", temploc)

    # Walk downstream until you hit a dam or a segment thats
    # already been processed
    while damflag == 0:
        step = step + 1
        dtemp = segments.loc[temploc, 'DnHydroseq']
        # print(dtemp)
        if dtemp in segments.index:
            templist.append(dtemp)
            damflag = segments.loc[dtemp, 'Frag']
            segments.loc[dtemp, 'step'] = step
            print("Step", step, "Downstream SegID", temploc)
            temploc = dtemp
        else:
            damflag = fexit+1
            # add an entry to the fragments DF
            s = fragments.iloc[1]
            s['flength'] = 0
            s.name = damflag
            fragments = fragments.append(s)
            fexit = fexit+1

    # assign the DamID fragment number to all of the segments
    segments.loc[templist, 'Frag'] = damflag
    # calculate the total segment lengths and add it to the fragment length
    fragments.loc[damflag]+= segments.loc[templist, 'LENGTHKM'].sum()
    print("Segement", ind, "finished. Fragment #", damflag)

# test.loc[queue.index[ind], 'step'] = istep

# %%
# %matplotlib inline
print(segments.columns)
segments['Frag'] = segments['Frag'].fillna(0)

fig, ax = plt.subplots(1, 2)
segments.plot(column='DamID', ax=ax[0], legend=True)
segments.plot(column='Frag', ax=ax[1], legend=True)
# segments.plot(column='step', ax=ax[1], legend=True)
plt.show()

# %%
# #index testing
# #ind=test.index[[1,2,50]]
# print(test.loc[550201446])
# test['LENGTHKM'][1:3]
# print(test.at[550201446, 'LENGTHKM'])
# test.at[550201446, 'LENGTHKM']= 17
