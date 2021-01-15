import geopandas as gp, pandas as pd, numpy as np
# how to summarize the HUC data after it is created in run_workflow.py
## print out each HUC analysis to a csv named basin_HUC2/4/8.csv
## join all these csvs into one big one
## then, join the big one with the corresponding shapefile from the Drive
### this will be a new file that we can use for mapping in QGIS


def avg_HUC2(combo_segGeo, gdrive, folder):
    """Averages attribute by HUC 2.

        This function

        Parameters:
            huc2 (pandas.DataFrame): 
                
        
        Returns:
    """  
    huc2 = gp.read_file(gdrive+"hucs/HUC2_CONUS.shp")
    huc2['HUC2'] = huc2['HUC2'].astype('int32')
    indices_by_huc2 = combo_segGeo.pivot_table(values = ['avg_LengthUp', 'Norm_stor_up', 'Norm_stor','DamCount_up'], index='HUC2', aggfunc=np.mean)
        
    huc2 = huc2.merge(indices_by_huc2, on = 'HUC2', how = 'left')
    huc2.to_file(gdrive+folder+'huc2_indices.shp')
    print('Finished writing huc2 indices to shp')

def avg_HUC4(combo_segGeo, gdrive, folder):
    """Averages attribute by HUC 4.

        This function

        Parameters:
            huc4 (pandas.DataFrame): 
                
        
        Returns:
    """  
    huc4 = gp.read_file(gdrive+"hucs/HUC4_CONUS.shp") 
    indices_by_huc4 = combo_segGeo.pivot_table(values = ['avg_LengthUp', 'Norm_stor_up', 'Norm_stor','DamCount_up'], index='HUC4', aggfunc=np.mean)
        
    huc4 = huc4.merge(indices_by_huc4, left_on = 'HUC4_no', right_on = 'HUC4', how = 'left')
    huc4.to_file(gdrive+folder+'huc4_indices.shp')
    print('Finished writing huc4 indices to shp')

def avg_HUC8(combo_segGeo, gdrive, folder):
    """Averages attribute by HUC 8.

        This function

        Parameters:
            huc8 (pandas.DataFrame): 
                
        
        Returns:
    """  
    huc8 = gp.read_file(gdrive+"hucs/HUC8_CONUS.shp") 
    indices_by_huc8 = combo_segGeo.pivot_table(values = ['avg_LengthUp', 'Norm_stor_up', 'Norm_stor','DamCount_up'], index='HUC8', aggfunc=np.mean)
        
    huc8 = huc8.merge(indices_by_huc8, left_on = 'HUC8_no', right_on = 'HUC8', how = 'left')
    huc8.to_file(gdrive+folder+'huc8_indices.shp')
    print('Finished writing huc8 indices to shp')