"""
stack of functions for the program
"""
import numpy as np
import pandas as pd

def get_dic_nei(pitch_class_display):
    """for musical_plot_hex it need the neighbouring notes in the hexagonal shape, return dictionary
        ref is the list of note that we are refering to
        pos is the position of the neighbouring note that we want to know
        note is the note at the position from the refering note
        sup is the accidental of the note at the given position
    """
    if pitch_class_display:
        # for every note there is a row 
        dic_nei = {'ref':[i for sublist in [[i]*6 for i in range(12)] for i in sublist],
                 'pos': [(1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1)]*12,
                 'note': [4, 7, 3, 8, 5, 9,
                          5, 8, 4, 9, 6, 10,
                          6, 9, 5, 10, 7, 11,
                          7, 10, 6, 11, 8, 0,
                          8, 11, 7, 0, 9, 1,
                          9, 0, 8, 1, 10, 2,
                          10, 1, 9, 2, 11, 3,
                          11, 2, 10, 3, 0, 4,
                          0, 3, 11, 4, 1, 5,
                          1, 4, 0, 5, 2, 6,
                          2, 5, 1, 6, 3, 7,
                          3, 6, 2, 7, 4, 8]}
    else:
        dic_nei = {'ref':[c for sublist in [[c]*6 for c in 'FCGDAEB'] for c in sublist],
                 'pos': [(1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1)]*7,
                 'note': ['A', 'C', 'A', 'D', 'B', 'D',
                          'E', 'G', 'E', 'A', 'F', 'A',
                          'B', 'D', 'B', 'E', 'C', 'E',
                          'F', 'A', 'F', 'B', 'G', 'B',
                          'C', 'E', 'C', 'F', 'D', 'F',
                          'G', 'B', 'G', 'C', 'A', 'C',
                          'D', 'F', 'D', 'G', 'E', 'G'],
                 'acc': [0, 0, -1, -1, -1, 0,
                         0, 0, -1, -1, 0, 0,
                         0, 0, -1, -1, 0, 0,
                         1, 0, 0, -1, 0, 0,
                         1, 0, 0, 0, 0, 1,
                         1, 0, 0, 0, 0, 1,
                         1, 1, 0, 0, 0, 1]}
    return dic_nei

def sampling(value, sampling_frequency):
    """return the sampled value at a given sampling frequency"""
    ret_value = 0
    
    if value%(1/sampling_frequency) <= (1/sampling_frequency)/2:
        ret_value = value - (value%(1/sampling_frequency))
    else:
        ret_value = value - (value%(1/sampling_frequency)) + (1/sampling_frequency)
        
    return ret_value

def put_flat_sharp(step, acc):
    """get a step and its acc and return the note in tpc notation, return str"""
    ret_note = step # not needed
    ret_acc = acc
    
    #put the flats and sharps
    if ret_acc > 0:
        for l in range(ret_acc):
            ret_note = ret_note + '#'     
    if ret_acc < 0:
        ret_acc = abs(ret_acc)
        for l in range(ret_acc):
            ret_note = ret_note + 'b'
    return ret_note # not needed

def is_tpc(note):
    """check if note has the same format as tpc, return boolean"""
    s_tpc_values_1 = pd.Series(['F', 'C', 'G', 'D', 'A', 'E', 'B'])
    s_tpc_values_2 = pd.Series(['b', '#'])

    correct_format_tpc = True
    count = 0

    for i in str(note):
        count = count + 1

        #check first character
        if (count == 1): 
            if (i == s_tpc_values_1).any() == False:
                correct_format_tpc = False
                    
        #check the flats and sharps
        else: 
            if (i == s_tpc_values_2).any() == False:
                correct_format_tpc = False
        if correct_format_tpc == False:
            break
    return correct_format_tpc

def is_pc(note):
    """check if note has the same format as pc, return boolean"""
    return note in range(12)

def get_acc(note):
    """get the acc from a tpc format, return int"""
    if is_tpc(note):
        acc = 0
        for i in str(note):
            if i == '#':
                acc = acc + 1
            if i == 'b':
                acc = acc - 1
        return acc

def get_step(note):
    """get the step from a tpc format, return str"""
    if is_tpc(note):
        step = ''
        step = str(note)[0]
        return step

def get_pc(note):
    """get the pitch class from a tpc value, return int"""
    pc = np.NaN
    s_tpc_pc = pd.Series(data=[0, 2, 4, 5, 7, 9, 11], index=['C', 'D', 'E', 'F', 'G', 'A', 'B'])
    if pd.isnull(note) == False:
        pc = s_tpc_pc.at[get_step(note)]
        pc = pc + get_acc(note)
        ###heck modulo
        while pc < 0:
            pc = pc + 12
        while pc > 11:
            pc = pc - 12
    return pc

def get_fifth_nb(note):
    """return the position of the note in the fifth line"""
    step = get_step(note)
    acc = get_acc(note)
    dic = {'F':0, 'C':1, 'G':2, 'D':3, 'A':4, 'E':5, 'B':6}
    return dic[step] + acc * 7

#change note to fifth_number Use same dictionnary
def get_fifth_note(note):
    """return the note after the fifth number"""
    count = 0
    ret_note = 0
    copy_note = int(note)
    while copy_note < 0 or copy_note > 6:
        if copy_note < 0:
            copy_note = copy_note + 7
            count = count - 1
        if copy_note > 6:
            copy_note = copy_note - 7
            count = count + 1
    if copy_note == 0: ret_note = 'F'
    if copy_note == 1: ret_note = 'C'
    if copy_note == 2: ret_note = 'G'
    if copy_note == 3: ret_note = 'D'
    if copy_note == 4: ret_note = 'A'
    if copy_note == 5: ret_note = 'E'
    if copy_note == 6: ret_note = 'B'
    ret_note = put_flat_sharp(ret_note, count)
    return ret_note
