"""
module that has to read what is given to the plotting functions
"""
import pandas as pd
from pitchplots.functions import get_acc, get_step, get_pc

def get_df_short(
    piece,
    vocabulary={0:'C', 1:'Db', 2:'D', 3:'Eb', 4:'E', 5:'F', 6:'Gb', 7:'G', 8:'Ab', 9:'A', 10:'Bb', 11:'B'},
    pitch_type='tpc',
    duration=False,
    measures=None):
    """return a Dataframe with the condenced information about the piece for static plots

    Function:
    Get a file columns and read it to create a dataFrame with the following informations:
        pitch class value('pc'), number of appearences('nb'), total duration of the note('duration'),
        tpc format note('tpc'), sharps and flats('acc')
    Keyword arguments:
    piece -- the absolute path to the .csv file containing the data
    pitch_type -- the type of data that contains the file (default 'tpc')
        (tpc:[A, B#, Gbbb, ...], pc (pitch class):[0, 3, 7, ...])
    vocabulary -- the conversion table from pitch class to tpc(F#, A, ...) format,
        the position indicate the pitch class value (default [C, Db, D, Eb, E, F, Gb, G, Ab, A, Bb, B])
    measures -- give a set of measures example [5, 18], will display the notes of the measures 5 to 18 included
    """ 
    #check if it is a path to .csv or a DataFrame
    if isinstance(piece, pd.DataFrame):
        df_data = piece.copy()
    else:
        df_data =  pd.read_csv(piece)
    
    #the column with the pc values is called pitch_class so it rename it to 'pc'
    if 'pitch_class' in df_data.columns:
        df_data.rename(columns={'pitch_class': 'pc'}, inplace=True)
        
    if type(measures) is list:
        df_data.drop(df_data[df_data.measure_no < measures[0]].index, inplace=True)
        df_data.drop(df_data[df_data.measure_no > measures[1]].index, inplace=True)
        df_data.reset_index(drop=True, inplace=True)
    
    #If pitch_type is "tpc" we get a small DataFrame with the the columns:
    #   tpc, nb, duration (if exist), pc, acc, step
    if 'tpc' in df_data.columns and pitch_type == 'tpc':
        s_tpc = df_data['tpc'].groupby(df_data['tpc']).size()
        if not duration:
            s_tpc.sort_values(inplace=True, ascending=False)
        df_tpc = pd.DataFrame({'tpc':s_tpc.index, 'nb':s_tpc.values})
        if 'duration' in df_data.columns:
            df_duration = pd.DataFrame(df_data.groupby('tpc').duration.sum())
            df_tpc = pd.merge(df_tpc, df_duration, on='tpc')
            if duration:
                df_tpc.sort_values('duration', inplace=True, ascending=False)
            
        #get the pc values from tpc
        df_tpc['pc'] = df_tpc['tpc'].apply(get_pc)
        
        #add the sup column
        df_tpc['acc'] = df_tpc['tpc'].apply(get_acc)
        
        df_tpc['step'] = df_tpc['tpc'].apply(get_step)
        
        return df_tpc
    
    #If pitch_type is "pc" we get a small DataFrame with the the columns:
    #   pc, nb, duration (if exist), tpc(from vocabulary), acc, step
    if 'pc' in df_data.columns and pitch_type == 'pc':
        s_pc = df_data['pc'].groupby(df_data['pc']).size()
        if not duration:
            s_pc.sort_values(inplace=True, ascending=False)
        df_pc = pd.DataFrame({'pc':s_pc.index, 'nb':s_pc.values})

        #add the duration column
        if 'duration' in df_data.columns:
            df_duration = pd.DataFrame(df_data.groupby('pc').duration.sum())
            df_pc = pd.merge(df_pc, df_duration, on='pc')
            if duration:
                df_pc.sort_values('duration', inplace=True, ascending=False)
            
        #add the tpc column
        s_tpc_pc = []
        for i in range(df_pc.shape[0]):
            s_tpc_pc.append(vocabulary[int(df_pc.at[i, 'pc'])])

        df_pc['tpc'] = pd.Series(s_tpc_pc)

        #add the sup column
        df_pc['acc'] = df_pc['tpc'].apply(get_acc)

        #keep only the step from tpc
        df_pc['step'] = df_pc['tpc'].apply(get_step)

        return df_pc
