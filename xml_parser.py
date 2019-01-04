"""
Parse .xml or .mxl files and return a pandas DataFrameself.
"""

import os
import sys
import numpy as np
import pandas as pd
import re
# import matplotlib.pyplot as plt
# import seaborn as sns
# % matplotlib inline

# import xml parser from magenta
from magenta.music import musicxml_parser

### DEFINE PARSER
def musicxml2df(filepath):

    #add of this variable for control of the time and key signature000
    #/.
    key_signature_on = False
    time_signature_on = False
    #./
    
    #adding of the time_signature after the filename column000
    columns = ['filepath', # piece ID or something (TODO)
               'composer',
               'filename',
               'time_signature', #add time_signature000
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

    composer = re.search('[A-Z]\w*',filepath).group()
    filename = re.search(composer+'\\\(.*)\.', filepath).group(1)

    parsed = musicxml_parser.MusicXMLDocument(filepath)
    df = pd.DataFrame(columns=columns)

    for part in parsed.parts:
        measure_no = 0
        for measure in part.measures:
            measure_no += 1
            
            #keep the previous key signature000
            #because the key signature appears only if it changes000
            #/.
            if pd.isnull(measure.key_signature) == False:
                key_signature_on = True
                root = measure.key_signature.key
                mode = measure.key_signature.mode
                key_area = measure.key_signature.time_position
            elif key_signature_on == False:
                root = np.nan
                mode = np.nan
                key_area = np.nan
            #./
            
            #adding of the time_signature like the key_signature000
            #/.
            if pd.isnull(measure.time_signature) == False:
                time_signature_on = True
                time_signature = str(measure.time_signature.numerator) + \
                    '/' + str(measure.time_signature.denominator)
            elif time_signature_on == False:
                time_signature = np.nan
            #./

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

                #adding of the time_signature after the filename column000
                values = [filepath,
                          composer,
                          filename,
                          time_signature,
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
    return df

### READ FILES
PATH = os.path.join('..', 'data','scores')

xmls = []
for (dirpath, dirnames, filenames) in os.walk(PATH):
    for f in filenames:
        if f.endswith(('.xml', '.mxl')):
            xmls.append(f)

print('There are {} .xml or .mxl files.'.format(len(xmls)))

### CHECK WHICH FILES ARE ALREADY PARSED
meta = pd.read_csv(os.path.join('..', 'metadata.csv'), sep='\t', index_col=0, encoding='utf-8')
unparsed = meta[meta.parsed.isnull() & meta.filename.notnull()]

### PARSE UNPARSED FILES
dfs = []
for i, piece in unparsed.iterrows():
    composer_last = piece.composer
    composer_first = piece.composer_first.replace(" ", "").replace("é", "e")
    filename = piece.filename
    filepath = os.path.join('..', 'data', 'scores', f'{composer_last}'+'_'+f'{composer_first}', filename)

    if piece.parsed != 1:
        print(f"Parsing {filename}")
        try:
            df = musicxml2df(filepath)

            meta.loc[i, 'no_notes'] = df.shape[0] # number of notes
            meta.loc[i, 'parsed'] = 1 # mark state as parsed
            dfs.append(df)
            df.to_csv(os.path.join('..', 'data','DataFrames', f'{filename}' + '.csv'))

            print(f'Success: {filepath}')
        except Exception as e:
            meta.at[i, piece.parsed] = 0
            print(f'--> Error: {filepath}')
            print("Unexpected error:", sys.exc_info())
            print(e)
            pass

### UPDATE METADATA FILE
meta.to_csv(os.path.join('..', 'metadata.csv'), sep='\t', encoding='utf-8')

### RETURN MESSAGE
print('DONE!')
print(f'{str(len(dfs))} files have been parsed.')

### SUMMARY STATISTICS
notes = meta.no_notes.sum()
parsed = meta.parsed.sum()
print(f'There are now {int(parsed)} parsed pieces and {int(notes)} notes in the dataset.')