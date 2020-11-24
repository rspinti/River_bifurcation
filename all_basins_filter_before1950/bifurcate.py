import numpy as np
import datetime

def make_fragments(segments, exit_id=999000, verbose=False, subwatershed=True):
    """Create stream fragments from stream segments based on dam locations.

    This function traverses through a stream network using NHD stream segment
    IDs delineating stream fragments that are divide by dams (refer to xx)
    for details on stream fragment definition.  This function requires a databse
    of stream segments where each stream segment (1) a unique identifier and
    identified upstream and downstream segments.  Additionaly, dams must be mapped
    to stream segments and have their own unique identifiers. 

    The resulting fragment designations will be assigned the Dam ID for any fragment
    ending in a dam or another unique identifieer starting at the exit_ID number
    for fragments which end at the terminal point of a river (default value is 999000). 

    Parameters:
        segments (pandas.DataFrame): 
             Dataframe providing segment informatation. The index for this dataframe
            must be the unique segment identifiers an it must have the following 
            columns
                - DnHydroseq: Unique segment ID for the downstream segment
                - UpHydroseq: Unique segment ID for the upstream segment
                - DamID: Unique ID of a Dam located on the segment. Segments with 
                    no dams should have a value of 0. 
        
        exit_id (int, optional): 
            Initial ID number to use for labeling terminal fragments.
        
        subwatershed (boolean, optional):
             If Subbasins is set to true it will identify headwaters as segements 
             which are not listed as downstream neighbors (DnHydroSeq) to any other basins

             If this is set to False it  will select all subbasins whith an UpHydroseq == 0 

    
    Returns:
        segments (pandas.DataFrame): An updated dataframe with a fragments column.
    """
    
    # Add a column for Fragment #'s and initilze with the DamIDs
    segments['Frag'] = segments['DamID']
    #print(segments['Frag'])


    # if the subwatershed option is true any segment which is not the
    # downstream neigbhor of another segment is  identified as a headwater
    # If not only grab those segments with an upstream  hydroseq = 0
    if subwatershed:
        intersect = np.intersect1d(segments.index, segments.DnHydroseq.values)
        queue = segments[~segments.index.isin(intersect)]
    else: 
        #initialize queue with all segments with upstream ID of 0
        queue = segments.loc[segments.UpHydroseq == 0]
    #print(len(queue))

    #record these segments as headwaters
    segments['Headwater']=np.zeros(len(segments))
    segments.loc[queue.index,'Headwater'] = 1

    snum = 0  # Counter for the segment starting points -- just for print purposes
    while len(queue) > 0:
        # Initialiazation for starting segment:
        step = 0  # start a counter for steps down the fragment
        snum = snum + 1
        temploc = queue.index[0]  # start with the segment at the top of the queue
        tempstart = temploc  # keep track of its ID for later
        templist = []   # make a list to store segments until you get to a dam
        templist.append(temploc)  # seed the list with the initial segment
        ftemp = segments.loc[temploc, 'Frag']  # Fragment # of current segment
        #if verbose == True:
        #    print("Satarting headwater #", snum, "SegID", temploc,
        #        "damflag", ftemp)

        # Walk downstream until you hit a dam or a segment thats
        # already been processed
        while ftemp == 0:
            step = step + 1
            dtemp = segments.loc[temploc, 'DnHydroseq']  # ID of downstream segment

            # if the downstream segment exists in the stream network then
            # walk downstream adding to the templist of stream segments
            if dtemp in segments.index:
                templist.append(dtemp)
                ftemp = segments.loc[dtemp, 'Frag']
                segments.loc[dtemp, 'step'] = step
                #if verbose == True:
                #    print("Step", step, "Downstream SegID", dtemp,
                #        "Downstream Frag", ftemp)
                temploc = dtemp

            # If not then you have reached a terminal point
            # add another Fragment ID for this teminal fragment
            # And set the dam flag to the fragment ID
            else:
                #if verbose == True:
                #    print("Step", step, "Ending", temploc)
                ftemp = exit_id+1  # New Fragment ID to be assigned
                exit_id = exit_id+1
                temploc = 0

        # print('Temploc', temploc, "Dtemp", dtemp)

        # assign the DamID fragment number to all of the segments
        segments.loc[templist, 'Frag'] = ftemp
        
        # If it wasn't a terminal fragment
        # add the downstream segment to the end of the queue
        if temploc > 0:
            newstart = segments.loc[temploc, 'DnHydroseq']
            #add to the count of dams
            #fragments.loc[ftemp, 'Ndam'] += segments.loc[temploc, 'DamCount']

            # If the downstream segment is in the index and it hasn't been processed yet
            if newstart in segments.index and segments.loc[newstart, 'Frag'] == 0:
                queue = queue.append(segments.loc[newstart])
                #if verbose == True:
                #    print("Adding to Queue!", newstart)

            # If the downstream segment is in the index and is another dam
            if newstart in segments.index and segments.loc[newstart, 'DamID'] > 0:
                queue = queue.append(segments.loc[newstart])
                #if verbose == True:
                #    print("Adding to Queue!", newstart)

        # delete the segment that was just finished from the queue
        queue = queue.drop(tempstart)
        #if verbose == True:
        #    print("Removing From Queue:", tempstart)

    # Add a column with the fragment indexes
    segments['Frag_Index'] = segments.Frag.rank(method='dense')

    return segments
  
