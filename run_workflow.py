"""
This script runs the entire river bifurcation workflow.

Created by: Laura Condon and Rachel Spinti
"""
# %%
import pandas as pd, numpy as np, geopandas as gp, matplotlib.pyplot as plt
import datetime, matplotlib as mpl
import bifurcate as bfc, create_csvs as crc
from shapely import wkt
from pathlib import Path
plt.style.use('classic')

##folder on the GDrive to save output files to
folder = 'test_workflow/'
gdrive = "/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo/" #where shapefiles/csv live 

# %%
# Read in data

##all the basins
# basin_ls = ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes',
# 'Gulf Coast','Mississippi', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']

##w/o the Mississippi
# basin_ls = ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes',
# 'Gulf Coast', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']

##other
# basin_ls = ['Columbia', 'Red']
# basin_ls = ['Columbia', 'South Atlantic']
# basin_ls = ['Mississippi']
basin_ls = ['Colorado']

# %%
# Create the basin csvs
crc.create_basin_csvs(basin_ls, gdrive, folder)   #if the specified basin csv does not exist, extract it

# Run bifurcate analysis
t_start = datetime.datetime.now()

for basin in basin_ls:

    # 1. Read  in the segment information for the basin
    segments = pd.read_csv(gdrive + folder + basin + ".csv", index_col='Hydroseq',
                   usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                            'LENGTHKM', 'StartFlag', 'DamCount',
                            'Coordinates', 'DamID',  'QC_MA', 'Norm_stor',
                            'HUC2', 'HUC4', 'HUC8', 'StreamOrde'])

    # Unit conversion  - convert flow and storage to million cubic meters
    segments.QC_MA = (segments.QC_MA * 365 * 24 * 3600 * 0.0283168)/(10**6) #QC_MA = Average flow in cfs 
    segments.Norm_stor = (segments.Norm_stor * 1233.48)/(10**6) #Norm_stor =  normal storage in acre feet

    #__________________________________________________________

    # 2. Aggregate segment values by upstream area
    # Aggregate upstream storage, number of dams, and upstream length for every segment
    t0 = datetime.datetime.now()
    agg_list = ['Norm_stor', 'DamCount', 'LENGTHKM', 'QC_MA']
    segments_up = bfc.upstream_ag(data=segments, downIDs='DnHydroseq', 
                                agg_value=agg_list)
    
    t1 = datetime.datetime.now()
    print("Aggregate by Upstream segments:", (t1-t0))

    # Add the resulting upstream aggregates back into segments DF with the upstream_count
    uplist=[i+'_up' for i in agg_list]
    segments[uplist]=segments_up[uplist]
    segments["upstream_count"] = segments_up["upstream_count"]

    #__________________________________________________________
    
    # 3.  Calculate Degree of Regulation 
    t2 = datetime.datetime.now()
    segments['DOR'] = segments.Norm_stor_up /  \
        segments.QC_MA 
    #Give a value of -1 to locations where QC_MA is 0 and storage is positive
    segments.DOR[(segments['QC_MA'] == 0) & (segments['Norm_stor_up'] >0)] = -1
    # Give a value of 0 to anywhere that Norm_stor_up is 0 (results in NAs when norm stor up is 0 and q is 0)
    segments.DOR[segments['Norm_stor_up'] == 0] = 0

    t3 = datetime.datetime.now()
    print("Calculate DOR:", (t3-t2))

    #__________________________________________________________

    # 4. Divide into fragments and get average fragment properties
    # Create fragments 
    t4 = datetime.datetime.now()
    segments = bfc.make_fragments(
        segments, exit_id=52000, verbose=False, subwatershed=True)
    t5 = datetime.datetime.now()
    print("Make Fragments:", (t5-t4))

    # Aggregate values by fragments
    fragments = bfc.agg_by_frag(segments)

    #__________________________________________________________

    # 5. Caculate the DCI
    # adding length squared for aggregation
    fragments['LENGTHKM_sq'] = fragments.LENGTHKM ** 2

    # aggregate l2 by upstream 
    t6 = datetime.datetime.now()

    fragments_dci = bfc.upstream_ag(
        data=fragments, downIDs='Frag_dstr', agg_value=['LENGTHKM_sq', 'LENGTHKM'])
    #sum of upstream square fragment length excluding current fragment
    fragments_dci['LENGTHKM_sq_upexclude'] = fragments_dci['LENGTHKM_sq_up'] - \
                                            fragments_dci['LENGTHKM_sq']
    t7 = datetime.datetime.now()
    print("Aggregate by Upstream fragments:", (t7-t6))

    ## Calculate fragment dcis
    t8 = datetime.datetime.now()
    fragments_dci['dci'] = (fragments_dci['LENGTHKM_sq_upexclude']) / \
        (fragments_dci['LENGTHKM_up'] ** 2)
    segments_dci = segments.merge(fragments_dci, how='left', left_on='Frag',
                            right_index=True, suffixes=('_seg', '_frag'))

    ## Add to segmentsGeo
    var = 'dci'
    segments['dci'] = segments_dci[var]

    t9 = datetime.datetime.now()
    print("Calculate DCI:", (t9-t8))
    fragments.to_csv(gdrive+folder+basin+"_fragments.csv")

    #__________________________________________________________
    
    # 6. Aggregate by HUC
    #Aggregate segment values first
    HUC_vallist=['HUC2','HUC4','HUC8']
    # HUC_vallist=['HUC8']

    for HUC_val in HUC_vallist:
        # print(HUC_val)
        # HUC_val = 'HUC8' # choices are HUC2, HUC4, HUC*

        # Summarize values in the segments table
        HUC_summary = segments.pivot_table(values=['Norm_stor', 'DamCount', 'LENGTHKM'],
                                       index=HUC_val, aggfunc={'Norm_stor': (np.sum, np.max),
                                                                'DamCount': np.sum,
                                                                'LENGTHKM': np.sum})

        #Fixing pivot table columns
        HUC_summary.columns = ["_".join((i,j)) for i,j in HUC_summary.columns]
        HUC_summary.reset_index()

        # print('HUC summary test 1')
        # print(HUC_summary.columns)
        # Then grab variables from the fragments table
        HUC_summaryf = fragments.pivot_table(values=['LENGTHKM'],  index=HUC_val, 
                                         aggfunc={'LENGTHKM': (np.mean, len, np.max)})

        HUC_summaryf.columns = ["_".join((i,j)) for i,j in HUC_summaryf.columns]
        HUC_summaryf.reset_index()

        HUC_summary = pd.concat([HUC_summary, HUC_summaryf], axis=1)

        # print('HUC summary test 2')
        # print(HUC_summary.columns)

        # Identify the most downstream segment in each HUC based on the upstream segment length
        seg_group = segments.groupby(HUC_val)

        # Identify the segment_outlet
        seg_outlet = seg_group.LENGTHKM_up.idxmax() 
        HUC_summary['seg_outlet'] = seg_group.LENGTHKM_up.idxmax() #segment 'outlet'

        # print('HUC summary test 3')
        # print(HUC_summary.columns)

        #Use the segment outlet to look up other columns of interest
        column_list = ['Frag', 'LENGTHKM_up', 'DOR', 'dci', 'Norm_stor_up', 'QC_MA']
        outlet_vals = segments.loc[HUC_summary.seg_outlet, column_list]
        HUC_summary = HUC_summary.join(outlet_vals, on='seg_outlet', rsuffix='_outlet')
    
        # print('HUC summary test 4')
        # print(HUC_summary.columns)

        # HUC_summary = HUC_summary[column_list].add_suffix('_outlet')
        add_suffix = [(i, i+'_outlet') for i in column_list]
        HUC_summary.rename(columns = dict(add_suffix), inplace=True)
        
        # print('HUC summary test 5')
        # print(HUC_summary.columns)

        #LC I think you should stop here in this workflow -- write out the HUC data to csv
        #Then do the merging with shapefiles one time in a separate workflow for HUC analysis

        # write out to csv
        HUC_summary.to_csv(gdrive+folder+basin+HUC_val+'_indices.csv')
        print('Finished writing huc indices to csv')

    #__________________________________________________________

    # 7. Make Segments into a geo dataframe for plotting
    segmentsGeo = segments.copy()
    segmentsGeo.Coordinates = segmentsGeo.Coordinates.astype(str)
    segmentsGeo['Coordinates'] = segmentsGeo['Coordinates'].apply(wkt.loads)
    segmentsGeo = gp.GeoDataFrame(segmentsGeo, geometry='Coordinates')

    ##Create segGeo shapefile for each basin to plot in QGIS
    segmentsGeo.to_file(basin + '_segGeo.shp')
    #__________________________________________________________

## Time to run all basins in basin_ls
t_end = datetime.datetime.now()
print('Time to run all basins = ', t_end-t_start)
print('I ran successfully!')
# %%
