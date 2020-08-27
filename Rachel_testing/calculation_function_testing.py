#Testing how functions and classes work
# %%
import pandas as pd
import calculate as calc

# import sys
# sys.path.insert(0, '/Users/rachelspinti/Documents/River_bifurcation')

#small basin

#HUC4
fragments = pd.read_csv('fragments_extracted1019.csv')
segments = pd.read_csv('segments_extracted1019.csv')
#HUC2
# fragments = pd.read_csv('/Users/rachelspinti/Documents/River_bifurcation/fragments_Columbia.csv')
# segments = pd.read_csv('/Users/rachelspinti/Documents/River_bifurcation/segments_Columbia.csv')

keep_cols = ['Frag', 'NDamUp']
dams_up = fragments[keep_cols]
# print(dams_up)
segments_update = segments.merge(dams_up, how= 'left', on='Frag') # Merge 
# Calculate the total river volume
tot_vol = fragments['QC_MA'].sum()
# print(tot_vol)
# %%
rfi = calc.calc_rfi(fragments, tot_vol)
# print(fragments.columns)
# print(segments.columns)
# print(len(fragments))
# print(len(segments))

rri = calc.calc_rri(segments_update, tot_vol)

# %%