def agg_by_frag(segments): 
    """Make a fragment data frame and aggregate by fragment.

    Starting from the segment dataframe this will create a new dataframe with 
    entries for every fragment value and summarize valued by fragment. 

    Parameters:
        segments (pandas.DataFrame): 
             Dataframe providing segment informatation. The index for this dataframe
            must be the unique segment identifiers an it must have the following 
            columns 
                (1) DnHydroseq: Unique segment ID for the downstream segment
                (2) UpHydroseq: Unique segment ID for the upstream segment
                (3) DamID: Unique ID of a Dam located on the segment. Segments with 
                    no dams should have a value of 0. 
                (4) Frag: Fragment ID assigned to every segment
        
        exit_id (int, optional): 
            Initial ID number to use for labeling terminal fragments.
    
    Returns:
        fragments (pandas.DataFrame): Fragments dataframe with summary information by fragment
    """
    # Making a fragment data frame and aggregated by fragment
    # Fill in fragment information
    # Total fragment length calculated using a pivot table from segment lengths
    #fragments0 = segments.pivot_table('LENGTHKM', index='Frag', aggfunc=sum)
    # fragments0 = segments.pivot_table(values=['LENGTHKM', 'DamCount', 'Norm_stor'], index='Frag', aggfunc=sum)
    fragments0 = segments.pivot_table(values=['LENGTHKM', 'DamCount', 'Norm_stor', 'HUC2','HUC4','HUC8'], index='Frag', aggfunc={'LENGTHKM' : np.sum, 'DamCount' : np.sum, 'Norm_stor' : np.sum, 'HUC2': np.median,'HUC4': np.median, 'HUC8': np.median})
    # Add in the fragment index
    fragments0 = fragments0.join(segments.pivot_table(values=['Frag_Index'], index='Frag', aggfunc=min))
    
    # Determining downstream segment ID --
    # Join in the downstream segment for the segments that that contains the dam
    # Using a pivot table with a sum here since there should only be one
    # value for a each non zero DamID and the zero will not be
    # included in the join
    frgDN = segments.pivot_table('DnHydroseq', index='DamID', aggfunc=sum)
    fragments0 = fragments0.join(frgDN)

    #Determine the flow for the segment with the dam
    frgQ = segments.pivot_table('QC_MA', index='DamID', aggfunc=sum)
    fragments0 = fragments0.join(frgQ)
    
    # Get the downstream fragment ID -
    # Use the downstream segment for each fragment to get its
    # downstream fragment ID
    fragments = fragments0.merge(segments.Frag, left_on='DnHydroseq',
                                 right_on=segments.index, suffixes=('_left', '_right'), how='left')
    fragments.index = fragments0.index
    fragments = fragments.rename(columns={'Frag': 'FragDn'})
    
    # Identify headwater fragments  -
    # Mark fragments that are headwaters
    #headlist = segments.loc[segments.UpHydroseq == 0, 'Frag'].unique()
    headlist = segments.loc[segments.Headwater == 1, 'Frag'].unique()
    fragments['HeadFlag'] = np.zeros(len(fragments))
    fragments.loc[headlist, 'HeadFlag'] = 1

    #Gettting the # of dams on a segment

    #Obtain HUCs in the fragment df
    # segments_filtered = segments[['Frag','HUC2','HUC4']]
    # fragments = fragments.merge(segments_filtered, on = 'Frag', how= 'right')

    return fragments


