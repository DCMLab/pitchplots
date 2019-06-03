"""
module that has to read what is given to the plotting functions
"""
import os

from pitchplots.functions import get_acc, get_step, get_pc, sampling

import pandas as pd
import moviepy.editor as mpe
#from midiutil import MIDIFile
#import librosa
#import numpy

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
    vocabulary -- the conversion table from pitch class to tpc(F#, A, ...) format,
        the position indicate the pitch class value (default [C, Db, D, Eb, E, F, Gb, G, Ab, A, Bb, B])
    pitch_type -- the type of data that contains the file (default 'tpc')
        (tpc:[A, B#, Gbbb, ...], pc (pitch class):[0, 3, 7, ...])
    duration -- tell him if he has to class the notes by their total duration or their number of appearance
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
    
def get_df_long(
        piece,
        vocabulary={0:'C', 1:'Db', 2:'D', 3:'Eb', 4:'E', 5:'F', 6:'Gb', 7:'G', 8:'Ab', 9:'A', 10:'Bb', 11:'B'},
        pitch_type='tpc',
        measures=None,
        sampling_frequency=50,
        speed_ratio=1,
        audio=False):
    """get the whole columns 
    need a column 'onset_seconds' that is the onset but in seconds
    Keyword arguments:
    piece -- the absolute path to the .csv file containing the data
    vocabulary -- the conversion table from pitch class to tpc(F#, A, ...) format,
        the position indicate the pitch class value (default [C, Db, D, Eb, E, F, Gb, G, Ab, A, Bb, B])
    pitch_type -- the type of data that contains the file (default 'tpc')
        (tpc:[A, B#, Gbbb, ...], pc (pitch class):[0, 3, 7, ...])
    measures -- give a set of measures example [5, 18], will display the notes of the measures 5 to 18 included
    sampling_frequency -- the frequency of lecture of the piece, also correspond to the fps of the video
    speed_ratio -- set the speed at which the video is read, for example : 2 accelerate the speed of the video by 2
    audio -- if True render the soundtrack for the animation
    """ 
    if isinstance(piece, pd.DataFrame):
        df_data = piece.copy()
    else:
        df_data =  pd.read_csv(piece)
    
    #the column with the pc values is called pitch_class so it rename it to 'pc'
    if 'pitch_class' in df_data.columns:
        df_data.rename(columns={'pitch_class': 'pc'}, inplace=True)
    
    #drop the unwanted measures
    if type(measures) is list:
        df_data.drop(df_data[df_data.measure_no < measures[0]].index, inplace=True)
        df_data.drop(df_data[df_data.measure_no > measures[1]].index, inplace=True)
        df_data.reset_index(drop=True, inplace=True)
        df_data['onset_seconds'] -= df_data['onset_seconds'].min()
        df_data['onset'] -= df_data['onset'].min()
    
    if 'tpc' in df_data.columns and pitch_type=='tpc':
        if 'acc' not in df_data.columns:
            df_data['acc'] = df_data['tpc'].apply(get_acc)
        if 'step' not in df_data.columns:
            df_data['step'] = df_data['tpc'].apply(get_step)
    if 'pc' in df_data.columns and pitch_type=='pc':
        if 'tpc' not in df_data.columns:
            df_data['tpc'] = df_data.replace({"pc":vocabulary})
        if 'acc' not in df_data.columns:
            df_data['acc'] = df_data['tpc'].apply(get_acc)
        if 'step' not in df_data.columns:
            df_data['step'] = df_data['tpc'].apply(get_step)
    
    #the animation functions do not need the rests
    if 'type' in df_data.columns:
        df_data.drop(df_data[df_data.type == 'rest'].index, inplace=True)
            
    df_data.sort_values('onset_seconds', inplace = True)
    df_data['onset_seconds'] *= (1/speed_ratio)
    df_data.reset_index(inplace=True)
    
    ###AUDIO
    if audio:
        sound_path = os.path.dirname(os.path.realpath(__file__))+'\\'+'data'+'\\'
        soundtrack = mpe.AudioFileClip(sound_path+'silence.wav')
        print('Rendering the soundtrack')
        for i in range(df_data.shape[0]):
            note_sound = mpe.AudioFileClip(sound_path+'midi'+str(int(df_data.at[i, 'pitch']))+'.wav')
            #NOTE TO EXPLAIN THAT
            if df_data.at[i, 'duration']*4*60/df_data.at[i, 'qpm'] < 4:
                note_sound = note_sound.set_duration(df_data.at[i, 'duration']*4*60/df_data.at[i, 'qpm'])
            else:
                note_sound = note_sound.set_duration(4)
            note_sound = note_sound.set_start(df_data.at[i, 'onset_seconds'])
            soundtrack = mpe.CompositeAudioClip([soundtrack, note_sound])
        print('The soundtrack is done')
        
#    soundtrack.write_audiofile("test1.wav", fps=44100)
    
    df_data['onset_seconds'] = df_data['onset_seconds'].apply(sampling, sampling_frequency=sampling_frequency)
    
#    if midi:
#        midi_track    = 0
#        midi_channel  = 0
#        midi_time     = 0    # In beats
#        midi_tempo    = df_data.at[0, 'qpm']*speed_ratio   # In BPM
#        midi_volume   = 100  # 0-127, as per the MIDI standard
#        
#        MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
#                              # automatically)
#        MyMIDI.addTempo(midi_track, midi_time, midi_tempo)
#        s_onset = pd.Series(data=(df_data['onset']*df_data['time_sign_num']/df_data['time_sign_den'])*4)
#        
#        for i in range(df_data.shape[0]):
#            MyMIDI.addNote(midi_track, midi_channel, int(df_data.at[i, 'pitch']), s_onset[i], df_data.at[i, 'duration']*4, midi_volume)
#            
#        with open("pitchplots_midi.mid", "wb") as output_file:
#            MyMIDI.writeFile(output_file)
#            
#        y, sr = librosa.load('pitchplots_midi.mid')
#        librosa.output.write_wav('pitchplots_sound_only.wav', y, sr)
    if audio:
        return (df_data, soundtrack)
    else:
        return df_data
