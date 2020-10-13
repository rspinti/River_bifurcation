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

gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/GIS/Layers") #where shapefiles/csv live 

# %%
# # Read input data
# # "small1019.csv"
# # "extracted_HUC1019.csv"
# # "Red.csv"
# segments = pd.read_csv("Red.csv", index_col='Hydroseq',
#                    usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
#                             'LENGTHKM', 'StartFlag', 'DamCount',
#                             'Coordinates', 'DamID',  'QC_MA', 'Norm_stor'])

# basin_ls = ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes',
# 'Gulf Coast','Mississippi', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']

## w/o the Mississippi
# basin_ls = ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes',
# 'Gulf Coast', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']
basin_ls = ['extracted_HUC1019']

## If the specified basin csv does not exist, extract it
for basin in basin_ls:
    # Unit conversion  - convert flow and storage to cubic meters
    # QC_MA = Average flow in cfs 
    # Norm_stor =  normal storage in acre feet 

    segments = pd.read_csv(basin+".csv", index_col='Hydroseq',
                   usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                            'LENGTHKM', 'StartFlag', 'DamCount',
                            'Coordinates', 'DamID',  'QC_MA', 'Norm_stor'])


    segments.QC_MA = segments.QC_MA * 365 * 24 * 3600 * 0.0283168
    segments.Norm_stor = segments.Norm_stor * 1233.48



    # Make a geo dataframe for plotting
    segmentsGeo = segments.copy()
    segmentsGeo.Coordinates = segmentsGeo.Coordinates.astype(str)
    segmentsGeo['Coordinates'] = segmentsGeo['Coordinates'].apply(wkt.loads)
    segmentsGeo = gp.GeoDataFrame(segmentsGeo, geometry='Coordinates')



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
    segments_up.to_csv(basin + '_segments_up.csv')
    print(basin + " Upstream segments to csv")



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

    # Export  to csv in case of failure
    RRI_temp.to_csv(basin + '_rri_temp.csv')
    print(basin + " RRI temp to csv")

    RRI.to_csv(basin + '_rri.csv')
    print(basin + " RRI to csv")



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
    fragments.to_csv(basin + '_fragments.csv')
    print(basin + " Fragments to csv")



    # 4. Caculate the dci - actually I think this is DOF 
    # because I'm  doing it with Length for now?

    # adding length squared for aggregation
    fragments['LENGTHKM_sq'] = fragments.LENGTHKM ** 2

    # aggregate l2 by upstream 
    t0 = datetime.datetime.now()
    fragments_dci = bfc.upstream_ag(
        data=fragments, downIDs='FragDn', agg_value=['LENGTHKM_sq', 'LENGTHKM'])
    #sum of upstream square fragment length excluding current fragment
    fragments_dci['LENGTHKM_sq_upexclude'] = fragments_dci['LENGTHKM_sq_up'] - \
                                            fragments_dci['LENGTHKM_sq']
    t1 = datetime.datetime.now()
    print("Aggregate by Upstream fragments:", (t1-t0))

    ##  Calculating segement dcis but NOTE:
    ## This  number will only be correct at the end of fragments
    ## Upstream from there you need additional logic to figure out
    ## which fragments are actually upstream from a given segment
    #seg_dci = segments.merge(fragments_up, how='left', left_on='Frag',
    #                       right_index=True, suffixes=('_seg', '_frag'))
    # (Sum of upstream frag length^2 - length ^2 current frag)/ (length^2 upstream of seg)
    #seg_dci['LENGTHKM_seg_up'] = segments_up.LENGTHKM_up
    #seg_dci['dci'] = (seg_dci['LENGTHKM_sq_upexclude']) / \
    #    (seg_dci['LENGTHKM_seg_up'] ** 2)


    ## Calculate fragment dcis
    fragments_dci['dci'] = (fragments_dci['LENGTHKM_sq_upexclude']) / \
        (fragments_dci['LENGTHKM_up'] ** 2)
    segments_dci = segments.merge(fragments_dci, how='left', left_on='Frag',
                            right_index=True, suffixes=('_seg', '_frag'))
    
    # Export DCI to csv in case of failure
    segments_dci.to_csv(basin + '_segments_dci.csv')
    print(basin + " Segments DCI to csv")
    fragments_dci.to_csv(basin + '_fragments_dci.csv')
    print(basin + " Fragments DCI to csv")



    # Plotting
    # Upstream Storage
    var = "Norm_stor_up"
    segmentsGeo[var] = segments_up[var]
    # segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
    #                  legend_kwds={'label': var, 'orientation': "horizontal"})

    # Number of upstream segments
    var = "upstream_count"
    segmentsGeo[var] = segments_up[var]
    # segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
    #                  legend_kwds={'label': var, 'orientation': "horizontal"},
    #               vmin=1, vmax=500)

    #Length Upstream 
    var = "LENGTHKM_up"
    segmentsGeo[var] = segments_up[var]
    # segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
    #                  legend_kwds={'label': var, 'orientation': "horizontal"})


    #Number of dams upstream 
    var = "DamCount_up"
    segmentsGeo[var] = segments_up[var]
    # segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
    #                  legend_kwds={'label': var, 'orientation': "horizontal"},
    #                 vmin=0, vmax=10)

    #Number of dams 
    # var = "DamCount"
    # segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
    #                  legend_kwds={'label': var, 'orientation': "horizontal"})

    # #Average flow
    # var = "QC_MA"
    # segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
    #                  legend_kwds={'label': var, 'orientation': "horizontal"})

    #Degree of Regulation
    var = "DOR"
    segmentsGeo[var] = segments_up[var]
    # segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
    #                  legend_kwds={'label': var, 'orientation': "horizontal"},
    #                  vmin=0, vmax=1)

    #RRI
    var='RRI'
    segmentsGeo[var] = RRI
    # segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
    #                  legend_kwds={'label': var, 'orientation': "horizontal"}, 
    #                  vmin=0, vmax=1)

    #Fragment_Index
    var = 'Frag_Index'
    segmentsGeo[var] = segments[var]
    segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
                    legend_kwds={'label': var, 'orientation': "horizontal"})

    #Number of fragments upstream
    var = 'upstream_count'
    segmentsGeo[var] = segments_dci[var]
    # segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
    #                  legend_kwds={'label': var, 'orientation': "horizontal"},
    #                  vmin=0, vmax=4)

    #Average fragment length upstream
    var = 'avg_LengthUp'
    segmentsGeo[var] = segments_dci['LENGTHKM_up'] / segments_dci['upstream_count']
    # segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
    #                  legend_kwds={'label': var, 'orientation': "horizontal"})

    #dci
    var = 'dci'
    segmentsGeo[var] = segments_dci[var]
    # segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
    #                  legend_kwds={'label': var, 'orientation': "horizontal"},
    #                  vmin=0, vmax=0.1)

    segmentsGeo.to_csv(basin + '_segGeo.csv')
    # segmentsGeo.to_csv('extracted1019_segGeo.csv')

