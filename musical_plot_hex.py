import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib
import math
from musical_read_file import musical_get_data_reduced
from musical_functions import get_acc, get_step, get_pc, get_dic_nei, put_flat_sharp
    
def musical_plot_hex(
    location,
    dataType='tpc',
    pitchClassDisplay=False,
    duplicate=True,
    duration=False,
    log=False,
    colorbar=True,
    convertTable=['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'],
    size = 3,
    hexSize = 1,
    textSize = 1,
    figSize = 9,
    colorGeneral = 'Blues',
    colorZeroValue = 'nan',
    centerNote = 'nan'):
    """Plot a 2D grid of hexagons, each hexagons being a note

    Keyword arguments:
    location -- the absolute path to the .csv file containing the data
    dataType -- the type of data that contains the file (default 'tpc')
        (tpc:[A, B#, Gbbb, ...], pc (pitch class):[0, 3, 7, ...])
    pitchClassDisplay -- if True display the pitch class and no the tpc values and so the grid repeat itself.
    duplicate -- it False avoid any repetition in the grid
    duration -- if True the values taking account is the duration and note the number of appearence
    log -- if True the colors are distributed on a log scale, by default it's a lineare scale (default False)
    colorbar -- if true display the colorbar in the background
    convertTable -- the conversion table from pitch class to tpc(F#, A, ...) format,
        the position indicate the pitch class value (default [C, Db, D, Eb, E, F, Gb, G, Ab, A, Bb, B])
    size -- define the number of layers of the hexagonal grid (default 3)
    hexSize -- indicate the size of the hexagons (default 1)
    textSize -- indicate the size of the typo for the labels (default 1)
    figSize -- indicate the size of the produced figure in inches (default 9)
    colorGeneral -- indicate the type of color to use for the heatmap, see matplotlib color documentation (default 'Blues')
    colorZeroValue -- give the possibility to set a color for the note that do not appear in the piece (default 'nan')
    centerNote -- you can set the note that will be in the center of the grid,
        by default it put the most recurent note in the center (default 'nan')
    """
    #===================================================================================
    #constant, parameter, variables
    #===================================================================================

    #settings
    convertTable = pd.Series(convertTable)
    df_data = musical_get_data_reduced(location, convertTable=convertTable, dataType=dataType)
    
    #constant
    HEXEDGE = math.sqrt(3)/2 #math constant

    #intern variables
    length = 0.05 * hexSize#radius and border length of the hexagons
    center = [0.5, 0.5] # set the center on the center of the map
    size_text = length * 200 * textSize # parameter fontsize
    pos = [0, 0, 0] #x, y, z
    pos_ser = (0, 0, 0) #for serching in the data
    a_centerNote = ['F', 0] # the centerNote that was define (note, sup)
    color_nb = 0
    color_text = 'Black' # by default
    show_hex = True

    #Normalize the numbers for colours
    if duration:
        max_val_tpc = df_data['duration'].max()
        min_val_tpc = df_data['duration'].min()
    else:
        max_val_tpc = df_data['nb'].max()
        min_val_tpc = df_data['nb'].min()
    if log:
        norm = matplotlib.colors.LogNorm(vmin=min_val_tpc, vmax=max_val_tpc)
    else:
        norm = matplotlib.colors.Normalize(vmin=min_val_tpc, vmax=max_val_tpc)

    found = False

    #define figure
    figsize = [figSize*1.5, figSize] #define the size if the figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, aspect='equal')
    
    
    #colormap for the layout
    cmap = matplotlib.cm.get_cmap(colorGeneral)

    #is the list of hexagon already define
    if pitchClassDisplay:
        columns = ['pos', 'note']
    else:
        columns = ['pos', 'note', 'sup']
    df_pos = pd.DataFrame(columns=columns)

    #give the notes'neighbours
    df_nei = pd.DataFrame.from_dict(get_dic_nei(pitchClassDisplay))

    #give the direction to look to for the nearest define hexagon
    x_list = [-1, 1, 0, 0, 1, -1]
    y_list = [1, -1, -1, 1, 0, 0]
    z_list = [0, 0, 1, -1, -1, 1]

    #===================================================================================
    #hexgrid
    #===================================================================================

    #do the first hexagon of the center
    #if not define it takes the most current note
    if(centerNote == 'nan'):
        #draw the hexagon
        p = patches.RegularPolygon(center, 6, radius=length, color=cmap(1/1))
        
        if pitchClassDisplay:
            ax.text(
                center[0],
                center[1],
                str(int(df_data['pc'][0])),
                color='white',
                horizontalalignment='center',
                verticalalignment='center',
                size=size_text)
            df_pos = df_pos.append(
                {'pos':(0,0,0), 'note':df_data['pc'][0]},
                ignore_index=True)
        else:
            ax.text(
                center[0],
                center[1],
                df_data['tpc'][0].replace('#', r'$\sharp$') \
                                .replace('b', r'$\flat$'),
                color='white',
                horizontalalignment='center',
                verticalalignment='center',
                size=size_text)
            df_pos = df_pos.append(
                {'pos':(0,0,0), 'note':df_data['tpc'][0], 'sup':df_data['sup'][0]},
                ignore_index=True)
        ax.add_patch(p)
        
    else: #read the given note and display it
        if pitchClassDisplay:
            df_pos = df_pos.append(
                {'pos':(0,0,0), 'note':centerNote},
                ignore_index=True)
        else:
            a_centerNote[0] = get_step(centerNote)
            a_centerNote[1] = get_acc(centerNote)
            df_pos = df_pos.append(
                {'pos':(0,0,0), 'note':a_centerNote[0], 'sup':a_centerNote[1]},
                ignore_index=True)
        
        #set the color
        color = cmap(0)
        found = False
        color_nb = 0
        for l in range(df_data.shape[0]):
            if pitchClassDisplay:
                if str(int(df_data.at[l, 'pc'])) == str(centerNote):
                    if duration:
                        color = cmap(norm(df_data.at[l, 'duration']))
                        color_nb = norm(df_data.at[l, 'duration'])
                    else:
                        color = cmap(norm(df_data.at[l, 'nb']))
                        color_nb = norm(df_data.at[l, 'nb'])
                    found = True
            else:
                if df_data.at[l, 'tpc'] == a_centerNote[0] and df_data.at[l, 'sup'] == a_centerNote[1]:
                    if duration:
                        color = cmap(norm(df_data.at[l, 'duration']))
                        color_nb = norm(df_data.at[l, 'duration'])
                    else:
                        color = cmap(norm(df_data.at[l, 'nb']))
                        color_nb = norm(df_data.at[l, 'nb'])
                    found = True
                    
        if found == False and colorZeroValue != 'nan':
            color = colorZeroValue

        #define the color af the label in function of the color of the hexagon
        if color_nb > 0.6:
            color_text = 'White'
        else:
            color_text = 'Black'
            
        if pitchClassDisplay == False:
            a_centerNote[0] = put_flat_sharp(a_centerNote[0], a_centerNote[1])

        #draw and add labels
        p = patches.RegularPolygon(
            center,
            6,
            radius=length,
            facecolor=color,
            edgecolor='Black')
        if pitchClassDisplay:
            ax.text(
                center[0],
                center[1],
                str(int(centerNote)),
                color=color_text,
                horizontalalignment='center',
                verticalalignment='center',
                size=size_text)
        else:
            ax.text(
                center[0],
                center[1],
                a_centerNote[0].replace('#', r'$\sharp$') \
                               .replace('b', r'$\flat$'),
                color=color_text,
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

                    if pitchClassDisplay == False:
                        current_sup = df_pos[select_data].iat[0, 2]

                    #get df for the note of reference from df_nei
                    df_nei_gr = df_nei.groupby('ref').get_group(df_pos[select_data].iat[0, 1])

                    #select the name of the note from the hexagone
                    select_data = df_nei_gr['pos'] == pos_ser_n

                    #register the hex in function of the type of value
                    if pitchClassDisplay:
                        current_note = df_nei_gr[select_data].iat[0, 2]
                        df_pos = df_pos.append(
                            {'pos':(pos[0], pos[1], pos[2]),
                                'note':current_note},
                            ignore_index=True)
                    else:
                        current_note = df_nei_gr[select_data].iat[0, 2]
                        current_sup = current_sup + df_nei_gr[select_data].iat[0, 3]
                        df_pos = df_pos.append(
                            {'pos':(pos[0], pos[1], pos[2]),
                                'note':current_note,
                                'sup':current_sup},
                            ignore_index=True)
                        
                    #set the facecolor of the hex
                    color = cmap(0)
                    color_nb = 0
                    found = False
                    for l in range(df_data.shape[0]):
                        if pitchClassDisplay:
                            #check if he finds the note in the data and get its value for color
                            if str(int(df_data.at[l, 'pc'])) == str(current_note):
                                if duration:
                                    color = cmap(norm(df_data.at[l, 'duration']))
                                    color_nb = norm(df_data.at[l, 'duration'])
                                else:
                                    color = cmap(norm(df_data.at[l, 'nb']))
                                    color_nb = norm(df_data.at[l, 'nb'])
                                found = True
                        else:
                            if df_data.at[l, 'tpc'] == current_note and df_data.at[l, 'sup'] == current_sup:
                                if duration:
                                    color = cmap(norm(df_data.at[l, 'duration']))
                                    color_nb = norm(df_data.at[l, 'duration'])
                                else:
                                    color = cmap(norm(df_data.at[l, 'nb']))
                                    color_nb = norm(df_data.at[l, 'nb'])
                                found = True
                                
                    if found == False and colorZeroValue != 'nan':
                        color = colorZeroValue

                    #define the color af the label in function of the color of the hexagon
                    if color_nb > 0.6:
                        color_text = 'White'
                    else:
                        color_text = 'Black'

                    if pitchClassDisplay == False:
                        current_note = put_flat_sharp(current_note, current_sup)

                    #calcul the center position of the hex in function of the coordonnate
                    center = [0.5 + pos[0] * HEXEDGE * length - pos[1] * HEXEDGE * length,
                              0.5 + pos[0] * length / 2 + pos[1] * length / 2 - pos[2] * length]

                    show_hex = True

                    #if no duplicate then check if the note is already displaye
                    if duplicate == False:
                        for l in range(df_pos.shape[0] - 1):
                            if pitchClassDisplay:
                                if df_pos.at[l, 'note'] == df_pos.at[df_pos.shape[0] - 1, 'note']:
                                    show_hex = False
                            else:
                                if df_pos.at[l, 'note'] == df_pos.at[df_pos.shape[0] - 1, 'note'] and\
                                   df_pos.at[l, 'sup'] == df_pos.at[df_pos.shape[0] - 1, 'sup']:
                                    show_hex = False

                    #draw
                    if show_hex:
                        p = patches.RegularPolygon(
                            center,
                            6,
                            radius=length,
                            facecolor=color,
                            edgecolor='Black')
                        if pitchClassDisplay:
                            ax.text(
                                center[0],
                                center[1],
                                str(int(current_note)),
                                color=color_text,
                                horizontalalignment='center',
                                verticalalignment='center',
                                size=size_text)
                        else:
                            ax.text(
                                center[0],
                                center[1],
                                current_note.replace('#', r'$\sharp$') \
                                            .replace('b', r'$\flat$'),
                                color=color_text,
                                horizontalalignment='center',
                                verticalalignment='center',
                                size=size_text)
                        ax.add_patch(p)
    
    #display a colorbar if asked
    if colorbar:
        ax2 = fig.add_subplot(1, 10, 1)
        cb1 = matplotlib.colorbar.ColorbarBase(ax2, cmap=cmap,
                                        norm=norm,
                                        orientation='vertical')

    #display off the axis
    ax.axis('off')
    
    plt.show()
