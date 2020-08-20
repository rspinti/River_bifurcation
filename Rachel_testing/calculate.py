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

def my_lil_function():
    print('Hi your lil function worked')


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
        frag_vol = (fragments['QE_MA'][i])**2
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
    
    for i in range(len(segments_update.Hydroseq)):
        fragments.loc[i, 'NDamUp'] = fragments.loc[UpDict[i], 'DamCount'].sum()
    dor = (sum/tot_vol)*100