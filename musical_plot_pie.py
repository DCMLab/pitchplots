import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from musical_read_file import musical_read_file

def musical_plot_pie(
    location,
    dataType='tpc',
    convertTable=['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B'],
    tpc=True,
    duration=False,
    fifth=True,
    figSize = 9,
    colorGeneral='Blues'):
    """
    Plot a pie chart
    
    Function:
    Get a file location send it to musical_read_file
    from it plot a pie chart using heat map to indicate the importance of the notes
    the more colored are the note, the more its presence in the piece is important
    Keyword arguments:
    location -- the absolute path to the .csv file containing the data
    dataType -- the type of data that contains the file (default 'tpc')
        (tpc:[A, B#, Gbbb, ...], pc (pitch class):[0, 3, 7, ...])
    convertTable -- the conversion table from pitch class to tpc(F#, A, ...) format,
        the position indicate the pitch class value (default [C, Db, D, Eb, E, F, Gb, G, Ab, A, Bb, B])
    tpc -- boolean that indicates the type of label to indicate (default True)
    duration -- boolean that indicates if it should consider the total duration of the note in the piece or
        the number of appearances in the piece (default False)
    fifth -- boolean indicate if the adjacent notes in the pie chart are fifth or chromatic (default True)
    figSize -- indicate the size of the produced figure in inches (default 9)
    colorGeneral -- indicate the type of color to use for the heatmap,
        see matplotlib color documentation (default 'Blues')
    """
    #settings
    convertTable = pd.Series(convertTable)
    df = musical_read_file(location, convertTable=convertTable, dataType=dataType)
    
    #color map
    cmap = matplotlib.cm.get_cmap(colorGeneral)
    color_tpc = []

    #dataFrame for the plot if tpc
    df_tpc_pie = pd.DataFrame(columns=['tpc', 'part'])

    #remember position of data in Series
    s_pos = pd.Series()
    count = 0
    part = 0
    letter = 'nan'

    #Set the order in function of fifth
    if fifth:
        s_tpc_format = pd.Series((0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5))
    else:
        s_tpc_format = pd.Series((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11))

    #for plot if not tpc
    s_twelve_ones = pd.Series((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), index=s_tpc_format)

    if tpc:
        #put the right values in 'number'
        if duration:
            df_data = df.copy()
            del df_data['nb']
            df_data.rename(columns={'duration': 'number'},inplace=True)
        else:
            df_data = df.copy()
            del df_data['duration']
            df_data.rename(columns={'nb': 'number'},inplace=True)

        max_value = df_data['number'].max()

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
                    if df_data.at[s_pos.at[j], 'sup'] > 0:
                        for k in range(df_data.at[s_pos.at[j], 'sup'].astype(np.int64)):
                            letter = letter + '#'
                    if df_data.at[s_pos.at[j], 'sup'] < 0:
                        for k in range(abs(df_data.at[s_pos.at[j], 'sup']).astype(np.int64)):
                            letter = letter + 'b'

                    #set nicer sharps and flats
                    letter = letter.replace('#', r'$\sharp$')\
                                   .replace('b', r'$\flat$')

                    #register the informations
                    df_tpc_pie = df_tpc_pie.append({'tpc':letter, 'part':part},
                                                   ignore_index=True)
                    color_tpc.append(cmap(df_data.at[s_pos.at[j], 'number']/max_value))

            #if the pitch class do no appear in the piece
            else:
                letter = convertTable[s_tpc_format[i]]
                letter = letter.replace('#', r'$\sharp$')\
                               .replace('b', r'$\flat$')

                df_tpc_pie = df_tpc_pie.append({'tpc':letter, 'part':1}, ignore_index=True)
                color_tpc.append(cmap(0))

        #plot the piechart with index 'tpc'
        df_tpc_pie.index = df_tpc_pie['tpc']
        df_tpc_pie.plot(
            kind='pie',
            y='part',
            legend=False,
            label='',
            figsize=(figSize, figSize),
            colors=color_tpc)

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

        #set data df_data
        df_data = (df_data.groupby('pc')).sum()
        df_data = df_data.reindex(s_tpc_format)
        df_data.fillna(0, inplace=True)

        max_value = df_data['number'].max()

        #set colors
        for i in range(0, 12):
            color_tpc.append(cmap(df_data.iat[i, 0]/max_value))

        #plot with equal parts
        s_twelve_ones.plot(
            kind='pie',
            figsize=(figSize, figSize),
            label='',
            colors=color_tpc)
            
    plt.show()
