# %%
import geopandas as gp, pandas as pd, numpy as np
import create_csvs as crc, HUC_merge as hm
# how to summarize the HUC data after it is created in run_workflow.py
## print out each HUC analysis to a csv named basin_HUC2/4/8.csv
## join all these csvs into one big one
## then, join the big one with the corresponding shapefile from the Drive
### this will be a new file that we can use for mapping in QGIS

# %%
# folder on the GDrive to save output files to
folder = 'test_workflow/'
gdrive = "/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo/" #where shapefiles/csv live 

# Basin lists 
##all the basins
# basin_ls = ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes',
# 'Gulf Coast','Mississippi', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']

##w/o the Mississippi
# basin_ls = ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes',
# 'Gulf Coast', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']

##other
basin_ls = ['Red', 'Columbia']

# HUCs
huc = 'HUC8'
# HUC_vallist=['HUC2','HUC4','HUC8']

# Create the combined csv
crc.create_combined_csv(basin_ls, folder, huc)

# Merge the combined csvs with HUC shapefiles
# abh.avg_HUC2(combo_segGeo, gdrive, folder)
# abh.avg_HUC4(combo_segGeo, gdrive, folder)
hm.HUC8_indices_merge(gdrive, folder)


# %%
