import geopandas as gp, pandas as pd, numpy as np

def HUC2_indices_merge(gdrive, data_folder, results_folder, purpose):
    """Merges HUC2 summary with HUC2 shapefile.
        This function takes the combined HUC2 summary csv created in the
        create_combined_csv.py function and merges it with the HUC2 shapefile for
        CONUS. The HUC2 summary csv and HUC2 shapefile are read in. Then, the
        two are merged on the HUC2 column. Finally, this dataframe is written
        to a shapefile.
        Parameters:
            gdrive (string):
                Location on the Google Drive where data is saved.
            folder (string):
                Folder on the Google Drive where combined csv is saved.
            HUC2_summary (pandas.DataFrame):
                Dataframe containing indices summarized by HUC2.
                columns
            huc2 (geopandas.GeoDataFrame): 
                Geodataframe containing geospatial info by HUC2.
                columns
                
        
        Returns:
            A shapefile containing geometry and indices by HUC2.
    """  
    HUC2_summary = pd.read_csv(gdrive+data_folder+'HUC2_summary_'+purpose+'.csv')

    huc2 = gp.read_file(gdrive+"hucs/HUC2_CONUS.shp")
    huc2 = huc2[['OBJECTID', 'AreaSqKm', 'AreaAcres', 'Name', 'States', 'HUC2_db', 'geometry']]
    
    huc2 = huc2.merge(HUC2_summary, left_on = 'HUC2_db', right_on = 'HUC2', how = 'left')
    # print(type(huc2))
    # print(huc2)
    # huc2 = huc2.fillna(0)

    huc2.to_file(gdrive+results_folder+'huc2_indices_'+purpose+'.shp')
    print('Finished writing huc2 indices to shp')
    
    return huc2

def HUC4_indices_merge(gdrive, data_folder, results_folder, purpose):
    """Merges HUC4 summary with HUC4 shapefile.
        This function takes the combined HUC4 summary csv created in the
        create_combined_csv.py function and merges it with the HUC4 shapefile for
        CONUS. The HUC4 summary csv and HUC4 shapefile are read in. Then, the
        two are merged on the HUC4 column. Finally, this dataframe is written
        to a shapefile.
        Parameters:
            gdrive (string):
                Location on the Google Drive where data is saved.
            folder (string):
                Folder on the Google Drive where combined csv is saved.
            HUC4_summary (pandas.DataFrame):
                Dataframe containing indices summarized by HUC4.
                columns
            huc4 (geopandas.GeoDataFrame): 
                Geodataframe containing geospatial info by HUC4.
                columns
                
        
        Returns:
            A shapefile containing geometry and indices by HUC4.
    """   
    HUC4_summary = pd.read_csv(gdrive+data_folder+'HUC4_summary_'+purpose+'.csv')

    huc4 = gp.read_file(gdrive+"hucs/HUC4_CONUS.shp")
    huc4 = huc4[['OBJECTID', 'AreaSqKm', 'AreaAcres', 'Name', 'States', 'HUC4_no', 'geometry']]

    huc4 = huc4.merge(HUC4_summary, left_on = 'HUC4_no', right_on = 'HUC4', how = 'left')
    # huc4 = huc4.merge(HUC4_summary, on = 'HUC4', how = 'left')
    huc4 = huc4.drop(columns=['HUC4'])
    # huc4 = huc4.fillna(0)

    huc4.to_file(gdrive+results_folder+'huc4_indices_'+purpose+'.shp')
    print('Finished writing huc4 indices to shp')
    
    return huc4

def HUC8_indices_merge(gdrive, data_folder, results_folder, purpose):
    """Merges HUC8 summary with HUC8 shapefile.
        This function takes the combined HUC8 summary csv created in the
        create_combined_csv.py function and merges it with the HUC8 shapefile for
        CONUS. The HUC8 summary csv and HUC8 shapefile are read in. Then, the
        two are merged on the HUC8 column. Finally, this dataframe is written
        to a shapefile.
        Parameters:
            gdrive (string):
                Location on the Google Drive where data is saved.
            folder (string):
                Folder on the Google Drive where combined csv is saved.
            HUC8_summary (pandas.DataFrame):
                Dataframe containing indices summarized by HUC8.
                columns
            huc8 (geopandas.GeoDataFrame): 
                Geodataframe containing geospatial info by HUC8.
                columns
                
        
        Returns:
            A shapefile containing geometry and indices by HUC8.
    """   
    HUC8_summary = pd.read_csv(gdrive+data_folder+'HUC8_summary_'+purpose+'.csv')

    huc8 = gp.read_file(gdrive+"hucs/HUC8_CONUS.shp") 
    huc8 = huc8[['OBJECTID', 'AreaSqKm', 'AreaAcres', 'Name', 'States', 'HUC8_no', 'geometry']]
        
    huc8 = huc8.merge(HUC8_summary, left_on = 'HUC8_no', right_on = 'HUC8', how = 'left')
    huc8 = huc8.drop(columns=['HUC8'])
    # huc8 = huc8.fillna(0)
    
    huc8.to_file(gdrive+results_folder+'huc8_indices_'+purpose+'.shp')
    # print(type(huc8))
    print('Finished writing huc8 indices to shp')
    
    return huc8