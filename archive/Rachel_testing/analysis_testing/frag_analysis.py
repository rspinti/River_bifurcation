#%%
import geopandas as gp, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
from matplotlib.pyplot import cm
# sns.set()
sns.set_style("ticks", {"axes.facecolor": ".8"})

#%%
#Folders and stuff to pull the data from
gdrive = "/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo/" #where shapefiles/csv live
data_folder = 'final_analysis/processed_data/'
results_folder = 'final_analysis/analyzed_data/len_analysis/'

# basin_ls_old = ['California', 'Colorado', 'Columbia', 'Great_Basin', 'Great_Lakes', 'Gulf_Coast','Mississippi', 'North_Atlantic', 'Red', 'Rio_Grande','South_Atlantic']
# basin_ls = ['California', 'Colorado']

basin_ls = ['Great_Basin', 'Colorado', 'Rio_Grande', 'California', 'Gulf_Coast', 'Red', 'Mississippi', 'Columbia', 'South_Atlantic', 'Great_Lakes', 'North_Atlantic']
# basin_ls = ['Great_Basin', 'Colorado', 'Rio_Grande', 'California', 'Gulf_Coast', 'Red', 'Columbia', 'South_Atlantic', 'Great_Lakes', 'North_Atlantic']
#%%
#Function to get info by fragment length
def make_df(basin, years,  bin_ls, gdrive, results_folder):
    bins = np.clip(bin_ls, bin_ls[0], bin_ls[-1])
    labels = [str(x) for x in bins[1:]]

    nabd_basins = pd.DataFrame(0, index=years, columns=labels)
    nabd_diff = pd.DataFrame(0, index=years, columns=labels)
    small_dams = pd.DataFrame(0, index=years, columns=labels)

    grand_basins = pd.DataFrame(0, index=years, columns=labels)
    grand_diff = pd.DataFrame(0, index=years, columns=labels)
    big_dams = pd.DataFrame(0, index=years, columns=labels)

    for year in years:
        frags_nabd = pd.read_csv(gdrive+data_folder+"nabd_data/"+year+"/"+basin+"_fragments.csv")
        frag_nabd_bins = pd.cut(frags_nabd["LENGTHKM"], bins=bins, labels=labels)
        frag_nabd_bins.value_counts().sort_index()

        frags_grand = pd.read_csv(gdrive+data_folder+"grand_data/"+year+"/"+basin+"_fragments.csv")
        frag_grand_bins = pd.cut(frags_grand["LENGTHKM"], bins=bins, labels=labels)
        frag_grand_bins.value_counts().sort_index()

        for count, value in enumerate(nabd_basins.columns):
            nabd_basins.loc[year,value]=frag_nabd_bins.value_counts()[count]
            grand_basins.loc[year,value]=frag_grand_bins.value_counts()[count]

            percent_big = grand_basins.loc[year,value]/nabd_basins.loc[year,value]
            big_dams.loc[year,value] = percent_big
            small_dams.loc[year,value] = 1-percent_big

        for value in nabd_diff.columns:
            if year != "no_dams":
                nabd_diff.loc[year,value] = nabd_basins.loc[year,value]-nabd_basins.loc["no_dams",value]
                grand_diff.loc[year,value] = grand_basins.loc[year,value]-grand_basins.loc["no_dams",value]
            else:
                nabd_diff.loc[year,value]=0
                grand_diff.loc[year,value]=0
    # nabd_basins.to_csv(results_folder+basin+"_nabd_basins.csv")
    nabd_diff.to_csv(gdrive+results_folder+basin+"_nabd_frag_diff.csv")
    # grand_basins.to_csv(results_folder+basin+"_grand_basins.csv")
    grand_diff.to_csv(gdrive+results_folder+basin+"_grand_frag_diff.csv")
    small_dams.to_csv(gdrive+results_folder+basin+"_small_dams_fraction.csv")
    big_dams.to_csv(gdrive+results_folder+basin+"_big_dams_fraction.csv")
    return nabd_basins, nabd_diff, grand_basins, grand_diff, small_dams, big_dams

