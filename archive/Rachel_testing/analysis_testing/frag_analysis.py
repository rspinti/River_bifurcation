#%%
import geopandas as gp, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
from matplotlib.pyplot import cm
sns.set()

#%%
#Folders and stuff to pull the data from
gdrive = "/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo/" #where shapefiles/csv live

## NABD
data_folder = 'HPC_runs_fixed/processed_data/'
results_folder = 'HPC_runs_fixed/analyzed_data/'

### GRanD
# data_folder = 'HPC_runs_fixed/processed_data/grand_dams/'
# grand_data_folder = 'HPC_runs_fixed/processed_data/grand_dams/'
# results_folder = 'HPC_runs_fixed/analyzed_data/grand_dams/'
# results_folder2 = 'HPC_runs_fixed/analyzed_data/'

# year = ["no_dams", "1920", "1950", "1980", "2010"]
# year = ["grand_dams"]
# basin_ls_old = ['California', 'Colorado', 'Columbia', 'Great_Basin', 'Great_Lakes', 'Gulf_Coast','Mississippi', 'North_Atlantic', 'Red', 'Rio_Grande','South_Atlantic']
# basin_ls = ['California', 'Colorado']

basin_ls = ['Great_Basin', 'Colorado', 'Rio_Grande', 'California', 'Gulf_Coast', 'Red', 'Mississippi', 'Columbia', 'South_Atlantic', 'Great_Lakes', 'North_Atlantic']
#%%
#Function to get info by fragment length
def make_df(basin, years,  bin_ls):
    bins = np.clip(bin_ls, bin_ls[0], bin_ls[-1])
    labels = [str(x) for x in bins[1:]]

    nabd_basins = pd.DataFrame(0, index=years, columns=labels)
    nabd_diff = pd.DataFrame(0, index=years, columns=labels)
    small_dams = pd.DataFrame(0, index=years, columns=labels)

    grand_basins = pd.DataFrame(0, index=years, columns=labels)
    grand_diff = pd.DataFrame(0, index=years, columns=labels)
    big_dams = pd.DataFrame(0, index=years, columns=labels)

    for year in years:
        frags_nabd = pd.read_csv(gdrive+data_folder+year+"/"+basin+"_fragments.csv")
        frag_nabd_bins = pd.cut(frags_nabd["LENGTHKM"], bins=bins, labels=labels)
        frag_nabd_bins.value_counts().sort_index()

        frags_grand = pd.read_csv(gdrive+data_folder+"grand_dams/"+year+"/"+basin+"_fragments.csv")
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
    return nabd_basins, nabd_diff, grand_basins, grand_diff, small_dams, big_dams

# def make_tot_df(basin):
#     years = ["no_dams", "1920", "1950", "1980", "2010"]
#     bins = [0, 1, 10, 100, 1000, 10000, 100000, 1000000]
#     # labels = [str(x) for x in bins[1:]]
#     basin_df = pd.DataFrame(0, index=years, columns=["total_frags"])

#     for year in years:
#         frags = pd.read_csv(gdrive+data_folder+year+"/"+basin+"_fragments.csv")
#         basin_df.loc[year,"total_frags"]=len(frags["LENGTHKM"])
    
#     return basin_df
#%%
#Plotting
years = ["no_dams", "1920", "1950", "1980", "2010"]
bin_ls = [0, 10, 100, 1000, 10000]
lengths = [10, 100, 1000, 10000]
# upper_limit=[2500, 18000, 4500, 800, 300, 30, 3]
xlabels =["Pre-development", "1920", "1950", "1980", "2010"]
# lengths = [1]
# c_old = ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fee08b', '#ffffa3', '#c7f58c', '#abdda4', '#66c2a5', '#3288bd', '#5e4fa2']
c = ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#ffffa3', '#c7f58c', '#abdda4', '#66c2a5', '#3288bd', '#3952aa', 'purple']   #'#4f438e'

fig, axes = plt.subplots(4, 4, figsize=(20, 25))
# for num, l in enumerate(lengths):
for count, basin in enumerate(basin_ls):
    df = make_df(basin, years, bin_ls)
    for row, l in enumerate(lengths):
        #NABD
        axes[row,0].plot(df[1].index, df[1][str(l)], label = basin, color=c[count], marker='o')
        axes[row,0].set_title(str(l)+" km")
        plt.xticks(np.arange(0,len(xlabels)),labels=xlabels)
        #GRanD
        axes[row,1].plot(df[3].index, df[3][str(l)], label = basin, color=c[count], marker='o')
        axes[row,1].set_title(str(l)+"km")
        # axes[row,1].set_xticks(np.arange(0,len(xlabels)),labels=xlabels)
        #Small dams
        axes[row,2].plot(df[4].index, df[4][str(l)], label = basin, color=c[count], marker='o')
        axes[row,2].set_title(str(l)+" km")
        # axes[row,2].set_xticks(np.arange(0,len(xlabels)),labels=xlabels)
        #Large dams
        axes[row,3].plot(df[5].index, df[5][str(l)], label = basin, color=c[count], marker='o')
        axes[row,3].set_title(str(l)+" km")
        # axes[row,3].set_xticks(np.arange(0,len(xlabels)),labels=xlabels)


    # #NABD
    # axes[0,0].plot(df[1].index, df[1][str(lengths[0])], label = basin, color=c[count], marker='o')
    # axes[1,0].plot(df[1].index, df[1][str(lengths[1])], label = basin, color=c[count], marker='o')
    # axes[2,0].plot(df[1].index, df[1][str(lengths[2])], label = basin, color=c[count], marker='o')
    # axes[3,0].plot(df[1].index, df[1][str(lengths[3])], label = basin, color=c[count], marker='o')
    # axes[0,0].set_title("All dams")
    # axes[1,0].set_title("100km")
    # axes[3,0].set_xlabel("Time")

    # #GRanD
    # axes[0,1].plot(df[3].index, df[3][str(lengths[0])], label = basin, color=c[count], marker='o')
    # axes[1,1].plot(df[3].index, df[3][str(lengths[1])], label = basin, color=c[count], marker='o')
    # axes[2,1].plot(df[3].index, df[3][str(lengths[2])], label = basin, color=c[count], marker='o')
    # axes[3,1].plot(df[3].index, df[3][str(lengths[3])], label = basin, color=c[count], marker='o')
    # axes[0,1].set_title("Big dams")

    # #Small dams
    # axes[0,2].plot(df[4].index, df[4][str(lengths[0])], label = basin, color=c[count], marker='o')
    # axes[1,2].plot(df[4].index, df[4][str(lengths[1])], label = basin, color=c[count], marker='o')
    # axes[2,2].plot(df[4].index, df[4][str(lengths[2])], label = basin, color=c[count], marker='o')
    # axes[3,2].plot(df[4].index, df[4][str(lengths[3])], label = basin, color=c[count], marker='o')
    # axes[0,2].set_title("Small dams percent")

    # #Large dams
    # axes[0,3].plot(df[5].index, df[5][str(lengths[0])], label = basin, color=c[count], marker='o')
    # axes[1,3].plot(df[5].index, df[5][str(lengths[1])], label = basin, color=c[count], marker='o')
    # axes[2,3].plot(df[5].index, df[5][str(lengths[2])], label = basin, color=c[count], marker='o')
    # axes[3,3].plot(df[5].index, df[5][str(lengths[3])], label = basin, color=c[count], marker='o')
    # axes[0,3].set_title("Big dams percent")
    
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

# %%
