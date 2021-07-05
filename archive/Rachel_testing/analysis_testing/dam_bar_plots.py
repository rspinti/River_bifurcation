#%%
import geopandas as gp, pandas as pd, numpy as np, matplotlib.pyplot as plt
# %%
## Where to pull stuff from
gdrive = "/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo/" 
data_folder = "HPC_runs_fixed/processed_data/"

## Where to put stuff
results_folder = "HPC_runs_fixed/analyzed_data/"

## The basins
basin_ls = ['California', 'Colorado', 'Columbia', 'Great_Basin', 'Great_Lakes',
'Gulf_Coast','Mississippi', 'North_Atlantic', 'Red', 'Rio_Grande','South_Atlantic']

# basin_ls = ['California', 'Colorado']
# basin = "California"

# %%
for basin in basin_ls:
    #GRanD
    grand = pd.read_csv(gdrive+data_folder+"grand_dams/2010/"+basin+".csv", index_col='Hydroseq',
                    usecols=['Hydroseq', 'DamCount','geometry', 'DamID',  'QC_MA', 'Norm_stor',
                                'HUC2', 'HUC4', 'HUC8', 'Year_compl'])
    grand = grand[grand["DamID"]!=0]

    #NABD
    nabd = pd.read_csv(gdrive+data_folder+"2010/"+basin+".csv", index_col='Hydroseq',
                    usecols=['Hydroseq', 'DamCount','geometry', 'DamID',  'QC_MA', 'Norm_stor',
                                'HUC2', 'HUC4', 'HUC8', 'Year_compl'])
    nabd = nabd[nabd["DamID"]!=0]

    ## Total # of dams
    fig1 = plt.figure()
    plt.bar("NABD",len(nabd), label="All dams", color = "black")
    plt.bar("GRanD",len(grand), label = "Big dams", color = "#b63410")
    plt.ylabel("Total number of dams")
    plt.title(basin)
    plt.legend()
    plt.savefig(gdrive+results_folder+"2010/dam_bar_plots/number/"+basin+".png")

    ## Total storage
    fig2 = plt.figure()
    plt.bar("NABD",(sum(nabd.Norm_stor)*1233.48)/(10**6), label="All dams", color = "black")
    plt.bar("GRanD",(sum(grand.Norm_stor)*1233.48)/(10**6), label = "Big dams", color = "#b63410")
    plt.ylabel("Total storage (MCM)")
    plt.title(basin)
    plt.legend()
    plt.savefig(gdrive+results_folder+"2010/dam_bar_plots/storage/"+basin+".png")

# %%
