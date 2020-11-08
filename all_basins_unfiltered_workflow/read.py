import pandas as pd, numpy as np, geopandas as gp, datetime, os

def read_lines_dams(gdrive):
    # Read in data
    t0 = datetime.datetime.now()
    ## NABD
    nabd_dams = gp.read_file(gdrive+"nabd/nabd_fish_barriers_2012.shp")  #read in NABD from Drive
#     nabd_dams = pd.DataFrame(nabd_dams)
#     nabd_dams = nabd_dams[['COMID', 'NIDID', 'Norm_stor', 'Max_stor', 'Year_compl', 'Purposes', 'Dam_name', 'geometry']]
#     nabd_dams = nabd_dams.drop_duplicates(subset='NIDID', keep="first").reset_index(drop=True)   #drop everything after first duplicate

    #Updating the NIDIDs that are wrong

    #Adding the large dams that were missing 
    dams_adding = pd.read_csv('/Users/rachelspinti/Documents/River_bifurcation/dams_to_add_sjoin.csv', usecols=['join_COMID', 'NIDID', 'Norm_stor', 'Max_stor', 'Year_compl', 'Purposes', 'WKT'])
    dams_adding = dams_adding.rename(columns = {'join_COMID':'COMID', 'WKT':'geometry'})
    nabd_dams = nabd_dams.append(dams_adding)

   #Create new NABD shapefile w/ adding dams
   os.chdir(gdrive+'nabd')
   read_flag = False
   if os.path.isfile('nabd_updated.csv'):  #does it exist? 
         print( 'nabd_updated exists')

   else:
      if read_flag == False:
         nabd_dams.to_file(gdrive+'nabd/nabd_updated.shp')
         read_flag = True
         print('\n', 'nabd_updated does not exist')
    

    #Add things to NABD
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
    flowlines['HUC8'] = flowlines['REACHCODE']/(10**6) #convert Reachcode to HUC 8 format
    flowlines[['HUC2', 'HUC4', 'HUC8']] = flowlines[['HUC2', 'HUC4', 'HUC8']].apply(np.floor) #round down to integer

    #round the hydroseq values because of bug
    flowlines[['UpHydroseq', 'DnHydroseq', 'Hydroseq']] = flowlines[['UpHydroseq', 
                                                                        'DnHydroseq', 
                                                                        'Hydroseq']].round(decimals=0)

    read_flag = 1
    t1 = datetime.datetime.now()
    print("Time to read in flowlines and dams:", (t1-t0))

    return flowlines, nabd