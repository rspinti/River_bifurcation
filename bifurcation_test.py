# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import geopandas as gp
import matplotlib.pyplot as plt
from shapely import wkt
from pathlib import Path
gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/GIS/Layers/NHDPlusNationalData") #where csv live
plt.style.use('classic')

# %%
# Read in the csv and set Hydroseq as the index
## test with only flowline attributes
# test = pd.read_csv("small1019.csv", index_col='Hydroseq',
#                    usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
#                             'Pathlength', 'LENGTHKM', 'StartFlag',
#                             'WKT', 'DamID'])
## test with dams and flowlines
test = pd.read_csv(gdrive/"sample_nabd_nhd.csv", index_col='Hydroseq',
                   usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                            'Pathlength', 'LENGTHKM', 'StartFlag',
                            'WKT', 'DamID'])
# test_i=test.set_index('Hydroseq') #alternate way to set the index
# after the fact

# add a column to keep track of steps
test.insert(5, "step", np.zeros(len(test)), True)
# fill in the NA's for the dam column with 0s
test['DamID'] = test['DamID'].fillna(0)
test.DamID = test.DamID.astype(int)
# print(test.DamID.unique())
# Copying over the dam IDs into a new fragment column
test['Frag'] = test['DamID']


# %%
# test.rename(columns={'WKT': 'Coordinates'}) #rename column
test2 = test.rename(columns={'WKT': 'Coordinates'})          #rename column
test2.Coordinates = test2.Coordinates.astype(str)            #change datatype to string
test2['Coordinates'] = test2['Coordinates'].apply(wkt.loads) #use the wkt package
test2Geo = gp.GeoDataFrame(test2, geometry='Coordinates')    #Make gdf

# %%
segments = test2Geo.copy()   #create segments
# segments.insert(10, "upstream_count", np.zeros(len(segments)), True)
# %%
# make a data frame for the fragments
frag_list = segments.DamID.unique()   #grab unique dam IDs
flength = np.zeros(len(frag_list))    #create numpy array with length of frag_list
fragments = pd.DataFrame(data={'flength': flength}, index=frag_list) #add flength to fragments df

# %%
# looping to make fragments
# To do - calculate downstream fragment
# iterate over this loop by making a second queue
queue = segments.loc[segments.UpHydroseq == 0]   #start with headwaters
fexit = 0     #variable to tell the for loop to exit
for ind in range(len(queue)):   #go through queue
    step = 0                    #set the step number
    temploc = queue.index[ind]  # set index to ind?
    templist = []               #create empty list to fill
    templist.append(temploc)    #add current ind to list
    damflag = segments.loc[temploc, 'Frag']  #create damflag, which has 'Frag'?
    print("Starting headwater #", ind, "SegID", temploc)  #print the step out

    # Walk downstream until you hit a dam or a segment thats
    # already been processed
    while [damflag == 0]:   #while there is no damID
        step = step + 1   #next step
        dtemp = segments.loc[temploc, 'DnHydroseq']  #select downstream flowline
        # print(dtemp)
        if dtemp in segments.index:  #if that flowline is in the segmentsindex?
            templist.append(dtemp)   #add downstream flowline to templist
            damflag = segments.loc[dtemp, 'Frag']  #select the Fragment ID for dam we will hit?
            segments.loc[dtemp, 'step'] = step     #tell the step we are on
            # segments.loc[dtemp, 'upstream_count'] = 1
            print("Step", step, "Downstream SegID", temploc)  #print the step and downstream ID
            temploc = dtemp   #reset now
        else:
            damflag = fexit+1  #if there is a dam, exit now and start new list
            # add an entry to the fragments DF, this is the 1.0 we see, which is looking for the next ID
            s = fragments.iloc[1]
            s['flength'] = 0
            s.name = damflag
            fragments = fragments.append(s)
            fexit = fexit+1

    # assign the DamID fragment number to all of the segments
    segments.loc[templist, 'Frag'] = damflag
    # calculate the total segment lengths and add it to the fragment length
    fragments.loc[damflag]+= segments.loc[templist, 'LENGTHKM'].sum()
    print("Segment", ind, "finished. Fragment #", damflag)

# test.loc[queue.index[ind], 'step'] = istep
    
    

# %%
# %matplotlib inline
print(segments.columns)
segments['Frag'] = segments['Frag'].fillna(0)
print(fragments.head(10))

fig, ax = plt.subplots(1, 2)
# segments.plot(column='LENGTHKM', ax=ax[0], legend=True)
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
