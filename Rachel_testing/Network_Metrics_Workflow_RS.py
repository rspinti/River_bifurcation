# %%
import pandas as pd, numpy as np, geopandas as gp, matplotlib.pyplot as plt
import matplotlib as mpl, extract as ex
import datetime
from shapely import wkt
from pathlib import Path
plt.style.use('classic')

import sys
sys.path.insert(0, '/Users/rachelspinti/Documents/River_bifurcation')
import bifurcate as bfc

from pathlib import Path
gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/GIS/Layers") #where shapefiles/csv live 

# %%
# RUN this cell only once
# Read in data
## NABD
nabd_dams = gp.read_file(gdrive/"nabd_fish_barriers_2012.shp", 
                        usecols=['COMID', 'NIDID', 'Norm_stor', 'Max_stor', 
                                 'Year_compl', 'Purposes', 'geometry'])  #read in NABD from Drive
nabd_dams = nabd_dams.drop_duplicates(subset='NIDID', keep="first")  #drop everything after first duplicate
nabd_dams["DamID"] = range(len(nabd_dams.COMID))  #add DamID 
nabd_dams = pd.DataFrame(nabd_dams)
nabd_dams['Grand_flag'] = np.zeros(len(nabd_dams))  #add flag column
# print(nabd.DamID.unique)  #check the DamIDs

## GRanD
grand = pd.read_csv(gdrive/"Reservoir_Attributes.csv", 
                        usecols=['GRAND_ID', 'NABD_ID'])  #read in NABD from Drive
#Filter out dams without NABD IDs
grand['NABD_ID'] = grand['NABD_ID'].fillna(0)
# print(grand.GRAND_ID.unique())
grand = grand[grand['NABD_ID']!=0]

#Merge NABD and GRanD
nabd = pd.merge(nabd_dams, grand, left_on = 'NIDID', right_on = 'NABD_ID', how = 'left')
nabd['GRAND_ID'] = nabd['GRAND_ID'].fillna(0)
nabd.loc[nabd.GRAND_ID != 0, 'Grand_flag'] = 1 #if a GRanD ID exists, make flag =1 

## NHD
flowlines = pd.read_csv(gdrive/"NHDPlusNationalData/NHDFlowlines.csv",
                            usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                                     'REACHCODE','LENGTHKM', 'StartFlag', 
                                     'FTYPE', 'COMID', 'WKT', 'QE_MA', 'QC_MA'])  #all NHD Flowlines
# flowlines = pd.read_csv("/Users/rachelspinti/Documents/River_bifurcation/data/nhd/NHDFlowlines.csv",
#                         usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
#                                  'REACHCODE','LENGTHKM', 'StartFlag', 
#                                  'FTYPE', 'COMID', 'WKT', 'QE_MA', 'QC_MA'])  #all NHD Flowlines
#Filter the flowlines to select by HUC 2
flowlines['REACHCODE'] = flowlines['REACHCODE']/(10**12) #convert Reachcode to HUC 2 format
# flowlines['REACHCODE'] = flowlines['REACHCODE']/(10**10) #convert Reachcode to HUC 4 format
flowlines['REACHCODE'] = flowlines['REACHCODE'].apply(np.floor) #round down to integer
#round the hydroseq values because of bug
flowlines[['UpHydroseq', 'DnHydroseq', 'Hydroseq']] = flowlines[['UpHydroseq', 
                                                                     'DnHydroseq', 
                                                                     'Hydroseq']].round(decimals=0)
flowlines = flowlines[flowlines['FTYPE']!= 'Coastline']  #filter out coastlines
# %%
# Choose the major river basin to Run
run_name = 'Rio Grande'  #type river basin name
#run name options
# ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes', 
#  'Gulf Coast','Mississippi', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']


# %%
# Read in data
## If the specified basin csv does not exist, extract it
if os.path.isfile(run_name+'.csv'):  #does it exist?
    #Read specified basin 
    print('Exists')
    segments = pd.read_csv(run_name+'.csv', usecols=['Hydroseq', 'UpHydroseq',
    'DnHydroseq', 'LENGTHKM', 'StartFlag', 'Coordinates','DamID', 'DamCount',
    'Norm_stor', 'QE_MA', 'QC_MA', 'geometry'])
else:
    print('Does not exist')
    nabd_nhd = ex.join_dams_flowlines(flowlines, run_name, nabd)
    segments = pd.read_csv(run_name+'.csv', usecols=['Hydroseq', 'UpHydroseq', 
                                            'DnHydroseq', 
                                            'LENGTHKM', 'StartFlag',
                                            'Coordinates','DamID', 'DamCount', 
                                            'Norm_stor', 'QE_MA', 'QC_MA', 'geometry'])