def map_up_frag(fragments):
    """Create a dictionary of upstream fragments for every fragment.

    Starting from the fragments dataframe created by agg_by_frag() 
    This creates a dictionary where each fragment is a Key and each Key
    contains a list of upstream fragment IDs. 

    Parameters:
        fragments (pandas.DataFrame): 
             Fragments data frame created by the agg_by_fragg function
    
    Returns:
        UpDict (dict): Dictionary of upstream fragment IDs for ever fragment
    """
    # STEP 3 : Make a list of the upstream fragments for every fragment
    #  Make a dictionary using the fragments as Keys
    #  with a list for every fragment of its upstream fragments

    # Initialize the dictionary
    UpDict = dict.fromkeys(fragments.index)

    #Loop through and initialize every fragment list with itself
    for ind in range(len(fragments)):
        ftemp = fragments.index[ind]
        UpDict[ftemp] = [ftemp]
        #print(ftemp)

    #Make a list of all the headwater fragments to start from
    #queuef = fragments.loc[fragments.HeadFlag == 1]

    # Figure out how many fragments are directly upstream from each fragment
    # i.e. how many parents it  has
    fragments['nparent'] = np.zeros(len(fragments))
    for f in range(len(fragments)):
        fragments.nparent[f] = len(fragments.loc[fragments.FragDn ==
                                                 fragments.index[f]])

    # Make a queue of fragments with no parents to start from
    queuef = fragments.loc[fragments.nparent == 0]

    #Initialize a counter of the number of parents visited
    fragments['parent_count'] = np.zeros(len(fragments))

    # Work downstream adding to the fragment lists
    while len(queuef) > 0:
        DnFrag = queuef.FragDn.iloc[0]
        ftemp = queuef.index[0]

        #print("Fragment:", ftemp, "Downstream:", DnFrag)

        # if the downstream fragment exists 
        # Add all of the parents of the current fragment to its downstream neigbor
        # and add one to the visited parent count of that neighbor
        if not np.isnan(DnFrag):
            UpDict[DnFrag].extend(UpDict[ftemp])
            fragments.loc[DnFrag, 'parent_count'] += 1

            # If the # of visitied parents ('parent_count')
            #  == the number of parents (nparent) then 
            # add the downstream neigbor to the queue 

            if fragments.loc[DnFrag, 'parent_count'] ==  \
                    fragments.loc[DnFrag, 'nparent']:

                #print("HERE Fragment:", ftemp, "Downstream fragment",
                #      DnFrag,  "nparent ", fragments.loc[DnFrag, 'nparent'],
                #      fragments.loc[DnFrag, 'parent_count'])

                queuef = queuef.append(fragments.loc[DnFrag])

        #remove the current fragment from the queue
        queuef = queuef.drop(queuef.index[0])

    # Remove the duplicate values in each list
    # Shouldn't need to do this anymore
    #for key in UpDict:
    #    #print(key)
    #    UpDict[key] = list(dict.fromkeys(UpDict[key]))

    return UpDict


def agg_by_frag_up(fragments, UpDict):
    """Aggregates fragment values by upstream area.

    Using the upstream dictionary and the fragment summary database created by
    map_up_frag() and agg_by_frag() respectively. This function appends columns
    to the fragments database with values aggregated by upstream area. 

    Parameters:
        fragments (pandas.DataFrame): 
             Fragments data frame created by the agg_by_fragg function
        
        UpDict (dict): 
            Dictionary of upstream fragments created by map_up_frag function.
    
    Returns:
        fragments (pandas.DataFrame): appended fragments dataframe.
    """

    fragments['NFragUp'] = np.zeros(len(fragments))
    fragments['LengthUp'] = np.zeros(len(fragments))
    fragments['NDamUp'] = np.zeros(len(fragments))
    fragments['StorUp'] = np.zeros(len(fragments))

    for key in UpDict:
        #print(key)
        fragments.loc[key, 'NFragUp'] = len(UpDict[key])
        fragments.loc[key, 'LengthUp'] = fragments.loc[UpDict[key],
                                                     'LENGTHKM'].sum()
        fragments.loc[key, 'NDamUp'] = fragments.loc[UpDict[key],
                                                       'DamCount'].sum()
        fragments.loc[key, 'StorUp'] = fragments.loc[UpDict[key],
                                                     'Norm_stor'].sum()
    
    return fragments


