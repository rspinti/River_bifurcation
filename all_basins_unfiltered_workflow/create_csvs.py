
import pandas as pd, numpy as np, geopandas as gp, extract as ex, os, glob
import datetime
from pathlib import Path

gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo") #where data lives 

def create_basin_csvs(basin_ls):
    # Read in data
    ## NABD
    nabd_dams = gp.read_file(gdrive/"nabd/nabd_fish_barriers_2012.shp", 
                            usecols=['COMID', 'NIDID', 'Norm_stor', 'Max_stor', 
                                    'Year_compl', 'Purposes', 'geometry'])  #read in NABD from Drive
    nabd_dams = nabd_dams.drop_duplicates(subset='NIDID', keep="first")  #drop everything after first duplicate
    nabd_dams["DamID"] = range(len(nabd_dams.COMID))  #add DamID 
    nabd_dams = pd.DataFrame(nabd_dams)
    nabd_dams['Grand_flag'] = np.zeros(len(nabd_dams))  #add flag column
    # print(nabd.DamID.unique)  #check the DamIDs

    ## GRanD
    grand = pd.read_csv(gdrive/"other_dam_datasets/Reservoir_Attributes.csv", 
                            usecols=['GRAND_ID', 'NABD_ID'])  #read in NABD from Drive
    #Filter out dams without NABD IDs
    grand['NABD_ID'] = grand['NABD_ID'].fillna(0)
    # print(grand.GRAND_ID.unique())
    grand = grand[grand['NABD_ID']!=0]

    #Merge NABD and GRanD
    nabd = pd.merge(nabd_dams, grand, left_on = 'NIDID', right_on = 'NABD_ID', how = 'left')
    nabd['GRAND_ID'] = nabd['GRAND_ID'].fillna(0)
    nabd.loc[nabd.GRAND_ID != 0, 'Grand_flag'] = 1 #if a GRanD ID exists, make flag =1 

    #Merge NABD and GRanD
    nabd = pd.merge(nabd_dams, grand, left_on = 'NIDID', right_on = 'NABD_ID', how = 'left')
    nabd['GRAND_ID'] = nabd['GRAND_ID'].fillna(0)
    nabd.loc[nabd.GRAND_ID != 0, 'Grand_flag'] = 1 #if a GRanD ID exists, make flag =1 

    ## NHD
    flowlines = pd.read_csv(gdrive/"nhd/NHDFlowlines.csv",
                                usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                                        'REACHCODE','LENGTHKM', 'StartFlag', 
                                        'FTYPE', 'COMID', 'WKT', 'QE_MA', 'QC_MA',
                                        'STREAMORDER'])  #all NHD Flowlines
    
    #Filter the flowlines to select by HUC 2
    flowlines['HUC2'] = flowlines['REACHCODE']/(10**12) #convert Reachcode to HUC 2 format
    flowlines['HUC4'] = flowlines['REACHCODE']/(10**10) #convert Reachcode to HUC 4 format
    flowlines['HUC8'] = flowlines['REACHCODE']/(10**8) #convert Reachcode to HUC 4 format
    flowlines[['HUC2', 'HUC4', 'HUC8']] = flowlines[['HUC2', 'HUC4', 'HUC8']].apply(np.floor) #round down to integer

    #round the hydroseq values because of bug
    flowlines[['UpHydroseq', 'DnHydroseq', 'Hydroseq']] = flowlines[['UpHydroseq', 
                                                                        'DnHydroseq', 
                                                                        'Hydroseq']].round(decimals=0)
    # flowlines = flowlines[flowlines['FTYPE']!= 'Coastline']  #filter out coastlines

    
    # Read in data
    # basin_ls = ['Red']
    # basin_ls = ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes',
    # 'Gulf Coast','Mississippi', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']


    ## If the specified basin csv does not exist, extract it
    for basin in basin_ls:
        if os.path.isfile(basin+'.csv'):  #does it exist?
            #Read specified basin 
            print(basin + ': Exists')

        else:
            print('\n'basin +  ': Does not exist')
            nabd_nhd = ex.join_dams_flowlines(flowlines, basin, nabd)

def create_combined_csv(basin_ls, folder):
    """Create combined csv of all flowlines.

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


    # Seg Geos
    extension = '_segGeo.csv'
    all_segGeos = [i+extension for i in basin_ls]
    # all_segGeos

    #combine all files in the list
    combined_csv = pd.concat([pd.read_csv(f) for f in all_segGeos])

    #export to csv
    combined_csv.to_csv("combined_segGeo.csv", index=False, encoding='utf-8-sig')

