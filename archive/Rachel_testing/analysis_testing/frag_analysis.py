#%%
import geopandas as gp, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
from matplotlib.pyplot import cm
sns.set()

#%%
#Folders and stuff to pull the data from
gdrive = "/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo/" #where shapefiles/csv live

## NABD
# data_folder = 'HPC_runs_fixed/processed_data/'
# results_folder = 'HPC_runs_fixed/analyzed_data/'
### GRanD
data_folder = 'HPC_runs_fixed/processed_data/grand_dams/'
grand_data_folder = 'HPC_runs_fixed/processed_data/grand_dams/'
results_folder = 'HPC_runs_fixed/analyzed_data/grand_dams/'
results_folder2 = 'HPC_runs_fixed/analyzed_data/'

# year = ["no_dams", "1920", "1950", "1980", "2010"]
# year = ["grand_dams"]
# basin_ls = ['California', 'Colorado', 'Columbia', 'Great_Basin', 'Great_Lakes', 'Gulf_Coast','Mississippi', 'North_Atlantic', 'Red', 'Rio_Grande','South_Atlantic']
# basin_ls = ['California', "Colorado"]

basin_ls = ['Columbia', 'California', 'Great_Basin', 'Colorado',  'Rio_Grande', 'Gulf_Coast', 'Mississippi', 'Red',  'Great_Lakes', 'North_Atlantic', 'South_Atlantic']
#%%
#Function to get info by fragment length
def make_df(basin):
    years = ["no_dams", "1920", "1950", "1980", "2010"]
    bins = [0, 1, 10, 100, 1000, 10000, 100000, 1000000]
    labels = [str(x) for x in bins[1:]]
    basin_df = pd.DataFrame(0, index=years, columns=labels)
    diff_df = pd.DataFrame(0, index=years, columns=labels)

    for year in years:
        frags = pd.read_csv(gdrive+data_folder+year+"/"+basin+"_fragments.csv")
        # frags_grand = pd.read_csv(gdrive+grand_data_folder+year+"/"+basin+"_fragments.csv")
        frag_bins = pd.cut(frags["LENGTHKM"], bins=bins, labels=labels)
        frag_bins.value_counts().sort_index()

        for count, value in enumerate(basin_df.columns):
            basin_df.loc[year,value]=frag_bins.value_counts()[count]
        for value in diff_df.columns:
            if year != "no_dams":
                r = basin_df.loc[year,value]-basin_df.loc["no_dams",value]
                diff_df.loc[year,value]=r 
            else:
                diff_df.loc[year,value]=0
    return basin_df, diff_df

def make_tot_df(basin):
    years = ["no_dams", "1920", "1950", "1980", "2010"]
    bins = [0, 1, 10, 100, 1000, 10000, 100000, 1000000]
    # labels = [str(x) for x in bins[1:]]
    basin_df = pd.DataFrame(0, index=years, columns=["total_frags"])

    for year in years:
        frags = pd.read_csv(gdrive+data_folder+year+"/"+basin+"_fragments.csv")
        basin_df.loc[year,"total_frags"]=len(frags["LENGTHKM"])
    
    return basin_df
#%%
#Plotting
lengths = [1, 10, 100, 1000, 10000, 100000, 1000000]
upper_limit=[2500, 18000, 4500, 800, 300, 30, 3]
labels =["Pre-development", "1920", "1950", "1980", "2010"]
# lengths = [1]
c = ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fee08b', '#ffffa3', '#c7f58c', '#abdda4', '#66c2a5', '#3288bd', '#5e4fa2']
for num, l in enumerate(lengths):
    # color=iter(cm.gist_rainbow(np.linspace(0,0.8,len(basin_ls))))
    for count, basin in enumerate(basin_ls):
        df = make_df(basin)
        # c=next(color)
        
        # plt.plot(df[1].index, df[1][str(l)], label = basin, color=c[count], marker='o')
        plt.plot(df[1].index, df[1][str(l)], label = basin, color=c[count], marker='o', linestyle="--")
        plt.xlabel("Time")
        plt.xticks(np.arange(0,len(labels)),labels=labels)
        plt.ylabel("Change in number of fragments")
        # plt.yscale("symlog")
        plt.ylim(0,upper_limit[num])
        # plt.yticks([0, 1, 10, 100, 1000, 10000, 100000])
        plt.title("Change in number of fragments "+str(l)+" km long")
    plt.tight_layout(rect=[0, 0, 0.72, 1])    
    plt.legend(bbox_to_anchor=(1.05, 1))
    

    # plt.savefig(gdrive+results_folder+"/len_analysis/nabd/len_"+str(l)+".png", dpi=150)
    # plt.savefig(gdrive+results_folder2+"len_analysis/grand/len_"+str(l)+".png", dpi=150)
    plt.show()

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
