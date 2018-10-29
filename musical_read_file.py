import numpy as np
import pandas as pd
from pitchplots1.musical_functions import check_tpc, check_pc, check_duration, get_acc, get_step, get_pc

def musical_read_file(location, minNote = 50):
    """Read a given file and put in a DataFrame the number of the column correspondant to the dataType

    Keyword arguments:
    location -- the absolute path to the .csv file containing the data
    minNote -- the minimum number of notes in the datas, can be set to 0, but useful for reading the file
    Return:
    return a small DataFrame with the columns of the tpc, pc and duration values if they exist
    """
    df_data = pd.read_csv(location)

    #booleans of he finds the tpc pc and duration values
    col_tpc = False
    col_duration = False
    col_pc = False

    columns = ['tpc', 'pc', 'duration']
    df_ret_col = pd.DataFrame(columns=columns)

    #if columns are already named correctly i read them automatically
    if df_data.columns.isin(['tpc']).any() and df_data.columns.isin(['pitch_class']).any() and df_data.columns.isin(['duration']).any():
        for i in range(df_data.shape[1]):
            if df_data.columns[i] == 'tpc':
                df_ret_col.at[0, 'tpc'] = i
            if df_data.columns[i] == 'pitch_class':
                df_ret_col.at[0, 'pc'] = i
            if df_data.columns[i] == 'duration':
                df_ret_col.at[0, 'duration'] = i
        return df_ret_col
    
    #read every columns
    for i in range(df_data.shape[1]):

        if df_data[df_data.columns[i]].dropna().shape[0] > minNote:
            #no error detected for pc
            if df_data[df_data.columns[i]].dropna().apply(check_pc).all() == True:
                col_pc = True
                df_ret_col.at[0, 'pc'] = i
                
            #no error detected for tpc
            if df_data[df_data.columns[i]].dropna().apply(check_tpc).all() == True and col_tpc == False:
                col_tpc = True
                df_ret_col.at[0, 'tpc'] = i

            #no error detected for duration
            if df_data[df_data.columns[i]].dropna().apply(check_duration).all() == True and col_duration == False:
                col_duration = True
                df_ret_col.at[0, 'duration'] = i

            #if he finds them all he breaks
            if col_pc and col_tpc and col_duration:
                break

    return df_ret_col

#========================================================================================================
def musical_get_data_full(location, dataType='tpc'):
    """get the columns to read and put them in a DataFrame

    Keyword arguments:
    location -- the absolute path to the .csv file containing the data
    dataType -- tell the program to read primarily the tpc or pc values
    Return:
    return every notes with their durations and pc and tpc values (step, acc)
    """
    df_data = pd.read_csv(location)
    df_col = musical_read_file(location)
    df_ret_data = pd.DataFrame()

    if pd.isnull(df_col.at[0, 'tpc']) == False and dataType == 'tpc':
        df_ret_data['tpc'] = pd.Series(df_data.iloc[:, df_col.at[0, 'tpc']])
        
        #add the sup column
        df_ret_data['sup'] = df_ret_data['tpc'].apply(get_acc)

        #keep only the step from tpc
        df_ret_data['tpc'] = df_ret_data['tpc'].apply(get_step)

        #check if the columns exist for duration
        if isinstance(df_col.at[0, 'duration'], int):
            df_ret_data['duration'] = pd.Series(df_data.iloc[:, df_col.at[0, 'duration']])

    if pd.isnull(df_col.at[0, 'pc']) == False and dataType == 'pc':
        df_ret_data['pc'] = pd.Series(df_data.iloc[:, df_col.at[0, 'pc']])
        
        #check if the columns exist for duration
        if isinstance(df_col.at[0, 'duration'], int):
            df_ret_data['duration'] = pd.Series(df_data.iloc[:, df_col.at[0, 'duration']])

    return df_ret_data

#=========================================================================================================
def musical_get_data_reduced(
    location,
    convertTable=['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'],
    dataType='tpc'):
    """get the columns to read and put the important elements in a DataFrame

    Function:
    Get a file columns and read it to create a dataFrame with the following informations:
        pitch class value('pc'), number of appearences('nb'), total duration of the note('duration'),
        tpc format note('tpc'), sharps and flats('sup')
    Keyword arguments:
    location -- the absolute path to the .csv file containing the data
    dataType -- the type of data that contains the file (default 'tpc')
        (tpc:[A, B#, Gbbb, ...], pc (pitch class):[0, 3, 7, ...])
    convertTable -- the conversion table from pitch class to tpc(F#, A, ...) format,
        the position indicate the pitch class value (default [C, Db, D, Eb, E, F, Gb, G, Ab, A, Bb, B])
    """
    df_data = pd.read_csv(location)
    df_col = musical_read_file(location)

    #read with priority to tpc values
    if pd.isnull(df_col.at[0, 'tpc']) == False and dataType == 'tpc':
        s_tpc = df_data.iloc[:, df_col.at[0, 'tpc']]
        s_tpc = s_tpc.groupby(s_tpc).size()

        #the most current note first
        s_tpc.sort_values(inplace=True, ascending=False)

        df_tpc = pd.DataFrame(s_tpc)
        df_tpc.columns = ['nb']
        df_tpc.reset_index(inplace=True)
        df_tpc.columns = ['tpc', 'nb']

        #add the duration column
        if pd.isnull(df_col.at[0, 'duration']) == False:
            df_duration = pd.concat([
                    df_data[df_data.columns[df_col.at[0, 'tpc']]],
                    df_data[df_data.columns[df_col.at[0, 'duration']]]],
                axis=1,
                keys=['tpc', 'duration'])
            df_duration = (df_duration.groupby('tpc')).sum()
            df_tpc = pd.merge(df_tpc, df_duration, on=['tpc', 'tpc'])

        #get the pc values from tpc
        df_tpc['pc'] = df_tpc['tpc'].apply(get_pc)
        
        #add the sup column
        df_tpc['sup'] = df_tpc['tpc'].apply(get_acc)

        #keep only the step from tpc
        df_tpc['tpc'] = df_tpc['tpc'].apply(get_step)

        return df_tpc

    #read with priority to pc values
    if pd.isnull(df_col.at[0, 'pc']) == False and dataType == 'pc':
        s_pc = df_data.iloc[:, df_col.at[0, 'pc']]
        s_pc = s_pc.groupby(s_pc).size()

        #the most current note first
        s_pc.sort_values(inplace=True, ascending=False)

        df_pc = pd.DataFrame(s_pc)
        df_pc.columns = ['nb']
        df_pc.reset_index(inplace=True)
        df_pc.columns = ['pc', 'nb']

        #add the duration column
        if pd.isnull(df_col.at[0, 'duration']) == False:
            df_duration = pd.concat([
                    df_data[df_data.columns[df_col.at[0, 'pc']]],
                    df_data[df_data.columns[df_col.at[0, 'duration']]]],
                axis=1,
                keys=['pc', 'duration'])
            df_duration = (df_duration.groupby('pc')).sum()
            df_pc = pd.merge(df_pc, df_duration, on=['pc', 'pc'])

        #add the tpc column
        s_tpc_pc = []
        for i in range(df_pc.shape[0]):
            s_tpc_pc.append(convertTable[int(df_pc.at[i, 'pc'])])

        df_pc['tpc'] = pd.Series(s_tpc_pc)

        #add the sup column
        df_pc['sup'] = df_pc['tpc'].apply(get_acc)

        #keep only the step from tpc
        df_pc['tpc'] = df_pc['tpc'].apply(get_step)

        return df_pc
