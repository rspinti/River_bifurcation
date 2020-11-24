
import pandas as pd, numpy as np, geopandas as gp, extract as ex, os, glob
import datetime, read
from pathlib import Path

# gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo") #where data lives 

def create_basin_csvs(basin_ls, gdrive, folder):
    """Determines if a basin csv exists.

        This function

        Parameters:
            nabd_dams (pandas.DataFrame): 
                
        
        Returns:
    """   
    ## If the specified basin csv does not exist, extract it
    os.chdir(gdrive+folder)
    read_flag = False

    for basin in basin_ls:
        if os.path.isfile(basin+'.csv'):  #does it exist?
            #Read specified basin 
            print(basin + ': Exists')

        else:
            if read_flag == False:
                flowlines, dams = read.read_lines_dams(gdrive)
                read_flag = True
            print('\n', basin +  ': Does not exist')
            nabd_nhd = ex.join_dams_flowlines(basin, flowlines, dams)
            

def create_combined_csv(basin_ls, folder):
    """Creates combined csv of all flowlines.

        This function

        Parameters:
            segments (pandas.DataFrame): 
                
        
        Returns:
    """        
    os.chdir("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo/"+folder+"/")

    # extension = '.csv'
    # all_flowlines = [i+extension for i in basin_ls]     # all_flowlines

    # #combine all files in the list
    # combined_csv = pd.concat([pd.read_csv(f) for f in all_flowlines ])

    # #export to csv
    # combined_csv.to_csv("combined_flowlines.csv", index=False, encoding='utf-8-sig')


    # # Seg Geos
    # extension = '_segGeo.csv'
    # all_segGeos = [i+extension for i in basin_ls]
    # # all_segGeos

    # #combine all files in the list
    # combined_csv = pd.concat([pd.read_csv(f) for f in all_segGeos])

    # #export to csv
    # combined_csv.to_csv("combined_segGeo.csv", index=False, encoding='utf-8-sig')

    
    # Seg DCI
    extension = '_segments_dci.csv'
    all_segdci = [i+extension for i in basin_ls]
    # all_segGeos

    #combine all files in the list
    combined_csv = pd.concat([pd.read_csv(f) for f in all_segdci])

    #export to csv
    combined_csv.to_csv("combined_seg_dci.csv", index=False, encoding='utf-8-sig')

    
    # Fragments
    # extension = '_fragments.csv'
    # all_frags = [i+extension for i in basin_ls]
    # # all_segGeos

    # #combine all files in the list
    # combined_csv = pd.concat([pd.read_csv(f) for f in all_frags])

    # #export to csv
    # combined_csv.to_csv("combined_frag.csv", index=False, encoding='utf-8-sig')

