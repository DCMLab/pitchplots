import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib
import math
from pitchplots.reader import get_df_short
from pitchplots.functions import get_acc, get_step, get_pc, get_dic_nei, put_flat_sharp, get_fifth_nb, get_fifth_note

def pie_chart(
    location,
    data_type='tpc',
    log=False,
    convert_table=['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'],
    pitch_class_display=False,
    colorbar=True,
    duration=False,
    fifth=True,
    figure_size=9,
    top_note='nan',
    rotation=0,
    clockwise=True,
    cmap='Blues',
    color_zero_value='nan'):
    """return the figure of a piechart with importance of the notes that are represented by the colour as a heatmap

    Keyword arguments:
    location -- the absolute path to the .csv file containing the data
    data_type -- the type of data that contains the file (default 'tpc'), 'pc' could be use for twelve parts chart tpc form
        (tpc:[A, B#, Gbbb, ...], pc (pitch class):[0, 3, 7, ...])
    log -- if True the colors are distributed on a log scale, by default it's a lineare scale (default False)
    convert_table -- the conversion table from pitch class to tpc(F#, A, ...) format,
        the position indicate the pitch class value (default [C, Db, D, Eb, E, F, Gb, G, Ab, A, Bb, B])
    pitch_class_display -- if True display the pitch class and no the tpc values and so the grid repeat itself.
    colorbar -- if true display the colorbar aside of the pie chart
    duration -- tell him if he has to class the importance by the total duration of the note or by the number of appearence.
    fifth -- if True class the notes by fifth order, if not class by the chromatic order
    figure_size -- tell the size of the figure in inches
    top_note -- tell whiche note should be on the top of the piechart, different for tpc or pc
    rotation -- allows to rotate the piechart, int angle in degres
    clockwise -- if True the piechart is displayed clockwise if not counter-clockwise
    cmap -- indicate the type of color to use for the heatmap, see matplotlib color documentation (default 'Blues')
    color_zero_value -- give the possibility to set a color for the note that do not appear in the piece (default 'nan')
    """
    #settings
    convert_table = pd.Series(convert_table)
    df = get_df_short(location, convert_table=convert_table, data_type=data_type)

    #color map
    cmap = matplotlib.cm.get_cmap(cmap)
    color_note = []

    #dataFrame for the plot if tpc
    df_tpc_pie = pd.DataFrame(columns=['note', 'part', 'pc'])

    #remember position of data in Series
    s_pos = pd.Series()
    count = 0
    part = 0
    letter = 'nan'
    s_fifth = pd.Series()

    figure_size = [figure_size*1.5, figure_size] #define the size if the figure
    fig = plt.figure(figure_size=figure_size)
    ax = fig.add_subplot(111, aspect='equal')

    #Set the order in function of fifth
    if fifth:
        s_tpc_format = pd.Series((0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5))
    else:
        s_tpc_format = pd.Series((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11))

    #for plot if pitch_class_display
    s_twelve_ones = pd.Series((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), index=s_tpc_format)

    #if it show the tpc values
    if pitch_class_display == False:
        #put the right values in 'number'
        if duration:
            df_data = df.copy()
            del df_data['nb']
            df_data.rename(columns={'duration': 'number'},inplace=True)
        else:
            df_data = df.copy()
            del df_data['duration']
            df_data.rename(columns={'nb': 'number'},inplace=True)

        #Normalize the values for the colors
        max_value = df_data['number'].max()
        min_value = df_data['number'].min()
        if log:
            norm = matplotlib.colors.LogNorm(vmin=min_value, vmax=max_value)
        else:
            norm = matplotlib.colors.Normalize(0, vmax=max_value)
        
        #for chromatic order
        if fifth == False:

            #for each pitch class values
            for i in range(12):

                #if a pitch class is represented in the data
                if df_data['pc'].isin([s_tpc_format[i]]).any():
                    count = 0
                    s_pos.drop(s_pos.index, inplace=True)
                    
                    #count how much time there is tpc values for a same pitch class
                    for j in range(df_data['pc'].isin([s_tpc_format[i]]).shape[0]):
                       if df_data['pc'].isin([s_tpc_format[i]])[j]:
                           s_pos.at[count] = j
                           count = count + 1

                    #devide the pie part and set color
                    for j in range(count):
                        part = 1/count
                        letter = df_data.at[s_pos.at[j], 'tpc']

                        #write the notes
                        letter = put_flat_sharp(letter, df_data.at[s_pos.at[j], 'sup'])

                        #register the informations
                        df_tpc_pie = df_tpc_pie.append({'note':letter, 'part':part},
                                                       ignore_index=True)
                        color_note.append(cmap(norm(df_data.at[s_pos.at[j], 'number'])))

                #if the pitch class do no appear in the piece
                else:
                    letter = convert_table[s_tpc_format[i]]

                    df_tpc_pie = df_tpc_pie.append({'note':letter, 'part':1}, ignore_index=True)
                    if color_zero_value == 'nan':
                        color_note.append(cmap(0))
                    else:
                        color_note.append(color_zero_value)
        else:
            #get the fifth numbers of the notes
            for i in range(df_data.shape[0]):
                s_fifth.at[i] = get_fifth_nb(df_data.at[i, 'tpc'], df_data.at[i, 'sup'])
            df_data['fifth'] = s_fifth

            #create df_tpc_pie and get the colours
            for i in range(df_data['fifth'].max()-df_data['fifth'].min()+1):
                #the part are equal for the moment
                df_tpc_pie.at[i, 'part'] = 1
                df_tpc_pie.at[i, 'note'] = get_fifth_note(i + df_data['fifth'].min())
                df_tpc_pie.at[i, 'pc'] = get_pc(df_tpc_pie.at[i, 'note'])
                
                if df_data['fifth'].isin([i + df_data['fifth'].min()]).any():
                    #get the colour for the note who has the good fifth number
                    color_note.append(cmap(norm(df_data['number'][df_data['fifth']==(i + df_data['fifth'].min())].iat[0])))
                elif df_data['fifth'].isin([i + df_data['fifth'].min()]).any() == False and color_zero_value != 'nan':
                    color_note.append(color_zero_value)
                else:
                    color_note.append(cmap(0))

        #if clockwise invert the order of the data to be displayed clockwise, inverse also the index
        if clockwise:
            df_tpc_pie = df_tpc_pie.iloc[::-1]
            color_note = list(reversed(color_note))

        #calculate the angle for the topPitchClass to be at the top
        if top_note != 'nan' and fifth == False and df_tpc_pie['note'].isin([top_note]).any() == True:
            if clockwise:
                rotation = rotation + 90 + df_tpc_pie.at[0, 'part'] * 15
            else:
                rotation = rotation + 90 - df_tpc_pie.at[0, 'part'] * 15
            for i in range(df_tpc_pie.shape[0]):
                if top_note == df_tpc_pie.at[i, 'note']:
                    if df_tpc_pie.at[i, 'part'] != 1:
                        if clockwise:
                            rotation = rotation - 15*df_tpc_pie.at[i, 'part']
                        else:
                            rotation = rotation + 15*df_tpc_pie.at[i, 'part']
                    break
                else:
                    if clockwise:
                        rotation = rotation + 30*df_tpc_pie.at[i, 'part']
                    else:
                        rotation = rotation - 30*df_tpc_pie.at[i, 'part']

        #put the top note at the top
        if top_note != 'nan' and fifth == True and df_tpc_pie['note'].isin([top_note]).any() == True:
            if clockwise:
                rotation = rotation + 90 + 180/df_tpc_pie.shape[0]
            else:
                rotation = rotation  + 90 - 180/df_tpc_pie.shape[0]
            for i in range (df_tpc_pie.shape[0]):
                if df_tpc_pie.at[i, 'note'] == top_note:
                    break
                else:
                    #the sens of reading depend on the orientation
                    if clockwise:
                        rotation = rotation + 360/df_tpc_pie.shape[0]
                    else:
                        rotation = rotation - 360/df_tpc_pie.shape[0]
                

        #put nice sharps and flats
        for i in range(df_tpc_pie.shape[0]):
            df_tpc_pie.at[i, 'note'] = df_tpc_pie.at[i, 'note'].replace('b', r'$\flat$')\
                                                               .replace('#', r'$\sharp$')
            
        #plot the piechart with index 'tpc'
        df_tpc_pie.index = df_tpc_pie['note']
        
        #do the pie chart
        ax.pie(labels=df_tpc_pie.index, x=df_tpc_pie['part'], colors=color_note, startangle=rotation)

        #if asked plot the colorbar left of the piechart
        if colorbar:
            ax2 = fig.add_subplot(1, 10, 1)
            cb1 = matplotlib.colorbar.ColorbarBase(ax2, cmap=cmap, norm=norm, orientation='vertical')
            
    #display with the pc values
    else:
        #put the right values in 'number'
        if duration:
            df_data = pd.concat(
                [df['pc'], df['duration']],
                axis=1,
                keys=['pc', 'number'])
        else:
            df_data = pd.concat(
                [df['pc'], df['nb']],
                axis=1,
                keys=['pc', 'number'])

        #Normalize the values for the colors
        max_value = df_data['number'].max()
        min_value = df_data['number'].min()
        if log:
            norm = matplotlib.colors.LogNorm(vmin=min_value, vmax=max_value)
        else:
            norm = matplotlib.colors.Normalize(0, vmax=max_value)
        
        #set data df_data
        df_data = (df_data.groupby('pc')).sum()
        df_data = df_data.reindex(s_tpc_format)
        df_data.fillna(0, inplace=True)

        #set colors
        for i in range(0, 12):
            if df_data.iat[i, 0] != 0:
                color_note.append(cmap(norm(df_data.iat[i, 0])))
            else:
                if color_zero_value == 'nan':
                    color_note.append(cmap(0))
                else:
                    color_note.append(color_zero_value)

        #if clockwise invert the order of the data to be displayed clockwise
        if clockwise:
            s_twelve_ones = s_twelve_ones.iloc[::-1]
            color_note = list(reversed(color_note))

        #calculate the angle for the topPitchClass to be at the top
        if top_note != 'nan':
            for i in range(s_tpc_format.shape[0]):
                if top_note == (s_twelve_ones.index)[i]:
                    rotation = rotation + 75 - i * 30
                    break

        ax.pie(labels=s_twelve_ones.index, x=s_twelve_ones, colors=color_note, startangle=rotation)

        #if asked plot the colorbar left of the piechart
        if colorbar:
            ax2 = fig.add_subplot(1, 10, 1)
            cb1 = matplotlib.colorbar.ColorbarBase(ax2, cmap=cmap, norm=norm, orientation='vertical')
        
    return fig

