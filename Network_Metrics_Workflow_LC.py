# %%
from pathlib import Path
import pandas as pd
import numpy as np
import geopandas as gp
import matplotlib.pyplot as plt
import matplotlib as mpl
import bifurcate as bfc
import datetime
from shapely import wkt
from pathlib import Path
plt.style.use('classic')

# %%
# OPTIONAL AS NEEDED - reload the Bifucate module --- for testing
#import importlib
#importlib.reload(bfc)

# %%
# Read input data
# "small1019.csv"
# "extracted_HUC1019.csv"
# "Red.csv"
segments = pd.read_csv("extracted_HUC1019.csv", index_col='Hydroseq',
                   usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                            'LENGTHKM', 'StartFlag', 'DamCount',
                            'Coordinates', 'DamID',  'QC_MA', 'Norm_stor'])

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

# %%
# 2. River regulation index
# Weighted average of degree of regulation 
# sum(DOR * segment flow/(sum of all upstream segment flow))

#First multiple DOR * the segment flow/total of all upstream segements flow
segments_up['DOR_scaler'] = segments_up.DOR * segments_up.QC_MA 
t0 = datetime.datetime.now()
RRI_temp = bfc.upstream_ag(
    data=segments_up, downIDs='DnHydroseq', agg_value=['DOR_scaler'])
t1 = datetime.datetime.now()
print('RRI upstream agg', (t1-t0))

RRI = RRI_temp.DOR_scaler_up / segments_up.QC_MA_up

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


# %%
# 4. Caculate the RFI - actually I think this is DOF 
# because I'm  doing it with Length for now?

# adding length squared for aggregation
fragments['LENGTHKM_sq'] = fragments.LENGTHKM ** 2

# aggregate l2 by upstream 
t0 = datetime.datetime.now()
fragments_RFI = bfc.upstream_ag(
    data=fragments, downIDs='FragDn', agg_value=['LENGTHKM_sq', 'LENGTHKM'])
#sum of upstream square fragment length excluding current fragment
fragments_RFI['LENGTHKM_sq_upexclude'] = fragments_RFI['LENGTHKM_sq_up'] - \
                                        fragments_RFI['LENGTHKM_sq']
t1 = datetime.datetime.now()
print("Aggregate by Upstream fragments:", (t1-t0))

##  Calculating segement RFIs but NOTE:
## This  number will only be correct at the end of fragments
## Upstream from there you need additional logic to figure out
## which fragments are actually upstream from a given segment
#seg_RFI = segments.merge(fragments_up, how='left', left_on='Frag',
#                       right_index=True, suffixes=('_seg', '_frag'))
# (Sum of upstream frag length^2 - length ^2 current frag)/ (length^2 upstream of seg)
#seg_RFI['LENGTHKM_seg_up'] = segments_up.LENGTHKM_up
#seg_RFI['RFI'] = (seg_RFI['LENGTHKM_sq_upexclude']) / \
#    (seg_RFI['LENGTHKM_seg_up'] ** 2)


## Calculate fragment RFIs
fragments_RFI['RFI'] = (fragments_RFI['LENGTHKM_sq_upexclude']) / \
    (fragments_RFI['LENGTHKM_up'] ** 2)
segments_RFI = segments.merge(fragments_RFI, how='left', left_on='Frag',
                         right_index=True, suffixes=('_seg', '_frag'))


# %% 
# Plotting
# Upstream Storage
var = "Norm_stor_up"
segmentsGeo[var] = segments_up[var]
segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
                 legend_kwds={'label': var, 'orientation': "horizontal"})

# Number of upstream segments
var = "upstream_count"
segmentsGeo[var] = segments_up[var]
segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
                 legend_kwds={'label': var, 'orientation': "horizontal"},
              vmin=1, vmax=500)

#Length Upstream 
var = "LENGTHKM_up"
segmentsGeo[var] = segments_up[var]
segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
                 legend_kwds={'label': var, 'orientation': "horizontal"})


#Number of dams upstream 
var = "DamCount_up"
segmentsGeo[var] = segments_up[var]
segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
                 legend_kwds={'label': var, 'orientation': "horizontal"},
                vmin=0, vmax=10)

#Number of dams 
var = "DamCount"
segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
                 legend_kwds={'label': var, 'orientation': "horizontal"})

#Average flow
var = "QC_MA"
segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
                 legend_kwds={'label': var, 'orientation': "horizontal"})

#Degree of Regulation
var = "DOR"
segmentsGeo[var] = segments_up[var]
segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
                 legend_kwds={'label': var, 'orientation': "horizontal"},
                 vmin=0, vmax=1)

#RRI
var='RRI'
segmentsGeo[var] = RRI
segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
                 legend_kwds={'label': var, 'orientation': "horizontal"}, 
                 vmin=0, vmax=1)

#Fragment_Index
var = 'Frag_Index'
segmentsGeo[var] = segments[var]
segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
                 legend_kwds={'label': var, 'orientation': "horizontal"})

#Number of fragments upstream
var = 'upstream_count'
segmentsGeo[var] = segments_RFI[var]
segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
                 legend_kwds={'label': var, 'orientation': "horizontal"},
                 vmin=0, vmax=4)

#Average fragment length upstream
var = 'avg_LengthUp'
segmentsGeo[var] = segments_RFI['LENGTHKM_up'] / segments_RFI['upstream_count']
segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
                 legend_kwds={'label': var, 'orientation': "horizontal"})

#RFI
var = 'RFI'
segmentsGeo[var] = segments_RFI[var]
segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
                 legend_kwds={'label': var, 'orientation': "horizontal"},
                 vmin=0, vmax=0.1)

