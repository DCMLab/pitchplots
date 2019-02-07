# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 15:29:48 2018

@author: timothy
"""
import pandas as pd

def data_onset_duration_corrector(data):
    """
    corrects the duration and onset of the piece and normalize by the measure
    
    Keyword arguments:
    data -- the pandas DataFrame of the piece
    
    return:
    ret_data -- the pandas DataFrame of the the correction of the piece
    """
    corr_data = data.copy()
    
    min_onset = 0
    max_onset = 0
    onset_ratio = 0
    duration_ratio = 0
    current_minimum_time = 0
    time_ratio = 0
    
    #get rid of all the notes that have a zero duration
    corr_data.drop(corr_data[corr_data.duration == 0].index, inplace=True)
    
    #group the notes by measure 
    gb_mesure_no = corr_data.groupby('measure_no')
    
    ret_data = pd.DataFrame()
    
    for i in range(corr_data['measure_no'].max()):
        df_group = gb_mesure_no.get_group(i+1)
        
        #assume that the onset_ratio is the same for the last and before last measure
        if i != corr_data['measure_no'].max() - 1:
            df_group_next = gb_mesure_no.get_group(i+1+1)
            
            #it is assumed that the first note of the measure begins at the start of the measure
            min_onset = df_group['onset'].min()
            max_onset = df_group_next['onset'].min()
            onset_ratio = 1/(max_onset-min_onset)
        
        #set the onset like the first note start at the at the start of the onset
        df_group['onset'] *= onset_ratio
        df_group['onset'] += (i - df_group['onset'].min())
        
        #the time signature is the same for the whole measure
        duration_ratio = df_group['time_sign_den'].iloc[0]/df_group['time_sign_num'].iloc[0]
        df_group['duration'] *= duration_ratio
        
        #the ratio between the time in second when the note is played and the measure relative timing
        time_ratio = (4 * 60)/(duration_ratio * df_group['qpm'].iloc[0])
        
        #the adding of the time column using the onset column as base
        df_group = df_group.assign(time=df_group['onset'].values)
        df_group['time'] += -i
        df_group['time'] *= time_ratio
        df_group['time'] += current_minimum_time
        
        #the calculation of the time in second when the next measure begins
        current_minimum_time = current_minimum_time + time_ratio
        
        #add the group to the note sequence
        ret_data = pd.concat([ret_data, df_group])
    
    return ret_data

location = r'C:\Users\timothy\Python_converter\ragtime.csv'
data_read = pd.read_csv(location, sep=',')

data_onset_duration_corrector(data_read).to_csv('data_ragtime_corr.csv', sep=',')