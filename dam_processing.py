"""
This script completes the processing necessary to add the large dams that are 
missing from NABD.

Created by: Rachel Spinti
"""
# %%
import pandas as pd, geopandas as gp
from pathlib import Path

gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo") #where shapefiles/csv live 
# %%
# Workflow for the dams that are completely missing

##Read in NID
nid = pd.read_csv(gdrive/'other_dam_datasets/NID2019_U.csv')

##Convert the storage units
nid.NORMAL_STORAGE = nid.NORMAL_STORAGE * 1233.48   #convert units to cubic meters

# %%
# Figure out what is missing 

# ##Read in NABD
# nabd_dams = gp.read_file(gdrive/"nabd/nabd_fish_barriers_2012.shp")  #read in NABD from Drive
# nabd_dams = pd.DataFrame(nabd_dams)
# nabd_dams = nabd_dams.drop_duplicates(subset='NIDID', keep="first").reset_index(drop=True) #filter out duplicates

# ##Merge on NID
# nid_by_ID = nid.merge(nabd_dams, on = 'NIDID', how = 'left')
# nid_by_ID['COMID'] = nid_by_ID['COMID'].fillna(0)
# missing = nid_by_ID[nid_by_ID['COMID'] ==0]

# print('missing #',len(missing))

# large_missing = missing[missing['NORMAL_STORAGE']>=10**8]  #is it 10^8 or 10^6?
# print('large missing #', len(large_missing))
# large_missing.to_csv('large_dams_missing.csv')

#%%
# Retrieve the attributes we need from NID for the missing dams

##Make NID match NABD 
nid_gdf = gp.GeoDataFrame(nid, geometry=gp.points_from_xy(nid.LONGITUDE, nid.LATITUDE))
nid_gdf = nid_gdf[['NIDID', 'NORMAL_STORAGE', 'MAX_STORAGE', 'YEAR_COMPLETED', 'PURPOSES', 'geometry']]
nid_gdf = nid_gdf.rename(columns = {'NORMAL_STORAGE':'Norm_stor', 'MAX_STORAGE':'Max_stor','YEAR_COMPLETED':'Year_compl', 'PURPOSES':'Purposes'})
nid_gdf = nid_gdf.drop_duplicates(subset='NIDID', keep="first").reset_index(drop=True)
nid_gdf['COMID'] = 0

##Read in dams to add csv created after manual check
add_dams = pd.read_csv('/Users/rachelspinti/Documents/River_bifurcation/archive/Rachel_testing/large_dams_to_add.csv', index_col = 0, usecols= ['NIDID', 'DAM_NAME'])
add_dams = add_dams.drop_duplicates(subset='NIDID', keep="first").reset_index(drop=True)

##Make a list of the NIDIDs of missing dams
dam_ls = []
for i in add_dams.NIDID:
    dam_ls.append(i)

##Filter nid to pull out the dams in dam_ls
nid_filtered = nid_gdf[nid_gdf['NIDID'] == dam_ls[0]] 

##Select the missing dams from NID to create csv for QGIS
for j in range(len(nid_gdf.NIDID)):
    for i in range(1,len(dam_ls)):
        if nid_gdf.loc[j,'NIDID'] == dam_ls[i]:
            nid_filtered = nid_filtered.append(nid_gdf[nid_gdf['NIDID'] == dam_ls[i]])

nid_filtered.to_csv('dams_to_add.csv')

# %%
# Workflow for dams that need NIDID update