
# %% Run this block only once
import os
import numpy as np
import pandas as pd
import geopandas as gp
import matplotlib as mpl
import matplotlib.pyplot as plt
import bifurcate as bfc
from shapely import wkt
plt.style.use('classic')

import sys
sys.path.insert(0, '/Users/rachelspinti/Documents/River_bifurcation/Rachel_testing')
import extract as ex

from pathlib import Path
gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/GIS/Layers") #where shapefiles/csv live 


# Read in data
## NABD
nabd_dams = gp.read_file(gdrive/"nabd_fish_barriers_2012.shp", 
                        usecols=['COMID', 'NIDID', 'Norm_stor', 'Max_stor', 
                                 'Year_compl', 'Purposes', 'geometry'])  #read in NABD from Drive
nabd_dams = nabd_dams.drop_duplicates(subset='NIDID', keep="first")  #drop everything after first duplicate
nabd_dams["DamID"] = range(len(nabd_dams.COMID))  #add DamID 
nabd_dams = pd.DataFrame(nabd_dams)
nabd_dams['Grand_flag'] = np.zeros(len(nabd_dams))  #add flag column
# print(nabd.DamID.unique)  #check the DamIDs

## GRanD
grand = pd.read_csv(gdrive/"Reservoir_Attributes.csv", 
                        usecols=['GRAND_ID', 'NABD_ID'])  #read in NABD from Drive
#Filter out dams without NABD IDs
grand['NABD_ID'] = grand['NABD_ID'].fillna(0)
# print(grand.GRAND_ID.unique())
grand = grand[grand['NABD_ID']!=0]

#Merge NABD and GRanD
nabd = pd.merge(nabd_dams, grand, left_on = 'NIDID', right_on = 'NABD_ID', how = 'left')
nabd['GRAND_ID'] = nabd['GRAND_ID'].fillna(0)
nabd.loc[nabd.GRAND_ID != 0, 'Grand_flag'] = 1 #if a GRanD ID exists, make flag =1 

## NHD

# flowlines = pd.read_csv(gdrive/"NHDPlusNationalData/NHDFlowlines.csv",
#                             usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
#                                      'REACHCODE','LENGTHKM', 'StartFlag', 
#                                      'FTYPE', 'COMID', 'WKT', 'QE_MA', 'QC_MA'])  #all NHD Flowlines
flowlines = pd.read_csv("/Users/rachelspinti/Documents/River_bifurcation/data/nhd/NHDFlowlines.csv",
                        usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                                 'REACHCODE','LENGTHKM', 'StartFlag', 
                                 'FTYPE', 'COMID', 'WKT', 'QE_MA', 'QC_MA'])  #all NHD Flowlines
#Filter the flowlines to select by HUC 2
flowlines['REACHCODE'] = flowlines['REACHCODE']/(10**12) #convert Reachcode to HUC 2 format
flowlines['REACHCODE'] = flowlines['REACHCODE'].apply(np.floor) #round down to integer
#round the hydroseq values because of bug
flowlines[['UpHydroseq', 'DnHydroseq', 'Hydroseq']] = flowlines[['UpHydroseq', 
                                                                     'DnHydroseq', 
                                                                     'Hydroseq']].round(decimals=0)
flowlines = flowlines[flowlines['FTYPE']!= 'Coastline']  #filter out coastlines
# %%
# Choose the major river basin to Run
run_name = 'Mississippi'  #type river basin name
#run name options
# ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes', 
#  'Gulf Coast','Mississippi', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']


# %%
# Read in data
## If the specified basin csv does not exist, extract it
if os.path.isfile(run_name+'.csv'):  #does it exist?
    #Read specified basin 
    print('Exists')
    segments = pd.read_csv(run_name+'.csv', usecols=['Hydroseq', 'UpHydroseq',
    'DnHydroseq', 'LENGTHKM', 'StartFlag', 'Coordinates','DamID', 'DamCount',
    'Norm_stor', 'QE_MA', 'QC_MA'])
else:
    print('Does not exist')
    nabd_nhd = ex.join_dams_flowlines(flowlines, run_name, nabd)
    segments = pd.read_csv(run_name+'.csv', usecols=['Hydroseq', 'UpHydroseq', 
                                            'DnHydroseq', 
                                            'LENGTHKM', 'StartFlag',
                                            'Coordinates','DamID', 'DamCount', 
                                            'Norm_stor', 'QE_MA', 'QC_MA'])


#%%
from time import time
t1 = time()
# STEP1:  Make Fragments
segments=bfc.make_fragments(segments, exit_id=99900000)
t2 = time()
print("Make Fragments:", (t2-t1))

# STEP 2: Making a fragment data frame and aggregated by fragment
fragments = bfc.agg_by_frag(segments)
t3 = time()
print("Aggregate by fragments:", (t3-t2))

# STEP 3: Map Upstream Fragments 
UpDict = bfc.map_up_frag(fragments)
t4 = time()
print("Map Upstream fragments:", (t4-t3))

#STEP 4: Aggregate by upstream area
fragments=bfc.agg_by_frag_up(fragments, UpDict)
t5 = time()

print("---- TIMING SUMMARY -----")
print("Make Fragments:", (t2-t1))
print("Aggregate by fragments:", (t3-t2))
print("Map Upstream fragments:", (t4-t3))
print("Aggregate by upstream:", (t5-t4))
print("Total Time:", (t5-t1))

# %%
# Preparing for plotting
print(segments.columns)
segments['Frag'] = segments['Frag'].fillna(0)

segments.Coordinates = segments.Coordinates.astype(str)
segments['Coordinates'] = segments['Coordinates'].apply(wkt.loads)
segments_gdf = gp.GeoDataFrame(segments, geometry='Coordinates')



# %%
# fig, ax = plt.subplots(1, 2)
# segments_gdf.plot(column='DamID', ax=ax[0], legend=True)
# segments_gdf.plot(column='Frag', ax=ax[1], legend=True)
# #segments_gdf.plot(column='step', ax=ax[1], legend=True)
# plt.show()

# segments_gdf.plot(column='Frag', legend=True, cmap='viridis_r',
#               legend_kwds={'label': "Fragment #", 'orientation': "horizontal"})
segments_gdf.plot(column='Frag', legend=True, cmap='viridis_r',
              legend_kwds={'label': "Fragment #", 'orientation': "horizontal"},
              vmin=3000,vmax=4400)

# # %%
# # Doing some summaries to cross check calculations
# #print(fragments)
# print(segments_gdf.loc[segments.Frag == 0]) #check for any segments not covered
# temp = segments_gdf.pivot_table('LENGTHKM', index='Frag', aggfunc=sum)
# print(temp)
# print(sum(temp['LENGTHKM']))
# print(sum(segments_gdf.LENGTHKM))
# # alternate approach to pivot table
# # segments_gdf.groupby('Frag')[['LENGTHKM']].sum()


# # %%
# ## Rachel testing the plotting to see what happens with Fragments
# ## Was testing HUC4 1019
# fig, ax = plt.subplots(1, 2)
# x = segments_gdf[segments_gdf['Frag'] <12000]  #this filter value might change 
#                                   # depending on the range of vlaues for Frags
# x.plot(column='Frag', ax=ax[0], legend=True)
# y = segments_gdf[segments_gdf['Frag'] >12000]  #this filter value might change 
# y.plot(column='Frag', ax=ax[1], legend=True)
# plt.show()



