
import numpy as np
import geopandas as gp
import pandas as pd
from pathlib import Path
from shapely import wkt
gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/GIS/Layers") #where shapefiles/csv live 


def extract_dams():
    ## NABD
    nabd_df = gp.read_file(gdrive/"nabd_fish_barriers_2012.shp")  #read in NABD from Drive
    nabd_df = nabd_df.drop_duplicates(subset='NIDID', keep="first")  #drop everything after first duplicate
    nabd = nabd_df
    nabd["DamID"] = range(len(nabd.COMID))  #add DamID 
    # print(nabd.DamID.unique)  #check the DamIDs
    # return nabd


def join_dams_flowlines(run_name):
    ## NABD
    nabd = gp.read_file(gdrive/"nabd_fish_barriers_2012.shp")  #read in NABD from Drive
    nabd = nabd.drop_duplicates(subset='NIDID', keep="first")  #drop everything after first duplicate
    nabd["DamID"] = range(len(nabd.COMID))  #add DamID 
    # print(nabd.DamID.unique)  #check the DamIDs
    
    ## NHD
    #Dictionary with river basin names and associated HUC 2s
    major_basins = {'California' : [18],
                    'Colorado' : [14, 15],
                    'Columbia' : [17],
                    'Great Basin' : [16], 
                    'Great Lakes' : [4],
                    'Gulf Coast' : [12],
                    'Mississippi' : [5, 6, 7, 8, 10, 11],
                    'North Atlantic' : [1, 2],
                    'Red' : [9],
                    'Rio Grande' : [13],
                    'South Atlantic' : [3]}
    print(major_basins)
    
    flowlines = pd.read_csv(gdrive/"NHDPlusNationalData/NHDFlowlines.csv",usecols=['Hydroseq', 'UpHydroseq', 
                                                                                   'DnHydroseq','REACHCODE', 
                                                                                   'Pathlength', 'LENGTHKM',
                                                                                   'StartFlag', 'FTYPE', 
                                                                                   'COMID', 'WKT'])  #all NHD Flowlines
    flowlines['REACHCODE'] = flowlines['REACHCODE']/(10**12) #convert Reachcode to HUC 2 format
    flowlines['REACHCODE'] = flowlines['REACHCODE'].apply(np.floor) #round down to integer
    #round the hydroseq values because of bug
    flowlines[['UpHydroseq', 'DnHydroseq', 'Hydroseq']] = flowlines[['UpHydroseq', 'DnHydroseq', 'Hydroseq']].round(decimals=0)
    flowlines = flowlines[flowlines['FTYPE']!= 'Coastline']  #filter out coastlines


    #Based on the run name, a different basin will be selected
    
    if run_name == 'California':
        california = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
        nabd_nhd_join = nabd.merge(california, how= 'right', on='COMID') # Merge NABD and NHD
    
    if run_name == 'Colorado':
        colorado = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])| 
        (flowlines['REACHCODE'] == major_basins[run_name][1])]
        nabd_nhd_join = nabd.merge(colorado, how= 'right', on='COMID') # Merge NABD and NHD
    
    if run_name == 'Columbia':
        columbia = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
        nabd_nhd_join = nabd.merge(columbia, how= 'right', on='COMID') # Merge NABD and NHD
    
    if run_name == 'Great Basin':
        great_basin = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
        nabd_nhd_join = nabd.merge(great_basin, how= 'right', on='COMID') # Merge NABD and NHD
    
    if run_name == 'Great Lakes':
        great_lakes = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
        nabd_nhd_join = nabd.merge(great_lakes, how= 'right', on='COMID') # Merge NABD and NHD
    
    if run_name == 'Gulf Coast':
        gulf_coast = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
        nabd_nhd_join = nabd.merge(gulf_coast, how= 'right', on='COMID') # Merge NABD and NHD
        
    if run_name == 'Mississippi':
        mississippi = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])|
        (flowlines['REACHCODE'] == major_basins[run_name][1]) |
        (flowlines['REACHCODE'] == major_basins[run_name][2]) |
        (flowlines['REACHCODE'] == major_basins[run_name][3]) | 
        (flowlines['REACHCODE'] == major_basins[run_name][4]) |
        (flowlines['REACHCODE'] == major_basins[run_name][5])]
        nabd_nhd_join = nabd.merge(mississippi, how= 'right', on='COMID') # Merge NABD and NHD
        
    if run_name == 'North Atlantic':
        north_atlantic = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])|
        (flowlines['REACHCODE'] == major_basins[run_name][1])]
        nabd_nhd_join = nabd.merge(north_atlantic, how= 'right', on='COMID') # Merge NABD and NHD
    
    if run_name == 'Red':
        red = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
        nabd_nhd_join = nabd.merge(red, how= 'right', on='COMID') # Merge NABD and NHD
    
    if run_name == 'Rio Grande':
        rio_grande = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
        nabd_nhd_join = nabd.merge(rio_grande, how= 'right', on='COMID') # Merge NABD and NHD
    
    if run_name == 'South Atlantic':
        south_atlantic = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
        nabd_nhd_join = nabd.merge(south_atlantic, how= 'right', on='COMID') # Merge NABD and NHD
    
    #Creates new csv to run
    print('hi, i worked')
    
    return nabd_nhd_join