# %%
# OPTIONAL AS NEEDED - reload the Bifucate module --- for testing
#import importlib
#importlib.reload(bfc)

# %%
# Read input data
# "small1019.csv"
# "extracted_HUC1019.csv"
# "Red.csv"
# segments = pd.read_csv("/Users/rachelspinti/Documents/River_bifurcation/extracted_HUC1019.csv", index_col='Hydroseq',
#                    usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
#                             'LENGTHKM', 'StartFlag', 'DamCount',
#                             'Coordinates','DamID','QC_MA','Norm_stor','geometry'])
# segments = pd.read_csv("/Users/rachelspinti/Documents/River_bifurcation/Red.csv", index_col='Hydroseq',
#                    usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
#                             'LENGTHKM', 'StartFlag', 'DamCount',
#                             'Coordinates', 'DamID',  'QC_MA', 'Norm_stor'])

# Unit conversion  - conver flow and storage to cubic meters
# QC_MA = Average flow in cfs 
# Norm_stor =  normal storage in acre feet 
segments.QC_MA = segments.QC_MA * 365 * 24 * 3600 * 0.0283168
segments.Norm_stor = segments.Norm_stor * 1233.48

# %%
# Make a geo dataframe for plotting
segmentsGeo = segments.copy()
segmentsGeo.Coordinates = segmentsGeo.Coordinates.astype(str)
segmentsGeo['Coordinates'] = segmentsGeo['Coordinates'].apply(wkt.loads)
segmentsGeo = gp.GeoDataFrame(segmentsGeo, geometry='Coordinates')

#%%
# 1. Aggregate segment values by upstream area
# Aggregate upstream storage, number of dams, and upstream length for every segment
t0 = datetime.datetime.now()
segments_up = bfc.upstream_ag(
    data=segments, downIDs='DnHydroseq', agg_value=['Norm_stor', 'DamCount', 'LENGTHKM', 'QC_MA'])
t1 = datetime.datetime.now()
print("Aggregate by Upstream segments:", (t1-t0))

# Calculate Degree of Regulation - need to check units on this
segments_up['QC_MA'] = segments.QC_MA
segments_up['DOR'] = segments_up.Norm_stor_up /  \
    segments.QC_MA 

#Give a value of -1 to locations where QC_MA is 0 and storage is positive
segments_up.DOR[(segments_up['QC_MA'] == 0) & (segments_up['Norm_stor_up'] >0)] = -1

# Give a value of 0 to anywhere that Norm_stor_up is 0 (results in NAs when norm stor up is 0 and q is 0)
segments_up.DOR[segments_up['Norm_stor_up'] == 0] = 0

# Export segments upstream to csv in case of failure
segments_up.to_csv(run_name + '_segments_up.csv')
print("Upstream segments to csv")

# %%
# 2. River regulation index
# Weighted average of degree of regulation 
# sum(DOR * segment flow/(sum of all upstream segment flow))

#First multiple DOR * the segment flow/total of all upstream segments flow
segments_up['DOR_scaler'] = segments_up.DOR * segments_up.QC_MA 
t0 = datetime.datetime.now()
RRI_temp = bfc.upstream_ag(
    data=segments_up, downIDs='DnHydroseq', agg_value=['DOR_scaler'])
t1 = datetime.datetime.now()
print('RRI upstream agg', (t1-t0))

RRI = RRI_temp.DOR_scaler_up / segments_up.QC_MA_up

# Export  to csv in case of failure
RRI_temp.to_csv(run_name + '_rri_temp.csv')
print("RRI temp to csv")

RRI.to_csv(run_name + '_rri.csv')
print("RRI to csv")


# %%
# 3. divide into fragments and get average fragment properties
# Create fragments 
t1 = datetime.datetime.now()
segments = bfc.make_fragments(
    segments, exit_id=52000, verbose=False, subwatershed=True)
t2 = datetime.datetime.now()
print("Make Fragments:", (t2-t1))

# Summarize basic fragment properites
fragments = bfc.agg_by_frag(segments)

# Export fragments to csv in case of failure
fragments.to_csv(run_name + '_fragments.csv')
print("Fragments to csv")

# %%
# 4. Caculate the DCI
# because I'm  doing it with Length for now?

# adding length squared for aggregation
fragments['LENGTHKM_sq'] = fragments.LENGTHKM ** 2

