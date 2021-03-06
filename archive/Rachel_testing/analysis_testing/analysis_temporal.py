# %%
import geopandas as gp, pandas as pd, numpy as np
import create_csvs as crc, huc_merge as hm, time_diff as td

# %%
# Specifying inputs
## Basin lists 
#all the basins
basin_ls = ['California', 'Colorado', 'Columbia', 'Great_Basin', 'Great_Lakes',
'Gulf_Coast','Mississippi', 'North_Atlantic', 'Red', 'Rio_Grande','South_Atlantic']

# basin_ls = ['Red']

data_folder = 'HPC_runs_fixed/processed_data/'
results_folder = 'HPC_runs_fixed/analyzed_data/'

# data_folder = 'HPC_runs_fixed/processed_data/grand_dams'
# results_folder = 'HPC_runs_fixed/analyzed_data/grand_dams'
gdrive = "/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo/" 

# purposes = ['no_dams', '1920', '1950', '1980', '2010']
purposes = ['2010']

for purp in purposes:
#     ## folder on the GDrive to save output files to
    data_folder2 = data_folder+purp+'/'
    # data_folder = 'HPC_runs_fixed/processed_data/'+purp+'/'
    # data_folder = 'HPC_runs_fixed/processed_data/grand_dams/'+purp+'/'

    results_folder2 = results_folder+purp+'/'
    # results_folder = 'HPC_runs_fixed/analyzed_data/testing'
    # results_folder = 'HPC_runs_fixed/analyzed_data/'+purp+'/'
    # results_folder = 'HPC_runs_fixed/analyzed_data/grand_dams/'+purp+'/'
    # gdrive = "/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo/" 
    print("     ---------------"+purp+"---------------")

    #HUC analysis
    ## HUC values
    HUC_list=['HUC2','HUC4','HUC8']
    # HUC_list=['HUC8']

    ## Create combined csv
    for huc in HUC_list:
        crc.combined_huc_csv(basin_ls, gdrive, data_folder2, results_folder2, huc)

    ## Merge the combined csvs with HUC shapefiles
    huc2 = hm.HUC2_indices_merge(gdrive, results_folder2, purp)  #HUC2
    print("HUC 2 indices finished")
    huc4 = hm.HUC4_indices_merge(gdrive, results_folder2, purp)  #HUC4
    print("\n"+"HUC 4 indices finished")
    huc8 = hm.HUC8_indices_merge(gdrive, results_folder2, purp)    #HUC8
    print("\n" +"HUC 8 indices finished")

    #segGeo analysis
    # crc.combined_segGeo_csv(basin_ls, gdrive, data_folder, results_folder)

     #fragment analysis
    # crc.combined_frag_csv(basin_ls, gdrive, data_folder, results_folder)

    # print("\n" +"Create combined csv finished")
#__________________________________________________________
# the stor difference shapefiles
# folder = 'HPC_runs_fixed/analyzed_data/'
# td.stor_diff(gdrive, folder)


# %%
print("\n"+"** Analysis Complete **")
# %%
