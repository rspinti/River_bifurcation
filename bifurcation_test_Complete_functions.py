# %%
import pandas as pd
import numpy as np
import geopandas as gp
import matplotlib.pyplot as plt
import matplotlib as mpl
import bifurcate as bfc
import datetime
from shapely import wkt
plt.style.use('classic')

# %%
# Read in the csv and set Hydroseq as the index
test = pd.read_csv("extracted_HUC1019.csv", index_col='Hydroseq',
                    usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
                           'Pathlength', 'LENGTHKM', 'StartFlag',
                            'WKT', 'DamID', 'DamCount'])
#"small1019.csv"
# "extracted_HUC1019.csv"
#test = pd.read_csv("small1019.csv", 
#                   usecols=['Hydroseq', 'UpHydroseq', 'DnHydroseq',
#                            'Pathlength', 'LENGTHKM', 'StartFlag',
#                            'WKT', 'DamID'])
# test_i=test.set_index('Hydroseq') #alternate way to set the indes
# after the fact

# add a column to keep track of steps
test.insert(5, "step", np.zeros(len(test)), True)
# fill in the NA's for the dam column with 0s
test['DamID'] = test['DamID'].fillna(0)
# Copying over the dam IDs into a new fragment column
#Making adding this step to the function so its not needed here
#test['Frag'] = test['DamID']
# make a column to indicate if a dam is present or not
#test['DamCount'] = np.zeros(len(test))
#test.loc[test.DamID>0, 'DamCount'] = 1

# Fix the hydroseq columns, so they are integers
#test['UpHydroseq'] = test['UpHydroseq'].round(decimals=0)
#test['DnHydroseq'] = test['DnHydroseq'].round(decimals=0)
#test['Hydroseq'] = test['Hydroseq'].round(decimals=0)
#test.set_index('Hydroseq')

# %%
# test.rename(columns={'WKT': 'Coordinates'}) #rename column
test2 = test.rename(columns={'WKT': 'Coordinates'})
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

#STEP 4: Aggregate by upstream area
fragments=bfc.agg_by_frag_up(fragments, UpDict)
t5 = datetime.datetime.now()

print("---- TIMING SUMMARY -----")
print("Make Fragments:", (t2-t1))
print("Aggregate by fragments:", (t3-t2))
print("Map Upstream fragments:", (t4-t3))
print("Aggregate by upstream:", (t5-t4))
print("Total Time:", (t5-t1))

# %%
#testing = segments.loc[segments.Frag == 0]
print(segments.loc[segments.Frag == 0])  # check for any segments not covered

# %%
fig, ax = plt.subplots(1, 1)
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
segments.plot(column='Frag', legend=True, cmap='viridis_r',
              legend_kwds={'label': "Fragment #", 'orientation': "horizontal"},
              vmin=3600,vmax=4400)

# %%
segments.plot(column='Frag', legend=True, cmap='viridis_r',
              legend_kwds={'label': "Fragment #", 'orientation': "horizontal"})



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