def make_tot_df(basin, years, gdrive, results_folder):
    # years = ["no_dams", "1920", "1950", "1980", "2010"]
    nabd_df = pd.DataFrame(0, index=years, columns=["total_frags"])
    grand_df = pd.DataFrame(0, index=years, columns=["total_frags"])
    small_dams = pd.DataFrame(0, index=years, columns=["total_frags"])

    for year in years:
        nabd_frags = pd.read_csv(gdrive+data_folder+"nabd_data/"+year+"/"+basin+"_fragments.csv")
        nabd_df.loc[year,"total_frags"]=len(nabd_frags["LENGTHKM"])
        grand_frags = pd.read_csv(gdrive+data_folder+"grand_data/"+year+"/"+basin+"_fragments.csv")
        grand_df.loc[year,"total_frags"]=len(grand_frags["LENGTHKM"])

        small_dams.loc[year, "total_frags"] = nabd_df.loc[year,"total_frags"]-grand_df.loc[year,"total_frags"]
        percent_big = grand_df["total_frags"]/nabd_df["total_frags"]
        small_dams["percent_small"] = 1-percent_big
    small_dams["percent_small"]["no_dams"] = 0

    nabd_df.to_csv(gdrive+results_folder+basin+"_nabd_totfrag.csv")
    grand_df.to_csv(gdrive+results_folder+basin+"_grand_totfrag.csv")
    small_dams.to_csv(gdrive+results_folder+basin+"_small_dams_totfraction.csv")
    return nabd_df, grand_df, small_dams
#%%
#Plotting
years = ["no_dams", "1920", "1950", "1980", "2010"]
bin_ls = [0, 10, 100, 1000, 10000]
lengths = [10, 100, 1000, 10000]
upper_limit=[18000, 4500, 800, 300]
# smaller_limit = [100, 250, 210, 150]
xlabels =["PD", "1920", "1950", "1980", "2012"]
basin_abr = ["GB", "CO", "RG", "CA", "GC", "RE", "MI", "CB", "SA", "GL", "NA"]
c = ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fff66f', '#d1ef77', '#79ce6b', '#5bbb9d', '#3288bd', '#3952aa', '#4f438e']

# ### Figure 1
# fig, axes = plt.subplots(4, 2, figsize=(20, 25))
# pad=5

# # for num, l in enumerate(lengths):
# for count, basin in enumerate(basin_ls):
#     df = make_df(basin, years, bin_ls, gdrive, results_folder)
#     for row, l in enumerate(lengths):
#         #NABD
#         axes[row,0].plot(df[1].index, df[1][str(l)], label = basin, color=c[count], marker='o', lw=4, ms=15)
#         axes[row,0].set_ylim(0, upper_limit[row])
#         # axes[row,0].set_ylim(0, smaller_limit[row])
#         # axes[row,0].set_title("Fragment length "+str(bin_ls[row])+" - "+str(l)+" km", weight="bold")
#         axes[0,0].set_title("Number of fragments\nfor all dams", weight="bold", size=32)
#         axes[row,0].set_xticklabels(xlabels)
#         # axes[row,0].set_ylabel("Number of fragments", weight="bold", size=30)
#         # axes[row,0].annotate("Fragment length\n "+str(bin_ls[row])+" - "+str(l)+" km", xy=(0, 0.5), xytext=(-axes[row,0].yaxis.labelpad - pad, 0),
#         #         xycoords=axes[row,0].yaxis.label, textcoords='offset points',
#         #         size=30, ha='right', va='center', rotation=90)
#         axes[row,0].annotate(str(bin_ls[row])+" - "+str(l)+" km", xy=(0, 0.5), xytext=(-axes[row,0].yaxis.labelpad - pad, 0),
#                 xycoords=axes[row,0].yaxis.label, textcoords='offset points',
#                 size=30, ha='right', va='center', rotation=90)
#         axes[row, 0].tick_params(axis = 'both', which = 'major', labelsize = 28, width=2.5, length=5)

#         #Small dams
#         axes[row,1].plot(df[4][1:].index, df[4][str(l)][1:], label = basin, color=c[count], marker= 'o', lw=4, ms=15)
#         axes[row,1].set_ylim(0, 1)
#         # axes[row,2].set_title("Fragment length "+str(bin_ls[row])+" - "+str(l)+" km", weight="bold")
#         axes[0,1].set_title("Fraction of fragments\nfrom small dams", weight="bold", size=32)
#         axes[row,1].set_xticklabels(xlabels[1:])
#         # axes[row,1].set_ylabel("Fraction of fragments", weight="bold", size=30)
#         # axes[row,2].set_xlabel("Time", weight="bold")
#         axes[row, 1].tick_params(axis = 'both', which = 'major', labelsize = 28, width=2.5, length=5)