def upstream_ag(data, downIDs, agg_value):
    """Aggregates values by upstream 

    This function traverses through a stream network summing aggregating variable by 
    upstream area.  It requries an input dataframe which contains segment or fragment
    IDs, downstream IDs (downIDs) and a list of columns to be aggregated (agg_value). 

    The resulting dataframe will have '_up' fields added which are the upstream sums
    of all of the fields listed in agg_value. Additionally, a count of the number of 
    upstream segments or fragments is provided if you would like to convert sums to averages

    Parameters:
        data (pandas.DataFrame): 
            Data frame of segements or fragments where the index is the segment or fragment
            ID. It must contain a 'downIDs' column with downstream segement or fragment IDS
            and at least on column to be aggregated (agg_value).
        
        downIDs (string): 
            Column name that contains the downstream IDs within the dataframe
        
        agg_value (list):
            List of columns in the data frame to be aggregated. 
    
    Returns:
        segments (pandas.DataFrame): An updated dataframe with the aggregated values
    """


    #Make a dataframe with just the values of interest
    pick=agg_value.copy()
    pick.append(downIDs)
    up_agg = data[pick]
    #up_agg = data[[downIDs, agg_value]]

    #Start off giving every ID its onwn v
    upvar = [s + '_up' for s in agg_value]
    up_agg[upvar] = up_agg[agg_value]

    # Figure out how segments are directly upstream from each segment
    # i.e. how many parents it has
    t1 = datetime.datetime.now()
    pcount = up_agg[downIDs].value_counts(ascending=True)
    up_agg['nparent'] = pcount
    up_agg['nparent'] = up_agg['nparent'].fillna(0)
    #up_agg.isnull().sum(axis=0)
    t2 = datetime.datetime.now()
    #print("Counting parents: ", (t2-t1))

    # Make a queue of segments with no parents to start from
    queuef = up_agg.loc[up_agg['nparent'] == 0]

    #Initialize a counter of the number of parents visited
    up_agg['parent_count'] = np.zeros(len(up_agg))

    #Count number of segments in the upstream aggregation
    up_agg['upstream_count'] = np.ones(len(up_agg))

    # Work downstream adding to the fragment lists
    t1 = datetime.datetime.now()
    while len(queuef) > 0:
        #DnTemp = queuef.downIDs.iloc[0] #downstream ID
        DnTemp = queuef.iloc[0][downIDs]  # downstream ID
        ftemp = queuef.index[0] #current ID

        # if the downstream ID exists
        # Add all of the parents of the current fragment to its downstream neigbor
        # and add one to the visited parent count of that neighbor
        if not np.isnan(DnTemp) and DnTemp in up_agg.index:
            up_agg.loc[DnTemp, upvar] += up_agg.loc[ftemp, upvar]
            up_agg.loc[DnTemp, 'upstream_count'] += up_agg.loc[ftemp,
                                                               'upstream_count']
            up_agg.loc[DnTemp, 'parent_count'] += 1

            # If the # of visitied parents ('parent_count')
            #  == the number of parents (nparent) then
            # add the downstream neigbor to the queue

            if up_agg.loc[DnTemp, 'parent_count'] ==  \
                    up_agg.loc[DnTemp, 'nparent']:

                queuef = queuef.append(up_agg.loc[DnTemp])

        #remove the current fragment from the queue
        queuef = queuef.drop(queuef.index[0])

    t2 = datetime.datetime.now()
    #print("Aggregating: ", (t2-t1))


    return up_agg
