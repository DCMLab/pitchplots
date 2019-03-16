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
def xml_to_csv(filepath=os.path.dirname(os.path.realpath(__file__))+'\\'+'data_example.mxl',
               filename=None, save_csv=True):
    """return the Dataframe, and possbily register it in csv, of the musicxml file
    
    Keyword arguments:
    filepath -- absolute path to the xml file by default goes to the example file
    filename -- give the name of the .csv file, by default give the same name as the .mxl file
    save_cvs -- if True save the csv file in the csv directory or at the given path
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