def filter_join(nabd_nhd_join, run_name):
  # Add stuff for bifurcation analysis
  ## add a column to keep track of steps
  nabd_nhd_join.insert(5, "step", np.zeros(len(nabd_nhd_join)), True)
  
  ## Filtering the Hydroseq, storage, and dam count
  # Group by Hydroseq and sum storage
  storage_sum = nabd_nhd_join.groupby(['Hydroseq'])['Norm_stor'].sum().reset_index()
  
  # Count # of duplicate dams
  nabd_nhd_join['DamCount'] = np.zeros(len(nabd_nhd_join))  #add count column
  dam_count = nabd_nhd_join.pivot_table(index=['Hydroseq'], aggfunc={'DamCount':'size'}).reset_index() #Aggregate by the size of each Hydroseq
  
  # Merge count and storage dataframes
  count_sum_merge = storage_sum.merge(dam_count, how= 'left', on='Hydroseq')  #merge count and sum 
  
  # Filter nabd_nhd_join for merge
  nabd_nhd_filtered = nabd_nhd_join.drop_duplicates(subset='Hydroseq', keep="last")  #drop everything but last duplicate
  nabd_nhd_filtered = nabd_nhd_filtered.drop(columns=['Norm_stor'])  #drop Norm_stor, so new one is added
  # nabd_nhd_filtered = nabd_nhd_filtered.drop(columns=['Norm_stor', 'DamCount'])  #if dam count exists, use this
  
  # Merge the dataframes so the storage and DamIDs are how we want
  nabd_nhd_join = nabd_nhd_filtered.merge(count_sum_merge, how= 'left', on='Hydroseq') # Merge NABD and NHD
  
  # Fill in the NA's for the dam column with 0s
  nabd_nhd_join['DamID'] = nabd_nhd_join['DamID'].fillna(0)
  
  # Make a column to indicate if a dam is present or not
  nabd_nhd_join.loc[nabd_nhd_join.DamID==0, 'DamCount'] = 0 #if the DamID is 0, make dam count =0
  
  # Set index to Hydroseq
  nabd_nhd_join = nabd_nhd_join.set_index('Hydroseq')


  # Create geodataframe (for plotting)
  nabd_nhd_join2 = nabd_nhd_join.rename(columns={'WKT': 'Coordinates'})
  nabd_nhd_join2.Coordinates = nabd_nhd_join2.Coordinates.astype(str)
  nabd_nhd_join2['Coordinates'] = nabd_nhd_join2['Coordinates'].apply(wkt.loads)
  nabd_nhd_gdf = gp.GeoDataFrame(nabd_nhd_join2, geometry='Coordinates')
  
  #Make segments for bifurcate function
  segments_df = nabd_nhd_gdf.copy()
  # print('segments', segments_df.head(3))
  
  # Creates csv for each run_name
  segments_df.to_csv(run_name+'.csv')  
  print('Finished writing segments_df to csv..........', segments_df.head(3))
  
  # return segments_df

