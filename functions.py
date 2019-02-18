import numpy as np
import pandas as pd

def get_dic_nei(pitch_class_display):
    """for musical_plot_hex it need the neighbouring notes in the hexagonal shape, return dictionary"""
    if pitch_class_display:
        dic_nei = {'ref':[0, 0, 0, 0, 0, 0,
                          1, 1, 1, 1, 1, 1,
                          2, 2, 2, 2, 2, 2,
                          3, 3, 3, 3, 3, 3,
                          4, 4, 4, 4, 4, 4,
                          5, 5, 5, 5, 5, 5,
                          6, 6, 6, 6, 6, 6,
                          7, 7, 7, 7, 7, 7,
                          8, 8, 8, 8, 8, 8,
                          9, 9, 9, 9, 9, 9,
                          10, 10, 10, 10, 10, 10,
                          11, 11, 11, 11, 11, 11],
                 'pos': [(1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1),
                         (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1),
                         (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1),
                         (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1),
                         (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1),
                         (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1),
                         (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1),
                         (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1),
                         (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1),
                         (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1),
                         (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1),
                         (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1)],
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
        dic_nei = {'ref':['F', 'F', 'F', 'F', 'F', 'F',
                          'C', 'C', 'C', 'C', 'C', 'C',
                          'G', 'G', 'G', 'G', 'G', 'G',
                          'D', 'D', 'D', 'D', 'D', 'D',
                          'A', 'A', 'A', 'A', 'A', 'A',
                          'E', 'E', 'E', 'E', 'E', 'E',
                          'B', 'B', 'B', 'B', 'B', 'B'],
                 'pos': [(1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1),
                         (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1),
                         (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1),
                         (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1),
                         (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1),
                         (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1),
                         (1,0,-1), (1,-1,0), (0,-1,1), (-1,0,1), (-1,1,0), (0,1,-1)],
                 'note': ['A', 'C', 'A', 'D', 'B', 'D',
                          'E', 'G', 'E', 'A', 'F', 'A',
                          'B', 'D', 'B', 'E', 'C', 'E',
                          'F', 'A', 'F', 'B', 'G', 'B',
                          'C', 'E', 'C', 'F', 'D', 'F',
                          'G', 'B', 'G', 'C', 'A', 'C',
                          'D', 'F', 'D', 'G', 'E', 'G'],
                 'sup': [0, 0, -1, -1, -1, 0,
                         0, 0, -1, -1, 0, 0,
                         0, 0, -1, -1, 0, 0,
                         1, 0, 0, -1, 0, 0,
                         1, 0, 0, 0, 0, 1,
                         1, 0, 0, 0, 0, 1,
                         1, 1, 0, 0, 0, 1]}
    return dic_nei

def put_flat_sharp(note, acc):
    """get a step and its acc and return the note in tpc notation, return str"""
    ret_note = note
    ret_acc = acc
    
    #put the flats and sharps
    if ret_acc > 0:
        for l in range(ret_acc):
            ret_note = ret_note + '#'     
    if ret_acc < 0:
        ret_acc = abs(ret_acc)
        for l in range(ret_acc):
            ret_note = ret_note + 'b'
    return ret_note

def check_tpc(note):
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

def check_pc(note):
    """check if note has the same format as pc, return boolean"""
    s_pc_values = pd.Series([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
    correct_format_pc = True

    if isinstance(note, int) or isinstance(note, float):
        if (note == s_pc_values).any() == False:
            correct_format_pc = False
    else:
        correct_format_pc = False
        
    return correct_format_pc

def check_duration(note):
    """check if note has the same format as duration, return bolean"""
    correct_format_duration = True

    if isinstance(note, int) or isinstance(note, float):
        if note <= 0 or note > 4:
            correct_format_duration = False
    else:
        correct_format_duration = False
        
    return correct_format_duration

def get_acc(note):
    """get the acc from a tpc format, return int"""
    acc = 0
    for i in str(note):
        if i == '#':
            acc = acc + 1
        if i == 'b':
            acc = acc - 1
    return acc

def get_step(note):
    """get the step from a tpc format, return str"""
    step = np.NaN
    if pd.isnull(note) == False:
        step = str(note)[0]
    return step

def get_pc(note):
    """get the pitch class from a tpc value, return int"""
    pc = np.NaN
    s_tpc_pc = pd.Series(data=[0, 2, 4, 5, 7, 9, 11], index=['C', 'D', 'E', 'F', 'G', 'A', 'B'])
    if pd.isnull(note) == False:
        pc = s_tpc_pc.at[get_step(note)]
        pc = pc + get_acc(note)
        while pc < 0:
            pc = pc + 12
        while pc > 11:
            pc = pc - 12
    return pc

def get_fifth_nb(note, acc):
    """return the position of the note in the fifth line"""
    ret_nb = 0
    if note == 'F': ret_nb = 0
    if note == 'C': ret_nb = 1
    if note == 'G': ret_nb = 2
    if note == 'D': ret_nb = 3
    if note == 'A': ret_nb = 4
    if note == 'E': ret_nb = 5
    if note == 'B': ret_nb = 6
    ret_nb = ret_nb + acc * 7
    return ret_nb

def get_fifth_note(note):
    """return the note after the fifth number"""
    count = 0
    ret_note = 0
    copy_note = int(note.copy())
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

