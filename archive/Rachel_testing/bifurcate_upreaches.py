import numpy as np

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
    
    Returns:
        segments (pandas.DataFrame): An updated dataframe with a fragments column.
    """

    # Add a column for Fragment #'s and initilze with the DamIDs
    segments['Frag'] = segments['DamID']
    #segments['Frag'] = np.zeros(len(segments))
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

    ## Old Queu steup -- need to delete
    ##If the flag is on then also add segments who's upstream segment is not included
    ##or that are not any other segments downstream neighbor
    #if subwatershed: 
    #    print("Including segments with upstream hydro seq not in segments list as headwaters")
    #    for ii in segments.index: 
    #        #print(ii)
    #        upstream = segments.loc[ii, 'UpHydroseq']
    #        #Check if the upstream neigbhor doesn't exist in the segments DF
    #        if not upstream in segments.index and upstream != 0:
    #            #print("adding segment",  ii, " upstream=", upstream, "queue length", len(queue))
    #            queue = queue.append(segments.loc[ii])
#
    #        #Check if there are no segments which drain to this one
    #        if not ii in segments.DnHydroseq.values:
    #            #print("adding segment",  ii, "queue length", len(queue))
    #            queue = queue.append(segments.loc[ii])
  

    # Initail number to use for fragments that are existing the  domain
    # Rather than hitting a dam. Exiting framents will start counting from
    # this number
    #fexit = 11

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
    fragments0 = segments.pivot_table(values=['LENGTHKM', 'DamCount'], index='Frag', aggfunc=sum)
    
    # Determining downstream segment ID --
    # Join in the downstream segment for the segments that that contains the dam
    # Using a pivot table with a sum here since there should only be one
    # value for a each non zero DamID and the zero will not be
    # included in the join
    frgDN = segments.pivot_table('DnHydroseq', index='DamID', aggfunc=sum)
    fragments0 = fragments0.join(frgDN)
    
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
    queuef = fragments.loc[fragments.HeadFlag == 1]

    # Work downstream adding to the fragment lists
    while len(queuef) > 0:
        DnFrag = queuef.FragDn.iloc[0]
        ftemp = queuef.index[0]
        #print("Fragment:", ftemp, "Downstream:", DnFrag)

        # if the downstream fragment exists adppend the current fagments list to it
        # and add the downstream fragment to the queue
        if not np.isnan(DnFrag):
            #print("HERE")
            UpDict[DnFrag].extend(UpDict[ftemp])
            queuef = queuef.append(fragments.loc[DnFrag])

        #remove the current fragment from the queue
        queuef = queuef.drop(queuef.index[0])

    # Remove the duplicate values in each list
    for key in UpDict:
        #print(key)
        UpDict[key] = list(dict.fromkeys(UpDict[key]))

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

    for key in UpDict:
        #print(key)
        fragments.loc[key, 'NFragUp'] = len(UpDict[key])
        fragments.loc[key, 'LengthUp'] = fragments.loc[UpDict[key],
                                                     'LENGTHKM'].sum()
        fragments.loc[key, 'NDamUp'] = fragments.loc[UpDict[key],
                                                       'DamCount'].sum()
    
    return fragments


def map_up_seg(segments):
    """Create a dictionary of upstream segments for every segment.

    Starting from the segments dataframe created by agg_by_frag() 
    This creates a dictionary where each segment is a Key and each Key
    contains a list of upstream segment IDs. 

    Parameters:
        segments (pandas.DataFrame): 
             Segments data frame created by the agg_by_fragg function
    
    Returns:
        UpDict_reaches (dict): Dictionary of upstream segment IDs for every segment
    """
    # STEP 5 : Make a list of the upstream segmentss for every segments
    #  Make a dictionary using the segments as Keys
    #  with a list for every segment of its upstream segments

    # Identify headwater fragments  -
    # Mark fragments that are headwaters
    #headlist = segments.loc[segments.UpHydroseq == 0, 'Frag'].unique()
    headlist = segments.loc[segments.Headwater == 1, 'Frag'].unique()
    segments['HeadFlag'] = np.zeros(len(segments))
    segments.loc[headlist, 'HeadFlag'] = 1

    # Initialize the dictionary
    UpDict_reaches = dict.fromkeys(segments.index)

    #Loop through and initialize every segment list with itself
    for ind in range(len(segments)):
        ftemp = segments.index[ind]
        UpDict_reaches[ftemp] = [ftemp]
        #print(ftemp)

    #Make a list of all the headwater segments to start from
    queuef = segments.loc[segments.HeadFlag == 1]

    # Work downstream adding to the segment lists
    while len(queuef) > 0:
        DnSeg = queuef.DnHydroseq.iloc[0]
        ftemp = queuef.index[0]
        #print("segment:", ftemp, "Downstream:", DnFrag)

        # if the downstream segment exists, append the current segments list to it
        # and add the downstream segment to the queue
        if not np.isnan(DnSeg):
            #print("HERE")
            UpDict_reaches[DnSeg].extend(UpDict_reaches[ftemp])
            queuef = queuef.append(segments.loc[DnSeg])

        #remove the current segment from the queue
        queuef = queuef.drop(queuef.index[0])

    # Remove the duplicate values in each list
    for key in UpDict_reaches:
        #print(key)
        UpDict_reaches[key] = list(dict.fromkeys(UpDict_reaches[key]))

    return UpDict_reaches


def agg_by_frag_up(segments, UpDict_reaches):
    """Aggregates segment values by upstream area.

    Using the upstream dictionary and the segment summary database created by
    map_up_frag() and agg_by_frag() respectively. This function appends columns
    to the segments database with values aggregated by upstream area. 

    Parameters:
        segments (pandas.DataFrame): 
             segments data frame created by the agg_by_fragg function
        
        UpDict (dict): 
            Dictionary of upstream segments created by map_up_frag function.
    
    Returns:
        segments (pandas.DataFrame): appended segments dataframe.
    """

    segments['NSegUp'] = np.zeros(len(segments))
    segments['LengthUp'] = np.zeros(len(segments))
    segments['NDamUp'] = np.zeros(len(segments))

    for key in UpDict_reaches:
        #print(key)
        segments.loc[key, 'NSegUp'] = len(UpDict_reaches[key])
        segments.loc[key, 'LengthUp'] = segments.loc[UpDict_reaches[key],
                                                     'LENGTHKM'].sum()
        segments.loc[key, 'NDamUp'] = segments.loc[UpDict_reaches[key],
                                                       'DamCount'].sum()
    
    return segments