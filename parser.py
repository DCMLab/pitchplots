"""
Parse .xml or .mxl files and return a pandas DataFrameself.
"""
import sys
import os

import numpy as np
import pandas as pd

# import xml parser from magenta
from pitchplots.modified_musicxml_parser import MusicXMLDocument

class ParseError(Exception):
    """
    Exception thrown when the MusicXML contents cannot be parsed.
    """
    pass

### DEFINE PARSER
def xml_to_csv(filepath=os.path.dirname(os.path.realpath(__file__))+'\\'+'data'+'\\'+'data_example.mxl',
               filename=None, save_csv=True, duration='whole_note'):
    """return the Dataframe, and possbily register it in csv, of the musicxml file
    
    Keyword arguments:
    filepath -- absolute path to the xml file by default goes to the example file
    filename -- give the name of the .csv file, by default give the same name as the .mxl file
    save_cvs -- if True save the csv file in the csv directory or at the given path
    duration -- define of the duration will be in seconds or relative to a whole note
                (possible values: 'seconds' or 'whole_note'(default value))
    """
    columns = ['filepath', # piece ID or something (TODO)
               'qpm', #add qpm, the beat per minute
               'time_sign_num', #add the time signature numerator
               'time_sign_den', #add the time signature denumerator
               'measure_no', # number of measure
               'no_accs', # number of accidentals
               'mode', # mode of key as defined in XML (not reliable)
               'key_area', # begin of key signature
               'type', # type of event (note or rest)
               'note_name', # note name (e.g. C4, Bb2)
               'tpc', # tonal pitch class: note name w/o octave, e.g. C, F#...
               'step', # diatonic step in A, B, C, D, E, F, G
               'acc', # accidentals
               'octave', # octave number (int)
               'pitch', # MIDI pitch name (i.e. C4 = 60)
               'pitch_class', # pitch modulo 12
               'duration', # note duration in beats as float (i.e. a quarter note is 0.25) ???? IS THIS CORRECT?
               'onset' # onset in seconds
              ]
    
    #add of these variables for control
    key_signature_on = False
    time_signature_on = False
    qpm_on = False
    
    try:
        parsed = MusicXMLDocument(filepath)
    except:
        raise ParseError('There is a problem with the path to the xml/mxl file or the files are not standard.')
    
    df = pd.DataFrame(columns=columns)

    for part in parsed.parts:
        measure_no = 0
        for measure in part.measures:
            measure_no += 1
            
            #keep the previous key signature
            #because the key signature appears only if it changes
            if pd.isnull(measure.key_signature) == False:
                key_signature_on = True
                root = measure.key_signature.key
                mode = measure.key_signature.mode
                key_area = measure.key_signature.time_position
            elif key_signature_on == False:
                root = np.nan
                mode = np.nan
                key_area = np.nan
            
            #adding of the time_signature like the key_signature
            if pd.isnull(measure.time_signature) == False:
                time_signature_on = True
                time_sign_num = measure.time_signature.numerator
                time_sign_den = measure.time_signature.denominator
            elif time_signature_on == False:
                time_sign_num = np.nan
                time_sign_den = np.nan
            
            #adding of qpm
            if pd.isnull(measure.state.qpm) == False:
                qpm_on = True
                qpm = measure.state.qpm
            elif qpm_on == False:
                qpm = np.nan
            
            for note in measure.notes:
                if note.is_rest:
                    ntype = 'rest'
                else:
                    ntype = 'note'
                if note.pitch is not None:
                    note_name = note.pitch[0]
                    tpc = note_name[:-1]
                    pitch = int(note.pitch[1])
                    pitch_class = int(note.pitch[1] % 12)
                    step = note_name[0]
                    if '#' in note_name:
                        acc = 1
                    elif 'bb' in note_name:
                        acc = -2
                    elif 'b' in note_name:
                        acc = -1
                    elif 'x' in note_name:
                        acc = 2
                    else:
                        acc = 0
                    octave = note_name[-1]
                else:
                    note_name = np.nan
                    tpc = np.nan
                    pitch = np.nan
                    step = np.nan
                    acc = np.nan
                    pitch_class = np.nan
                    octave = np.nan
                duration =  note.note_duration.duration_float()
                onset = note.note_duration.time_position

                # final list of of the columns of the dataframe
                values = [filepath,
                          qpm,
                          time_sign_num,
                          time_sign_den,
                          measure_no,
                          root,
                          mode,
                          key_area,
                          ntype,
                          note_name,
                          tpc,
                          step,
                          acc,
                          octave,
                          pitch,
                          pitch_class,
                          duration,
                          onset]
                row = dict(zip(columns, values))
                df = df.append(row, ignore_index=True)
    
    # correct the onset to be quantized by the measure number
    # add the 'onset_seconds' column from the new onset, for the dynamic plotting
    df = data_onset_duration_corrector(df, duration)
    
    if save_csv:
        #  path to the csv directory
        csv_path = os.path.dirname(sys.argv[0])+r'/csv'
        # get the name from the xml file and put in csv dir
        if pd.isnull(filename):
            if not os.path.exists(csv_path):
                os.makedirs(csv_path)
            filename = os.path.basename(filepath).split('.')[0] + '.csv'
            df.to_csv(os.path.join(csv_path,filename), sep=',')
        # if filename is a path, register the csv file at the given path
        elif "\\" in filename or "/" in filename:
            df.to_csv(filename, sep=',')
        # get the name and put it in csv folder
        else:
            # check if the csv folder already exist if not create one
            if not os.path.exists(csv_path):
                os.makedirs(csv_path)
            df.to_csv(os.path.join(csv_path,filename), sep=',')

    return df

def data_onset_duration_corrector(data, duration):
    """
    corrects the duration and onset of the piece and normalize by the measure
    
    Keyword arguments:
    data -- the pandas DataFrame of the piece
    duration -- define of the duration will be in seconds or relative to a whole note
                (possible values: 'seconds' or 'whole_note'(default value))
    return:
    ret_data -- the pandas DataFrame of the the correction of the piece
    """
    corr_data = data.copy()
    
    #get rid of notes and rests that have a 0 duration
    #they are more likely falsely parsed notes from musicxml_parser
    corr_data.drop(corr_data[corr_data.duration == 0].index, inplace=True)
    
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
        df_group = gb_mesure_no.get_group(i+1).copy()
        
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
        
        # if True change the duration to be in seconds using the BPM value
        if duration =='seconds':
            #so the duration is equal to the number of seconds of the quatized note
            df_group['duration'] *= (4*60)/df_group['qpm'].iloc[0]
        
        #the ratio between the time in second when the note is played and the measure relative timing
        time_ratio = (4 * 60)/(duration_ratio * df_group['qpm'].iloc[0])
        
        #the adding of the time column using the onset column as base
        df_group = df_group.assign(onset_seconds=df_group['onset'].values)
        df_group['onset_seconds'] += -i
        df_group['onset_seconds'] *= time_ratio
        df_group['onset_seconds'] += current_minimum_time
        
        #the calculation of the time in second when the next measure begins
        current_minimum_time = current_minimum_time + time_ratio
        
        #add the group to the note sequence
        ret_data = pd.concat([ret_data, df_group])
        
    return ret_data