#=====================================================================================================
#hex
#=====================================================================================================
def hexagonal_chart(
    location,
    data_type='tpc',
    pitch_class_display=False,
    duplicate=True,
    duration=False,
    log=False,
    colorbar=True,
    convert_table=['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'],
    size=3,
    hex_size=1,
    text_size=1,
    figure_size=9,
    cmap='Blues',
    color_zero_value='nan',
    center_note='nan'):
    """return the figure of a 2D grid of hexagons, each hexagons being a note

    Keyword arguments:
    location -- the absolute path to the .csv file containing the data
    data_type -- the type of data that contains the file (default 'tpc')
        (tpc:[A, B#, Gbbb, ...], pc (pitch class):[0, 3, 7, ...])
    pitch_class_display -- if True display the pitch class and not the tpc values and so the grid repeat itself.
    duplicate -- it False avoid any repetition in the grid
    duration -- if True the values taking account is the duration and note the number of appearence
    log -- if True the colors are distributed on a log scale, by default it's a lineare scale (default False)
    colorbar -- if true display the colorbar in the background
    convert_table -- the conversion table from pitch class to tpc(F#, A, ...) format,
        the position indicate the pitch class value (default [C, Db, D, Eb, E, F, Gb, G, Ab, A, Bb, B])
    size -- define the number of layers of the hexagonal grid (default 3)
    hex_size -- indicate the size of the hexagons (default 1)
    text_size -- indicate the size of the typo for the labels (default 1)
    figure_size -- indicate the size of the produced figure in inches (default 9)
    cmap -- indicate the type of color to use for the heatmap, see matplotlib color documentation (default 'Blues')
    color_zero_value -- give the possibility to set a color for the note that do not appear in the piece (default 'nan')
    center_note -- you can set the note that will be in the center of the grid,
        by default it put the most recurent note in the center (default 'nan')
    """
    #===================================================================================
    #constant, parameter, variables
    #===================================================================================

    #settings
    convert_table = pd.Series(convert_table)
    df_data = get_df_short(location, convert_table=convert_table, data_type=data_type)
    
    #constant
    HEXEDGE = math.sqrt(3)/2 #math constant

    #intern variables
    length = 0.05 * hex_size#radius and border length of the hexagons
    center = [0.5, 0.5] # set the center on the center of the map
    size_text = length * 200 * text_size # parameter fontsize
    pos = [0, 0, 0] #x, y, z
    pos_ser = (0, 0, 0) #for serching in the data
    a_center_note = ['F', 0] # the center_note that was define (note, sup)
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
    figure_size = [figure_size*1.5, figure_size] #define the size if the figure
    fig = plt.figure(figure_size=figure_size)
    ax = fig.add_subplot(111, aspect='equal')
    
    
    #colormap for the layout
    cmap = matplotlib.cm.get_cmap(cmap)

    #is the list of hexagon already define
    if pitch_class_display:
        columns = ['pos', 'note']
    else:
        columns = ['pos', 'note', 'sup']
    df_pos = pd.DataFrame(columns=columns)

    #give the notes'neighbours
    df_nei = pd.DataFrame.from_dict(get_dic_nei(pitch_class_display))

    #give the direction to look to for the nearest define hexagon
    x_list = [-1, 1, 0, 0, 1, -1]
    y_list = [1, -1, -1, 1, 0, 0]
    z_list = [0, 0, 1, -1, -1, 1]

    #===================================================================================
    #hexgrid
    #===================================================================================

    #do the first hexagon of the center
    #if not define it takes the most current note
    if(center_note == 'nan'):
        #draw the hexagon
        p = patches.RegularPolygon(center, 6, radius=length, color=cmap(1/1))
        
        if pitch_class_display:
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
                put_flat_sharp(df_data['tpc'][0], df_data['sup'][0]).replace('#', r'$\sharp$') \
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
        if pitch_class_display:
            df_pos = df_pos.append(
                {'pos':(0,0,0), 'note':center_note},
                ignore_index=True)
        else:
            a_center_note[0] = get_step(center_note)
            a_center_note[1] = get_acc(center_note)
            df_pos = df_pos.append(
                {'pos':(0,0,0), 'note':a_center_note[0], 'sup':a_center_note[1]},
                ignore_index=True)
        
        #set the color
        color = cmap(0)
        found = False
        color_nb = 0
        for l in range(df_data.shape[0]):
            if pitch_class_display:
                if str(int(df_data.at[l, 'pc'])) == str(center_note):
                    if duration:
                        color = cmap(norm(df_data.at[l, 'duration']))
                        color_nb = norm(df_data.at[l, 'duration'])
                    else:
                        color = cmap(norm(df_data.at[l, 'nb']))
                        color_nb = norm(df_data.at[l, 'nb'])
                    found = True
            else:
                if df_data.at[l, 'tpc'] == a_center_note[0] and df_data.at[l, 'sup'] == a_center_note[1]:
                    if duration:
                        color = cmap(norm(df_data.at[l, 'duration']))
                        color_nb = norm(df_data.at[l, 'duration'])
                    else:
                        color = cmap(norm(df_data.at[l, 'nb']))
                        color_nb = norm(df_data.at[l, 'nb'])
                    found = True
                    
        if found == False and color_zero_value != 'nan':
            color = color_zero_value

        #define the color af the label in function of the color of the hexagon
        if color_nb > 0.6:
            color_text = 'White'
        else:
            color_text = 'Black'
            
        if pitch_class_display == False:
            a_center_note[0] = put_flat_sharp(a_center_note[0], a_center_note[1])

        #draw and add labels
        p = patches.RegularPolygon(
            center,
            6,
            radius=length,
            facecolor=color,
            edgecolor='Black')
        if pitch_class_display:
            ax.text(
                center[0],
                center[1],
                str(int(center_note)),
                color=color_text,
                horizontalalignment='center',
                verticalalignment='center',
                size=size_text)
        else:
            ax.text(
                center[0],
                center[1],
                a_center_note[0].replace('#', r'$\sharp$') \
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

                    if pitch_class_display == False:
                        current_sup = df_pos[select_data].iat[0, 2]

                    #get df for the note of reference from df_nei
                    df_nei_gr = df_nei.groupby('ref').get_group(df_pos[select_data].iat[0, 1])

                    #select the name of the note from the hexagone
                    select_data = df_nei_gr['pos'] == pos_ser_n

                    #register the hex in function of the type of value
                    if pitch_class_display:
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
                        if pitch_class_display:
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
                                
                    if found == False and color_zero_value != 'nan':
                        color = color_zero_value

                    #define the color af the label in function of the color of the hexagon
                    if color_nb > 0.6:
                        color_text = 'White'
                    else:
                        color_text = 'Black'

                    if pitch_class_display == False:
                        current_note = put_flat_sharp(current_note, current_sup)

                    #calcul the center position of the hex in function of the coordonnate
                    center = [0.5 + pos[0] * HEXEDGE * length - pos[1] * HEXEDGE * length,
                              0.5 + pos[0] * length / 2 + pos[1] * length / 2 - pos[2] * length]

                    show_hex = True

                    #if no duplicate then check if the note is already displaye
                    if duplicate == False:
                        for l in range(df_pos.shape[0] - 1):
                            if pitch_class_display:
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
                        if pitch_class_display:
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
    
    return fig