# -*- coding: utf-8 -*-
"""
Created on Thu Jan  3 17:58:30 2019

@author: timothy
"""

#import xml parser from magenta and midi_io
from magenta.music import midi_io
from magenta.scripts import convert_dir_to_note_sequences

def convert_musicxml_to_midi(full_file_path, name_midi_file, root_dir = None, sub_dir = None):
    """
    convert a musicxml file into a midi file using the magenta library
    
    Keyword arguments:
    full_file_path -- the full path to the musicxml document
    name_midi_file -- the name of the midi file, don't forget to end with .mid
    root_dir -- the root directory for the classification of the piece in midi
    sub_dir -- the sub root directory for the classification of the piece in midi
    """
    #parse the xml file to a proto_note_sequence in magenta
    parsed_proto = convert_dir_to_note_sequences.convert_musicxml(root_dir, sub_dir, full_file_path)
    
    #transform the proto_note_sequence in midi file
    midi_io.sequence_proto_to_midi_file(parsed_proto, name_midi_file)
    