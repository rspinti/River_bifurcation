#%%
import geopandas as gp, pandas as pd, numpy as np, matplotlib.pyplot as plt
from numpy.core.fromnumeric import size
# %%
## Where to pull stuff from
gdrive = "/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo/" 
data_folder = "final_analysis/processed_data/"

## Where to put stuff
results_folder = "final_analysis/analyzed_data/"

## The basins
basin_ls = ['Great_Basin', 'Colorado', 'Rio_Grande', 'California', 'Gulf_Coast', 'Red', 
'Mississippi', 'Columbia', 'South_Atlantic', 'Great_Lakes', 'North_Atlantic']
# basin_ls = ['Great_Basin', 'Colorado', 'Rio_Grande', 'California', 'Gulf_Coast', 'Red',
#  'Columbia', 'South_Atlantic', 'Great_Lakes', 'North_Atlantic']

# basin_ls = ['California', 'Colorado']
# basin = "California"
basin_abr = ["GB", "CO", "RG", "CA", "GC", "RE", "MI", "CB", "SA", "GL", "NA"]
# %%
# Plotting
c_nabd = ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fff66f', '#d1ef77', '#79ce6b', '#5bbb9d', '#3288bd', '#3952aa', '#4f438e']
# c_nabd = ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fff66f', '#d1ef77', '#5bbb9d', '#3288bd', '#3952aa', '#4f438e']
# # c_grand = ['#800035', '#992c39', '#cc5a38', '#d99453', '#e6de64', '#b3cc65', '#62a656', '#4a9980', '#287099', '#2e448c', '#383066']
c_grand = ['#740030', '#842532', '#9a422a', '#98683a', '#afa94c', '#86994c', '#416e39', '#326857', '#1b4c69', '#213063', '#2a244e']
# c_grand = ['#740030', '#842532', '#9a422a', '#98683a', '#afa94c', '#86994c', '#326857', '#1b4c69', '#213063', '#2a244e']
# xlabels = ['Great Basin', 'Colorado', 'Rio Grande', 'California', 'Gulf Coast', 'Red',
#  'Columbia', 'South Atlantic', 'Great Lakes', 'North Atlantic']

# fig1 = plt.figure()
fig1, ax1 = plt.subplots(1, 1, figsize=(15, 10))
fig2, ax2 = plt.subplots(1, 1, figsize=(15, 10))
for count, basin in enumerate(basin_ls):
    #GRanD
    grand = pd.read_csv(gdrive+data_folder+"grand_data/2010/"+basin+".csv", index_col='Hydroseq',
                    usecols=['Hydroseq', 'DamCount','geometry', 'DamID',  'QC_MA', 'Norm_stor',
                                'HUC2', 'HUC4', 'HUC8', 'Year_compl'])
    grand = grand[grand["DamID"]!=0]

    #NABD
    nabd = pd.read_csv(gdrive+data_folder+"nabd_data/2010/"+basin+".csv", index_col='Hydroseq',
                    usecols=['Hydroseq', 'DamCount','geometry', 'DamID',  'QC_MA', 'Norm_stor',
                                'HUC2', 'HUC4', 'HUC8', 'Year_compl'])
    nabd = nabd[nabd["DamID"]!=0]

    ## Total # of dams
    # ax1 = plt.subplot()
    # ax1.bar(basin,len(nabd), label="All dams "+basin, color = c_nabd[count])
    ax1.bar(basin,len(nabd), color = c_nabd[count])
    # ax1.bar(basin,len(grand), label ="Big dams "+basin, color = c_grand[count])
    ax1.bar(basin,len(grand), color = c_grand[count])
    ax1.set_ylabel("Total number of dams", size=30)
    ax1.set_xlabel("Basin", size=30)
    ax1.set_xticklabels(basin_abr)
    ax1.tick_params(axis = 'both', which = 'major', labelsize = 28)
    #plt.legend()
    # plt.show()
    fig1.savefig(gdrive+results_folder+"bar_plots/number_dams.png")

    ## Total storage
    ax2 = plt.subplot(111)
    
    ax2.bar(basin,(sum(nabd.Norm_stor)*1233.48)/(10**6), color = c_nabd[count])
    ax2.bar(basin,(sum(grand.Norm_stor)*1233.48)/(10**6), color = c_grand[count])
    ax2.set_ylabel("Total storage (MCM)", size=30)
    ax2.set_xlabel("Basins", size=30)
    ax2.set_xticklabels(basin_abr)
    ax2.tick_params(axis='both', which='major', labelsize=28)
    # plt.title(basin)
    # plt.legend(bbox_to_anchor=(1, 0.7, 0.5, 0), fontsize=14)
    plt.tight_layout()
    # plt.legend(bbox_to_anchor=[1, 0.75, 0.2, 0])
    # plt.show()
    fig2.savefig(gdrive+results_folder+"bar_plots/dam_storage.png")

# %%
