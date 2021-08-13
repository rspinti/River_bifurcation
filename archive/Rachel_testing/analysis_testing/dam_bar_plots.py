#%%
import geopandas as gp, pandas as pd, numpy as np, matplotlib.pyplot as plt, matplotlib.ticker as mtick
from numpy.core.fromnumeric import size
from decimal import Decimal, getcontext
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

# basin_ls = ['Great_Basin', 'Colorado', 'Mississippi']
# basin = "California"
basin_abr = ["GB", "CO", "RG", "CA", "GC", "RE", "MI", "CB", "SA", "GL", "NA"]

# %%
# Plotting
c_nabd = ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fff66f', '#d1ef77', '#79ce6b', '#5bbb9d', '#3288bd', '#3952aa', '#4f438e']
c_grand = ['#740030', '#842532', '#9a422a', '#98683a', '#afa94c', '#86994c', '#416e39', '#326857', '#1b4c69', '#213063', '#2a244e']

fig, axs = plt.subplots(4, 1, sharex=True, sharey=False, figsize=(25, 30))
fig.subplots_adjust(hspace=0.05)
pad=5
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
    # print(basin)

    ## Total # of dams
    nabd_bar=axs[0].bar(basin,len(nabd), label=basin, color = c_nabd[count])
    nabd_bar2 = axs[1].bar(basin,len(nabd), label=basin, color = c_nabd[count])
    axs[0].bar(basin,len(grand), label=basin, color = c_grand[count])
    axs[1].bar(basin,len(grand), label=basin, color = c_grand[count])

    #Setting labels/axes size
    # ylabels0 = ['2.3x10$^4$', '2.4x10$^4$', '2.5x10$^4$']
    # ylabels0 = ['2.3e$^4$', '2.4e$^4$', '2.5e$^4$']
    # axs[0].set_yticklabels(ylabels0)
    axs[0].ticklabel_format(axis='y', style='sci', scilimits=(0,0))
    axs[0].tick_params(axis = 'both', which = 'major', labelsize = 70)
    axs[0].set_ylim(23000,25000)
    # ylabels1 = ['0','5x10$^3$','1x10$^4$']
    # ylabels1 = ['0','5e$^3$','1e$^4$']
    # axs[1].set_yticklabels(ylabels1)
    axs[1].ticklabel_format(axis='y', style='sci', scilimits=(0,0))
    axs[1].tick_params(axis = 'both', which = 'major', labelsize = 70)
    axs[1].set_ylim(0,10000)
    axs[1].set_xticklabels(basin_abr)
    fig.text(0.0001,0.76, "Total number of dams", ha="center", va="center", size = 72, rotation=90)
    # axs[1].annotate("Total number of dams", xy=(0, 0.5), xytext=(-axs[1].yaxis.labelpad - pad, 0),
    #             xycoords=axs[1].yaxis.label, textcoords='offset points',
    #             size=30, ha='right', va='center', rotation=90)
     # axs[0].set_ylabel("Total number of dams", size=72)

     #Split the axis
    axs[0].spines.bottom.set_visible(False)
    axs[1].spines.top.set_visible(False)
    axs[0].xaxis.tick_top()
    axs[0].tick_params(labeltop=False)  # don't put tick labels at the top
    axs[1].xaxis.tick_bottom()
    d = .5  # proportion of vertical to horizontal extent of the slanted line
    kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
              linestyle="none", color='k', mec='k', mew=1, clip_on=False)
    axs[0].plot([0, 1], [0, 0], transform=axs[0].transAxes, **kwargs)
    axs[1].plot([0, 1], [1, 1], transform=axs[1].transAxes, **kwargs)

    #Adding the percentage of small dams
    fraction = 1-(len(grand)/len(nabd))
    rfraction = Decimal(str(round(fraction, 3)))
    getcontext().prec = 3
    for rect in nabd_bar:
        # print(rect)
        # print(n)
        height = rect.get_height()
        if height < 20000:
            axs[1].text(rect.get_x() + rect.get_width()/1.6, 1.01*height,
                    str(rfraction*100)+"%", ha='center', va='bottom', rotation=0, size=38)
        else:
            axs[0].text(rect.get_x() + rect.get_width()/1.6, 1*height,
                    str(rfraction*100)+"%", ha='center', va='bottom', rotation=0, size=38)    


    ## Total storage
    nabd_sbar = axs[2].bar(basin,(sum(nabd.Norm_stor)*1233.48)/(10**6), color = c_nabd[count])
    axs[3].bar(basin,(sum(nabd.Norm_stor)*1233.48)/(10**6), color = c_nabd[count])
    axs[2].bar(basin,(sum(grand.Norm_stor)*1233.48)/(10**6), color = c_grand[count])
    axs[3].bar(basin,(sum(grand.Norm_stor)*1233.48)/(10**6), color = c_grand[count])
    
    # ylabels2 = ['1.8x10$^5$','1.9x10$^5$','2x10$^5$']
    # ylabels2 = ['1.8e$^5$','1.9e$^5$','2e$^5$']
    # axs[2].set_yticklabels(ylabels2)
    axs[2].ticklabel_format(axis='y', style='sci', scilimits=(0,0))
    axs[2].tick_params(axis = 'both', which = 'major', labelsize = 70)
    axs[2].set_ylim(180000,200000)
    # ylabels3 = ['0','5x10$^3$','1x10$^4$']
    # ylabels3 = ['0','5e$^3$','1e$^4$']
    # axs[3].set_yticklabels(ylabels3)
    axs[3].ticklabel_format(axis='y', style='sci', scilimits=(0,0))
    axs[3].tick_params(axis='both', which='major', labelsize=70)
    axs[3].set_ylim(0,130000)
    axs[3].set_xlabel("Basin", size=72)
    fig.text(0.0000001,0.3, "Total storage (MCM)", ha="center", va="center", size = 72, rotation=90)
    # axs[2].set_ylabel("Total storage (MCM)", size=62)

    #Adding the percentage of small dams
    nabd_stor= (sum(nabd.Norm_stor)*1233.48)/(10**6)
    grand_stor = (sum(grand.Norm_stor)*1233.48)/(10**6)
    fraction2 = round(1-(grand_stor/nabd_stor), 3)
    rfraction2 = Decimal(str(fraction2))
    if rfraction2 > 0.08:
        getcontext().prec = 3
    else:
        getcontext().prec = 2
    
    for rec in nabd_sbar:
        height = rec.get_height()
        if height < 180000:
            axs[3].text(rec.get_x() + rec.get_width()/1.6, 1.01*height,
                    str(rfraction2*100)+"%", ha='center', va='bottom', rotation=0, size=38)
        else:
            axs[2].text(rec.get_x() + rec.get_width()/1.6, 1*height,
                    str(rfraction2*100)+"%", ha='center', va='bottom', rotation=0, size=38)  

    # hide the spines between ax1 and ax2
    axs[2].spines.bottom.set_visible(False)
    axs[3].spines.top.set_visible(False)
    axs[2].xaxis.tick_top()
    axs[3].tick_params(labeltop=False)  # don't put tick labels at the top
    axs[2].xaxis.tick_bottom()

    d = .5  # proportion of vertical to horizontal extent of the slanted line
    kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
              linestyle="none", color='k', mec='k', mew=1, clip_on=False)
    axs[2].plot([0, 1], [0, 0], transform=axs[2].transAxes, **kwargs)
    axs[3].plot([0, 1], [1, 1], transform=axs[3].transAxes, **kwargs)

    plt.tight_layout()
    # plt.show()
    plt.savefig(gdrive+results_folder+"bar_plots/together.png")

 # %%
