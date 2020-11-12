import geopandas as gp, pandas as pd, numpy as np
# def avg_HUC2(combo_segGeo, gdrive, folder):
#     """Averages attribute by HUC 2.

#         This function

#         Parameters:
#             huc2 (pandas.DataFrame): 
                
        
#         Returns:
#     """  
#     huc2 = gp.read_file(gdrive+"hucs/HUC2_CONUS.shp")
#     huc2['HUC2'] = huc2['HUC2'].astype('int32')
#     indices_by_huc2 = combo_segGeo.pivot_table(values = ['avg_LengthUp', 'Norm_stor_up', 'Norm_stor','DamCount_up'], index='HUC2', aggfunc=np.mean)
        
#     huc2 = huc2.merge(indices_by_huc2, on = 'HUC2', how = 'left')
#     huc2.to_file(gdrive+folder+'huc2_indices.shp')
#     print('Finished writing huc2 indices to shp')

# def avg_HUC4(combo_segGeo, gdrive, folder):
#     """Averages attribute by HUC 4.

#         This function

#         Parameters:
#             huc4 (pandas.DataFrame): 
                
        
#         Returns:
#     """  
#     huc4 = gp.read_file(gdrive+"hucs/HUC4_CONUS.shp") 
#     indices_by_huc4 = combo_segGeo.pivot_table(values = ['avg_LengthUp', 'Norm_stor_up', 'Norm_stor','DamCount_up'], index='HUC4', aggfunc=np.mean)
        
#     huc4 = huc4.merge(indices_by_huc4, left_on = 'HUC4_no', right_on = 'HUC4', how = 'left')
#     huc4.to_file(gdrive+folder+'huc4_indices.shp')
#     print('Finished writing huc4 indices to shp')

# def avg_HUC8(combo_segGeo, gdrive, folder):
    # """Averages attribute by HUC 8.

    #     This function

    #     Parameters:
    #         huc8 (pandas.DataFrame): 
                
        
    #     Returns:
    # """  
    # huc8 = gp.read_file(gdrive+"hucs/HUC8_CONUS.shp") 
    # indices_by_huc8 = combo_segGeo.pivot_table(values = ['avg_LengthUp', 'Norm_stor_up', 'Norm_stor','DamCount_up'], index='HUC8', aggfunc=np.mean)
        
    # huc8 = huc8.merge(indices_by_huc8, left_on = 'HUC8_no', right_on = 'HUC8', how = 'left')
    # huc8.to_file(gdrive+folder+'huc8_indices.shp')
    # print('Finished writing huc8 indices to shp')

def agg_HUC2(combo_frag, gdrive, folder):
    """Averages attribute by HUC 2.

        This function

        Parameters:
            huc2 (pandas.DataFrame): 
                
        
        Returns:
    """  
    huc2 = gp.read_file(gdrive+"hucs/HUC2_CONUS.shp")
    huc2['HUC2'] = huc2['HUC2'].astype('int32')

    sum_by_huc2 = combo_frag.pivot_table(values = ['DamCount', 'Norm_stor'], index='HUC2', aggfunc=np.sum)

    avg_by_huc2 = combo_frag.pivot_table(values = ['LENGTHKM_frag'], index='HUC2', aggfunc=np.mean)
    avg_by_huc2 = avg_by_huc2.rename(columns = {'LENGTHKM_frag':'avg_frag_length'})

    max_by_huc2 = combo_frag.pivot_table(values = ['LENGTHKM_frag'], index='HUC2', aggfunc=np.max)
    max_by_huc2 = max_by_huc2.rename(columns = {'LENGTHKM_frag':'max_frag_length'})
            
    huc2 = huc2.merge(sum_by_huc2, on = 'HUC2', how = 'left')
    huc2 = huc2.merge(avg_by_huc2, on = 'HUC2', how = 'left')
    huc2 = huc2.merge(max_by_huc2, on = 'HUC2', how = 'left')
    huc2['avg_dam_size'] = huc2.Norm_stor/huc2.DamCount

    huc2.to_file(gdrive+folder+'huc2_indices.shp')
    print('Finished writing huc2 indices to shp')

def agg_HUC4(combo_frag, gdrive, folder):
    """Averages attribute by HUC 4.

        This function

        Parameters:
            huc4 (pandas.DataFrame): 
                
        
        Returns:
    """  
    huc4 = gp.read_file(gdrive+"hucs/HUC4_CONUS.shp")
    sum_by_huc4 = combo_frag.pivot_table(values = ['DamCount', 'Norm_stor'], index='HUC4', aggfunc=np.sum)

    avg_by_huc4 = combo_frag.pivot_table(values = ['LENGTHKM_frag'], index='HUC4', aggfunc=np.mean)
    avg_by_huc4 = avg_by_huc4.rename(columns = {'LENGTHKM_frag':'avg_frag_length'})

    max_by_huc4 = combo_frag.pivot_table(values = ['LENGTHKM_frag'], index='HUC4', aggfunc=np.max)
    max_by_huc4 = max_by_huc4.rename(columns = {'LENGTHKM_frag':'max_frag_length'})
            
    huc4 = huc4.merge(sum_by_huc4, left_on = 'HUC4_no', right_on = 'HUC4', how = 'left')
    huc4 = huc4.merge(avg_by_huc4, left_on = 'HUC4_no', right_on = 'HUC4', how = 'left')
    huc4 = huc4.merge(max_by_huc4, left_on = 'HUC4_no', right_on = 'HUC4', how = 'left')
    huc4['avg_dam_size'] = huc4.Norm_stor/huc4.DamCount
        
    huc4.to_file(gdrive+folder+'huc4_indices.shp')
    print('Finished writing huc4 indices to shp')

def agg_HUC8(combo_frag, gdrive, folder):
    """Averages attribute by HUC 8.

        This function

        Parameters:
            huc8 (pandas.DataFrame): 
                
        
        Returns:
    """  
    huc8 = gp.read_file(gdrive+"hucs/HUC8_CONUS.shp") 

    sum_by_huc8 = combo_frag.pivot_table(values = ['DamCount', 'Norm_stor'], index='HUC8', aggfunc=np.sum)

    avg_by_huc8 = combo_frag.pivot_table(values = ['LENGTHKM_frag'], index='HUC8', aggfunc=np.mean)
    avg_by_huc8 = avg_by_huc8.rename(columns = {'LENGTHKM_frag':'avg_frag_length'})

    max_by_huc8 = combo_frag.pivot_table(values = ['LENGTHKM_frag'], index='HUC8', aggfunc=np.max)
    max_by_huc8 = max_by_huc8.rename(columns = {'LENGTHKM_frag':'max_frag_length'})
            
    huc8 = huc8.merge(sum_by_huc8, left_on = 'HUC8_no', right_on = 'HUC8', how = 'left')
    huc8 = huc8.merge(avg_by_huc8, left_on = 'HUC8_no', right_on = 'HUC8', how = 'left')
    huc8 = huc8.merge(max_by_huc8, left_on = 'HUC8_no', right_on = 'HUC8', how = 'left')
    huc8['avg_dam_size'] = huc8.Norm_stor/huc8.DamCount

    huc8.to_file(gdrive+folder+'huc8_indices.shp')
    print('Finished writing huc8 indices to shp')
