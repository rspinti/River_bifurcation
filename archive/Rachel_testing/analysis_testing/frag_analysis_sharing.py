#%%
import geopandas as gp, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
from matplotlib.pyplot import cm
sns.set_style("ticks", {"axes.facecolor": ".8"})

#%%
#Folders and stuff to pull the data from
gdrive = "/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo/" #where shapefiles/csv live
data_folder = 'final_analysis/processed_data/'
results_folder = 'final_analysis/analyzed_data/len_analysis/'
huc2 = gp.read_file(gdrive+"hucs/huc2_clipped.shp")

basin_ls = ['Great_Basin', 'Colorado', 'Rio_Grande', 'California', 'Gulf_Coast', 'Red', 'Mississippi', 'Columbia', 'South_Atlantic', 'Great_Lakes', 'North_Atlantic']
#%%
#Function to get info by fragment length
def make_df(basin, years,  bin_ls, gdrive, results_folder):
    bins = np.clip(bin_ls, bin_ls[0], bin_ls[-1])
    labels = [str(x) for x in bins[1:]]

    nabd_basins = pd.DataFrame(0, index=years, columns=labels)
    nabd_diff = pd.DataFrame(0, index=years, columns=labels)
    big_dams = pd.DataFrame(0, index=years, columns=labels)
    small_dams = pd.DataFrame(0, index=years, columns=labels)

    big_basins = pd.DataFrame(0, index=years, columns=labels)
    big_diff = pd.DataFrame(0, index=years, columns=labels)

    # small_basins = pd.DataFrame(0, index=years, columns=labels)
    # small_diff = pd.DataFrame(0, index=years, columns=labels)

    for year in years:
        frags_nabd = pd.read_csv(gdrive+data_folder+"nabd_data/"+year+"/"+basin+"_fragments.csv")
        frag_nabd_bins = pd.cut(frags_nabd["LENGTHKM"], bins=bins, labels=labels)
        frag_nabd_bins.value_counts().sort_index()

        frags_big = pd.read_csv(gdrive+data_folder+"grand_data/"+year+"/"+basin+"_fragments.csv")
        frag_big_bins = pd.cut(frags_big["LENGTHKM"], bins=bins, labels=labels)
        frag_big_bins.value_counts().sort_index()

        # frags_small = pd.read_csv(gdrive+data_folder+"small_dams/"+year+"/"+basin+"_fragments.csv")
        # frag_small_bins = pd.cut(frags_small["LENGTHKM"], bins=bins, labels=labels)
        # frag_small_bins.value_counts().sort_index()

        for count, value in enumerate(nabd_basins.columns):
            nabd_basins.loc[year,value]=frag_nabd_bins.value_counts()[count]
            big_basins.loc[year,value]=frag_big_bins.value_counts()[count]
            # small_basins.loc[year,value]=frag_small_bins.value_counts()[count]

            percent_big = big_basins.loc[year,value]/nabd_basins.loc[year,value]
            big_dams.loc[year,value] = percent_big
            small_dams.loc[year,value] = 1- percent_big

            # percent_small = small_basins.loc[year,value]/nabd_basins.loc[year,value]
            # small_dams.loc[year,value] = percent_small

        for value in nabd_diff.columns:
            if year != "no_dams":
                nabd_diff.loc[year,value] = nabd_basins.loc[year,value]-nabd_basins.loc["no_dams",value]
                big_diff.loc[year,value] = big_basins.loc[year,value]-big_basins.loc["no_dams",value]
                # small_diff.loc[year,value] = small_basins.loc[year,value]-small_basins.loc["no_dams",value]
            else:
                nabd_diff.loc[year,value]=0
                big_diff.loc[year,value]=0
                # small_diff.loc[year,value]=0
    # nabd_basins.to_csv(results_folder+basin+"_nabd_basins.csv")
    nabd_diff.to_csv(gdrive+results_folder+basin+"_nabd_frag_diff.csv")
    # big_basins.to_csv(results_folder+basin+"_big_basins.csv")
    # big_diff.to_csv(gdrive+results_folder+basin+"_big_frag_diff.csv")
    # big_dams.to_csv(gdrive+results_folder+basin+"_big_dams_fraction.csv")
