"""
Functions for none moving charts
"""
import math

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib

from pitchplots.reader import get_df_short
from pitchplots.functions import get_acc, get_step, get_pc, get_dic_nei, put_flat_sharp, get_fifth_nb, get_fifth_note, is_tpc, is_pc

class StaticError(Exception):
    """Exception thrown when the static module cannot plot."""
    pass

class InvalidDataTypeTypeError(StaticError):
    """Exception thrown when pitch_type is not pc or tpc"""
    pass

class InvalidSetMeasureTypeError(StaticError):
    """Exception thrown when set_measure is not a list of 2 numbers with the first and last measures to take in count"""
    pass

class InvalidConvertTableTypeError(StaticError):
    """Exception thrown when vocabulary does not have 12 elements or its elements are not tpc notes"""
    pass

def line(
    piece,
    pitch_type='tpc',
    measures=None,
    log=False,
    normalize=False,
    vocabulary={0:'C', 1:'Db', 2:'D', 3:'Eb', 4:'E', 5:'F', 6:'Gb', 7:'G', 8:'Ab', 9:'A', 10:'Bb', 11:'B'},
    pitch_class_display=False,
    duration=False,
    color='blue',
    figsize=[6, 4],
    xmin=None,
    xmax=None,
    start=0,
    show=False,
    **kwargs):
    """return the figure of a linechart with the notes in the X axis and their value in the Y axis

    Keyword arguments:
    piece -- the absolute path to the .csv file containing the data or a DataFrame
    pitch_type -- the type of data that you want to be read (default 'tpc'), 'pc' could be use for twelve parts chart tpc form
        (tpc:[A, B#, Gbbb, ...], pc (pitch class):[0, 3, 7, ...])
    measures -- give a set of measures example [5, 18], will display the notes of the measures 5 to 18 included
    log -- if True the colors are distributed on a log scale, by default it's a lineare scale (default False)
    vocabulary -- the conversion dictionary from pitch class to tpc(F#, A, ...) format,
    pitch_class_display -- if True display the pitch class and no the tpc values and so the grid repeat itself.
    duration -- tell him if he has to class the notes by their total duration or their number of appearance
    figsize -- tell the size of the figure in inches [x, y]
    xmin, xmax -- the notes that will be displayed are in this range according to this values
        {0 : F, 1 : C, 2 : G, 3 : D, 4 : A, 5 : E, 6 : B} and +- 7 for a sharp and a flat
    display -- if True the figure is displayed, if False it is hidden so you can have only the returned figure
    **kwargs -- these arguments are redirected to the matplotlib.pyplot.pie function, see informations at
                https://matplotlib.org/api/_as_gen/matplotlib.pyplot.bar.html
    """
    #get the df
    if pitch_class_display:
        df = get_df_short(piece, vocabulary=vocabulary, pitch_type='pc', measures=measures)
    else:
        df = get_df_short(piece, vocabulary=vocabulary, pitch_type=pitch_type, measures=measures)
    #create the figure and close it so it wont be display
    fig = plt.figure(figsize=figsize)
    if not show:
        plt.close(fig)
    ax = fig.add_subplot(111)
    
    if not pitch_class_display:
        df['fifth_number'] = df['tpc'].apply(get_fifth_nb)
        xmin = df['fifth_number'].min() if xmin == None else xmin+1
        xmax = df['fifth_number'].max() if xmax == None else xmax+1
        labels = [get_fifth_note(i) for i in range(xmin, xmax+1)]
    # Give the value to the notes, for their number of appearance
    if normalize:
        s = pd.Series(df['duration']/df['duration'].sum()) if duration else pd.Series(df['nb']/df['nb'].sum())
    else:
        s = pd.Series(df['duration']) if duration else pd.Series(df['nb'])
    s.index = df['pc'] if pitch_class_display else df['tpc']
    if pitch_class_display:
        #reindex with integers to be compatible with the 'pc' value
        pc_labels = np.roll([0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5],
                            -([0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5].index(start)))
        s = s.reindex(pc_labels).fillna(0)
        #get the index in strings so it wont be reorder by the bar function
        s.index = np.roll(['0', '7', '2', '9', '4', '11', '6', '1', '8', '3', '10', '5'],
                          -([0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5].index(start)))
    else:
        s = s.reindex(labels).fillna(0)
    # Do the bar plot
    ax.bar(x=s.index, color=color, height = s.values, log=log, **kwargs)
    
    return fig
    
