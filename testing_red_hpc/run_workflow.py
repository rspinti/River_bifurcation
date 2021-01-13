"""
This script runs the entire river bifurcation workflow.

Created by: Laura Condon and Rachel Spinti
"""
# %%
import pandas as pd, numpy as np, geopandas as gp, matplotlib.pyplot as plt
import datetime, matplotlib as mpl
import bifurcate as bfc, create_csvs as crc, average_by_HUC as abh
from shapely import wkt
from pathlib import Path
plt.style.use('classic')

##folder on the GDrive to save output files to
# folder = 'test_workflow/'

# gdrive = "/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo/" #where shapefiles/csv live 

# %%
# Read in data

##all the basins
# basin_ls = ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes',
# 'Gulf Coast','Mississippi', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']

##w/o the Mississippi
# basin_ls = ['California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes',
# 'Gulf Coast', 'North Atlantic', 'Red', 'Rio Grande','South Atlantic']

##other
# basin_ls = ['Columbia']
basin_ls = ['Red']

# %%
# Create the basin csvs
# crc.create_basin_csvs(basin_ls, gdrive, folder)   #if the specified basin csv does not exist, extract it
crc.create_basin_csvs(basin_ls)   #if the specified basin csv does not exist, extract it

# Run bifurcate analysis
t_start = datetime.datetime.now()

