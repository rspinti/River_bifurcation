import geopandas as gp, pandas as pd
def agg_HUC2(combo_segGeo, folder):
    huc2 = gp.read_file("hucs_to_test/HUC2_CONUS.shp")
    indices_by_huc2 = combo_segGeo.pivot_table(values = ['avg_LengthUp'], index='HUC2', aggfunc=np.mean)
        
    huc2 = huc2.join(indices_by_huc2, left_on = 'HUC2_no', right_on = 'HUC2', how = 'left', lsuffix='_left', rsuffix='_right')
    huc2.to_csv(folder+'huc2_indices.csv')
    print('Finished writing huc2 indices to csv')

def agg_HUC4(combo_segGeo, folder):
    huc4 = gp.read_file("hucs_to_test/HUC4_CONUS.shp") 
    indices_by_huc4 = combo_segGeo.pivot_table(values = ['avg_LengthUp'], index='HUC4', aggfunc=np.mean)
        
    huc4 = huc4.join(indices_by_huc4, left_on = 'HUC4_no', right_on = 'HUC4', how = 'left', lsuffix='_left', rsuffix='_right')
    huc4.to_csv(folder+'huc4_indices.csv')
    print('Finished writing huc4 indices to csv')

def agg_HUC9(combo_segGeo, folder):
    huc8 = gp.read_file("hucs_to_test/HUC8_CONUS.shp") 
    indices_by_huc8 = combo_segGeo.pivot_table(values = ['avg_LengthUp'], index='HUC8', aggfunc=np.mean)
        
    huc8 = huc8.join(indices_by_huc8, left_on = 'HUC8_no', right_on = 'HUC8', how = 'left', lsuffix='_left', rsuffix='_right')
    huc8.to_csv(folder+'huc8_indices.csv')
    print('Finished writing huc8 indices to csv')