def circle(
    piece,
    pitch_type='tpc',
    measures=None, # need documentation
    log=False,
    vocabulary={0:'C', 1:'Db', 2:'D', 3:'Eb', 4:'E', 5:'F', 6:'Gb', 7:'G', 8:'Ab', 9:'A', 10:'Bb', 11:'B'},
    pitch_class_display=False,
    colorbar=True,
    duration=False,
    fifths=True,
    figsize=[7, 4],
    top=None,
    rotation=0,
    clockwise=True,
    cmap='Blues',
    nan_color=None,
    show=False,
    **kwargs):
    """return the figure of a piechart with importance of the notes that are represented by the colour as a heatmap

    Keyword arguments:
    piece -- the absolute path to the .csv file containing the data or a DataFrame
    pitch_type -- the type of data that you want to be read (default 'tpc'), 'pc' could be use for twelve parts chart tpc form
        (tpc:[A, B#, Gbbb, ...], pc (pitch class):[0, 3, 7, ...])
    measures -- give a set of measures example [5, 18], will display the notes of the measures 5 to 18 included
    log -- if True the colors are distributed on a log scale, by default it's a lineare scale (default False)
    vocabulary -- the conversion dictionary from pitch class to tpc(F#, A, ...) format,
    pitch_class_display -- if True display the pitch class and no the tpc values and so the grid repeat itself.
    colorbar -- if true display the colorbar aside of the pie chart
    duration -- tell him if he has to class the notes by their total duration or their number of appearance
    fifths -- if True class the notes by fifths order, if not class by the chromatic order
    figsize -- tell the size of the figure in inches [x, y]
    top -- tell which note should be on the top of the piechart, different for tpc or pc
    rotation -- allows to rotate the piechart, int angle in degrees
    clockwise -- if True the piechart is displayed clockwise if not counter-clockwise
    cmap -- indicate the type of color to use for the heatmap, see matplotlib color documentation (default 'Blues')
    nan_color -- give the possibility to set a color for the note that do not appear in the piece (default 'nan')
    display -- if True the figure is displayed, if False it is hidden so you can have only the returned figure
    **kwargs -- these arguments are redirected to the matplotlib.pyplot.pie function, see informations at
                https://matplotlib.org/api/_as_gen/matplotlib.pyplot.pie.html
    """
    #settings
    df = get_df_short(piece, vocabulary=vocabulary, pitch_type=pitch_type, measures=measures, duration=duration)

    #color map
    cmap = matplotlib.cm.get_cmap(cmap)
    color_note = []

    #dataFrame for the plot if tpc
    df_tpc_pie = pd.DataFrame(columns=['note', 'part', 'pc'])

    #put top in the right form
    if pd.isnull(top) == False:
        if is_tpc(top) and pitch_class_display:
            top = get_pc(top)
        if is_pc(top) and not pitch_class_display:
            top = vocabulary[int(top)]

    #remember position of data in Series
    s_pos = pd.Series()
    count = 0
    part = 0
    letter = 'nan'
    s_fifth = pd.Series()
    
    fig = plt.figure(figsize=figsize)
    if not show:
        plt.close(fig)
    ax = fig.add_subplot(111, aspect='equal')
    
    #Set the order in function of fifth
    if fifths:
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
            df_data.rename(columns={'duration': 'number'},inplace=True)
        else:
            df_data = df.copy()
            df_data.rename(columns={'nb': 'number'},inplace=True)

        #Normalize the values for the colors
        max_value = df_data['number'].max()
        min_value = df_data['number'].min()
        if log:
            norm = matplotlib.colors.LogNorm(vmin=min_value, vmax=max_value)
        else:
            norm = matplotlib.colors.Normalize(0, vmax=max_value)
        
        #for chromatic order
        if fifths == False:

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
                        letter = df_data.at[s_pos.at[j], 'step']

                        #write the notes
                        letter = put_flat_sharp(letter, df_data.at[s_pos.at[j], 'acc'])

                        #register the informations
                        df_tpc_pie = df_tpc_pie.append({'note':letter, 'part':part},
                                                       ignore_index=True)
                        color_note.append(cmap(norm(df_data.at[s_pos.at[j], 'number'])))

                #if the pitch class do no appear in the piece
                else:
                    letter = vocabulary[s_tpc_format[i]]

                    df_tpc_pie = df_tpc_pie.append({'note':letter, 'part':1}, ignore_index=True)
                    if pd.isnull(nan_color):
                        color_note.append(cmap(0))
                    else:
                        color_note.append(nan_color)
        else:
            #get the fifth numbers of the notes
            for i in range(df_data.shape[0]):
                s_fifth.at[i] = get_fifth_nb(df_data.at[i, 'tpc'])
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
                elif df_data['fifth'].isin([i + df_data['fifth'].min()]).any() == False and pd.isnull(nan_color) == False:
                    color_note.append(nan_color)
                else:
                    color_note.append(cmap(0))

        #if clockwise invert the order of the data to be displayed clockwise, inverse also the index
        if clockwise:
            df_tpc_pie = df_tpc_pie.iloc[::-1]
            color_note = list(reversed(color_note))

        #calculate the angle for the topPitchClass to be at the top
        if pd.isnull(top) == False and fifths == False and df_tpc_pie['note'].isin([top]).any() == True:
            if clockwise:
                rotation = rotation + 90 + df_tpc_pie.at[0, 'part'] * 15
            else:
                rotation = rotation + 90 - df_tpc_pie.at[0, 'part'] * 15
            for i in range(df_tpc_pie.shape[0]):
                if top == df_tpc_pie.at[i, 'note']:
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
        if pd.isnull(top) == False and fifths == True and df_tpc_pie['note'].isin([top]).any() == True:
            if clockwise:
                rotation = rotation + 90 + 180/df_tpc_pie.shape[0]
            else:
                rotation = rotation  + 90 - 180/df_tpc_pie.shape[0]
            for i in range (df_tpc_pie.shape[0]):
                if df_tpc_pie.at[i, 'note'] == top:
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
        ax.pie(labels=df_tpc_pie.index, x=df_tpc_pie['part'], colors=color_note, startangle=rotation, **kwargs)

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
                if pd.isnull(nan_color):
                    color_note.append(cmap(0))
                else:
                    color_note.append(nan_color)

        #if clockwise invert the order of the data to be displayed clockwise
        if clockwise:
            s_twelve_ones = s_twelve_ones.iloc[::-1]
            color_note = list(reversed(color_note))

        #calculate the angle for the topPitchClass to be at the top
        if pd.isnull(top) == False:
            for i in range(s_tpc_format.shape[0]):
                if top == (s_twelve_ones.index)[i]:
                    rotation = rotation + 75 - i * 30
                    break
        ax.pie(labels=s_twelve_ones.index, x=s_twelve_ones, colors=color_note, startangle=rotation, **kwargs)

        #if asked plot the colorbar left of the piechart
        if colorbar:
            ax2 = fig.add_subplot(1, 10, 1)
            cb1 = matplotlib.colorbar.ColorbarBase(ax2, cmap=cmap, norm=norm, orientation='vertical')
    return fig


