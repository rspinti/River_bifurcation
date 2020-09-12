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
# Read in the csv and set Hydroseq as the index
#test = pd.read_csv("extracted_HUC1019.csv", index_col='Hydroseq',
#                    usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
#                           'Pathlength', 'LENGTHKM', 'StartFlag',
#                            'WKT', 'DamID', 'DamCount'])
#"small1019.csv"
# "extracted_HUC1019.csv"
# "Red.csv"
test = pd.read_csv("extracted_HUC1019.csv", index_col='Hydroseq',
                   usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                            'LENGTHKM', 'StartFlag', 'DamCount',
                            'Coordinates', 'DamID',  'QC_MA', 'Norm_stor'])
# test_i=test.set_index('Hydroseq') #alternate way to set the indes
# after the fact


# Test for the Mississippi
#gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/GIS/Layers")  # where shapefiles/csv live 
#test = pd.read_csv(run_name+'.csv', usecols=['Hydroseq', 'UpHydroseq',
#                                                 'DnHydroseq',
#                                                 'LENGTHKM', 'StartFlag',
#                                                 'Coordinates', 'DamID', 'DamCount',
#                                                 'Norm_stor', 'QE_MA', 'QC_MA'])

# fill in the NA's for the dam column with 0s
test['DamID'] = test['DamID'].fillna(0)

# %%
# add a column to keep track of steps
#test.insert(5, "step", np.zeros(len(test)), True)


# Copying over the dam IDs into a new fragment column
#Making adding this step to the function so its not needed here
#test['Frag'] = test['DamID']
# make a column to indicate if a dam is present or not 
##!!ONLY uncomment this if you are running small1019.csv. The others already have this column
#test['DamCount'] = np.zeros(len(test))
#test.loc[test.DamID>0, 'DamCount'] = 1

# Fix the hydroseq columns, so they are integers
#test['UpHydroseq'] = test['UpHydroseq'].round(decimals=0)
#test['DnHydroseq'] = test['DnHydroseq'].round(decimals=0)
#test['Hydroseq'] = test['Hydroseq'].round(decimals=0)
#test.set_index('Hydroseq')

# %%
# test.rename(columns={'WKT': 'Coordinates'}) #rename column
#test2 = test.rename(columns={'WKT': 'Coordinates'})
test2 = test
test2.Coordinates = test2.Coordinates.astype(str)
test2['Coordinates'] = test2['Coordinates'].apply(wkt.loads)
test2Geo = gp.GeoDataFrame(test2, geometry='Coordinates')

segments = test2Geo.copy()

# %%
#reload the Bifucate module --- for testing
import importlib
importlib.reload(bfc)

#%%
t1 = datetime.datetime.now() 
# STEP1:  Make Fragments
segments=bfc.make_fragments(segments, exit_id=52000, verbose=False, subwatershed=True)
t2 = datetime.datetime.now()
print("Make Fragments:", (t2-t1))

# STEP 2: Making a fragment data frame and aggregated by fragment
fragments = bfc.agg_by_frag(segments)
t3 = datetime.datetime.now()
print("Aggregate by fragments:", (t3-t2))

# STEP 3: Map Upstream Fragments 
UpDict = bfc.map_up_frag(fragments)
t4 = datetime.datetime.now()
print("Map Upstream fragments:", (t4-t3))

#STEP 4: Aggregate fragments by upstream area
fragments=bfc.agg_by_frag_up(fragments, UpDict)
#convert annual flow to acre feet
fragments['QC_MA_AF'] = (fragments.QC_MA * 365 * 24 * 3600) / 43559.9 
fragments['DOR'] = (fragments.StorUp) / (fragments.QC_MA_AF)
t5 = datetime.datetime.now()
print("Aggregate by Upstream fragments:", (t5-t4))

#STEP 5: Aggregate segments by upstream 
t6 = datetime.datetime.now()
segments_up = bfc.upstream_ag(data=segments, downIDs = 'DnHydroseq', agg_value='Norm_stor')
t7 = datetime.datetime.now()
print("Aggregate by Upstream segments:", (t7-t6))

## add these columns to the segments datafamre
segments['segment_count'] = segments_up['segment_count']
segments['Norm_stor_up'] = segments_up['Norm_stor_up']

print("---- TIMING SUMMARY -----")
print("Make Fragments:", (t2-t1))
print("Aggregate by fragments:", (t3-t2))
print("Map Upstream fragments:", (t4-t3))
print("Map Upstream fragments:", (t5-t4))
print("Agg Segments Upstream:", (t7-t6))


# %%
# STEP 5: Map Upstream Segments
t5.5 = datetime.datetime.now()
UpDictSeg = bfc.map_up_seg(segments)
t6 = datetime.datetime.now()
print("Map Upstream segments:", (t6-t5.5))


print("---- TIMING SUMMARY -----")
print("Make Fragments:", (t2-t1))
print("Aggregate by fragments:", (t3-t2))
print("Map Upstream fragments:", (t4-t3))
print("Aggregate by upstream:", (t5-t4))
print("Map Upstream segments:", (t6-t5.5))
print("Total Time:", (t6-t1))

# %%
# Working on metrics
# Problems 
# - For the fragments the QC_MA is NA for the no dam fragments -- ie the outlet ones
# - DOR actually only makes sense on the fragment level. See issuues with segments. 
# - Would need to recalculate upstream storage by segments. 

#STEP 5: Merge the fragment information back to the segments
segments_summary = segments.merge(fragments, how='left', left_on='Frag',
                       right_index=True, suffixes=('_seg', '_frag'))


