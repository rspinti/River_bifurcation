#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 16:15:39 2020

@author: rachelspinti
"""
# -*- coding: utf-8 -*-
# Load modules and set path
import geopandas as gp
import pandas as pd

from pathlib import Path
gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/GIS/Layers") #where shapefiles/csv live 


# %%
# Read in data
## NHD
# flowlines_test = pd.read_csv(gdrive/"NHDPlusNationalData/NHDFlowlines.csv")  #all NHD Flowlines
flowlines_test = pd.read_csv(gdrive/"NHDPlusNationalData/Test1019.csv")        #HUC 1019 dataset
# flowlines_test = gp.read_file(gdrive/"HUC_test/Test1029.shp")                #this is actually HUC 1019

# flowlines_test = pd.read_csv(gdrive/"NHDPlusNationalData/small1019.csv")     #subset of the 1019
# flowlines_test = pd.read_csv(gdrive/"NHDPlusNationalData/small1019_test2.csv") #another subset of 1019

## NABD
nabd = gp.read_file(gdrive/"nabd_fish_barriers_2012.shp")  #read in NABD from Drive
nabd["DamID"] = range(len(nabd.COMID))  #add DamID 
print(nabd.DamID.unique)

# # %%
# # Merge NABD and NHD
# nabd_nhd_join = nabd.merge(flowlines_test, how= 'right', on='COMID')  # how = 'right': merge is done by adding NABD attributes to NHD flowlines based on COMID
#                                                                       # the result will have the same length as "flowlines_test"
# nabd_nhd_join.to_csv(gdrive/'NHDPlusNationalData/sample_nabd_nhd.csv')  #creates new csv to run in bifurcation_test.py
# print('Finished writing nabd_nhd_join to csv..........', nabd_nhd_join.head(3))