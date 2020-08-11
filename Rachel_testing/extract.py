
import numpy as np
import geopandas as gp
import pandas as pd
from pathlib import Path
gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/GIS/Layers") #where shapefiles/csv live 

def my_function():
  print("Hello from a very nice function")


# def extract_dams(nabd):
#     ## NABD
#     nabd = gp.read_file(gdrive/"nabd_fish_barriers_2012.shp")  #read in NABD from Drive
#     nabd = nabd.drop_duplicates(subset='NIDID', keep="first")  #drop everything after first duplicate
#     nabd["DamID"] = range(len(nabd.COMID))  #add DamID 
#     # print(nabd.DamID.unique)  #check the DamIDs
#     return nabd


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
  # print(major_basins)
    flowlines = pd.read_csv(gdrive/"NHDPlusNationalData/NHDFlowlines.csv",
                    usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                            'REACHCODE', 'Pathlength', 'LENGTHKM', 
                            'StartFlag', 'FTYPE', 'COMID', 'WKT'])  #all NHD Flowlines
    flowlines['REACHCODE'] = flowlines['REACHCODE']/(10**12) #convert Reachcode to HUC 2 format
    flowlines['REACHCODE'] = flowlines['REACHCODE'].apply(np.floor) #round down to integer
    flowlines[['UpHydroseq', 'DnHydroseq', 'Hydroseq']] = flowlines[['UpHydroseq', 'DnHydroseq', 'Hydroseq']].round(decimals=0)
        #round the hydroseq values because of bug
    flowlines['FTYPE'] = flowlines[flowlines['FTYPE']!= "Coastline"]
    

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
                                (flowlines['REACHCODE'] == major_basins[run_name][1])| 
                                (flowlines['REACHCODE'] == major_basins[run_name][2])| 
                                (flowlines['REACHCODE'] == major_basins[run_name][3]) |
                                (flowlines['REACHCODE'] == major_basins[run_name][4])|
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
  nabd_nhd_join.to_csv(run_name+'.csv')  
  print('Finished writing nabd_nhd_join to '+run_name+'.csv....', nabd_nhd_join.head(3))

  # return nabd_nhd_join

def filter_join(nabd_nhd_join):
  # Add stuff for bifurcation analysis
  ## add a column to keep track of steps
  nabd_nhd_join.insert(5, "step", np.zeros(len(nabd_nhd_join)), True)

  ## fill in the NA's for the dam column with 0s
  nabd_nhd_join['DamID'] = nabd_nhd_join['DamID'].fillna(0)

  ## make a column to indicate if a dam is present or not
  nabd_nhd_join['DamCount'] = np.zeros(len(nabd_nhd_join))
  nabd_nhd_join.loc[nabd_nhd_join.DamID>0, 'DamCount'] = 1

  ## set index to Hydroseq
  nabd_nhd_join = nabd_nhd_join.set_index('Hydroseq')

  # Create geodataframe (for plotting)
  nabd_nhd_join2 = nabd_nhd_join.rename(columns={'WKT': 'Coordinates'})
  nabd_nhd_join2.Coordinates = nabd_nhd_join2.Coordinates.astype(str)
  nabd_nhd_join2['Coordinates'] = nabd_nhd_join2['Coordinates'].apply(wkt.loads)
  nabd_nhd_join2_Geo = gp.GeoDataFrame(nabd_nhd_join2, geometry='Coordinates')

  segments = nabd_nhd_join2_Geo.copy()