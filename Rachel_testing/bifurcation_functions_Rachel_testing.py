
# %%
import os
import pandas as pd
import numpy as np
import geopandas as gp
import matplotlib.pyplot as plt
import matplotlib as mpl
import extract as ex
from shapely import wkt
plt.style.use('classic')

import sys
sys.path.insert(0, '/Users/rachelspinti/Documents/River_bifurcation')
import bifurcate as bfc

from pathlib import Path
gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/GIS/Layers") #where shapefiles/csv live 


# %%
# Choose the major river basin to Run
run_name = 'Red'  #type river basin name
#run name options
# ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes', 
#  'Gulf Coast','Mississippi', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']


# %%
# Read in data
# dams = ex.extract_dams()
# print(dams.head(3))

# function = ex.my_function()

# If the specified basin csv does not exist, extract it
if os.path.isfile(run_name+'.csv'):  #does it exist?
    #Read specified basin 
    print('exists')
    segments = pd.read_csv(run_name+'.csv', usecols=['Hydroseq', 'UpHydroseq',
    'DnHydroseq','Pathlength', 'LENGTHKM', 'StartFlag', 'Coordinates','DamID', 'DamCount'])
else:
    print('does not exist')
    nabd_nhd = ex.join_dams_flowlines(run_name)
    filtered_join = ex.filter_join(nabd_nhd, run_name)  #filter the joined data
    segments = pd.read_csv(run_name+'.csv', usecols=['Hydroseq', 'UpHydroseq', 
                                            'DnHydroseq','Pathlength', 
                                            'LENGTHKM', 'StartFlag',
                                            'Coordinates','DamID', 'DamCount'])


# %%
## NABD
# nabd = gp.read_file(gdrive/"nabd_fish_barriers_2012.shp")  #read in NABD from Drive
# nabd = nabd.drop_duplicates(subset='NIDID', keep="first")  #drop everything after first duplicate
# nabd["DamID"] = range(len(nabd.COMID))  #add D

## NHD
# #Dictionary with river basin names and associated HUC 2s
# major_basins = {'California' : [18],
#                 'Colorado' : [14, 15],
#                 'Columbia' : [17],
#                 'Great Basin' : [16],
#                 'Great Lakes' : [4],
#                 'Gulf Coast' : [12],
#                 'Mississippi' : [5, 6, 7, 8, 10, 11],
#                 'North Atlantic' : [1, 2],
#                 'Red' : [9],
#                 'Rio Grande' : [13],
#                 'South Atlantic' : [3]}
# # print(major_basins)

# If the specified basin csv does not exist, extract it
# if os.path.isfile(run_name+'.csv'):  #does it exist?
#     #Read specified basin 
#     nabd_nhd_join = pd.read_csv(run_name+'.csv', usecols=['Hydroseq', 'UpHydroseq', 
#                                             'DnHydroseq','Pathlength', 
#                                             'LENGTHKM', 'StartFlag',
#                                             'WKT', 'FTYPE','DamID'])
#     print(nabd_nhd_join.head(3))
# else:
#     #Read NHD flowlines
#     flowlines = pd.read_csv(gdrive/"NHDPlusNationalData/NHDFlowlines.csv",
#                     usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
#                             'REACHCODE', 'Pathlength', 'LENGTHKM', 
#                             'StartFlag', 'FTYPE', 'COMID', 'WKT'])  #all NHD Flowlines
#     flowlines['REACHCODE'] = flowlines['REACHCODE']/(10**12) #convert Reachcode to HUC 2 format
#     flowlines['REACHCODE'] = flowlines['REACHCODE'].apply(np.floor) #round down to integer
#     flowlines[['UpHydroseq', 'DnHydroseq', 'Hydroseq']] = flowlines[['UpHydroseq', 'DnHydroseq', 'Hydroseq']].round(decimals=0)
#         #round the hydroseq values because of bug
#     flowlines = flowlines[flowlines['FTYPE']!= "Coastline"]
    

#     #Based on the run name, a different basin will be selected
#     if run_name == 'California':
#         california = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
#         nabd_nhd_join = nabd.merge(california, how= 'right', on='COMID') # Merge NABD and NHD

#     if run_name == 'Colorado':
#         colorado = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])| 
#                              (flowlines['REACHCODE'] == major_basins[run_name][1])]
#         nabd_nhd_join = nabd.merge(colorado, how= 'right', on='COMID') # Merge NABD and NHD

#     if run_name == 'Columbia':
#         columbia = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
#         nabd_nhd_join = nabd.merge(columbia, how= 'right', on='COMID') # Merge NABD and NHD

#     if run_name == 'Great Basin':
#         great_basin = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
#         nabd_nhd_join = nabd.merge(great_basin, how= 'right', on='COMID') # Merge NABD and NHD

#     if run_name == 'Great Lakes':
#         great_lakes = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
#         nabd_nhd_join = nabd.merge(great_lakes, how= 'right', on='COMID') # Merge NABD and NHD

#     if run_name == 'Gulf Coast':
#         gulf_coast = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
#         nabd_nhd_join = nabd.merge(gulf_coast, how= 'right', on='COMID') # Merge NABD and NHD