## Old plotting stuff
# fig1 = plt.figure()
# fig1, ax1 = plt.subplots(1, 1, figsize=(25, 15))
# fig2, ax2 = plt.subplots(1, 1, figsize=(15, 10))
# fig, axs = plt.subplots(2, sharex=True, sharey=False, figsize=(25, 30))

# for count, basin in enumerate(basin_ls):
   
#     #GRanD
#     grand = pd.read_csv(gdrive+data_folder+"grand_data/2010/"+basin+".csv", index_col='Hydroseq',
#                     usecols=['Hydroseq', 'DamCount','geometry', 'DamID',  'QC_MA', 'Norm_stor',
#                                 'HUC2', 'HUC4', 'HUC8', 'Year_compl'])
#     grand = grand[grand["DamID"]!=0]

#     #NABD
#     nabd = pd.read_csv(gdrive+data_folder+"nabd_data/2010/"+basin+".csv", index_col='Hydroseq',
#                     usecols=['Hydroseq', 'DamCount','geometry', 'DamID',  'QC_MA', 'Norm_stor',
#                                 'HUC2', 'HUC4', 'HUC8', 'Year_compl'])
#     nabd = nabd[nabd["DamID"]!=0]
#     # print(basin)

#     # ## Total # of dams
#     # ax1 = plt.subplot()
#     axs[0].bar(basin,len(nabd), label=basin, color = c_nabd[count])
#     # ax1.bar(basin,len(nabd), color = c_nabd[count])
#     axs[0].bar(basin,len(grand), label=basin, color = c_grand[count])
#     # ax1.bar(basin,len(grand), color = c_grand[count])
#     fraction = round(len(nabd)/len(grand), 1)
#     # print(fraction)
#     # for rect in nabd_bar:
#     #     height = rect.get_height()
#     #     axs.text(rect.get_x() + rect.get_width()/1.6, 1.01*height,
    # #             str(fraction)+"%", ha='center', va='bottom', rotation=0, size=34)
    
    # axs[0].set_ylabel("Total number of dams", size=42)
    # # # ax1.set_xlabel("Basin", size=30)
    # # axs.set_xticklabels(basin_abr)
    # axs[0].tick_params(axis = 'both', which = 'major', labelsize = 40)
    # #plt.legend()
    # plt.tight_layout(rect=[0.05, 0, 0.95, 1])
    # # plt.show()
    # # plt.savefig(gdrive+results_folder+"bar_plots/number_dams.png")

    # ## Total storage
    # # ax2 = plt.subplot(111)
    
    # axs[1].bar(basin,(sum(nabd.Norm_stor)*1233.48)/(10**6), color = c_nabd[count])
    # axs[1].bar(basin,(sum(grand.Norm_stor)*1233.48)/(10**6), color = c_grand[count])
    # # axs.set_ylabel("Total storage (MCM)", size=40)
    # fraction2 = round((sum(nabd.Norm_stor)*1233.48)/(10**6)/(sum(grand.Norm_stor)*1233.48)/(10**6), 1)
    # # for rect in nabd_bar2:
    # #     height = rect.get_height()
    # #     ax2.text(rect.get_x() + rect.get_width()/1.6, 1.01*height,
    # #             str(fraction2)+"%", ha='center', va='bottom', rotation=0, size=34)

    # axs[1].set_xlabel("Basins", size=42)
    # axs[1].set_xticklabels(basin_abr)
    # axs[1].tick_params(axis='both', which='major', labelsize=40)
    # # plt.title(basin)
    # # plt.legend(bbox_to_anchor=(1, 0.7, 0.5, 0), fontsize=14)
    # plt.tight_layout()
    # # plt.legend(bbox_to_anchor=[1, 0.75, 0.2, 0])
    # # plt.show()
    # plt.savefig(gdrive+results_folder+"bar_plots/dam_storage.png")
# %%
