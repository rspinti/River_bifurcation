#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 16:10:39 2020

@author: rachelspinti

Purpose: Calculate RFI and RRI for each major river basin
"""
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd


def calc_rfi(fragments, tot_vol):
    ## RFI
    # - number of fragments
    # - total river volume of fragment
    # - total river volume of entire network
    # RFI = 100 - (sum(vi^2/V^2)*100)

    #How many fragments?
    frag_num = len(fragments)
    print(frag_num)

    #Total volume of river network
    tot_vol2 = tot_vol**2
    
    #Sum the fractions
    fraction_list = []
    for i in range(len(fragments)):
        frag_vol = (fragments['QC_MA'][i])**2
        fraction = frag_vol/tot_vol2
        fraction_list.append(fraction)
    print(len(fraction_list))

    #Finish the calculation
    rfi = 100 - (sum(fraction_list)*100)
    print(rfi)


    return rfi

def calc_rri(segments_update, tot_vol):
    ## DOR
    # DOR = (sum(storage of dams upstream)/total annual discharge) *100
    segments_update = segments_update.set_index('Hydroseq')
    Up_flowlines = dict.fromkeys(segments_update.index)
    # print(Up_flowlines.keys())
    
    # *Decide if the current reach is upstream of itself and should be counted in dictionary*
    # #Loop through and initialize every segment list with itself
    # for ind in range(len(segments_update)):
    #     ftemp = segments_update.index[ind]
    #     Up_flowlines[ftemp] = [ftemp]
    #     #print(ftemp)

    #Make a list of all the headwater segments to start from
    queue_seg = segments_update.loc[segments_update.StartFlag == 1]
    # print('queue index', queue_seg.index)
    # print('queue', queue_seg)

    # Work downstream adding to the segment lists
    while len(queue_seg) > 0:
        DnSeg = queue_seg.DnHydroseq.iloc[0]
        ftemp = queue_seg.index[0]
        #print("Segment:", ftemp, "Downstream:", DnSeg)

        # if the downstream segment exists append the current segment list to it
        # and add the downstream segment to the queue
        # if not np.isnan(DnSeg):
        if not DnSeg == 0:
            print("HERE")
            Up_flowlines[DnSeg].extend(Up_flowlines[ftemp])
            queue_seg.append(segments_update.loc[DnSeg])

        #remove the current segment from the queue
        queue_seg = queue_seg.drop(queue_seg.index[0])

    # Remove the duplicate values in each list
    for key in Up_flowlines:
        #print(key)
        Up_flowlines[key] = list(dict.fromkeys(Up_flowlines[key]))

    print(Up_flowlines)

    segments_update['NSegUp'] = np.zeros(len(segments_update))
    segments_update['FlowUp'] = np.zeros(len(segments_update))
    segments_update['Norm_storUp'] = np.zeros(len(segments_update))

    for key in Up_flowlines:
        #print(key)
        segments_update.loc[key, 'NSegUp'] = len(Up_flowlines[key])
        segments_update.loc[key, 'FlowUp'] = segments_update.loc[Up_flowlines[key],
                                                     'QC_MA'].sum()
        segments_update.loc[key, 'NDamUp'] = segments_update.loc[Up_flowlines[key],
                                                       'Norm_stor'].sum()
    
    # return segments_update
    # dor = (sum/tot_vol)*100