#     if run_name == 'Mississippi':
#         mississippi = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])| 
#                                 (flowlines['REACHCODE'] == major_basins[run_name][1])| 
#                                 (flowlines['REACHCODE'] == major_basins[run_name][2])| 
#                                 (flowlines['REACHCODE'] == major_basins[run_name][3]) |
#                                 (flowlines['REACHCODE'] == major_basins[run_name][4])|
#                                 (flowlines['REACHCODE'] == major_basins[run_name][5])]
#         nabd_nhd_join = nabd.merge(mississippi, how= 'right', on='COMID') # Merge NABD and NHD
    
#     if run_name == 'North Atlantic':
#         north_atlantic = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])|
#                                    (flowlines['REACHCODE'] == major_basins[run_name][1])]
#         nabd_nhd_join = nabd.merge(north_atlantic, how= 'right', on='COMID') # Merge NABD and NHD

#     if run_name == 'Red':
#         red = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
#         nabd_nhd_join = nabd.merge(red, how= 'right', on='COMID') # Merge NABD and NHD

#     if run_name == 'Rio Grande':
#         rio_grande = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
#         nabd_nhd_join = nabd.merge(rio_grande, how= 'right', on='COMID') # Merge NABD and NHD

#     if run_name == 'South Atlantic':
#         south_atlantic = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
#         nabd_nhd_join = nabd.merge(south_atlantic, how= 'right', on='COMID') # Merge NABD and NHD
#     #Creates new csv to run
#     nabd_nhd_join.to_csv(run_name+'.csv')  
#     print('Finished writing nabd_nhd_join to '+run_name+'.csv....', nabd_nhd_join.head(3))


# %%
# Add stuff for bifurcation analysis
## add a column to keep track of steps
# nabd_nhd_join.insert(5, "step", np.zeros(len(nabd_nhd_join)), True)

# ## fill in the NA's for the dam column with 0s
# nabd_nhd_join['DamID'] = nabd_nhd_join['DamID'].fillna(0)

# ## make a column to indicate if a dam is present or not
# nabd_nhd_join['DamCount'] = np.zeros(len(nabd_nhd_join))
# nabd_nhd_join.loc[nabd_nhd_join.DamID>0, 'DamCount'] = 1

# ## set index to Hydroseq
# nabd_nhd_join = nabd_nhd_join.set_index('Hydroseq')


# %%
# Create geodataframe (for plotting)
# nabd_nhd_join2 = nabd_nhd_join.rename(columns={'WKT': 'Coordinates'})
# nabd_nhd_join2.Coordinates = nabd_nhd_join2.Coordinates.astype(str)
# nabd_nhd_join2['Coordinates'] = nabd_nhd_join2['Coordinates'].apply(wkt.loads)
# nabd_nhd_join2_Geo = gp.GeoDataFrame(nabd_nhd_join2, geometry='Coordinates')

# segments = nabd_nhd_join2_Geo.copy()


#%%
# STEP1:  Make Fragments
segments=bfc.make_fragments(segments, exit_id=99900000)

# STEP 2: Making a fragment data frame and aggregated by fragment
fragments = bfc.agg_by_frag(segments)

# STEP 3: Map Upstream Fragments 
UpDict = bfc.map_up_frag(fragments)

#STEP 4: Aggregate by upstream area
fragments=bfc.agg_by_frag_up(fragments, UpDict)


# %%
# Some plotting
print(segments.columns)
segments['Frag'] = segments['Frag'].fillna(0)

segments.Coordinates = segments.Coordinates.astype(str)
segments['Coordinates'] = segments['Coordinates'].apply(wkt.loads)
segments_gdf = gp.GeoDataFrame(segments, geometry='Coordinates')

# fig, ax = plt.subplots(1, 2)
# segments.plot(column='DamID', ax=ax[0], legend=True)
# segments.plot(column='Frag', ax=ax[1], legend=True)
# #segments.plot(column='step', ax=ax[1], legend=True)
# plt.show()

segments.plot(column='Frag', legend=True, cmap='viridis_r',
              legend_kwds={'label': "Fragment #", 'orientation': "horizontal"})

# # %%
# # Doing some summaries to cross check calculations
# #print(fragments)
# print(segments.loc[segments.Frag == 0]) #check for any segments not covered
# temp = segments.pivot_table('LENGTHKM', index='Frag', aggfunc=sum)
# print(temp)
# print(sum(temp['LENGTHKM']))
# print(sum(segments.LENGTHKM))
# # alternate approach to pivot tabel
# # segments.groupby('Frag')[['LENGTHKM']].sum()


# # %%
# ## Rachel testing the plotting to see what happens with Fragments
# ## Was testing HUC4 1019
# fig, ax = plt.subplots(1, 2)
# x = segments[segments['Frag'] <12000]  #this filter value might change 
#                                   # depending on the range of vlaues for Frags
# x.plot(column='Frag', ax=ax[0], legend=True)
# y = segments[segments['Frag'] >12000]  #this filter value might change 
# y.plot(column='Frag', ax=ax[1], legend=True)
# plt.show()


# # %%