# aggregate l2 by upstream 
t0 = datetime.datetime.now()
fragments_DCI = bfc.upstream_ag(
    data=fragments, downIDs='FragDn', agg_value=['LENGTHKM_sq', 'LENGTHKM'])
#sum of upstream square fragment length excluding current fragment
fragments_DCI['LENGTHKM_sq_upexclude'] = fragments_DCI['LENGTHKM_sq_up'] - \
                                        fragments_DCI['LENGTHKM_sq']
t1 = datetime.datetime.now()
print("Aggregate by Upstream fragments:", (t1-t0))

##  Calculating segment DCIs but NOTE:
## This  number will only be correct at the end of fragments
## Upstream from there you need additional logic to figure out
## which fragments are actually upstream from a given segment
#seg_DCI = segments.merge(fragments_up, how='left', left_on='Frag',
#                       right_index=True, suffixes=('_seg', '_frag'))
# (Sum of upstream frag length^2 - length ^2 current frag)/ (length^2 upstream of seg)
#seg_DCI['LENGTHKM_seg_up'] = segments_up.LENGTHKM_up
#seg_DCI['DCI'] = (seg_DCI['LENGTHKM_sq_upexclude']) / \
#    (seg_DCI['LENGTHKM_seg_up'] ** 2)


## Calculate fragment DCIs
fragments_DCI['DCI'] = (fragments_DCI['LENGTHKM_sq_upexclude']) / \
    (fragments_DCI['LENGTHKM_up'] ** 2)
segments_DCI = segments.merge(fragments_DCI, how='left', left_on='Frag',
                         right_index=True, suffixes=('_seg', '_frag'))

# Export segments upstream to csv in case of failure
fragments_DCI.to_csv(run_name + '_fragments_dci.csv')
print("Fragments DCI to csv")

# %% 
# Plotting
# Upstream Storage
# var = "Norm_stor_up"
# segmentsGeo[var] = segments_up[var]
# segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
#                  legend_kwds={'label': var, 'orientation': "horizontal"})

# # Number of upstream segments
# var = "upstream_count"
# segmentsGeo[var] = segments_up[var]
# segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
#                  legend_kwds={'label': var, 'orientation': "horizontal"},
#               vmin=1, vmax=500)

# #Length Upstream 
# var = "LENGTHKM_up"
# segmentsGeo[var] = segments_up[var]
# segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
#                  legend_kwds={'label': var, 'orientation': "horizontal"})


# #Number of dams upstream 
# var = "DamCount_up"
# segmentsGeo[var] = segments_up[var]
# segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
#                  legend_kwds={'label': var, 'orientation': "horizontal"},
#                 vmin=0, vmax=10)

# #Number of dams 
# var = "DamCount"
# segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
#                  legend_kwds={'label': var, 'orientation': "horizontal"})

# #Average flow
# var = "QC_MA"
# segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
#                  legend_kwds={'label': var, 'orientation': "horizontal"})

# #Degree of Regulation
# var = "DOR"
# segmentsGeo[var] = segments_up[var]
# segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
#                  legend_kwds={'label': var, 'orientation': "horizontal"},
#                  vmin=0, vmax=1)

# #RRI
# var='RRI'
# segmentsGeo[var] = RRI
# segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
#                  legend_kwds={'label': var, 'orientation': "horizontal"}, 
#                  vmin=0, vmax=1)

# #Fragment_Index
# var = 'Frag_Index'
# segmentsGeo[var] = segments[var]
# segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
#                  legend_kwds={'label': var, 'orientation': "horizontal"})

# #Number of fragments upstream
# var = 'upstream_count'
# segmentsGeo[var] = segments_DCI[var]
# segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
#                  legend_kwds={'label': var, 'orientation': "horizontal"},
#                  vmin=0, vmax=4)

# #Average fragment length upstream
# var = 'avg_LengthUp'
# segmentsGeo[var] = segments_DCI['LENGTHKM_up'] / segments_DCI['upstream_count']
# segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
#                  legend_kwds={'label': var, 'orientation': "horizontal"})

# #DCI
# var = 'DCI'
# segmentsGeo[var] = segments_DCI[var]
# segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
#                  legend_kwds={'label': var, 'orientation': "horizontal"},
#                  vmin=0, vmax=0.1)


# %%
segmentsGeo.to_csv(run_name + '_segGeo.csv')
# segmentsGeo.to_csv('extracted1019_segGeo.csv')
# %%