#calculate the upstream storage by segments
segments_summary['StorUp_seg'] = np.zeros(len(segments_summary))
damlist = segments_summary.index[segments_summary['Norm_stor_seg'] > 0]
notdamlist = segments_summary.index[segments_summary.Norm_stor_seg.isnull()]

# if its a segment with a dam then the upstream storage = fragment upstream storage
segments_summary.loc[damlist,
                'StorUp_seg'] = segments_summary.loc[damlist, 'StorUp']

# if its not a segment with a dam then the upstream storage = fragment upstream storage - fragmenst storage
segments_summary.loc[notdamlist,
                'StorUp_seg'] = segments_summary.loc[notdamlist, 'StorUp'] - segments_summary.loc[notdamlist, 'Norm_stor_frag']


#Degree of regulation 
# Total upstream storage/Flow
segments_summary['DOR'] = segments_summary.StorUp_seg  /  \
    segments_summary.QC_MA_seg



# %%
#testing = segments.loc[segments.Frag == 0]
print(segments.loc[segments.Frag == 0])  # check for any segments not covered

# %%
#fig, ax = plt.subplots(1, 1)
#gradient = np.linspace(2000, 4000, 256)
#divider = make_axes_locatable(ax)
#cax = divider.append_axes("right", size="5%", pad=0.1)
#pcm = ax.pcolormesh(x, y, segments.Frag, vmin=-1., vmax=1., cmap='RdBu_r'
#cbar = mpl.colorbar.ColorbarBase(ax, cmap=cm,
#     norm=mpl.colors.Normalize(vmin=-0.5, vmax=1.5))
#im=segments.plot(column='Frag', ax=ax,  legend=True, cmap='viridis_r',
#           legend_kwds={'label': "Fragment #", 'orientation': "horizontal"})
#fig.colorbar(im, ax=ax)
#im.sett_clim(0,10)
#plt.show()

#segments.plot(column='Frag', legend=True, cmap='viridis_r',
#              legend_kwds={'label': "Fragment #", 'orientation': "horizontal"},
#              vmin=51030, vmax=52040)
#segments.plot(column='Frag', legend=True, cmap='viridis_r',
#              legend_kwds={'label': "Fragment #", 'orientation': "horizontal"},
#              vmin=52000, vmax=52040)
#segments.plot(column='Frag', legend=True, cmap='viridis_r',
#              legend_kwds={'label': "Fragment #", 'orientation': "horizontal"},
#              vmin=51000,vmax=51005)

segments.plot(column='Frag_Index', legend=True, cmap='viridis_r',
              legend_kwds={'label': "Fragment Index", 'orientation': "horizontal"})

segments.plot(column='step', legend=True, cmap='viridis_r',
              legend_kwds={'label': "Fragment Index", 'orientation': "horizontal"})

segments.plot(column='segment_count', legend=True, cmap='viridis_r',
              legend_kwds={'label': "Fragment Index", 'orientation': "horizontal"},
              vmin=1, vmax=50)

segments.plot(column='Norm_stor_up', legend=True, cmap='viridis_r',
              legend_kwds={'label': "Fragment Index", 'orientation': "horizontal"})

segments.plot(column='Norm_stor', legend=True, cmap='viridis_r',
              legend_kwds={'label': "Fragment Index", 'orientation': "horizontal"})


# %%
 #plot segment information after the merge
fig, ax = plt.subplots(1, 3)
segments_summary.plot(column='StorUp',
                      ax=ax[0], legend=True)
segments_summary.plot(column='QC_MA_AF',
                      ax=ax[1], legend=True)
segments_summary.plot(column='DOR',
                      ax=ax[2], legend=True)

        
#segments_summary.columns
#Index(['Coordinates', 'LENGTHKM_seg', 'Pathlength', 'StartFlag', 'UpHydroseq',
 #      'step', 'DamID', 'DnHydroseq_seg', 'QC_MA_seg', 'Norm_stor_seg',
 #      'DamCount_seg', 'Frag', 'Headwater', 'Frag_Index_seg', 'DamCount_frag',
 #      'LENGTHKM_frag', 'Norm_stor_frag', 'Frag_Index_frag', 'DnHydroseq_frag',
 #      'QC_MA_frag', 'FragDn', 'HeadFlag', 'NFragUp', 'LengthUp', 'NDamUp',
 #     'StorUp'],
 #     dtype='object')

# %%
# Some plotting
#print(segments.columns)
#segments['Frag'] = segments['Frag'].fillna(0)

fig, ax = plt.subplots(1, 2)
segments.plot(column='DamID', ax=ax[0], legend=True)
segments.plot(column='Frag', ax=ax[1], legend=True)

#testplot = segments.loc[segments.Frag == 0]
#testplot.plot(column='DamID', ax=ax[1], legend=True)


#segments.plot(column='step', ax=ax[1], legend=True)
plt.show()

#

# %%
# Doing some summaries to cross check calculations
#print(fragments)
print(segments.loc[segments.Frag == 0]) #check for any segments not covered
temp = segments.pivot_table('LENGTHKM', index='Frag', aggfunc=sum)
print(temp)
print(sum(temp['LENGTHKM']))
print(sum(segments.LENGTHKM))
# alternate approach to pivot tabel
# segments.groupby('Frag')[['LENGTHKM']].sum()


# %%
## Rachel testing the plotting to see what happens with Fragments
## Was testing HUC4 1019
fig, ax = plt.subplots(1, 2)
x = segments[segments['Frag'] <12000]  #this filter value might change 
                                  # depending on the range of vlaues for Frags
x.plot(column='Frag', ax=ax[0], legend=True)
y = segments[segments['Frag'] >12000]  #this filter value might change 
y.plot(column='Frag', ax=ax[1], legend=True)
plt.show()
