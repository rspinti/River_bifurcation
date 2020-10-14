# %%
import pandas as pd
import numpy as np
import geopandas as gp
import matplotlib.pyplot as plt
from shapely import wkt
import datetime
plt.style.use('classic')

# %%
# Read in the csv and set Hydroseq as the index
test = pd.read_csv("small1019.csv", index_col='Hydroseq',
                    usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                            'Pathlength', 'LENGTHKM', 'StartFlag',
                            'WKT', 'DamID'])

#extracted_HUC1019.csv
#test = pd.read_csv("small1019.csv", 
#                    usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
#                            'Pathlength', 'LENGTHKM', 'StartFlag',
#                            'WKT', 'DamID'])

# test_i=test.set_index('Hydroseq') #alternate way to set the indes
# after the fact

# add a column to keep track of steps
test.insert(5, "step", np.zeros(len(test)), True)
# fill in the NA's for the dam column with 0s
test['DamID'] = test['DamID'].fillna(0)
# Copying over the dam IDs into a new fragment column
test['Frag'] = test['DamID']
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
# STEP 1: Making fragments
# looping to make fragments
# To do - calculate fragment totals  -- total number of dams upstream
#  Total storage upstream
t1 = datetime.datetime.now()
queue = segments.loc[segments.UpHydroseq == 0]
# Initail number to use for fragments that are existing the  domain
# Rather than hitting a dam. Exiting framents will start counting from
# this number
fexit = 12
ii=0

snum=0  #Counter for the segment starting points -- just for print purposes
while len(queue) > 0:
    # Initialiazation for starting segment:
    step = 0  # start a counter for steps down the fragment
    snum = snum + 1
    temploc = queue.index[0]  # start with the segment at the top of the queue
    tempstart = temploc  # keep track of its ID for later
    templist = []   # make a list to store segments until you get to a dam
    templist.append(temploc)  # seed the list with the initial segment
    ftemp = segments.loc[temploc, 'Frag']  # Fragment # of current segment
    #dtemp = segments.loc[temploc, 'DnHydroseq']
    ii=ii+1
    print(ii)
    print("Satarting headwater #", snum, "SegID", temploc,
          "damflag", ftemp)

    # Walk downstream until you hit a dam or a segment thats
    # already been processed
    while ftemp == 0:
        step = step + 1
        dtemp = segments.loc[temploc, 'DnHydroseq']  #ID of downstream segment

        # if the downstream segment exists in the stream network then
        # walk downstream adding to the templist of stream segments
        if dtemp in segments.index:
            templist.append(dtemp)
            ftemp = segments.loc[dtemp, 'Frag']
            ii=ii+1
            print(ii)
            segments.loc[dtemp, 'step'] = step
            print("Step", step, "Downstream SegID", dtemp,
                  "Downstream Frag", ftemp)
            temploc = dtemp

        # If not then you have reached a terminal point
        # add another Fragment ID for this teminal fragment
        # And set the dam flag to the fragment ID
        else:
            print("Step", step, "Ending", temploc)
            ftemp = fexit+1  # New Fragment ID to be assigned
            fexit = fexit+1
            temploc = 0

    # print('Temploc', temploc, "Dtemp", dtemp)

    # assign the DamID fragment number to all of the segments
    segments.loc[templist, 'Frag'] = ftemp


    # If it wasn't a terminal fragment, and the downstream segment hasn't alread been assigned a FragID
    # add the downstream segment to the end of the queue
    if temploc > 0 :  
        #if segments.loc[dtemp, 'Frag'] == 0:
            newstart = segments.loc[temploc, 'DnHydroseq']
            #add to the count of dams
            #fragments.loc[ftemp, 'Ndam'] += segments.loc[temploc, 'DamCount']
            if newstart in segments.index and segments.loc[newstart, 'Frag'] == 0:
                queue = queue.append(segments.loc[newstart])
                print("Adding to Queue!", newstart)

    # delete the segment that was just finished from the queue
    queue = queue.drop(tempstart)
    print("Removing From Queue:", tempstart)
t2 = datetime.datetime.now()
print( "Segments Timing:", (t2-t1))

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
# STEP 2: Making a fragment data frame and aggregated by fragment
# Fill in fragment information
# Total fragment length calculated using a pivot table from segment lengths
fragments = segments.pivot_table('LENGTHKM', index='Frag', aggfunc=sum)

# Determining downstream segment ID --
# Join in the downstream segment for the segments that that contains the dam
# Using a pivot table with a sum here since there should only be one
# value for a each non zero DamID and the zero will not be
# included in the join
frgDN=segments.pivot_table('DnHydroseq', index='DamID', aggfunc=sum)
fragments = fragments.join(frgDN)

# Get the downstream fragment ID -
# Use the downstream segment for each fragment to get its
# downstream fragment ID
fragments2 = fragments.merge(segments.Frag, left_on='DnHydroseq',  right_on=segments.index, suffixes=('_left', '_right'), how='left')
fragments2.index = fragments.index
fragments2 = fragments2.rename(columns={'Frag': 'FragDn'})

# Identify headwater fragments  -
# Mark fragments that are headwaters
headlist = segments.loc[segments.UpHydroseq == 0, 'Frag'].unique()
fragments2['HeadFlag'] = np.zeros(len(fragments2))
fragments2.loc[headlist, 'HeadFlag'] = 1

# %%
# STEP 3 : Make a list of the upstream fragments for every fragment
#  Make a dictionary using the fragments as Keys
#  with a list for every fragment of its upstream fragments

# Initialize the dictionary
UpDict = dict.fromkeys(fragments2.index)

#Loop through and initialize every fragment list with itself
for ind in range(len(fragments2)):
    ftemp = fragments2.index[ind]
    UpDict[ftemp]=[ftemp]
    print(ftemp)

#Make a list of all the headwater fragments to start from
queuef = fragments2.loc[fragments2.HeadFlag == 1]

# Work downstream adding to the fragment lists
while len(queuef) > 0:
    DnFrag = queuef.FragDn.iloc[0]
    ftemp = queuef.index[0]
    #print("Fragment:", ftemp, "Downstream:", DnFrag)

    # if the downstream fragment exists adppend the current fagments list to it
    # and add the downstream fragment to the queue
    if not np.isnan(DnFrag):
        #print("HERE")
        UpDict[DnFrag].extend(UpDict[ftemp])
        queuef = queuef.append(fragments2.loc[DnFrag])

    #remove the current fragment from the queue
    queuef = queuef.drop(queuef.index[0])

# Remove the duplicate values in each list
for key in UpDict:
    #print(key)
    UpDict[key] = list(dict.fromkeys(UpDict[key]))

# %%
# STEP 4 - Aggregate by upstream area
fragments2['NDam'] = np.zeros(len(fragments2))
fragments2['LengthUp'] = np.zeros(len(fragments2))

for key in UpDict:
    print(key)
    fragments2.loc[key, 'NDam'] = len(UpDict[key])
    fragments2.loc[key, 'LengthUp'] = fragments2.loc[UpDict[key],
                                                     'LENGTHKM'].sum()


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
## Rachel testing the plotting to see what happens with Fragments
## Was testing HUC4 1019
fig, ax = plt.subplots(1, 2)
x = segments[segments['Frag'] <12000]  #this filter value might change 
                                  # depending on the range of vlaues for Frags
x.plot(column='Frag', ax=ax[0], legend=True)
y = segments[segments['Frag'] >12000]  #this filter value might change 
y.plot(column='Frag', ax=ax[1], legend=True)
plt.show()

# %%
