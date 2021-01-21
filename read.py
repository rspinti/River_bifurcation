import pandas as pd, numpy as np, geopandas as gp, datetime

def read_lines_dams(gdrive):
    """Reads in dams and NHD flowlines for extraction by basin.

    This function is executed if the read_flag in create_csvs.py is False. It reads
    in NABD, then filters the data. Next, GRanD is read in to create the GRanD flag.
    NHD flowlines are read in and filtered to be joined with NABD in extract.py.

    Parameters:
        gdrive (string):
                Data location on the Google Drive.
        
        nabd_dams (pandas.DataFrame): 
            Dataframe providing NABD dam attributes. A unique DamID is added to 
            ID fragments in bifurcate.py. Duplicate dams were dropped.
            columns
                - COMID: Common ID of the NHD flowline, used to like NABD to NHD
                - NIDID: Official unique dam ID (string) from NID
                - Norm_stor: Normal storage of the resevoir in ac-ft
                - Max_stor: Maximum storage of the resevoir in ac-ft
                - Year_compl: Year when original dam structure was completed
                - Purposes: Abbreviations indicate current usage purpose
                - geometry: Point geometry for dam locations
                - DamID: Unique integer ID for each dam to use for fragments
                - Grand_flag: Identifies dams that are contained with GRanD
        grand (pandas.DataFrame):
            Dataframe providing GRanD dam attributes. Used to create a flag.
                - NABD_ID: Official unique dam ID (string) from NID
                - GRAND_ID: Official unique dam ID (string) from GRanD
        nabd (pandas.DataFrame): 
            Dataframe providing NABD dam attributes. Created from a join between
            NABD and GRanD to obtain values in Grand_flag.
            columns
                - COMID: Common ID of the NHD flowline, used to like NABD to NHD
                - NIDID: Official unique dam ID (string) from NID
                - Norm_stor: Normal storage of the resevoir in ac-ft
                - Max_stor: Maximum storage of the resevoir in ac-ft
                - Year_compl: Year when original dam structure was completed
                - Purposes: Abbreviations indicate current usage purpose
                - geometry: Point geometry for dam locations
                - DamID: Unique integer ID for each dam to use for fragments
                - Grand_flag: Identifies dams that are contained with GRanD (0:
                        not in GRand, 1: in GRanD)
        flowlines (pandas.DataFrame): 
            Dataframe containing NHD flowline attributes necessary for processing.
            Each data entry is considered a flowline segment.
            columns
                - Hydroseq: Unique segment ID for current segment, places flowlines
                in hydrologic order
                - UpHydroseq: Unique segment ID for the upstream segment
                - DnHydroseq: Unique segment ID for the downstream segment
                - REACHCODE: 14-digit Hydrologic Unit Code (HUC) from the USGS
                - LENGTHKM: Length of segment in km
                - StartFlag: Flag to indicate if segment is a headwater (0 = not
                headwater, 1 = headwater)
                - FTYPE: Type of flowline
                - COMID: Common ID of the NHD flowline
                - WKT: Geometry of flowline stored in WKT format
                - QE_MA: Estimate of actual mean flow
                - QC_MA: Estimate of “natural” mean flow
                - StreamOrde: Strahler stream order of the segment
                - HUC2: 2-digit HUC 
                - HUC4: 4-digit HUC 
                - HUC2: 8-digit HUC


    Returns:
        The dataframes nabd and flowlines for extract.py.
    """ 
    # Read in data
    t0 = datetime.datetime.now()
    ## NABD
    nabd_dams = gp.read_file(gdrive+"nabd/nabd_fish_barriers_2012.shp", 
                            usecols=['COMID', 'NIDID', 'Norm_stor', 'Max_stor', 
                                    'Year_compl', 'Purposes', 'geometry'])  #read in NABD from Drive
    nabd_dams = nabd_dams.drop_duplicates(subset='NIDID', keep="first")  #drop everything after first duplicate
    nabd_dams["DamID"] = range(len(nabd_dams.COMID))  #add DamID 
    nabd_dams = pd.DataFrame(nabd_dams)
    nabd_dams['Grand_flag'] = np.zeros(len(nabd_dams))  #add flag column

    ## GRanD
    grand = pd.read_csv(gdrive+"other_dam_datasets/Reservoir_Attributes.csv", 
                            usecols=['GRAND_ID', 'NABD_ID'])  #read in NABD from Drive
    #Filter out dams without NABD IDs
    grand['NABD_ID'] = grand['NABD_ID'].fillna(0)
    grand = grand[grand['NABD_ID']!=0]

    #Merge NABD and GRanD
    nabd = pd.merge(nabd_dams, grand, left_on = 'NIDID', right_on = 'NABD_ID', how = 'left')
    nabd['GRAND_ID'] = nabd['GRAND_ID'].fillna(0)
    nabd.loc[nabd.GRAND_ID != 0, 'Grand_flag'] = 1 #if a GRanD ID exists, make flag =1 

    ## NHD
    flowlines = pd.read_csv(gdrive+"nhd/NHDFlowlines.csv",
                                usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                                        'REACHCODE','LENGTHKM', 'StartFlag', 
                                        'FTYPE', 'COMID', 'WKT', 'QE_MA', 'QC_MA',
                                        'StreamOrde'])  #all NHD Flowlines
    
    #Filter the flowlines to select by HUC 2
    flowlines['HUC2'] = flowlines['REACHCODE']/(10**12) #convert Reachcode to HUC 2 format
    flowlines['HUC4'] = flowlines['REACHCODE']/(10**10) #convert Reachcode to HUC 4 format
    flowlines['HUC8'] = flowlines['REACHCODE']/(10**6) #convert Reachcode to HUC 4 format
    flowlines[['HUC2', 'HUC4', 'HUC8']] = flowlines[['HUC2', 'HUC4', 'HUC8']].apply(np.floor) #round down to integer

    #round the hydroseq values because of bug
    flowlines[['UpHydroseq', 'DnHydroseq', 'Hydroseq']] = flowlines[['UpHydroseq', 
                                                                        'DnHydroseq', 
                                                                        'Hydroseq']].round(decimals=0)

#     read_flag = 1
    t1 = datetime.datetime.now()
    print("Time to read in flowlines and dams:", (t1-t0))

    return flowlines, nabd