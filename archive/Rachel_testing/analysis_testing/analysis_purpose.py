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
purposes = ["flood_control", "hydroelectric", "other", "water_supply"]
# purposes = ["flood_control"]

for purp in purposes:
    ## folder on the GDrive to save output files to
    data_folder = 'HPC_runs_fixed/processed_data/'+purp+'/'
    # results_folder = 'HPC_runs_fixed/analyzed_data/testing'
    results_folder = 'HPC_runs_fixed/analyzed_data/'+purp+'/'
    gdrive = "/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo/" 
    print("     ---------------"+purp+"---------------")
    
    # Analyses
    #HUC analysis
    ## HUC values
    HUC_list=['HUC2','HUC4','HUC8']
    # HUC_list=['HUC8']

    ## Create combined csv
    for huc in HUC_list:
        crc.combined_huc_csv(basin_ls, gdrive, data_folder, results_folder, huc)

    ## Merge the combined csvs with HUC shapefiles
    huc2 = hm.HUC2_indices_merge(gdrive, results_folder, purp)  #HUC2
    print("HUC 2 indices finished")
    huc4 = hm.HUC4_indices_merge(gdrive, results_folder, purp)  #HUC4
    print("\n"+"HUC 4 indices finished")
    huc8 = hm.HUC8_indices_merge(gdrive, results_folder, purp)    #HUC8
    print("\n" +"HUC 8 indices finished")

    #__________________________________________________________

    # percent storage purpose analysis
    huc8_control = gp.read_file(gdrive+"HPC_runs_fixed/analyzed_data/huc8_indices.shp")
    huc8_control = huc8_control[["HUC8_no", "geometry", "Norm_sto_1", "States", "Name"]]

    drop_cols = [str(i) for i in huc8.columns]
    drop_cols.remove("HUC8_no")
    drop_cols.remove("Norm_stor_sum")
    drop_cols.remove("Name")
    drop_cols.remove("geometry")
    huc8 = huc8.drop(columns = drop_cols)

    huc8["percent_stor"] = 0
    huc8[["Name", "States"]] = huc8_control[[ "Name", "States"]]

    # if huc8.HUC8_no == huc8_control.HUC8_no:
    #     huc8["geometry"] = huc8_control["geometry"]
    #     huc8["percent_stor"] = huc8.Norm_stor_sum/huc8_control.Norm_sto_1
    for i in huc8.index:
        if huc8.HUC8_no[i] == huc8_control.HUC8_no[i]:
            # huc8["geometry"] = huc8_control["geometry"]
            huc8["percent_stor"][i] = huc8.Norm_stor_sum[i]/huc8_control.Norm_sto_1[i]    
            # huc8["percent_stor"][i] = huc8.Norm_stor_up_outlet[i]/huc8_control.Norm_sto_2[i]

    huc8.percent_stor.fillna(-1, inplace=True)
    huc8.to_file(gdrive+results_folder+'huc8_percent_stor_'+purp+'.shp')
        
print("\n" +"HUC8 storage difference analysis complete")


# %%
 #segGeo analysis
    # crc.create_combined_segGeo_csv(basin_ls, gdrive, folder)
    # print("\n" +"Create combined csv finished")
    
print("\n"+"** Analysis Complete **")
# %%
