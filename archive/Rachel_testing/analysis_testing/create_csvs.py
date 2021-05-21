
import pandas as pd, numpy as np, geopandas as gp, os, glob
import datetime
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
            

def combined_huc_csv(basin_ls, gdrive, data_folder, results_folder, huc):
    """Combines all the basins together into one csv by HUC.

        This function takes a list of basins and creates a combined csv. The 
        list of basins is used to read in each corresponding csv, which are 
        concatenated into the same dataframe. That combined dataframe is then 
        printed out to csv.

        Parameters:
            basin_ls (List):
                List of basins whose csvs will be read in.
            folder (string):
                Folder on the Google Drive where csv are be saved.
            huc (string):
                HUC value to be evaluated.
            extension (string):
                Csv extension that varies by HUC value.
            HUC_summary_list (List):
                List of basin names with their HUC extension added.
            combined_csv (pandas.DataFrame):
                Dataframe that contains all basins.
                columns
                    add columns here with descriptions
    

        Returns:
            A single csv containing all the data from each basin csv.
    """        
    os.chdir(gdrive+data_folder)

    # Make list of names of files to be read in (by basin and HUC value)
    extension = huc+'_indices.csv'
    HUC_summary_list = [i+extension for i in basin_ls]

    # Combine all basin csvs together into a dataframe
    combined_csv = pd.concat([pd.read_csv(f) for f in HUC_summary_list])

    # Export to csv 
    combined_csv.to_csv(gdrive+results_folder+huc+"_summary.csv", index=False, encoding='utf-8-sig')
    
    
def combined_segGeo_csv(basin_ls, gdrive, data_folder, results_folder):
    """Combines all the basins together into one csv.

        This function takes a list of basins and creates a combined csv. The 
        list of basins is used to read in each corresponding csv, which are 
        concatenated into the same dataframe. That combined dataframe is then 
        printed out to csv.

        Parameters:
            basin_ls (List):
                List of basins whose csvs will be read in.
            folder (string):
                Folder on the Google Drive where csv are be saved.
            huc (string):
                HUC value to be evaluated.
            extension (string):
                Csv extension that varies by HUC value.
            HUC_summary_list (List):
                List of basin names with their HUC extension added.
            combined_csv (pandas.DataFrame):
                Dataframe that contains all basins.
                columns
                    add columns here with descriptions
    

        Returns:
            A single csv containing all the data from each basin csv.
    """        
    os.chdir(gdrive+data_folder)

    # Make list of names of files to be read in (by basin and HUC value)
    extension = '_segGeo.shp'
    basin_summary_list = [i+extension for i in basin_ls]

    # Combine all basin csvs together into a dataframe
    combined_csv = pd.concat([gp.read_file(b) for b in basin_summary_list])
    print("all basins added")
    
    os.chdir(gdrive+results_folder)
    # Export to shp 
    # combined_csv.to_csv("all_basins_segGeo.csv", index=False, encoding='utf-8-sig')
    combined_csv.to_file("all_basins_segGeo.shp")
    print("combined shapefile written")
    # print(type(combined_csv))

    return combined_csv
    
    