for basin in basin_ls:

    # 1. Read  in the segment information for the basin
    # segments = pd.read_csv(gdrive + folder + basin + ".csv", index_col='Hydroseq',
    #                usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
    #                         'LENGTHKM', 'StartFlag', 'DamCount',
    #                         'Coordinates', 'DamID',  'QC_MA', 'Norm_stor',
    #                         'HUC2', 'HUC4', 'HUC8', 'StreamOrde'])
    segments = pd.read_csv(basin + ".csv", index_col='Hydroseq',
                   usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                            'LENGTHKM', 'StartFlag', 'DamCount',
                            'Coordinates', 'DamID',  'QC_MA', 'Norm_stor',
                            'HUC2', 'HUC4', 'HUC8', 'StreamOrde'])

    # Unit conversion  - convert flow and storage to cubic meters
    # QC_MA = Average flow in cfs 
    # Norm_stor =  normal storage in acre feet 
    segments.QC_MA = segments.QC_MA * 365 * 24 * 3600 * 0.0283168
    segments.Norm_stor = segments.Norm_stor * 1233.48
    #__________________________________________________________

    # 2. Aggregate segment values by upstream area
    # Aggregate upstream storage, number of dams, and upstream length for every segment
    t0 = datetime.datetime.now()
    agg_list = ['Norm_stor', 'DamCount', 'LENGTHKM', 'QC_MA']
    segments_up = bfc.upstream_ag(data=segments, downIDs='DnHydroseq', 
                                agg_value=agg_list)
    t1 = datetime.datetime.now()
    print("Aggregate by Upstream segments:", (t1-t0))

    # Add the resulting upstream aggregates back into segmetns DF with the upstream_count
    uplist=[i+'_up' for i in agg_list]
    segments[uplist]=segments_up[uplist]
    segments["upstream_count"] = segments_up["upstream_count"]
    #__________________________________________________________
    
    # 3.  Calculate Degree of Regulation - need to check units on this
    #segments_up['QC_MA'] = segments.QC_MA  #LC-This woulnd't cause a bug but you also dont need to do this this column  is already there
    segments['DOR'] = segments.Norm_stor_up /  \
        segments.QC_MA 
    #Give a value of -1 to locations where QC_MA is 0 and storage is positive
    segments.DOR[(segments['QC_MA'] == 0) & (segments['Norm_stor_up'] >0)] = -1
    # Give a value of 0 to anywhere that Norm_stor_up is 0 (results in NAs when norm stor up is 0 and q is 0)
    segments.DOR[segments['Norm_stor_up'] == 0] = 0

    # Export segments upstream to csv in case of failure
    # segments_up['DOR']=segments['DOR']
    # #segments_up.to_csv(basin + '_segments_up.csv')
    # print(basin + " Upstream segments to csv")
    #__________________________________________________________

    # 4. Calculate River regulation index
    # Weighted average of degree of regulation 
    # sum(DOR * segment flow/(sum of all upstream segment flow))

    #First multiple DOR * the segment flow/total of all upstream segments flow
    # segments['DOR_scaler'] = segments.DOR * segments.QC_MA 
    # t0 = datetime.datetime.now()
    # RRI_temp = bfc.upstream_ag(
    #     data=segments, downIDs='DnHydroseq', agg_value=['DOR_scaler'])
    # t1 = datetime.datetime.now()
    # print('RRI upstream agg', (t1-t0))

    # RRI = RRI_temp.DOR_scaler_up / segments.QC_MA_up

    # # Add to segements Geo
    # segments["RRI"] = RRI
    #LC - Note we should just write out segments, fragments and HUC CSVs in 
    # one step at the bottom. Now that we know it all runs we don't have to be as 
    # worried about saving checkpoints. 

    # Export  to csv in case of failure
    #RRI_temp.to_csv(basin + '_rri_temp.csv')
    #print(basin + " RRI temp to csv")

    #RRI.to_csv(basin + '_rri.csv')
    #print(basin + " RRI to csv")
    #__________________________________________________________
    #import importlib
    #importlib.reload(bfc)

    # 5. divide into fragments and get average fragment properties
    # Create fragments 
    t1 = datetime.datetime.now()
    segments = bfc.make_fragments(
        segments, exit_id=52000, verbose=False, subwatershed=True)
    t2 = datetime.datetime.now()
    print("Make Fragments:", (t2-t1))

    # fggregate values by fragments
    fragments = bfc.agg_by_frag(segments)
    print(fragments.shape)

    # LC - if we want to do any upstream aggregation by fragments this
    # will take some additional work. I deleted the 'average upstream fragment lenght'
    # because it was actually calculating average upstream segment length. 

    # Export fragments to csv in case of failure
    fragments.to_csv(basin + '_fragments.csv')
    print(basin + " Fragments to csv")
    #__________________________________________________________

    # 6. Caculate the dci - actually I think this is DOF 
    # because I'm  doing it with Length for now?

    # adding length squared for aggregation
    fragments['LENGTHKM_sq'] = fragments.LENGTHKM ** 2

    # aggregate l2 by upstream 
    t0 = datetime.datetime.now()
    # fragments_dci = bfc.upstream_ag(
    #     data=fragments, downIDs='FragDn', agg_value=['LENGTHKM_sq', 'LENGTHKM'])

    fragments_dci = bfc.upstream_ag(
        data=fragments, downIDs='Frag_dstr', agg_value=['LENGTHKM_sq', 'LENGTHKM'])
    #sum of upstream square fragment length excluding current fragment
    fragments_dci['LENGTHKM_sq_upexclude'] = fragments_dci['LENGTHKM_sq_up'] - \
                                            fragments_dci['LENGTHKM_sq']
    t1 = datetime.datetime.now()
    print("Aggregate by Upstream fragments:", (t1-t0))

    ##  Calculating segment dcis but NOTE:
    ## This  number will only be correct at the end of fragments
    ## Upstream from there you need additional logic to figure out
    ## which fragments are actually upstream from a given segment
    #  seg_dci = segments.merge(fragments_up, how='left', left_on='Frag',
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

    ## Add to segmentsGeo
    var = 'dci'
    segments['dci'] = segments_dci[var]

    # Export DCI to csv in case of failure
    # segments_dci.to_csv(basin + '_segments_dci.csv')
    # print(basin + " Segments DCI to csv")
    # fragments_dci.to_csv(basin + '_fragments_dci.csv')
    # print(basin + " Fragments DCI to csv")
    #__________________________________________________________
    
    # 7. Aggregate by HUC
    #Aggregate segment values first
    HUC_vallist=['HUC2','HUC4','HUC8']

    for HUC_val in HUC_vallist:
        # print(HUC_val)
        HUC_val = 'HUC8' # choices are HUC2, HUC4, HUC*

        # Summarize values in the segments table
        HUC_summary = segments.pivot_table(values=['Norm_stor', 'DamCount', 'LENGTHKM'],
                                       index=HUC_val, aggfunc={'Norm_stor': np.sum,
                                                                'DamCount': np.sum,
                                                                'LENGTHKM': np.sum})
        # Then grab variables from the fragments table
        HUC_summaryf = fragments.pivot_table(values=['LENGTHKM'],  index=HUC_val, 
                                         aggfunc={'LENGTHKM': (np.mean, len)})
        HUC_summary["Avg_FragLength"] = HUC_summaryf['LENGTHKM']['mean']
        HUC_summary["Frag_Count"] = HUC_summaryf['LENGTHKM']['len']

        # Identify the most downstream segment in each HUC based on the upstream segment length
        seg_group = segments.groupby(HUC_val)
        # Identify the segment_outlet
        seg_outlet = seg_group.LENGTHKM_up.idxmax() 
        HUC_summary['seg_outlet'] = seg_group.LENGTHKM_up.idxmax() #segment 'outlet'

        #Use the segment outlet to look up other columns of interest
        column_list = ['Frag', 'LENGTHKM_up', 'DOR']
        # column_list = ['Frag', 'LENGTHKM_up', 'DOR', 'RRI']
        outlet_vals = segments.loc[HUC_summary.seg_outlet, column_list]
        HUC_summary = HUC_summary.join(outlet_vals, on='seg_outlet', rsuffix='_outlet')
        HUC_summary = HUC_summary[column_list].add_suffix('_outlet')

       # LC - TO Do look into why there are two HUC8's that get the same fragment # 
       # I think its a headwater that crosses but need to be sure
       # Frag ID = 28196, seg IDs = 840000351 & 840000235

        #LC I think you should stop here in this workflow -- write out the HUC data to csv
        #Thendo  the merging withshape files one time in a separate workflow for HUC analysis


        # write out as a shape file
        #filename = gdrive+"hucs/" + HUC_val + "_CONUS.shp"
        #huc_shp = gp.read_file(filename)
        #huc_shp[HUC_val] = huc_shp[HUC_val].astype('int32')
        #huc_shp = huc_shp.merge(HUC_summary, on=HUC_val, how='left')
        #huc_shp.to_file(gdrive+folder+HUC_val+'_indices.shp')
        #print('Finished writing huc indices to shp')

    #__________________________________________________________

    # 8. Make Segments into a geo dataframe for plotting
    segmentsGeo = segments.copy()
    segmentsGeo.Coordinates = segmentsGeo.Coordinates.astype(str)
    segmentsGeo['Coordinates'] = segmentsGeo['Coordinates'].apply(wkt.loads)
    segmentsGeo = gp.GeoDataFrame(segmentsGeo, geometry='Coordinates')

    ##Create segGeo csv for each basin to plot in QGIS
    segmentsGeo.to_csv(basin + '_segGeo.csv')
    #__________________________________________________________
    


    # Optional Test plotting for debugging
    #var = "HUC8"
    #segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
     #                 legend_kwds={'label': var, 'orientation': "horizontal"})
                      #vmin=0, vmax=200)

    # #Average flow
    # var = "QC_MA"
    # segmentsGeo.plot(column=var, legend=True, cmap='viridis_r',
    #                  legend_kwds={'label': var, 'orientation': "horizontal"})


## Time to run all basins in basin_ls
t_end = datetime.datetime.now()
print('Time to run all basins = ', t_end-t_start)

# %%
## Create the combined csv
## LC - I think this should go to a differet script 

# crc.create_combined_csv(basin_ls, folder)
# # crc.create_combined_csv(basin_ls)

# ## Read in 
# combo_segGeo = pd.read_csv(gdrive+folder+'/combined_segGeo.csv')

# abh.avg_HUC2(combo_segGeo, gdrive, folder)
# abh.avg_HUC4(combo_segGeo, gdrive, folder)
# abh.avg_HUC8(combo_segGeo, gdrive, folder)

print('I ran successfully!')

# %%
