# %%
import pandas as pd
import numpy as np
import geopandas as gp
import matplotlib.pyplot as plt
# import bokeh
import extract as ex
from shapely import wkt
plt.style.use('classic')

from pathlib import Path
gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/GIS/Layers") #where shapefiles/csv live 

name = ex.my_function()
# %%
# # Read in the csv and set Hydroseq as the index
# ## Specify the run_name...
run_name = 'Red'  

# ## What was working, but was a bug
# test = pd.read_csv("small1019.csv", index_col='Hydroseq',
#                     usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
#                             'Pathlength', 'LENGTHKM', 'StartFlag',
#                             'WKT', 'DamID'])

# # Runs the extracted test basin, which does not have errors in the data from 
# # conversion from shapefile
nabd_nhd_join = pd.read_csv('extracted_HUC1019.csv',
                    usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                            'Pathlength', 'LENGTHKM', 'StartFlag', 
                            'WKT', 'DamID', 'Norm_stor'])

# # Fix: take out the index_col
# test = pd.read_csv(run_name+'.csv',usecols=['Hydroseq', 'UpHydroseq', 
#                                             'DnHydroseq','Pathlength', 
#                                             'LENGTHKM', 'StartFlag',
#                                             'WKT', 'DamID'])


# # #took out the index column for now
# test = pd.read_csv(gdrive/'NHDPlusNationalData/sample_nabd_nhd.csv',
#                     usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
#                             'Pathlength', 'LENGTHKM', 'StartFlag',
#                             'WKT', 'DamID'])


# # test_i=test.set_index('Hydroseq') #alternate way to set the indices
# # after the fact

## add a column to keep track of steps
nabd_nhd_join.insert(5, "step", np.zeros(len(nabd_nhd_join)), True)

## Filtering the Hydroseq, storage, and dam count
#Group by Hydroseq and sum the storage
storage_sum = nabd_nhd_join.groupby(['Hydroseq'])['Norm_stor'].sum().reset_index()

#Count # of duplicate dams
nabd_nhd_join['DamCount'] = np.zeros(len(nabd_nhd_join))
dam_count = nabd_nhd_join.pivot_table(index=['Hydroseq'], aggfunc={'DamCount':'size'}).reset_index()

#Merge count and storage dataframes
count_sum_merge = storage_sum.merge(dam_count, how= 'left', on='Hydroseq')  #merge count and sum 

#Keep only the last Hydroseq
nabd_nhd_filtered = nabd_nhd_join.drop_duplicates(subset='Hydroseq', keep="last")  #drop everything but last duplicate
nabd_nhd_filtered = nabd_nhd_filtered.drop(columns=['Norm_stor', 'DamCount'])  #drop Norm_stor

# #Merge the dataframes so the storage and DamIDs are how we want
nabd_nhd_join = nabd_nhd_filtered.merge(count_sum_merge, how= 'left', on='Hydroseq') # Merge NABD and NHD

## fill in the NA's for the dam column with 0s
nabd_nhd_join['DamID'] = nabd_nhd_join['DamID'].fillna(0)

## make a column to indicate if a dam is present or not
nabd_nhd_join.loc[nabd_nhd_join.DamID==0, 'DamCount'] = 0

# Copying over the dam IDs into a new fragment column
nabd_nhd_join['Frag'] = nabd_nhd_join['DamID']


# Fix the hydroseq columns, so they are integers
nabd_nhd_join['UpHydroseq'] = nabd_nhd_join['UpHydroseq'].round(decimals=0)
nabd_nhd_join['DnHydroseq'] = nabd_nhd_join['DnHydroseq'].round(decimals=0)
nabd_nhd_join['Hydroseq'] = nabd_nhd_join['Hydroseq'].round(decimals=0)
nabd_nhd_join.set_index('Hydroseq')

# %%
# test.rename(columns={'WKT': 'Coordinates'}) #rename column
test2 = nabd_nhd_join.rename(columns={'WKT': 'Coordinates'})
test2.Coordinates = test2.Coordinates.astype(str)
test2['Coordinates'] = test2['Coordinates'].apply(wkt.loads)
test2Geo = gp.GeoDataFrame(test2, geometry='Coordinates')

segments = test2Geo.copy()

# %%
# STEP 1: Making fragments
# looping to make fragments
# To do - calculate fragment totals  -- total number of dams upstream
#  Total storage upstream

queue = segments.loc[segments.UpHydroseq == 0]
# Initail number to use for fragments that are existing the  domain
# Rather than hitting a dam. Exiting framents will start counting from
# this number
fexit = 11

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
    print("Starting headwater #", snum, "SegID", temploc,
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
            fexit = fexit+1
            temploc = 0

    # print('Temploc', temploc, "Dtemp", dtemp)

    # assign the DamID fragment number to all of the segments
    segments.loc[templist, 'Frag'] = ftemp


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

#interactive plotting
from bokeh.plotting import figure, output_file, show
import getLineCoords

# output to static HTML file
output_file("flowlines.html")

# Calculate x coordinates of the line
segments['x'] = getLineCoords.get_LineCoords(segments, geom='Coordinates', coord_type='x')

# Calculate y coordinates of the line
segments['y'] = segments.apply(getLineCoords, geom='Coordinates', coord_type='y', axis=1)

# Let's see what we have now
segments.head()
import plotly as plty

fig = px.scatter_mapbox(segments, lat="lat", lon="lon", hover_name='Fragment', hover_data=["Hydroseq", "LENGTHKM"],
                        color_continuous_scale="Viridis", zoom=3, height=300)
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

# import pandas as pd
# us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")

# import plotly.express as px

# fig = px.scatter_mapbox(us_cities, lat="lat", lon="lon", hover_name="City", hover_data=["State", "Population"],
#                         color_discrete_sequence=["fuchsia"], zoom=3, height=300)
# fig.update_layout(mapbox_style="open-street-map")
# fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
# fig.show()




# %%