# plt.tight_layout(rect=[0, 0, 0.94, 1])  
# # # plt.savefig(gdrive+results_folder+"frag_len4x4_smally.png", dpi=150)
# # plt.savefig(gdrive+results_folder+"frag_len4x2_bigy.png", dpi=150)
# plt.savefig(gdrive+results_folder+"frag_len4x2.png", dpi=150)

# ### Figure 2
# fig2, axes2 = plt.subplots(1, 2, figsize=(25, 10))
# fig2.text(0.5,0.95, "a.", ha="center", va="center", size = 34, weight="bold")
# fig2.text(0.985,0.95, "b.", ha="center", va="center", size = 34, weight="bold")

# for count, basin in enumerate(basin_ls):
#     tot_df = make_tot_df(basin, years, gdrive, results_folder)
#     axes2[0].plot(tot_df[0].index, tot_df[0]["total_frags"], label = basin_abr[count], color=c[count], marker='o', lw=4, ms=15)
#     axes2[1].plot(tot_df[2].index[1:], tot_df[2]["percent_small"][1:], label = basin_abr[count], color=c[count], marker='o', lw=4, ms=15)
#     axes2[1].set_ylim(0, 1)

#     axes2[0].set_ylabel("Total number of fragments", weight="bold", size=34)
#     axes2[1].set_ylabel("Fraction of fragments from small dams", weight="bold", size=34)
#     axes2[0].set_xticklabels(xlabels)
#     axes2[1].set_xticklabels(xlabels[1:])
#     # axes[0].set_title("All dams", weight="bold", size = 32)
#     # axes[1].set_title("Small dams", weight="bold", size=32)

# # plt.tight_layout(rect=[0.04, 0.04, 1, 1])    
# # plt.legend(bbox_to_anchor=(1, 0.9, 0.5, 0), fontsize=20)
# # plt.legend(fontsize=28)
# axes2[0].legend(loc="upper left", fontsize=32)
# axes2[0].tick_params(axis = 'both', which = 'major', labelsize = 32, width=2.5, length=5)
# axes2[1].tick_params(axis = 'both', which = 'major', labelsize = 32, width=2.5, length=5)

# plt.subplots_adjust(wspace = 0.15)
# plt.savefig(gdrive+results_folder+"tot_frags1x2.png", dpi=150)
# plt.show()
#%%
#3 panel total frags plot
### Figure 2
fig2, axes2 = plt.subplots(1, 3, figsize=(35, 15))
# fig2.text(0.5,0.95, "a.", ha="center", va="center", size = 34, weight="bold")
# fig2.text(0.985,0.95, "b.", ha="center", va="center", size = 34, weight="bold")

for count, basin in enumerate(basin_ls):
    tot_df = make_tot_df(basin, years, gdrive, results_folder)
    axes2[0].plot(tot_df[0].index, tot_df[0]["total_frags"], label = basin_abr[count], color=c[count], marker='o', lw=4, ms=15)
    axes2[1].plot(tot_df[0].index, tot_df[0]["total_frags"], label = basin_abr[count], color=c[count], marker='o', lw=4, ms=15)
    axes2[2].plot(tot_df[2].index[1:], tot_df[2]["percent_small"][1:], label = basin_abr[count], color=c[count], marker='o', lw=4, ms=15)
    axes2[1].set_ylim(0, 10000)
    axes2[2].set_ylim(0, 1)

    axes2[0].set_ylabel("Total number of fragments", size=34)
    axes2[1].set_ylabel("Total number of fragments", size=34)
    axes2[2].set_ylabel("Fraction of fragments from small dams", size=34)
    axes2[0].set_xticklabels(xlabels)
    axes2[1].set_xticklabels(xlabels)
    axes2[2].set_xticklabels(xlabels[1:])
    # axes[0].set_title("All dams", weight="bold", size = 32)
    # axes[1].set_title("Small dams", weight="bold", size=32)

plt.tight_layout(rect=[0.04, 0.04, 1, 1])    
# plt.legend(bbox_to_anchor=(1, 0.9, 0.5, 0), fontsize=20)
# plt.legend(fontsize=28)
axes2[0].legend(loc="upper left", fontsize=32)
axes2[0].tick_params(axis = 'both', which = 'major', labelsize = 32, width=2.5, length=5)
axes2[1].tick_params(axis = 'both', which = 'major', labelsize = 32, width=2.5, length=5)
axes2[2].tick_params(axis = 'both', which = 'major', labelsize = 32, width=2.5, length=5)

