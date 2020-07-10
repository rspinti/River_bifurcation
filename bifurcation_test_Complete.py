# %%
import pandas as pd
import numpy as np
import geopandas as gp
import matplotlib.pyplot as plt
from shapely import wkt
plt.style.use('classic')

# %%
# Read in the csv and set Hydroseq as the index
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
# make a column to indicate if a dam is present or not
test['DamCount'] = np.zeros(len(test))
test.loc[test.DamID>0, 'DamCount'] = 1


# %%
# test.rename(columns={'WKT': 'Coordinates'}) #rename column
test2 = test.rename(columns={'WKT': 'Coordinates'})
test2.Coordinates = test2.Coordinates.astype(str)
test2['Coordinates'] = test2['Coordinates'].apply(wkt.loads)
test2Geo = gp.GeoDataFrame(test2, geometry='Coordinates')

segments = test2Geo.copy()

# %%
<<<<<<< HEAD
# STEP 1: Making fragments
=======
""" ## Dont need to do this anymore
## make a data frame for the fragments
#frag_list = segments.DamID.unique()
##flength = np.zeros(len(frag_list))
#fragments = pd.DataFrame(data={'flength': np.zeros(len(frag_list)),
#    'Ndam': np.zeros(len(frag_list)),
#    'DnSeg': np.zeros(len(frag_list))}, index=frag_list) """

# %%
>>>>>>> b08e31685550f82f28299a0f20cbffcae358162c
# looping to make fragments
# To do - calculate fragment totals  -- total number of dams upstream
#  Total storage upstream

queue = segments.loc[segments.UpHydroseq == 0]
# Initail number to use for fragments that are existing the  domain
# Rather than hitting a dam. Exiting framents will start counting from
# this number
fexit = 11
# for ind in range(len(queue)):
# for ind in range(len(queue)):
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
    #fragments.loc[ftemp, 'Ndam'] += segments.loc[temploc, 'DamCount']
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
            # add an entry to the fragments DF
            """ s = fragments.iloc[1]
            s['flength'] = 0
            s.name = ftemp
            fragments = fragments.append(s) """
            fexit = fexit+1
            temploc = 0

    # print('Temploc', temploc, "Dtemp", dtemp)

    # assign the DamID fragment number to all of the segments
    segments.loc[templist, 'Frag'] = ftemp

    # calculate the total segment lengths and add it to the fragment length
    # fragments.loc[damflag]+= segments.loc[templist, 'LENGTHKM'].sum()
    # print("Segement", ind, "finished. Fragment #", damflag,
    # 'Adding to length:', segments.loc[templist, 'LENGTHKM'].sum() )

    # If it wasn't a terminal fragment
    # add the downstream segment to the end of the queue
    if temploc > 0:
        newstart = segments.loc[temploc, 'DnHydroseq']
        #add to the count of dams
        #fragments.loc[ftemp, 'Ndam'] += segments.loc[temploc, 'DamCount']
        if newstart in segments.index:
            queue = queue.append(segments.loc[newstart])
            print("Adding to Queue!", newstart)

    # delete the segment that was just finished from the queue
    queue = queue.drop(tempstart)
    print("Removing From Queue:", tempstart)

# test.loc[queue.index[ind], 'step'] = istep

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

<<<<<<< HEAD
# Determining downstream segment ID -- 
# Join in the downstream segment for the segments that that contains the dam
# Using a pivot table with a sum here since there should only be one 
=======
#Join in the downstream segment for the segmane that contains the dam
# Using a pivot table with a sum here since there should only be one
>>>>>>> b08e31685550f82f28299a0f20cbffcae358162c
# value for a each non zero DamID and the zero will not be
# included in the join
frgDN=segments.pivot_table('DnHydroseq', index='DamID', aggfunc=sum)
fragments = fragments.join(frgDN)

# Get the downstream fragment ID - 
# Use the downstream segment for each fragment to get its
# downstream fragment ID
fragments2 = fragments.merge(segments.Frag, left_on='DnHydroseq',  right_on='Hydroseq', suffixes=('_left', '_right'), how='left')
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
    print("Fragment:", ftemp, "Downstream:", DnFrag)

    # if the downstream fragment exists adppend the current fagments list to it
    # and add the downstream fragment to the queue
    if not np.isnan(DnFrag):
        print("HERE")
        UpDict[DnFrag].extend(UpDict[ftemp])
        queuef = queuef.append(fragments2.loc[DnFrag])
    
    #remove the current fragment from the queue
    queuef = queuef.drop(queuef.index[0])


<<<<<<< HEAD
# Remove the duplicate values in each list
for key in UpDict:
    print(key)
    UpDict[key] = list(dict.fromkeys(UpDict[key]))
=======
#Next need to get aggregations by upstream area for fragments.
>>>>>>> b08e31685550f82f28299a0f20cbffcae358162c

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
<<<<<<< HEAD
=======

#Plot where dams are
colors = []
for i in range(len(segments)):
    if (pd.isnull(segments['DamID'][i])):
        colors.append('b')
    else:
        colors.append('r')

segments.plot(color=colors)
# plt.savefig('Small_dataset.png', dpi = 500)
plt.show()

# %%
# #index testing
# #ind=test.index[[1,2,50]]
# print(test.loc[550201446])
# test['LENGTHKM'][1:3]
# print(test.at[550201446, 'LENGTHKM'])
# test.at[550201446, 'LENGTHKM']= 17
>>>>>>> b08e31685550f82f28299a0f20cbffcae358162c
