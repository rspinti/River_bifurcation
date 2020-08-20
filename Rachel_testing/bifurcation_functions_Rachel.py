
# %% Run this block only once
import os
import numpy as np
import pandas as pd
import geopandas as gp
import matplotlib.pyplot as plt
import matplotlib as mpl
import bifurcate_upreaches as bfup
from shapely import wkt
plt.style.use('classic')

import sys
sys.path.insert(0, '/Users/rachelspinti/Documents/River_bifurcation/Rachel_testing')
import extract as ex

from pathlib import Path
gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/GIS/Layers") #where shapefiles/csv live 


# Read in data
## NABD
nabd = gp.read_file(gdrive/"nabd_fish_barriers_2012.shp", 
                        usecols=['COMID', 'NIDID', 'Norm_stor', 'Max_stor', 
                                 'Year_compl', 'Purposes', 'geometry'])  #read in NABD from Drive
nabd = nabd.drop_duplicates(subset='NIDID', keep="first")  #drop everything after first duplicate
nabd["DamID"] = range(len(nabd.COMID))  #add DamID 
# print(nabd.DamID.unique)  #check the DamIDs
    
## NHD
flowlines = pd.read_csv(gdrive/"NHDPlusNationalData/NHDFlowlines.csv",
                            usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                                     'REACHCODE','LENGTHKM', 'StartFlag', 
                                     'FTYPE', 'COMID', 'WKT', 'QE_MA', 'QC_MA'])  #all NHD Flowlines
#Filter the flowlines to select by HUC 2
flowlines['REACHCODE'] = flowlines['REACHCODE']/(10**10) #convert Reachcode to HUC 2 format
flowlines['REACHCODE'] = flowlines['REACHCODE'].apply(np.floor) #round down to integer
#round the hydroseq values because of bug
flowlines[['UpHydroseq', 'DnHydroseq', 'Hydroseq']] = flowlines[['UpHydroseq', 
                                                                     'DnHydroseq', 
                                                                     'Hydroseq']].round(decimals=0)
flowlines = flowlines[flowlines['FTYPE']!= 'Coastline']  #filter out coastlines
# %%
# Choose the major river basin to Run
run_name = 'Red'  #type river basin name
#run name options
# ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes', 
#  'Gulf Coast','Mississippi', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']


# %%
# Read in data
## If the specified basin csv does not exist, extract it
if os.path.isfile(run_name+'.csv'):  #does it exist?
    #Read specified basin 
    print('Exists')
    segments = pd.read_csv(run_name+'test.csv', usecols=['Hydroseq', 'UpHydroseq',
    'DnHydroseq', 'LENGTHKM', 'StartFlag', 'Coordinates','DamID', 'DamCount'])
else:
    print('Does not exist')
    nabd_nhd = ex.join_dams_flowlines(flowlines, run_name, nabd)
    segments = pd.read_csv(run_name+'test.csv', usecols=['Hydroseq', 'UpHydroseq', 
                                            'DnHydroseq', 
                                            'LENGTHKM', 'StartFlag',
                                            'Coordinates','DamID', 'DamCount'])


#%%
from time import time
t1 = time()
# STEP1:  Make Fragments
segments=bfup.make_fragments(segments, exit_id=99900000)
t2 = time()
print("Make Fragments:", (t2-t1))

# STEP 2: Making a fragment data frame and aggregated by fragment
fragments = bfup.agg_by_frag(segments)
t3 = time()
print("Aggregate by fragments:", (t3-t2))

# STEP 3: Map Upstream Fragments 
UpDict = bfup.map_up_frag(fragments)
t4 = time()
print("Map Upstream fragments:", (t4-t3))

#STEP 4: Aggregate by upstream area
fragments=bfup.agg_by_frag_up(fragments, UpDict)
t5 = time()

# STEP 5: Map Upstream Segments
UpDict_reaches = bfup.map_up_seg(segments)
t6 = time()
print("Map Upstream fragments:", (t4-t3))

#STEP 6: Aggregate by upstream segment
segments=bfup.agg_by_seg_up(segments, UpDict_reaches)
t7 = time()

print("---- TIMING SUMMARY -----")
print("Make Fragments:", (t2-t1))
print("Aggregate by fragments:", (t3-t2))
print("Map Upstream fragments:", (t4-t3))
print("Aggregate by upstream:", (t5-t4))
print("Map Upstream segments:", (t6-t5))
print("Aggregate by upstream segment:", (t7-t6))
print("Total Time:", (t7-t1))

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



