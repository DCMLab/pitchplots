import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from musical_read_file import musical_get_data_reduced
from musical_functions import get_acc, get_step, get_pc, get_dic_nei, put_flat_sharp, get_fifth_nb, get_fifth_note

def musical_plot_pie(
    location,
    dataType='tpc',
    log=False,
    convertTable=['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'],
    pitchClassDisplay=False,
    colorbar=True,
    duration=False,
    fifth=True,
    figSize = 9,
    topNote = 'nan',
    rotation = 0,
    clockwise = True,
    colorGeneral='Blues',
    colorZeroValue='nan'):
    """plot a piechart with importance of the notes that are represented ny the colour asa heatmap

    Keyword arguments:
    location -- the absolute path to the .csv file containing the data
    dataType -- the type of data that contains the file (default 'tpc')
        (tpc:[A, B#, Gbbb, ...], pc (pitch class):[0, 3, 7, ...])
    log -- if True the colors are distributed on a log scale, by default it's a lineare scale (default False)
    convertTable -- the conversion table from pitch class to tpc(F#, A, ...) format,
        the position indicate the pitch class value (default [C, Db, D, Eb, E, F, Gb, G, Ab, A, Bb, B])
    pitchClassDisplay -- if True display the pitch class and no the tpc values and so the grid repeat itself.
    colorbar -- if true display the colorbar aside of the pie chart
    duration -- tell him if he has to class the importance by the total duration of the note or by the number of appearence.
    fifth -- if True class the notes by fifth order, if not class by the chromatic order
    figSize -- tell the size of the figure in inches
    topNote -- tell whiche note should be on the top of the piechart, different for tpc or pc
    rotation -- allows to rotate the piechart, int angle in degres
    clockwise -- if True the piechart is displayed clockwise if not counter-clockwise
    colorGeneral -- indicate the type of color to use for the heatmap, see matplotlib color documentation (default 'Blues')
    colorZeroValue -- give the possibility to set a color for the note that do not appear in the piece (default 'nan')
    """
    #settings
    convertTable = pd.Series(convertTable)
    df = musical_get_data_reduced(location, convertTable=convertTable, dataType=dataType)

    #color map
    cmap = matplotlib.cm.get_cmap(colorGeneral)
    color_note = []

    #dataFrame for the plot if tpc
    df_tpc_pie = pd.DataFrame(columns=['note', 'part', 'pc'])

    #remember position of data in Series
    s_pos = pd.Series()
    count = 0
    part = 0
    letter = 'nan'
    s_fifth = pd.Series()

    figsize = [figSize*1.5, figSize] #define the size if the figure
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, aspect='equal')

    #Set the order in function of fifth
    if fifth:
        s_tpc_format = pd.Series((0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5))
    else:
        s_tpc_format = pd.Series((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11))

    #for plot if pitchClassDisplay
    s_twelve_ones = pd.Series((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), index=s_tpc_format)

    #if it show the tpc values
    if pitchClassDisplay == False:
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
                    letter = convertTable[s_tpc_format[i]]

                    df_tpc_pie = df_tpc_pie.append({'note':letter, 'part':1}, ignore_index=True)
                    if colorZeroValue == 'nan':
                        color_note.append(cmap(0))
                    else:
                        color_note.append(colorZeroValue)
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
                elif df_data['fifth'].isin([i + df_data['fifth'].min()]).any() == False and colorZeroValue != 'nan':
                    color_note.append(colorZeroValue)
                else:
                    color_note.append(cmap(0))

        #if clockwise invert the order of the data to be displayed clockwise, inverse also the index
        if clockwise:
            df_tpc_pie = df_tpc_pie.iloc[::-1]
            color_note = list(reversed(color_note))

        #calculate the angle for the topPitchClass to be at the top
        if topNote != 'nan' and fifth == False and df_tpc_pie['note'].isin([topNote]).any() == True:
            if clockwise:
                rotation = rotation + 90 + df_tpc_pie.at[0, 'part'] * 15
            else:
                rotation = rotation + 90 - df_tpc_pie.at[0, 'part'] * 15
            for i in range(df_tpc_pie.shape[0]):
                if topNote == df_tpc_pie.at[i, 'note']:
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
        if topNote != 'nan' and fifth == True and df_tpc_pie['note'].isin([topNote]).any() == True:
            if clockwise:
                rotation = rotation + 90 + 180/df_tpc_pie.shape[0]
            else:
                rotation = rotation  + 90 - 180/df_tpc_pie.shape[0]
            for i in range (df_tpc_pie.shape[0]):
                if df_tpc_pie.at[i, 'note'] == topNote:
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
                if colorZeroValue == 'nan':
                    color_note.append(cmap(0))
                else:
                    color_note.append(colorZeroValue)

        #if clockwise invert the order of the data to be displayed clockwise
        if clockwise:
            s_twelve_ones = s_twelve_ones.iloc[::-1]
            color_note = list(reversed(color_note))

        #calculate the angle for the topPitchClass to be at the top
        if topNote != 'nan':
            for i in range(s_tpc_format.shape[0]):
                if topNote == (s_twelve_ones.index)[i]:
                    rotation = rotation + 75 - i * 30
                    break

        ax.pie(labels=s_twelve_ones.index, x=s_twelve_ones, colors=color_note, startangle=rotation)

        #if asked plot the colorbar left of the piechart
        if colorbar:
            ax2 = fig.add_subplot(1, 10, 1)
            cb1 = matplotlib.colorbar.ColorbarBase(ax2, cmap=cmap, norm=norm, orientation='vertical')
        
    plt.show()

#location = r'D:\epfl\JOB_MUSICAL\some2.csv'
#musical_plot_pie(location, colorZeroValue='Silver', topPitchClass=5)