plt.subplots_adjust(wspace = 0.15)
plt.savefig(gdrive+results_folder+"tot_frags1x3.png", dpi=150)
plt.show()


#Split axis
### Figure 2
# fig2 = plt.figure(figsize=(20,15))
# ax1= fig2.add_subplot(2,2,1)
# ax2= fig2.add_subplot(2,2,3)
# ax3= fig2.add_subplot(1,2,2)

# for count, basin in enumerate(basin_ls):
#     tot_df = make_tot_df(basin, years, gdrive, results_folder)
#     ax1.plot(tot_df[0].index, tot_df[0]["total_frags"], label = basin_abr[count], color=c[count], marker='o')
#     ax2.plot(tot_df[0].index, tot_df[0]["total_frags"], label = basin_abr[count], color=c[count], marker='o')
#     ax3.plot(tot_df[2].index[1:], tot_df[2]["percent_small"][1:], label = basin_abr[count], color=c[count], marker='o')
    
#     ax1.set_ylabel("Total number of fragments", size=34)
#     ax1.set_ylim(22000, 26000)
#     ax2.set_ylim(0, 12000)
#     ax2.set_xticklabels(xlabels)
#     ax3.set_ylim(0, 1)
#     ax3.set_xticklabels(xlabels[1:])
#     ax3.set_ylabel("Fraction of fragments from small dams", size=34)

# ax1.tick_params(axis = 'both', which = 'major', labelsize = 32, width=2.5, length=5)  
# ax2.tick_params(axis = 'both', which = 'major', labelsize = 32, width=2.5, length=5)
# ax3.tick_params(axis = 'both', which = 'major', labelsize = 32, width=2.5, length=5)

# #Split the axis
# ax1.spines.bottom.set_visible(False)
# ax2.spines.top.set_visible(False)
# ax1.xaxis.tick_top()
# ax1.tick_params(labeltop=False)  # don't put tick labels at the top
# ax2.xaxis.tick_bottom()
# d = .3  # proportion of vertical to horizontal extent of the slanted line
# kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
#             linestyle="none", color='k', mec='k', mew=1, clip_on=False)
# ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
# ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)
# ax1.legend(loc="upper left", fontsize=32)

# plt.subplots_adjust(wspace = 0.15)
# # plt.savefig(gdrive+results_folder+"tot_frags_split.png", dpi=150)
plt.show()
#%%
# Old plotting
        # plt.plot(df[1].index, df[1][str(l)], label = basin, color=c[count], marker='o')
    #     plt.plot(df[1].index, df[1][str(l)], label = basin, color=c[count], marker='o', linestyle="--")
    #     plt.xlabel("Time")
    #     plt.xticks(np.arange(0,len(labels)),labels=labels)
    #     plt.ylabel("Change in number of fragments")
    #     # plt.yscale("symlog")
    #     # plt.ylim(0,upper_limit[num])
    #     # plt.yticks([0, 1, 10, 100, 1000, 10000, 100000])
    #     plt.title("Change in number of fragments "+str(l)+" km long")
    # plt.tight_layout(rect=[0, 0, 0.72, 1])    
    # plt.legend(bbox_to_anchor=(1.05, 1))
    

    # # plt.savefig(gdrive+results_folder+"/len_analysis/nabd/len_"+str(l)+".png", dpi=150)
    # # plt.savefig(gdrive+results_folder2+"len_analysis/grand/len_"+str(l)+".png", dpi=150)
    # plt.show()

# for count, basin in enumerate(basin_ls):
#     tot_df=make_tot_df(basin)
    
#     plt.plot(tot_df.index, tot_df["total_frags"], label = basin, color=c[count], marker='o')
#     # plt.plot(tot_df.index, tot_df["total_frags"], label = basin, color=c[count], marker='o', linestyle="--")
#     plt.xlabel("Time")
#     plt.xticks(np.arange(0,len(labels)),labels=labels)
#     plt.ylabel("Change in number of fragments")
#     # plt.yscale("symlog")
#     plt.ylim(0,30000)
#     # plt.yticks([0, 1, 10, 100, 1000, 10000, 100000])
#     plt.title("Total change in number of fragments")
# plt.tight_layout(rect=[0, 0, 0.72, 1])
# plt.legend(bbox_to_anchor=(1.05, 1))


# plt.savefig(gdrive+results_folder+"/len_analysis/nabd/total_frag.png", dpi=150)
# plt.savefig(gdrive+results_folder2+"/len_analysis/grand/total_frag2.png", dpi=150)
# plt.show()

# %%

