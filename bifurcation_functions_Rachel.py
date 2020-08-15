
# %%
import os
import pandas as pd
import geopandas as gp
import matplotlib.pyplot as plt
import matplotlib as mpl
import bifurcate as bfc
from shapely import wkt
plt.style.use('classic')

import sys
sys.path.insert(0, '/Users/rachelspinti/Documents/River_bifurcation/Rachel_testing')
import extract as ex

from pathlib import Path
gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/GIS/Layers") #where shapefiles/csv live 


# %%
# Choose the major river basin to Run
run_name = 'California'  #type river basin name
#run name options
# ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes', 
#  'Gulf Coast','Mississippi', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']


# %%
# Read in data
## If the specified basin csv does not exist, extract it
if os.path.isfile(run_name+'.csv'):  #does it exist?
    #Read specified basin 
    print('exists')
    segments = pd.read_csv(run_name+'.csv', usecols=['Hydroseq', 'UpHydroseq',
    'DnHydroseq', 'LENGTHKM', 'StartFlag', 'Coordinates','DamID', 'DamCount'])
else:
    print('does not exist')
    nabd_nhd = ex.join_dams_flowlines(run_name)
    filtered_join = ex.filter_join(nabd_nhd, run_name)  #filter the joined data
    segments = pd.read_csv(run_name+'.csv', usecols=['Hydroseq', 'UpHydroseq', 
                                            'DnHydroseq', 
                                            'LENGTHKM', 'StartFlag',
                                            'Coordinates','DamID', 'DamCount'])


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



