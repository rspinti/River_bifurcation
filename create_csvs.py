
import pandas as pd, numpy as np, geopandas as gp, extract as ex, os, glob
import datetime, read
from pathlib import Path

# gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo") #where data lives 

def create_basin_csvs(basin_ls, gdrive, folder):
    """Determines if a basin csv exists and create it if needed.

        This function passes in a list of basins and determines if a csv with each
        basin name exists. If the csv does not exist, it is created with read.py.
        The read_flag ensures that read.py is only executed once.

        Parameters:
            basin_ls (List):
                List of basins to be analyzed.
            gdrive (string):
                Location on the Google Drive to save the csvs.
            folder (string):
                Folder on the Google Drive where csvs will be saved.
            read_flag (boolean): 
                If False, flowlines and dams will be read in with read.py.
                If True, flowlines and dams will not be read in because they
                    already have been.
            flowlines (pandas.DataFrame):
                Dataframe containing all NHD flowlines from read.py.
            dams (pandas.DataFrame):
                Dataframe containing all dams from read.py.
            nabd_nhd (pandas.DataFrame):
                
        
        Returns:
            Csvs for each of the basins listed in basin_ls in a specified folder
                on the Google Drive.
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
            ex.join_dams_flowlines(basin, flowlines, dams)
            

def create_combined_csv(basin_ls, folder, huc):
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


    # Specified HUC indices
    extension = huc+'_indices.csv'
    HUC_summary_list = [i+extension for i in basin_ls]

    #combine all files in the list
    combined_csv = pd.concat([pd.read_csv(f) for f in HUC_summary_list])

    #export to csv
    combined_csv.to_csv(huc+"_summary.csv", index=False, encoding='utf-8-sig')