# 
    # small_basins.to_csv(results_folder+basin+"_small_basins.csv")
    # small_diff.to_csv(gdrive+results_folder+basin+"_small_frag_diff.csv")
    # small_dams.to_csv(gdrive+results_folder+basin+"_small_dams_fraction.csv")
    
    return nabd_basins, nabd_diff, big_basins, big_diff, small_dams, big_dams
    # return nabd_basins, nabd_diff, small_basins, small_diff, small_dams

def make_tot_df(basin, years, gdrive, results_folder):
    # years = ["no_dams", "1920", "1950", "1980", "2010"]
    nabd_df = pd.DataFrame(0, index=years, columns=["total_frags"])
    big_df = pd.DataFrame(0, index=years, columns=["total_frags"])
    big_dams = pd.DataFrame(0, index=years, columns=["total_frags"])
    small_df = pd.DataFrame(0, index=years, columns=["total_frags"])
    small_dams = pd.DataFrame(0, index=years, columns=["total_frags"])

    for year in years:
        nabd_frags = pd.read_csv(gdrive+data_folder+"nabd_data/"+year+"/"+basin+"_fragments.csv")
        nabd_df.loc[year,"total_frags"]=len(nabd_frags["LENGTHKM"])
        big_frags = pd.read_csv(gdrive+data_folder+"grand_data/"+year+"/"+basin+"_fragments.csv")
        big_df.loc[year,"total_frags"]=len(big_frags["LENGTHKM"])
        # small_frags = pd.read_csv(gdrive+data_folder+"small_dams/"+year+"/"+basin+"_fragments.csv")
        # small_df.loc[year,"total_frags"]=len(small_frags["LENGTHKM"])

        big_dams.loc[year, "total_frags"] = nabd_df.loc[year,"total_frags"]-big_df.loc[year,"total_frags"]
        # small_dams.loc[year, "total_frags"] = nabd_df.loc[year,"total_frags"]-small_df.loc[year,"total_frags"]
        percent_big = big_df["total_frags"]/nabd_df["total_frags"]
        percent_small = 1 - percent_big
        # percent_small = small_df["total_frags"]/nabd_df["total_frags"]
        small_dams["percent_small"] = percent_small
    small_dams["percent_small"]["no_dams"] = 0

    nabd_df.to_csv(gdrive+results_folder+basin+"_nabd_totfrag.csv")
    small_df.to_csv(gdrive+results_folder+basin+"_small_totfrag.csv")
    small_dams.to_csv(gdrive+results_folder+basin+"_small_dams_totfraction.csv")

    # return nabd_df, big_df, big_dams
    return nabd_df, small_df, small_dams
#%%
#Plotting
years = ["no_dams", "1920", "1950", "1980", "2010"]
bin_ls = [0, 10, 100, 1000, 10000]
lengths = [10, 100, 1000, 10000]
upper_limit=[20000, 4500, 800, 300]
smaller_limit = [2000, 700, 300, 100]
xlabels =["PD", "1920", "1950", "1980", "2012"]
basin_abr = ["GB", "CO", "RG", "CA", "GC", "RE", "MI", "CB", "SA", "GL", "NA"]
c = ['#9e0142', '#d53e4f', '#f46d43', '#fdae61', '#fff66f', '#d1ef77', '#79ce6b', '#5bbb9d', '#3288bd', '#3952aa', '#4f438e']

### Figure 1
fig, axes = plt.subplots(4, 2, figsize=(20, 25))
pad=5
for count, basin in enumerate(basin_ls):
    df = make_df(basin, years, bin_ls, gdrive, results_folder)
    for row, l in enumerate(lengths):
        basin = basin.replace("_", " ")
        select = huc2[huc2['basin']==basin]
        area = sum(select.AreaSqKm)

        #NABD
        axes[row,0].plot(df[1].index, df[1][str(l)]/area, label = basin, color=c[count], marker='o', lw=4, ms=15)
        axes[0,0].set_title("Number of fragments\nfor all dams", weight="bold", size=32)
        axes[row,0].set_xticklabels(xlabels)
        axes[row,0].annotate(str(bin_ls[row])+" - "+str(l)+" km", xy=(0, 0.5), xytext=(-axes[row,0].yaxis.labelpad - pad, 0),
                xycoords=axes[row,0].yaxis.label, textcoords='offset points',
                size=30, weight='bold', ha='right', va='center', rotation=90)
        axes[row, 0].tick_params(axis = 'both', which = 'major', labelsize = 28, width=2.5, length=5)
        axes[row, 0].ticklabel_format(axis='y', style='sci', scilimits=(0,0))
        axes[row, 0].yaxis.get_offset_text().set_fontsize(28)

        #Small dams
        axes[row,1].plot(df[4][1:].index, df[4][str(l)][1:], label = basin, color=c[count], marker= 'o', lw=4, ms=15)
        # axes[row,1].set_ylim(0, 1)
        axes[0,1].set_title("Fraction of fragments\nfrom small dams", weight="bold", size=32)
        axes[row,1].set_xticklabels(xlabels[1:])
        axes[row, 1].tick_params(axis = 'both', which = 'major', labelsize = 28, width=2.5, length=5)