def tonnetz(
    piece,
    pitch_type='tpc',
    measures=None,
    pitch_class_display=False,
    duplicate=True,
    duration=False,
    log=False,
    colorbar=True,
    vocabulary={0:'C', 1:'Db', 2:'D', 3:'Eb', 4:'E', 5:'F', 6:'Gb', 7:'G', 8:'Ab', 9:'A', 10:'Bb', 11:'B'},
    radius=3,
    hex_size=1,
    fontsize=1,
    figsize=[7, 4],
    cmap='Blues',
    nan_color=None,
    edgecolor=None,
    center=None,
    show=False, # CHANGE IT TO SHOW
    **kwargs):
    """return the figure of a 2D grid of hexagons, each hexagons being a note

    Keyword arguments:
    piece -- the absolute path to the .csv file containing the data or a DataFrame
    pitch_type -- the type of data that you want to be read (default 'tpc'), 'pc' could be use for twelve parts chart tpc form
        (tpc:[A, B#, Gbbb, ...], pc (pitch class):[0, 3, 7, ...])
    measures -- give a set of measures example [5, 18], will display the notes of the measures 5 to 18 included
    pitch_class_display -- if True display the pitch class and not the tpc values and so the grid repeat itself.
    duplicate -- it False avoid any repetition of the notes in the grid
    duration -- if True the values taking account is the duration and not the number of appearence
    log -- if True the colors are distributed on a log scale, by default it's a lineare scale (default False)
    colorbar -- if true display the colorbar aside of the chart
    vocabulary -- the conversion dictionary from pitch class to tpc(F#, A, ...) format,
    radius -- define the number of layers of the hexagonal grid (default 3)
    hex_size -- indicate the size of the hexagons (default 1)
    fontsize -- indicate the size of the typo for the labels (default 1)
    figsize -- tell the size of the figure in inches [x, y]
    cmap -- indicate the type of color to use for the heatmap, see matplotlib color documentation (default 'Blues')
    nan_color -- give the possibility to set a color for the note that do not appear in the piece (default None)
    center -- you can set the note that will be in the center of the grid,
        by default it put the most recurent note in the center (default None)
    display -- if True the figure is displayed, if False it is hidden so you can have only the returned figure
    **kwargs -- these arguments are redirected to matplotlib.patches.RegularPolygon, see informations at
                https://matplotlib.org/api/_as_gen/matplotlib.patches.RegularPolygon.html
    """
    #===================================================================================
    #constant, parameter, variables
    #===================================================================================

    #settings
    df_data = get_df_short(piece, vocabulary=vocabulary, pitch_type=pitch_type, measures=measures, duration=duration)
    
    #constant
    HEXEDGE = math.sqrt(3)/2 #math constant

    #intern variables
    length = 0.05 * hex_size * 1.5 * 3 / radius#radius and border length of the hexagons
    center_pos = [0.5, 0.5] # set the center on the center of the map
    size_text = length * 150 * fontsize # parameter fontsize
    pos = [0, 0, 0] #x, y, z
    pos_ser = (0, 0, 0) #for serching in the data
    a_center = ['F', 0] # the center that was define (note, sup)
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
    fig = plt.figure(figsize=figsize)
    if not show:
        plt.close(fig)
    ax = fig.add_subplot(111, aspect='equal')
    
    
    #colormap for the layout
    cmap = matplotlib.cm.get_cmap(cmap)

    #is the list of hexagon already define
    if pitch_class_display:
        columns = ['pos', 'note']
    else:
        columns = ['pos', 'note', 'acc']
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
    if pd.isnull(center):
        #draw the hexagon
        p = patches.RegularPolygon(center_pos, 6, radius=length, color=cmap(1/1), **kwargs)
        
        if pitch_class_display:
            ax.text(
                center_pos[0],
                center_pos[1],
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
                center_pos[0],
                center_pos[1],
                put_flat_sharp(df_data['step'][0], df_data['acc'][0]).replace('#', r'$\sharp$') \
                              .replace('b', r'$\flat$'),
                color='white',
                horizontalalignment='center',
                verticalalignment='center',
                size=size_text)
            df_pos = df_pos.append(
                {'pos':(0,0,0), 'note':df_data['step'][0], 'acc':df_data['acc'][0]},
                ignore_index=True)
        ax.add_patch(p)
        
    else: #read the given note and display it
        if pitch_class_display:
            df_pos = df_pos.append(
                {'pos':(0,0,0), 'note':center},
                ignore_index=True)
        else:
            a_center[0] = get_step(center)
            a_center[1] = get_acc(center)
            df_pos = df_pos.append(
                {'pos':(0,0,0), 'note':a_center[0], 'acc':a_center[1]},
                ignore_index=True)
        
        #set the color
        color = cmap(0)
        found = False
        color_nb = 0
        for l in range(df_data.shape[0]):
            if pitch_class_display:
                if str(int(df_data.at[l, 'pc'])) == str(center):
                    if duration:
                        color = cmap(norm(df_data.at[l, 'duration']))
                        color_nb = norm(df_data.at[l, 'duration'])
                    else:
                        color = cmap(norm(df_data.at[l, 'nb']))
                        color_nb = norm(df_data.at[l, 'nb'])
                    found = True
            else:
                if df_data.at[l, 'step'] == a_center[0] and df_data.at[l, 'acc'] == a_center[1]:
                    if duration:
                        color = cmap(norm(df_data.at[l, 'duration']))
                        color_nb = norm(df_data.at[l, 'duration'])
                    else:
                        color = cmap(norm(df_data.at[l, 'nb']))
                        color_nb = norm(df_data.at[l, 'nb'])
                    found = True
                    
        if found == False and pd.isnull(nan_color) == False:
            color = nan_color

        #define the color af the label in function of the color of the hexagon
        if color_nb > 0.6:
            color_text = 'White'
        else:
            color_text = 'Black'
            
        if pitch_class_display == False:
            a_center[0] = put_flat_sharp(a_center[0], a_center[1])
            
        if not edgecolor:
            edgecolor = color
        #draw and add labels
        p = patches.RegularPolygon(
            center_pos,
            6,
            radius=length,
            facecolor=color,
            edgecolor=edgecolor,
            **kwargs)
        if pitch_class_display:
            ax.text(
                center_pos[0],
                center_pos[1],
                str(int(center)),
                color=color_text,
                horizontalalignment='center',
                verticalalignment='center',
                size=size_text)
        else:
            ax.text(
                center_pos[0],
                center_pos[1],
                a_center[0].replace('#', r'$\sharp$') \
                               .replace('b', r'$\flat$'),
                color=color_text,
                horizontalalignment='center',
                verticalalignment='center',
                size=size_text)
        ax.add_patch(p)

    #do the rest of the plot except the first hex
    for layer in range(radius + 1): #for each layer
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
                                'acc':current_sup},
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
                            if df_data.at[l, 'step'] == current_note and df_data.at[l, 'acc'] == current_sup:
                                if duration:
                                    color = cmap(norm(df_data.at[l, 'duration']))
                                    color_nb = norm(df_data.at[l, 'duration'])
                                else:
                                    color = cmap(norm(df_data.at[l, 'nb']))
                                    color_nb = norm(df_data.at[l, 'nb'])
                                found = True
                                
                    if found == False and pd.isnull(nan_color) == False:
                        color = nan_color

                    #define the color af the label in function of the color of the hexagon
                    if color_nb > 0.6:
                        color_text = 'White'
                    else:
                        color_text = 'Black'

                    if pitch_class_display == False:
                        current_note = put_flat_sharp(current_note, current_sup)

                    #calcul the center position of the hex in function of the coordonnate
                    center_pos = [0.5 + pos[0] * HEXEDGE * length - pos[1] * HEXEDGE * length,
                              0.5 + pos[0] * length / 2 + pos[1] * length / 2 - pos[2] * length]

                    show_hex = True

                    #if no duplicate then check if the note is already display
                    if duplicate == False:
                        for l in range(df_pos.shape[0] - 1):
                            if pitch_class_display:
                                if df_pos.at[l, 'note'] == df_pos.at[df_pos.shape[0] - 1, 'note']:
                                    show_hex = False
                            else:
                                if df_pos.at[l, 'note'] == df_pos.at[df_pos.shape[0] - 1, 'note'] and\
                                   df_pos.at[l, 'acc'] == df_pos.at[df_pos.shape[0] - 1, 'acc']:
                                    show_hex = False

                    #draw
                    if show_hex:
                        if not edgecolor:
                            edgecolor = color
                        p = patches.RegularPolygon(
                            center_pos,
                            6,
                            radius=length,
                            facecolor=color,
                            edgecolor=edgecolor,
                            **kwargs)
                        if pitch_class_display:
                            ax.text(
                                center_pos[0],
                                center_pos[1],
                                str(int(current_note)),
                                color=color_text,
                                horizontalalignment='center',
                                verticalalignment='center',
                                size=size_text)
                        else:
                            ax.text(
                                center_pos[0],
                                center_pos[1],
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
