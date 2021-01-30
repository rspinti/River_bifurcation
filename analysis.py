# %%
import geopandas as gp, pandas as pd, numpy as np
import create_csvs as crc, HUC_merge as hm

# %%
# Specifying inputs
## folder on the GDrive to save output files to
folder = 'test_workflow/'
gdrive = "/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo/" #where shapefiles/csv live 

## Basin lists 
#all the basins
# basin_ls = ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes',
# 'Gulf Coast','Mississippi', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']

#w/o the Mississippi
# basin_ls = ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes',
# 'Gulf Coast', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']

#other
basin_ls = ['Red', 'Colorado']

# %%
# Analyses

#HUC analysis
## HUC values
HUC_list = ['HUC8']
# HUC_list=['HUC2','HUC4','HUC8']

## Create combined csv
for huc in HUC_list:
    crc.create_combined_csv(basin_ls, folder, huc)

## Merge the combined csvs with HUC shapefiles
# hm.HUC2_indices_merge(gdrive, folder)  #HUC2
# hm.HUC4_indices_merge(gdrive, folder)  #HUC4
hm.HUC8_indices_merge(gdrive, folder)    #HUC8

#__________________________________________________________

# %%
