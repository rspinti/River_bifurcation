
import numpy as np
import pandas as pd
from time import time


def join_dams_flowlines(flowlines, run_name, nabd):
    """Join the dams and flowlines with COMID to create a new dataset.

    This function obtains and filters NHDPlus V2 and NABD for analysis in 
    bifurcate.py. The NHD flowlines are split into major U.S. river basins by 
    their HUC 2 for processing. Dams are then joined to the each basin.
    
    Filters the joined dataset for analysis in bifurcate.py.

    This function further filters the dam and flowline data.
    It uses NHDPlus V2 and NABD to create the dataset. The NHD flowlines are split
    into major U.S. river basins by their HUC 2 for processing. 

    Parameters:
        flowlines (pandas.DataFrame): 
            List of the major U.S. river basins that correspond to the run_name.
            The HUC 2 values listed after the name are used to filter the 
            ReachCode into the groupings we want.
            columns
                - Hydroseq: Unique segment ID for current segment, places flowlines
                in hydrologic order
                - UpHydroseq: Unique segment ID for the upstream segment
                - DnHydroseq: Unique segment ID for the downstream segment
                - REACHCODE: 14-digit HUC 
                - LENGTHKM: Length of segment in km
                - StartFlag: Flag to indicate if segment is a headwater (0 = not
                headwater, 1 = headwater)
                - FTYPE: Type of flowline
                - COMID: Common ID of the NHD flowline
                - WKT: Geometry of flowline stored in WKT format
                
        nabd (pandas.DataFrame): 
            Dataframe providing dam attributes. A unique DamID is added to ID
            fragments in bifurcate.py. Duplicate dams were dropped because 
            their storage was the same.
            columns
                - COMID: Common ID of the NHD flowline, used to like NABD to NHD
                - NIDID: Official unique dam ID (string) from NID
                - Norm_stor: Normal storage of the resevoir in ac-ft
                - Max_stor: Maximum storage of the resevoir in ac-ft
                - Year_compl: Year when original dam structure was completed
                - Purposes: Abbreviations indicate current usage purpose
                - geometry: Point geometry for dam locations
                - DamID: Unique integer ID for each dam to use for fragments
                
        run_name (string):
            Specified in the main script to run a particular basin. Run options
            include:
            'California', 'Colorado', 'Columbia', 'Great Basin', 'Great Lakes',
            'Gulf Coast','Mississippi', 'North Atlantic', 'Red', 'Rio Grande',
            'South Atlantic'
                
        major_basins (list): 
            List of the major U.S. river basins that correspond to the run_name.
            The HUC 2 values listed after the name filter the REACHCODE into 
            river basin groupings.
            
        nabd_nhd_join (pandas.DataFrame):
            Dataframe containing dam and flowline attributes related by COMID.
            The data is joined using the merge function and takes its queue 
            from the NABD COMID.
            columns
                - Hydroseq: Unique segment ID for current segment, places flowlines
                in hydrologic order
                - UpHydroseq: Unique segment ID for the upstream segment
                - DnHydroseq: Unique segment ID for the downstream segment
                - REACHCODE: 14-digit HUC 
                - LENGTHKM: Length of segment in km
                - StartFlag: Flag to indicate if segment is a headwater (0 = not
                headwater, 1 = headwater)
                - FTYPE: Type of flowline
                - WKT: Line geometry of flowline stored in WKT format
                - NIDID: Official unique dam ID (string) from NID
                - Norm_stor: Normal storage of the resevoir in ac-ft
                - Max_stor: Maximum storage of the resevoir in ac-ft
                - Year_compl: Year when original dam structure was completed
                - Purposes: Abbreviations indicate current usage purpose
                - geometry: Point geometry for dam locations
                - DamID: Unique integer ID for each dam to use for fragments
                
        storage_sum (pandas.DataFrame):
            Dataframe created from the groupby function. The data is grouped
            by Hydroseq and Norm_stor is summed among each Hydroseq. This accounts
            for storage values of multiple dams lying on one segment.
            columns
                - Hydroseq
                - Norm_stor
            
        dam_count (pandas.Dataframe):
            Dataframe obtained from a pandas pivot table. The data was grouped
            by Hydroseq and then the number of occurences of that Hydroseq was
            summed to get the Dam_Count for each segment.
            columns
                - Hydroseq
                - Dam_Count
        
        count_sum_merge (pandas.DataFrame): 
            Dataframe that contains the filtered Dam_Count and Norm_stor values
            from storage_sum and dam_count. Hydroseq was used to merge storage_sum
            and dam_count.
            columns
                - Hydroseq
                - Norm_stor
                - Dam_Count

        nabd_nhd_filtered (pandas.DataFrame): 
            GeoDataframe that filters out the Norm_stor and Dam_Count columns as 
            well as duplicate values. This allows us to merge in the data from
            count_sum_merge.
            columns
                - Hydroseq: Unique segment ID for current segment, places flowlines
                in hydrologic order
                - UpHydroseq: Unique segment ID for the upstream segment
                - DnHydroseq: Unique segment ID for the downstream segment
                - REACHCODE: 14-digit HUC 
                - LENGTHKM: Length of segment in km
                - StartFlag: Flag to indicate if segment is a headwater (0 = not
                headwater, 1 = headwater)
                - FTYPE: Type of flowline
                - WKT: Line geometry of flowline stored in WKT format
                - NIDID: Official unique dam ID (string) from NID
                - Max_stor: Maximum storage of the resevoir in ac-ft
                - Year_compl: Year when original dam structure was completed
                - Purposes: Abbreviations indicate current usage purpose
                - geometry: Point geometry for dam locations
                - DamID: Unique integer ID for each dam to use for fragments
            
        nabd_nhd_df (geopandas.geodataframe.GeoDataFrame):
            GeoDataframe that contains the filtered Hydroseq, Norm_stor, and 
            Dam_count values. It also contains all prior attributes that are 
            needed for bifurcate.py.
            
            columns
                - Hydroseq: Unique segment ID for current segment, places flowlines
                in hydrologic order
                - UpHydroseq: Unique segment ID for the upstream segment
                - DnHydroseq: Unique segment ID for the downstream segment
                - REACHCODE: 14-digit HUC 
                - LENGTHKM: Length of segment in km
                - StartFlag: Flag to indicate if segment is a headwater (0 = not
                headwater, 1 = headwater)
                - FTYPE: Type of flowline
                - WKT: Line geometry of flowline stored in WKT format
                - NIDID: Official unique dam ID (string) from NID
                - Norm_stor: Normal storage of the resevoir in ac-ft
                - Max_stor: Maximum storage of the resevoir in ac-ft
                - Year_compl: Year when original dam structure was completed
                - Purposes: Abbreviations indicate current usage purpose
                - geometry: Point geometry for dam locations
                - DamID: Unique integer ID for each dam to use for fragments
                - Dam_Count: Indicates the number of dams along a segment (int)
                
    Returns:
        segments_df (geopandas.geodataframe.GeoDataFrame): A dataframe with filtered dam and 
        flowline attributes.
        'run_name'+.csv (csv): CSV file to be read into the main script
    
    """

    # Dictionary with river basin names and associated HUC 2s
    major_basins = {'California' : [18],
                    'Colorado' : [14, 15],
                    'Columbia' : [17],
                    'Great Basin' : [16], 
                    'Great Lakes' : [4],
                    'Gulf Coast' : [12],
                    'Mississippi' : [5, 6, 7, 8, 1019, 11],
                    'North Atlantic' : [1, 2],
                    'Red' : [9],
                    'Rio Grande' : [13],
                    'South Atlantic' : [3]}
    # print(major_basins)
    
    
    # Based on the run_name, a different basin will be selected
    t1 = time()
    if run_name == 'California':
        #create dataframe with California flowlines
        california = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])] 
        nabd_nhd_join = nabd.merge(california, how= 'right', on='COMID') # Merge NABD and California
    
    if run_name == 'Colorado':
        #create dataframe with Colorado flowlines
        colorado = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])| 
        (flowlines['REACHCODE'] == major_basins[run_name][1])]
        nabd_nhd_join = nabd.merge(colorado, how= 'right', on='COMID') # Merge NABD and Colorado
    
    if run_name == 'Columbia':
        #create dataframe with Columbia flowlines
        columbia = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
        nabd_nhd_join = nabd.merge(columbia, how= 'right', on='COMID') # Merge NABD and Columbia
    
    if run_name == 'Great Basin':
        #create dataframe with Great Basin flowlines
        great_basin = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
        nabd_nhd_join = nabd.merge(great_basin, how= 'right', on='COMID') # Merge NABD and Great Basin
    
    if run_name == 'Great Lakes':
        #create dataframe with Great Lakes flowlines
        great_lakes = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
        nabd_nhd_join = nabd.merge(great_lakes, how= 'right', on='COMID') # Merge NABD and Great Lakes
    
    if run_name == 'Gulf Coast':
        #create dataframe with Gulf Coast flowlines
        gulf_coast = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
        nabd_nhd_join = nabd.merge(gulf_coast, how= 'right', on='COMID') # Merge NABD and Gulf Coast
        
    # if run_name == 'Mississippi':
    #     #create dataframe with Mississippi flowlines
    #     mississippi = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])|
    #     (flowlines['REACHCODE'] == major_basins[run_name][1]) |
    #     (flowlines['REACHCODE'] == major_basins[run_name][2]) |
    #     (flowlines['REACHCODE'] == major_basins[run_name][3]) | 
    #     (flowlines['REACHCODE'] == major_basins[run_name][4]) |
    #     (flowlines['REACHCODE'] == major_basins[run_name][5])]
    #     nabd_nhd_join = nabd.merge(mississippi, how= 'right', on='COMID') # Merge NABD and Mississippi
    if run_name == 'Mississippi':
        #create dataframe with Mississippi flowlines
        mississippi = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][4])]
        nabd_nhd_join = nabd.merge(mississippi, how= 'right', on='COMID') # Merge NABD and Mississippi
        
    if run_name == 'North Atlantic':
        #create dataframe with North Atlantic flowlines
        north_atlantic = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])|
        (flowlines['REACHCODE'] == major_basins[run_name][1])]
        nabd_nhd_join = nabd.merge(north_atlantic, how= 'right', on='COMID') # Merge NABD and North Atlantic
    
    if run_name == 'Red':
        #create dataframe with Red flowlines
        red = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
        nabd_nhd_join = nabd.merge(red, how= 'right', on='COMID') # Merge NABD and Red
    
    if run_name == 'Rio Grande':
        #create dataframe with Rio Grande flowlines
        rio_grande = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
        nabd_nhd_join = nabd.merge(rio_grande, how= 'right', on='COMID') # Merge NABD and Rio Grande
    
    if run_name == 'South Atlantic':
        #create dataframe with South Atlantic flowlines
        south_atlantic = flowlines.loc[(flowlines['REACHCODE'] == major_basins[run_name][0])]
        nabd_nhd_join = nabd.merge(south_atlantic, how= 'right', on='COMID') # Merge NABD and Sounth Atlantic
    
    t2 = time()
    # Add to and filter data for bifurcation analysis
    ## add a column to keep track of steps
    nabd_nhd_join.insert(5, "step", np.zeros(len(nabd_nhd_join)), True)
  
    ## Filtering the Hydroseq, storage, and dam count
    # Group by Hydroseq and sum storage
    storage_sum = nabd_nhd_join.groupby(['Hydroseq'])['Norm_stor'].sum().reset_index()
    # storage_sum = nabd_nhd_join.groupby(['Hydroseq'])['Norm_stor'].sum()
    # print(type(storage_sum))
    # print(storage_sum.columns)
  
    # Count # of duplicate dams
    nabd_nhd_join['DamCount'] = np.zeros(len(nabd_nhd_join))  #add count column
    dam_count = nabd_nhd_join.pivot_table(index=['Hydroseq'], aggfunc={'DamCount':'size'}).reset_index() #Aggregate by the size of each Hydroseq
    # dam_count = nabd_nhd_join.pivot_table(index=['Hydroseq'], aggfunc={'DamCount':'size'}) #Aggregate by the size of each Hydroseq
    # print(type(dam_count))
    # print(dam_count.columns)
    
    # Merge count and storage dataframes
    count_sum_merge = storage_sum.merge(dam_count, how= 'left', on='Hydroseq')  #merge count and sum 
    # print(type(count_sum_merge))
    # print(count_sum_merge.columns)
  
    # Filter nabd_nhd_join for merge
    nabd_nhd_filtered = nabd_nhd_join.drop_duplicates(subset='Hydroseq', keep="last")  #drop everything but last duplicate
    nabd_nhd_filtered = nabd_nhd_filtered.drop(columns=['Norm_stor', 'DamCount'])  #drop Norm_stor and DamCount, so new one is added
    # print(type(nabd_nhd_filtered))
    # print(nabd_nhd_filtered.columns)
  
    # Merge the dataframes so the storage and DamIDs are how we want
    nabd_nhd_df = nabd_nhd_filtered.merge(count_sum_merge, how= 'left', on='Hydroseq') #Merge filtered dataframes
  
    # Fill in the NA's for the dam column with 0s
    nabd_nhd_df['DamID'] = nabd_nhd_df['DamID'].fillna(0)
  
    # Make a column to indicate if a dam is present or not
    nabd_nhd_df.loc[nabd_nhd_df.DamID==0, 'DamCount'] = 0 #if the DamID is 0, make dam count =0
  
    # Set index to Hydroseq
    nabd_nhd_df = nabd_nhd_df.set_index('Hydroseq')
    # print(type(nabd_nhd_df))
    # print(nabd_nhd_df.columns)
    
    # Rename WKT column
    nabd_nhd_df = nabd_nhd_df.rename(columns={'WKT': 'Coordinates'})
    
    t3 = time()
  
    # Creates csv for each run_name
    segments_df = nabd_nhd_df.copy()
    # segments_df.to_csv(run_name+'.csv')  
    segments_df.to_csv('extracted_HUC1019.csv') #for extracted HUC
    print('Finished writing segments_df to csv..........')
    
    t4 = time()
    print("---- TIMING SUMMARY -----")
    print('Select basin', t2-t1)
    print('Filtering', t3-t2)
    print('Write to csv', t4-t3)
    
    return segments_df

