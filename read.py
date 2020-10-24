import pandas as pd, numpy as np, geopandas as gp, datetime

def read_lines_dams(gdrive):
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
    flowlines['HUC8'] = flowlines['REACHCODE']/(10**8) #convert Reachcode to HUC 4 format
    flowlines[['HUC2', 'HUC4', 'HUC8']] = flowlines[['HUC2', 'HUC4', 'HUC8']].apply(np.floor) #round down to integer

    #round the hydroseq values because of bug
    flowlines[['UpHydroseq', 'DnHydroseq', 'Hydroseq']] = flowlines[['UpHydroseq', 
                                                                        'DnHydroseq', 
                                                                        'Hydroseq']].round(decimals=0)

    read_flag = 1
    t1 = datetime.datetime.now()
    print("Time to read in flowlines and dams:", (t1-t0))

    return flowlines, nabd