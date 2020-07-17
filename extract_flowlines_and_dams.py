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
# Select specific HUC 2s (sort by major river basins)
HUC2s = [(i+1) for i in range(18)] #create list with HUC 2 IDs
# print(HUC2s)

flowlines['REACHCODE'] = flowlines['REACHCODE']/(10**12) #convert Reachcode to HUC 2 format
flowlines['REACHCODE'] = flowlines['REACHCODE'].apply(np.floor) #round down to integer

## select Colorado river basin
colorado = flowlines.loc[(flowlines['REACHCODE'] == HUC2s[13])
                          | (flowlines['REACHCODE'] == HUC2s[14])] #select from flowlines by HUC 2
# print(colorado.head(5))
# print(colorado.REACHCODE.unique())

# %%
# Merge NABD and NHD
nabd_nhd_join = nabd.merge(colorado, how= 'right', on='COMID')  

## creates new csv to run in bifurcation_test_Complete.py
nabd_nhd_join.to_csv('colorado.csv')  
# nabd_nhd_join.to_csv(gdrive/'NHDPlusNationalData/sample_nabd_nhd.csv') 
print('Finished writing nabd_nhd_join to csv..........', nabd_nhd_join.head(3))