import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib
import math
from musical_read_file import musical_read_file

def musical_plot_hex(
    location,
    dataType='tpc',
    convertTable=['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'],
    size = 3,
    hexSize = 1,
    textSize = 1,
    figSize = 9,
    colorGeneral = 'Blues',
    centerNote = 'notDefine'):
    """Plot a 2D grid of hexagons, each hexagons being a note

    Function:
    Get a file location send it to musical_read_file
    from it plot a 2D grid of hexagons, one hexagon direction is the fifths, one the major thirds and
    the minor thirds, the importance of the note is shown by the color as a heatmap
    Keyword arguments:
    location -- the absolute path to the .csv file containing the data
    dataType -- the type of data that contains the file (default 'tpc')
        (tpc:[A, B#, Gbbb, ...], pc (pitch class):[0, 3, 7, ...])
    convertTable -- the conversion table from pitch class to tpc(F#, A, ...) format,
        the position indicate the pitch class value (default [C, Db, D, Eb, E, F, Gb, G, Ab, A, Bb, B])
    size -- define the number of layers of the hexagonal grid (default 3)
    hexSize -- indicate the size of the hexagons (default 1)
    textSize -- indicate the size of the typo for the labels (default 1)
    figSize -- indicate the size of the produced figure in inches (default 9)
    colorGeneral -- indicate the type of color to use for the heatmap, see matplotlib color documentation (default 'Blues')
    centerNote -- you can set the note that will be in the center of the grid,
        by default it put the most recurent note in the center (default 'notDefine')
    """
    #===================================================================================
    #constant, parameter, variables
    #===================================================================================

    #settings
    convertTable = pd.Series(convertTable)
    df_tpc = musical_read_file(location, convertTable=convertTable, dataType=dataType)
    
    #constant
    HEXEDGE = math.sqrt(3)/2 #math constant

    #intern variables
    length = 0.05 * hexSize#radius and border length of the hexagons
    center = [0.5, 0.5] # set the center on the center of the map
    size_text = length * 200 * textSize # maybe a parameter fontsize
    pos = [0, 0, 0] #x, y, z
    pos_ser = (0, 0, 0) #for serching in the data
    a_centerNote = ['F', 0] # the centerNote that was define (note, sup)

    #define figure
    figsize = [figSize, figSize] #define the size if the figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, aspect='equal')
    
    #colormap for the layout
    cmap = matplotlib.cm.get_cmap(colorGeneral)

    #is the list of hexagon already define
    columns = ['pos', 'note', 'sup']
    df_pos = pd.DataFrame(columns=columns)

    #give the notes'neighbours
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
    df_nei = pd.DataFrame.from_dict(dic_nei)

    #give the direction to look to for the nearest define hexagon
    x_list = [-1, 1, 0, 0, 1, -1]
    y_list = [1, -1, -1, 1, 0, 0]
    z_list = [0, 0, 1, -1, -1, 1]

    max_val_tpc = df_tpc['nb'].max()

    #===================================================================================
    #hexgrid
    #===================================================================================

    #do the first hexagon of the center
    if(centerNote == 'notDefine'): #if not define it takes the most current note
        p = patches.RegularPolygon(
            center,
            6,
            radius=length,
            color=cmap(1/1))
        ax.text(
            center[0],
            center[1],
            df_tpc['tpc'][0].replace('#', r'$\sharp$') \
                            .replace('b', r'$\flat$'),
            horizontalalignment='center',
            verticalalignment='center',
            size=size_text)
        df_pos = df_pos.append(
            {'pos':(0,0,0), 'note':df_tpc['tpc'][0], 'sup':df_tpc['sup'][0]},
            ignore_index=True)
        ax.add_patch(p)
        
    else: #read the given note and display it
        for j in centerNote:
            if j == '#':
                a_centerNote[1] = a_centerNote[1] + 1
            if j == 'b':
                a_centerNote[1] = a_centerNote[1] - 1
            if j != '#' and j != 'b':
                carac = j
        a_centerNote[0] = carac
        
        df_pos = df_pos.append(
            {'pos':(0,0,0), 'note':a_centerNote[0], 'sup':a_centerNote[1]},
            ignore_index=True)
        color = cmap(0)
        if (df_tpc['tpc'] == a_centerNote[0]).any():
            select_data = df_tpc['tpc'] == a_centerNote[0]
            current_index = df_tpc[select_data].index[0]
            if df_tpc[select_data].at[current_index, 'sup'] == a_centerNote[1]:
                color = cmap(df_tpc[select_data].at[current_index, 'nb']/max_val_tpc)

        if a_centerNote[1] > 0:
            for l in range(a_centerNote[1]):
                a_centerNote[0] = a_centerNote[0] + '#'     
        if a_centerNote[1] < 0:
            a_centerNote[1] = abs(a_centerNote[1])
            for l in range(a_centerNote[1]):
                a_centerNote[0] = a_centerNote[0] + 'b'

        p = patches.RegularPolygon(
            center,
            6,
            radius=length,
            facecolor=color,
            edgecolor='Black')
        ax.text(
            center[0],
            center[1],
            a_centerNote[0].replace('#', r'$\sharp$') \
                           .replace('b', r'$\flat$'),
            horizontalalignment='center',
            verticalalignment='center',
            size=size_text)
        ax.add_patch(p)
        
    #do the rest of the plot except the first hex
    for layer in range(size + 1): #for each layer
        for i in range(3): #for x,y,z
            for j in range(2): #for negative and positive value
                for k in range(layer): #to do the number of hexagon on sides
                    #set the position of the hexagon
                    pos[(0 + i) % 3] = layer * ((-1) ** j)
                    pos[(1 + i) % 3] = (-layer + k) * ((-1) ** j)
                    pos[(2 + i) % 3] = (-k) * ((-1) ** j)

                    #position of the nearest hexagon already defined
                    pos_ser = (
                        pos[0] + x_list[j+i*2],
                        pos[1] + y_list[j+i*2], 
                        pos[2] + z_list[j+i*2])
                    
                    #position to search in df_nei
                    pos_ser_n = (
                        x_list[j+i*2] * (-1),
                        y_list[j+i*2] * (-1),
                        z_list[j+i*2] * (-1)) 
                    
                    select_data = df_pos['pos'] == pos_ser

                    #get the # or b from the reference note
                    current_sup = df_pos[select_data].iat[0, 2]
                    
                    #get df for the note of reference from df_nei
                    df_nei_gr = df_nei.groupby('ref').get_group(df_pos[select_data].iat[0, 1])

                    #select the name of the note from the hexagone
                    select_data = df_nei_gr['pos'] == pos_ser_n 

                    current_note = df_nei_gr[select_data].iat[0, 2]
                    current_sup = current_sup + df_nei_gr[select_data].iat[0, 3]

                    #register the hex
                    df_pos = df_pos.append(
                        {'pos':(pos[0], pos[1], pos[2]),
                            'note':current_note,
                            'sup':current_sup},
                        ignore_index=True)

                    #set the facecolor of the hex
                    color = cmap(0)
                    if (df_tpc['tpc'] == current_note).any():
                        select_data = df_tpc['tpc'] == current_note

                        #get the index to be able to work with at and not iat
                        current_index = df_tpc[select_data].index[0]
                        
                        if df_tpc[select_data].at[current_index, 'sup'] == current_sup:
                            color = cmap(df_tpc[select_data].at[current_index, 'nb']/max_val_tpc)

                    #format current_note to display the # and b
                    current_sup = current_sup.astype(np.int64)
                    if current_sup > 0:
                        for l in range(current_sup):
                            current_note = current_note + '#'     
                    if current_sup < 0:
                        current_sup = abs(current_sup)
                        for l in range(current_sup):
                            current_note = current_note + 'b'

                    #calcul the center position of the hex in function of the coordonnate
                    center = [0.5 + pos[0] * HEXEDGE * length - pos[1] * HEXEDGE * length,
                              0.5 + pos[0] * length / 2 + pos[1] * length / 2 - pos[2] * length]

                    # put the number on hexagon (how he constructs them)
                    #ax.text(center[0], center[1], k + (j*layer) + (i*2*layer))

                    #put the name of the hex
                    ax.text(
                        center[0],
                        center[1],
                        current_note.replace('#', r'$\sharp$') \
                                    .replace('b', r'$\flat$'),
                        horizontalalignment='center',
                        verticalalignment='center',
                        size=size_text)

                    #draw the hex
                    p = patches.RegularPolygon(
                        center,
                        6,
                        radius=length,
                        facecolor=color,
                        edgecolor='Black')
                    ax.add_patch(p)

    plt.show()