plt.tight_layout(rect=[0, 0, 0.94, 1])  
# plt.savefig(gdrive+results_folder+"frag_len_dens2.png", dpi=150)

### Figure 2
fig2, axes2 = plt.subplots(1, 2, figsize=(25, 10))
# fig2.patch.set_facecolor('blue')
fig2.patch.set_alpha(0)

for count, basin in enumerate(basin_ls):
    tot_df = make_tot_df(basin, years, gdrive, results_folder)
    basin = basin.replace("_", " ")
    select = huc2[huc2['basin']==basin]
    area = sum(select.AreaSqKm)
    axes2[0].plot(tot_df[0].index, tot_df[0]["total_frags"]/area, label = basin_abr[count], color=c[count], marker='o', lw=4, ms=15)
    axes2[1].plot(tot_df[2].index[1:], tot_df[2]["percent_small"][1:], label = basin_abr[count], color=c[count], marker='o', lw=4, ms=15)
    # axes2[1].set_ylim(0, 1)

    axes2[0].set_ylabel("Total fragment density per km$^2$", weight="bold", size=34)
    axes2[1].set_ylabel("Relative change from small dams", weight="bold", size=34)
    axes2[0].set_xticklabels(xlabels)
    axes2[1].set_xticklabels(xlabels[1:])
    axes2[0].ticklabel_format(axis='y', style='sci', scilimits=(0,0))
    axes2[0].yaxis.get_offset_text().set_fontsize(32)
    
# plt.tight_layout()  
plt.legend(bbox_to_anchor=(1, 0.98, 0.1, 0), fontsize=32)
axes2[0].tick_params(axis = 'both', which = 'major', labelsize = 32, width=2.5, length=5)
axes2[1].tick_params(axis = 'both', which = 'major', labelsize = 32, width=2.5, length=5)

# plt.savefig(gdrive+results_folder+"tot_frags1x2_dens2.png", dpi=150)
plt.savefig(gdrive+results_folder+"tot_frags1x2_dens.png", dpi=150)
# %%
### Figure 2
fig2, ax2 = plt.subplots(1, 1, figsize=(15, 10))
fig3, ax3 = plt.subplots(1, 1, figsize=(30, 25))
fig2.patch.set_alpha(0)
fig3.patch.set_alpha(0)

for count, basin in enumerate(basin_ls):
    tot_df = make_tot_df(basin, years, gdrive, results_folder)
    basin = basin.replace("_", " ")
    select = huc2[huc2['basin']==basin]
    area = sum(select.AreaSqKm)
    ax2.plot(tot_df[0].index, tot_df[0]["total_frags"]/area, label = basin_abr[count], color=c[count], marker='o', lw=4, ms=15)
    ax3.plot(tot_df[2].index[1:], tot_df[2]["percent_small"][1:], label = basin_abr[count], color=c[count], marker='o', lw=8, ms=25)
    ax3.set_ylim(0, 1)

    ax2.set_ylabel("Total fragment density per km$^2$", weight="bold", size=34)
    ax3.set_ylabel("Relative change in fragments from small dams", weight="bold", size=60)
    ax2.set_xticklabels(xlabels)
    ax3.set_xticklabels(xlabels[1:])
    ax2.ticklabel_format(axis='y', style='sci', scilimits=(0,0))
    ax2.yaxis.get_offset_text().set_fontsize(32)
    

ax2.legend(bbox_to_anchor=(1, 0.92, 0.1, 0), fontsize=32)
ax2.tick_params(axis = 'both', which = 'major', labelsize = 32, width=2.5, length=5)
ax3.tick_params(axis = 'both', which = 'major', labelsize = 58, width=2.5, length=5)

fig2.tight_layout()  
fig2.savefig(gdrive+results_folder+"tot_frags_dens", dpi=150)
fig3.savefig(gdrive+results_folder+"tot_frags_small.png", dpi=150)
# %%
