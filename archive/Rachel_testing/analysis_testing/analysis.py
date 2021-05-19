# %%
import geopandas as gp, pandas as pd, numpy as np
import create_csvs as crc, huc_merge as hm

# %%
# Specifying inputs
## Basin lists 
#all the basins
basin_ls = ['California', 'Colorado', 'Columbia', 'Great_Basin', 'Great_Lakes',
'Gulf_Coast','Mississippi', 'North_Atlantic', 'Red', 'Rio_Grande','South_Atlantic']

## purpose folder names
# purposes = ["flood_control", "hydroelectric", "other", "water_supply"]
purposes = ["flood_control", "hydroelectric", "other"]

for i in purposes:
    ## folder on the GDrive to save output files to
    data_folder = 'HPC_runs_fixed/processed_data/'+i+'/'
    results_folder = 'HPC_runs_fixed/analyzed_data/'+i+'/'
    gdrive = "/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo/" 

    # Analyses

    #HUC analysis
    ## HUC values
    HUC_list=['HUC2','HUC4','HUC8']

    ## Create combined csv
    for huc in HUC_list:
        crc.combined_huc_csv(basin_ls, gdrive, data_folder, huc)

    ## Merge the combined csvs with HUC shapefiles
    huc2 = hm.HUC2_indices_merge(gdrive, data_folder, results_folder, i)  #HUC2
    print("HUC 2 indices finished")
    huc4 = hm.HUC4_indices_merge(gdrive, data_folder, results_folder, i)  #HUC4
    print("\n"+"HUC 4 indices finished")
    huc8 = hm.HUC8_indices_merge(gdrive, data_folder, results_folder, i)    #HUC8
    print("\n" +"HUC 8 indices finished")

    #__________________________________________________________

    # percent storage purpose analysis
    huc8_control = gp.read_file(gdrive+"HPC_runs_fixed/processed_data/all_basins_unfiltered/huc8_indices.shp")
    huc8_control = huc8_control[["HUC8_no", "geometry", "Norm_sto_2", "Name"]]

    drop_cols = [str(i) for i in huc8.columns]
    drop_cols.remove("HUC8_no")
    drop_cols.remove("Norm_stor_up_outlet")
    drop_cols.remove("geometry")
    huc8 = huc8.drop(columns = drop_cols)

    huc8["percent_stor"] = 0

    for i in huc8.index:
        if huc8.HUC8_no[i] == huc8_control.HUC8_no[i]:
            huc8["percent_stor"][i] = huc8.Norm_stor_up_outlet[i]/huc8_control.Norm_sto_2[i]

    huc8.stor_diff.fillna(-1, inplace=True)
    huc8.to_file(gdrive+results_folder+'huc8_percent_stor_'+i+'.shp')
        
print("\n" +"HUC8 storage difference")

print("\n"+"** Analysis Complete **")
# %%
 #segGeo analysis
    # crc.create_combined_segGeo_csv(basin_ls, gdrive, folder)
    # print("\n" +"Create combined csv finished")
# %%