# %%
# # Fixing the Seg Geo csv

# ## w/o the Mississippi
# basin_ls = ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes',
# 'Gulf Coast', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']
# ## If the specified basin csv does not exist, extract it
# for basin in basin_ls:
#     segments = pd.read_csv(basin+"_segGeo.csv")
#     segments_up = pd.read_csv(basin+"_segments_up.csv")
#     segmentsGeo = segments.copy()
#     fragments_dci = pd.read_csv(basin+"_fragments_dci.csv")
#     fragments = pd.read_csv(basin+"_fragments.csv")
#     segments2 = segments.merge(fragments, how='left', left_on='Frag_Index',
#                                 right_index=True, suffixes=('_seg', '_frag'))
#     segments_dci = segments2.merge(fragments_dci, how='left', left_on='Frag',
#                                 right_index=True, suffixes=('_seg', '_frag'))

#     #Storage upstream
#     var = "Norm_stor_up"
#     segmentsGeo[var] = segments_up[var]

#     #Upstream count
#     var = "upstream_count"
#     segmentsGeo[var] = segments_up[var]

#     #Length Upstream 
#     var = "LENGTHKM_up"
#     segmentsGeo[var] = segments_up[var]
        
#     #Number of dams upstream 
#     var = "DamCount_up"
#     segmentsGeo[var] = segments_up[var]

#     #Degree of Regulation
#     var = "DOR"
#     segmentsGeo[var] = segments_up[var]

#     #Number of fragments upstream
#     var = 'upstream_count'
#     segmentsGeo[var] = segments_dci[var]

#     # #Average fragment length upstream
#     var = 'avg_LengthUp'
#     segmentsGeo[var] = segments_dci['LENGTHKM_up'] / segments_dci['upstream_count']

#     #dci
#     var = 'dci'
#     segmentsGeo[var] = segments_dci[var]

#     # segmentsGeo to csv
#     segmentsGeo.to_csv(basin + '_segGeo.csv')
#     # segmentsGeo.to_csv('extracted1019_segGeo.csv')

# %%
