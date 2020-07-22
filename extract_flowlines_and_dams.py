#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 16:15:39 2020

@author: rachelspinti

Purpose: extract the flowlines of select HUC 2 basins and merge them with dams
"""
# -*- coding: utf-8 -*-
# Load modules and set path
import geopandas as gp
import pandas as pd
import numpy as np

from pathlib import Path
gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/GIS/Layers") #where shapefiles/csv live 

# %%
# Read in data
## NHD flowlines
flowlines = pd.read_csv(gdrive/"NHDPlusNationalData/NHDFlowlines.csv",
                    usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                            'REACHCODE', 'Pathlength', 'LENGTHKM', 
                            'StartFlag', 'COMID', 'WKT'])  #all NHD Flowlines

## NABD
nabd = gp.read_file(gdrive/"nabd_fish_barriers_2012.shp") #read in NABD from Drive
nabd["DamID"] = range(len(nabd.COMID))  #add DamID 
# print(nabd.DamID.unique)  #check the DamIDs

# %%
# Choose the major river basin to RUN
run_name = 'Mississippi'  #type river basin name
#run name options
# ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes', 
#  'Gulf Coast','Mississippi', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']

# Change REACHCODE to 2-digit format
flowlines['REACHCODE'] = flowlines['REACHCODE']/(10**12) #convert Reachcode to HUC 2 format
flowlines['REACHCODE'] = flowlines['REACHCODE'].apply(np.floor) #round down to integer


#put this in a function!!!
# Dictionary with river basin names and associated HUC 2s
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
    
# Based on the run name, a different basin will be selected
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

# %%
# Creates new csv to run in bifurcation_test_Complete.py
nabd_nhd_join.to_csv(run_name+'.csv')  
# nabd_nhd_join.to_csv(gdrive/'NHDPlusNationalData/sample_nabd_nhd.csv') 
print('Finished writing nabd_nhd_join to csv..........', nabd_nhd_join.head(3))