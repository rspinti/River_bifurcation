
# %%
import pandas as pd, geopandas as gp
from pathlib import Path
gdrive = Path("/Volumes/GoogleDrive/My Drive/Condon_Research_Group/Research_Projects/Rachel/Research/Data/bifurcation_data_repo") 

# NABD
nabd_dams = gp.read_file(gdrive/"nabd/nabd_fish_barriers_2012.shp")  #read in NABD from Drive
nabd_dams = pd.DataFrame(nabd_dams)

# CSV with correct NIDID
wrong_id = pd.read_csv('large_dams_wrongID.csv', index_col = 0, usecols= [1, 2, 3, 4,5,6,7,8,9,10,11,12,13,14,15])
wrong_id = wrong_id[wrong_id['NABD_NIDID'].notna()]

# Update NIDID with csv (broken)
for j in range(len(nabd_dams.NIDID)):
    for i in wrong_id.NABD_NIDID:
        if i in nabd_dams.NIDID.values:
            for k in range(len(wrong_id.NIDID)):
                nabd_dams.at[j,'NIDID'] = wrong_id.loc[k,'NIDID']


# %%
