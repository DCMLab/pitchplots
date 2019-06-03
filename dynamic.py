"""
Fonctions for animations
"""
import math
import os

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import moviepy.editor as mpe

from matplotlib import animation

from pitchplots.reader import get_df_long
from pitchplots.reader import get_df_short
from pitchplots.functions import get_acc, get_step, get_dic_nei, put_flat_sharp, is_tpc, is_pc, get_pc, get_fifth_nb, get_fifth_note

def circle_animation(
    piece,
    pitch_type='tpc',
    measures=None,
    log=False,
    audio=True,
    vocabulary={0:'C', 1:'Db', 2:'D', 3:'Eb', 4:'E', 5:'F', 6:'Gb', 7:'G', 8:'Ab', 9:'A', 10:'Bb', 11:'B'},
    pitch_class_display=False,
    colorbar=True,
    adaptive_scale=True,
    duration=False,
    sampling_frequency=10,
    speed_ratio=1,
    fifths=True,
    figsize=[7, 5],
    top=None,
    rotation=0,
    clockwise=True,
    cmap='Blues',
    nan_color='white',
    filename='animated_circle.mp4',
    **kwargs):
    """return the figure of a piechart with importance of the notes that are represented by the colour as a heatmap

    Keyword arguments:
    piece -- the absolute path to the .csv file containing the data or a DataFrame
    pitch_type -- the type of data that you want to be read (default 'tpc'), 'pc' could be use for twelve parts chart tpc form
        (tpc:[A, B#, Gbbb, ...], pc (pitch class):[0, 3, 7, ...])
    measures -- give a set of measures example [5, 18], will display the notes of the measures 5 to 18 included
    log -- if True the colors are distributed on a log scale, by default it's a lineare scale (default False)
    audio -- if True if the filename is an .mp4 add the sound to it
    vocabulary -- the conversion dictionary from pitch class to tpc(F#, A, ...) format,
    pitch_class_display -- if True display the pitch class and no the tpc values and so the grid repeat itself.
    colorbar -- if true display the colorbar aside of the pie chart
    adaptive_scale -- if True, the scale evolve with the video, if not it stays the same
    duration -- tell him if he has to class the notes by their total duration or their number of appearance
    sampling_frequency -- the frequency of lecture of the piece, also correspond to the fps of the video
    speed_ratio -- set the speed at which the video is read, for example : 2 accelerate the speed of the video by 2
    fifths -- if True class the notes by fifths order, if not class by the chromatic order
    figsize -- tell the size of the figure in inches [x, y]
    top -- tell which note should be on the top of the piechart, different for tpc or pc
    rotation -- allows to rotate the piechart, int angle in degrees
    clockwise -- if True the piechart is displayed clockwise if not counter-clockwise
    cmap -- indicate the type of color to use for the heatmap, see matplotlib color documentation (default 'Blues')
    nan_color -- give the possibility to set a color for the note that do not appear in the piece (default 'nan')
    filename -- the name of the file you want to save, the animation is in the format of filename
    **kwargs -- these arguments are redirected to the matplotlib.pyplot.pie function, see informations at
                https://matplotlib.org/api/_as_gen/matplotlib.pyplot.pie.html
    """
    #settings
    df_short = get_df_short(piece, vocabulary=vocabulary, pitch_type=pitch_type, measures=measures, duration=duration)
    if '.mp4' in filename and audio:
        df_long, soundtrack = get_df_long(piece, vocabulary, pitch_type, measures, sampling_frequency, speed_ratio, audio=True)
    else:
        df_long = get_df_long(piece, vocabulary, pitch_type, measures, sampling_frequency, speed_ratio, audio=False)

    #color map
    cmap = matplotlib.cm.get_cmap(cmap)
    color_note = []
    
    list_patches = []
    list_patches_init = []
    
    list_notes = []
    
    df_short['value'] = pd.Series()
    df_short['value'].fillna(0, inplace=True)
    
    fig = plt.figure(figsize=figsize)
    plt.close(fig)
    ax = fig.add_subplot(111, aspect='equal')
    
    count_time = pd.Series([0.0])
    count_note = pd.Series([-1])
    
    #set the norm for the first colorbar
    #Norm isn't passed to the animate function because of argument problems
    if adaptive_scale:
        if log:
            if duration:
                norm = matplotlib.colors.LogNorm(vmin=df_long['duration'].min(), vmax=df_long['duration'].max())
            else:
                norm = matplotlib.colors.LogNorm(vmin=1, vmax=2)
        else:
            if duration:
                norm = matplotlib.colors.Normalize(vmin=0, vmax=df_long['duration'].max())
            else:
                norm = matplotlib.colors.Normalize(vmin=0, vmax=1)
    else:
        if log:
            if duration:
                norm = matplotlib.colors.LogNorm(vmin=df_long['duration'].min(), vmax=df_short['duration'].max())
            else:
                norm = matplotlib.colors.LogNorm(vmin=1, vmax=df_short['nb'].max())
        else:
            if duration:
                norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['duration'].max())
            else:
                norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['nb'].max())
    
    #creation of a subplot for the colorbar and plotting of it
    if colorbar:
        ax2 = fig.add_subplot(1, 10, 1)
        cb1 = matplotlib.colorbar.ColorbarBase(ax2,cmap=cmap,norm=norm,orientation='vertical')
    
    #settings for the saving as a video file .mp4
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=sampling_frequency, metadata=dict(artist='Me'), bitrate=2000)

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
    
    #Set the order in function of fifth
    if fifths:
        s_tpc_format = pd.Series((0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5))
    else:
        s_tpc_format = pd.Series((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11))

    #for plot if pitch_class_display
    s_twelve_ones = pd.Series((1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), index=s_tpc_format)

    #if it show the tpc values
    if pitch_class_display == False:
        #for chromatic order
        if fifths == False:

            #for each pitch class values
            for i in range(12):

                #if a pitch class is represented in the data
                if df_short['pc'].isin([s_tpc_format[i]]).any():
                    count = 0
                    s_pos.drop(s_pos.index, inplace=True)
                    
                    #count how much time there is tpc values for a same pitch class
                    for j in range(df_short['pc'].isin([s_tpc_format[i]]).shape[0]):
                       if df_short['pc'].isin([s_tpc_format[i]])[j]:
                           s_pos.at[count] = j
                           count = count + 1

                    #devide the pie part and set color
                    for j in range(count):
                        part = 1/count
                        letter = df_short.at[s_pos.at[j], 'step']

                        #write the notes
                        letter = put_flat_sharp(letter, df_short.at[s_pos.at[j], 'acc'])

                        #register the informations
                        df_tpc_pie = df_tpc_pie.append({'note':letter, 'part':part},
                                                       ignore_index=True)
                        color_note.append(nan_color)

                #if the pitch class do no appear in the piece
                else:
                    letter = vocabulary[s_tpc_format[i]]

                    df_tpc_pie = df_tpc_pie.append({'note':letter, 'part':1}, ignore_index=True)
                    color_note.append(nan_color)
        else:
            #get the fifth numbers of the notes
            for i in range(df_short.shape[0]):
                s_fifth.at[i] = get_fifth_nb(df_short.at[i, 'tpc'])
            df_short['fifth'] = s_fifth

            #create df_tpc_pie and get the colours
            for i in range(df_short['fifth'].max()-df_short['fifth'].min()+1):
                #the part are equal for the moment
                df_tpc_pie.at[i, 'part'] = 1
                df_tpc_pie.at[i, 'note'] = get_fifth_note(i + df_short['fifth'].min())
                df_tpc_pie.at[i, 'pc'] = get_pc(df_tpc_pie.at[i, 'note'])
                color_note.append(nan_color)

        #if clockwise invert the order of the data to be displayed clockwise, inverse also the index
        if clockwise: ### WILL HAVE TO BE CHANGED FOR THE ANIMATION
            df_tpc_pie = df_tpc_pie.iloc[::-1]

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
        
        #save of the notes
#        list_notes = df_tpc_pie['note']
        list_notes = [df_tpc_pie['note'].iat[i] for i in range(len(df_tpc_pie['note']))]
        
        #put nice sharps and flats
        for i in range(df_tpc_pie.shape[0]):
            df_tpc_pie.at[i, 'note'] = df_tpc_pie.at[i, 'note'].replace('b', r'$\flat$')\
                                                               .replace('#', r'$\sharp$')
            
        #plot the piechart with index 'tpc'
        df_tpc_pie.index = df_tpc_pie['note'].copy()
        
        #do the pie chart
        ###WARNING EXTEND AND NOT APPEND!!!!!!!!
        #take the first element of the tuple made by the pie function that is a list of patches
        list_patches.extend(ax.pie(labels=df_tpc_pie.index, x=df_tpc_pie['part'], colors=color_note, startangle=rotation, **kwargs)[0])
            
    #display with the pc values
    else:
        #set colors
        for i in range(0, 12):
            color_note.append(nan_color)

        #if clockwise invert the order of the data to be displayed clockwise
        if clockwise:
            s_twelve_ones = s_twelve_ones.iloc[::-1]

        #calculate the angle for the topPitchClass to be at the top
        if pd.isnull(top) == False:
            for i in range(s_tpc_format.shape[0]):
                if top == (s_twelve_ones.index)[i]:
                    rotation = rotation + 75 - i * 30
                    break
                
        list_notes = s_twelve_ones.index
        ###WARNING EXTEND AND NOT APPEND!!!!!!!!
        #take the first element of the tuple made by the pie function that is a list of patches
        list_patches.extend(ax.pie(labels=s_twelve_ones.index, x=s_twelve_ones, colors=color_note, startangle=rotation, **kwargs)[0])
        
    #===================================================================================
    #function init and animate
    #===================================================================================
    #initiation function
    def init():
        return list_patches_init

    #animation function
    def animate(i):
        count_time.iat[0] = i/sampling_frequency
        #if pitch_class_display
        if pitch_class_display:
            if df_long[df_long.onset_seconds == count_time.iat[0]].shape[0] > 0:
                #for all the notes on this time
                for nb_onset in range(df_long[df_long.onset_seconds == count_time.iat[0]].shape[0]):
                    count_note.iat[0] = count_note.iat[0] + 1
                    #find the note concerned in the reduce table
                    for j in range(df_short.shape[0]):
                        if df_short.at[j, 'pc'] == df_long.at[count_note.iat[0], 'pc']:
                            #give +1 to the note or + the duration of the note
                            if duration:
                                df_short.at[j, 'value'] = df_short.at[j, 'value'] + df_long.at[count_note.iat[0], 'duration']
                            else:
                                df_short.at[j, 'value'] = df_short.at[j, 'value'] + 1
                            break
                # update the norm, depending of the following characters:
                #   adaptive_scale, log and duration
                if adaptive_scale:
                    if log:
                        if duration:
                            if df_short['value'].max() > df_long['duration'].min():
                                norm = matplotlib.colors.LogNorm(vmin=df_long['duration'].min(), vmax=df_short['value'].max())
                            else:
                                norm = matplotlib.colors.LogNorm(vmin=df_long['duration'].min(), vmax=df_long['duration'].max())
                        else:
                            if df_short['value'].max() > 1:
                                norm = matplotlib.colors.LogNorm(vmin=1, vmax=df_short['value'].max())
                            else:
                                norm = matplotlib.colors.LogNorm(vmin=1, vmax=2)
                    else:
                        if duration:
                            norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['value'].max())
                        else:
                            norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['value'].max())
                else:
                    if log:
                        if duration:
                            norm = matplotlib.colors.LogNorm(vmin=df_long['duration'].min(), vmax=df_short['duration'].max())
                        else:
                            norm = matplotlib.colors.LogNorm(vmin=1, vmax=df_short['nb'].max())
                    else:
                        if duration:
                            norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['duration'].max())
                        else:
                            norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['nb'].max())
                #update the colorbar
                if colorbar and adaptive_scale:
                    ax2.clear()
                    cb1 = matplotlib.colorbar.ColorbarBase(ax2,cmap=cmap,norm=norm,orientation='vertical')
                #read every patches of the pie chart (each patches is a part of the pie chart)
                for j in range(len(list_notes)):
                    #find the corresponding note and refresh the color of the pie part
                    for k in range(df_short.shape[0]):
                        if list_notes[j] == df_short.at[k, 'pc']:
                            if df_short.at[k, 'value'] != 0:
                                list_patches[j].set_facecolor(cmap(norm(df_short.at[k, 'value'])))
                                
        else:
            if df_long[df_long.onset_seconds == count_time.iat[0]].shape[0] > 0:
                #for all the notes on this time
                for nb_onset in range(df_long[df_long.onset_seconds == count_time.iat[0]].shape[0]):
                    count_note.iat[0] = count_note.iat[0] + 1
                    #find the note concerned in the reduce table
                    for j in range(df_short.shape[0]):
                        if df_short.at[j, 'tpc'] == df_long.at[count_note.iat[0], 'tpc']:
                            #give +1 to the note or + the duration of the note
                            if duration:
                                df_short.at[j, 'value'] = df_short.at[j, 'value'] + df_long.at[count_note.iat[0], 'duration']
                            else:
                                df_short.at[j, 'value'] = df_short.at[j, 'value'] + 1
                            break
                # update the norm, depending of the following characters:
                #   adaptive_scale, log and duration
                if adaptive_scale:
                    if log:
                        if duration:
                            if df_short['value'].max() > df_long['duration'].min():
                                norm = matplotlib.colors.LogNorm(vmin=df_long['duration'].min(), vmax=df_short['value'].max())
                            else:
                                norm = matplotlib.colors.LogNorm(vmin=df_long['duration'].min(), vmax=df_long['duration'].max())
                        else:
                            if df_short['value'].max() > 1:
                                norm = matplotlib.colors.LogNorm(vmin=1, vmax=df_short['value'].max())
                            else:
                                norm = matplotlib.colors.LogNorm(vmin=1, vmax=2)
                    else:
                        if duration:
                            norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['value'].max())
                        else:
                            norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['value'].max())
                else:
                    if log:
                        if duration:
                            norm = matplotlib.colors.LogNorm(vmin=df_long['duration'].min(), vmax=df_short['duration'].max())
                        else:
                            norm = matplotlib.colors.LogNorm(vmin=1, vmax=df_short['nb'].max())
                    else:
                        if duration:
                            norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['duration'].max())
                        else:
                            norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['nb'].max())
                #update the colorbar
                if colorbar and adaptive_scale:
                    ax2.clear()
                    cb1 = matplotlib.colorbar.ColorbarBase(ax2,cmap=cmap,norm=norm,orientation='vertical')
                #read every patches of the pie chart (each patches is a part of the pie chart)
                for j in range(len(list_notes)):
                    #find the corresponding note and refresh the color of the pie part
                    for k in range(df_short.shape[0]):
                        if list_notes[j] == df_short.at[k, 'tpc']:
                            if df_short.at[k, 'value'] != 0:
                                list_patches[j].set_facecolor(cmap(norm(df_short.at[k, 'value'])))
        return list_patches
    
    anim = animation.FuncAnimation(fig,animate,init_func=init,frames=int((1+df_long['onset_seconds'].max())*sampling_frequency),
                                   interval=1/sampling_frequency,blit=True)
    if '.mp4' in filename:
        if audio:
            anim.save('pitchplots_image_only.mp4', writer=writer)
            my_clip = mpe.VideoFileClip('pitchplots_image_only.mp4')
            my_clip = my_clip.set_audio(soundtrack)
            my_clip.write_videofile(filename)
            os.remove('pitchplots_image_only.mp4')
        else:
            anim.save(filename, writer=writer)
    if '.gif' in filename:
        anim.save(filename, writer='imagemagick', fps=sampling_frequency)
        
    return anim

#===================================================================================
#TONNETZ_ANIMATION
#===================================================================================
def tonnetz_animation(
    piece,
    pitch_type='tpc',
    measures=None,
    sampling_frequency=10,
    speed_ratio=1,
    pitch_class_display=False,
    adaptive_scale=True,
    duplicate=True,
    duration=False,
    log=False,
    audio=True,
    colorbar=True,
    vocabulary={0:'C', 1:'Db', 2:'D', 3:'Eb', 4:'E', 5:'F', 6:'Gb', 7:'G', 8:'Ab', 9:'A', 10:'Bb', 11:'B'},
    radius=3,
    hex_size=1,
    fontsize=1,
    figsize=[7,5],
    cmap='Blues',
    nan_color=None,
    center=None,
    edgecolor='black',
    filename='animated_tonnetz.mp4',
    **kwargs):
    """
    Animation a 2D grid of hexagons, each hexagons being a note
    
    Keyword arguments:
    piece -- the absolute path to the .csv file containing the data or a DataFrame
    pitch_type -- the type of data that you want to be read (default 'tpc'), 'pc' could be use for twelve parts chart tpc form
        (tpc:[A, B#, Gbbb, ...], pc (pitch class):[0, 3, 7, ...])
    measures -- give a set of measures example [5, 18], will display the notes of the measures 5 to 18 included
    sampling_frequency -- the frequency of lecture of the piece, also correspond to the fps of the video
    speed_ratio -- set the speed at which the video is read, for example : 2 accelerate the speed of the video by 2
    pitch_class_display -- if True display the pitch class and no the tpc values and so the grid repeat itself.
    adaptive_scale -- if True, the scale evolve with the video, if not it stays the same
    duplicate -- if False there wont be any duplicate of note in the chart
    duration -- if True the value taking in account is the total duration of the note, if False it's the number of appearance
    log -- if True the scale is logarithmic if False it's linear
    audio -- if True if the filename is an .mp4 add the sound to it
    colorbar -- if true display the colorbar in the background
    vocabulary -- the conversion dictionary from pitch class to tpc(F#, A, ...) format,
    radius -- define the number of layers of the hexagonal grid (default 3)
    hex_size -- indicate the size of the hexagons (default 1)
    fontsize -- indicate the size of the typo for the labels (default 1)
    figsize -- indicate the size of the produced figure in inches (default [14, 9])
    cmap -- indicate the type of color to use for the heatmap, see matplotlib color documentation (default 'Blues')
    nan_color -- give the possibility to set a color for the note that do not appear in the piece
    center -- you can set the note that will be in the center of the grid,
        by default it put the most recurent note in the center
    edgecolor -- the color of the edges of the hexagons
    filename -- the name of the file you want to save, the animation is in the format of filename
    **kwargs -- these arguments are redirected to matplotlib.patches.RegularPolygon, see informations at
                https://matplotlib.org/api/_as_gen/matplotlib.patches.RegularPolygon.html
    """
    #settings
    if '.mp4' in filename and audio:
        df_long, soundtrack = get_df_long(piece, vocabulary, pitch_type, measures, sampling_frequency, speed_ratio, audio=True)
    else:
        df_long = get_df_long(piece, vocabulary, pitch_type, measures, sampling_frequency, speed_ratio, audio=False)
    df_short = get_df_short(piece, vocabulary, pitch_type, duration, measures)
    
    #number will be the number of appearances of the note through the video
    df_short['value'] = pd.Series()
    df_short['value'].fillna(0, inplace=True)
    
    #samplig the duration and onset at the sampling_frequency
    #df_long['duration'] = df_long['duration'].apply(sampling, sampling_frequency=sampling_frequency, zero_plus=True)

    #constant
    HEXEDGE = math.sqrt(3)/2 #math constant

    #intern variables
    length = 0.05 * hex_size * 1.5 * 3 / radius#radius and border length of the hexagons
    center_pos = [0.5, 0.5] #set the center on the center of the map
    size_text = length * 150 * fontsize # maybe a parameter fontsize
    pos = [0, 0, 0] #x, y, z
    pos_ser = (0, 0, 0) #for serching in the data
    a_center = ['F', 0] # the centerNote that was define (note, sup)
    count_time = pd.Series([0.0])
    count_note = pd.Series([-1])
    is_pc = pd.Series([pitch_class_display])
    color_text = 'Black'
    show_hex = True
    list_hex_show = [True]
    
    #count the number of hexagons, POSSIBLY REMOVE
    nb_hex = 1
    for i in range(radius):
        nb_hex = nb_hex + (i + 1) * 6

    #here to memorize the text and hexagonal patches
    list_patches_text = []
    list_patches_text_init = []

    #define figure
    fig = plt.figure(figsize=figsize)
    #prevent an undesired window to open
    plt.close(fig)
    
    ax = fig.add_subplot(111, aspect='equal')
    ax.axis('off')
    
    #adding of a second axis for the colorbar
    if colorbar:
        ax2 = fig.add_subplot(1, 10, 1)
    
    #colormap for the layout
    cmap = matplotlib.cm.get_cmap(cmap)
    
    #a mettre en parametre
    default_facecolor = cmap(0/1)
    
    #set the color for the notes that do not appear
    if nan_color:
        default_facecolor = nan_color

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
    
    #set the norm for the first colorbar
    if adaptive_scale:
        if log:
            if duration:
                norm = matplotlib.colors.LogNorm(vmin=df_long['duration'].min(), vmax=df_long['duration'].max())
            else:
                norm = matplotlib.colors.LogNorm(vmin=1, vmax=2)
        else:
            if duration:
                norm = matplotlib.colors.Normalize(vmin=0, vmax=df_long['duration'].max())
            else:
                norm = matplotlib.colors.Normalize(vmin=0, vmax=1)
    else:
        if log:
            if duration:
                norm = matplotlib.colors.LogNorm(vmin=df_long['duration'].min(), vmax=df_short['duration'].max())
            else:
                norm = matplotlib.colors.LogNorm(vmin=1, vmax=df_short['nb'].max())
        else:
            if duration:
                norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['duration'].max())
            else:
                norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['nb'].max())
    
    if colorbar:
        cb1 = matplotlib.colorbar.ColorbarBase(ax2,cmap=cmap,norm=norm,orientation='vertical')
    
    #settings for the saving as a video file
    #warning the maximum number of fps is 200!
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=sampling_frequency, metadata=dict(artist='Me'), bitrate=2000)

    #===================================================================================
    #hexgrid
    #===================================================================================
    #if not define it takes the most current note
    if pd.isnull(center): 
        list_patches_text.append(patches.RegularPolygon(center_pos, 6, radius=length, color=default_facecolor, edgecolor=edgecolor, **kwargs))

        #add the labels and register the hexagons
        if pitch_class_display:
            list_patches_text.append(ax.text(
                center_pos[0],
                center_pos[1],
                str(int(df_short['pc'][0])),
                color=color_text,
                horizontalalignment='center',
                verticalalignment='center',
                size=size_text))
            df_pos = df_pos.append(
                {'pos':(0,0,0), 'note':df_short['pc'][0]},
                ignore_index=True)
        else:
            list_patches_text.append(ax.text(
                center_pos[0],
                center_pos[1],
                df_short['tpc'][0].replace('#', r'$\sharp$') \
                                .replace('b', r'$\flat$'),
                color=color_text,
                horizontalalignment='center',
                verticalalignment='center',
                size=size_text))
            df_pos = df_pos.append(
                {'pos':(0,0,0), 'note':df_short['step'][0], 'acc':df_short['acc'][0]},
                ignore_index=True)
    else:
        #register  the hexagons
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
       
        #put the sharps and the flats
        if pitch_class_display == False:
            a_center[0] = put_flat_sharp(a_center[0], a_center[1])

        #draw
        list_patches_text.append(patches.RegularPolygon(
            center_pos,
            6,
            radius=length,
            facecolor=default_facecolor,
            edgecolor=edgecolor,
            **kwargs))
        
        #add the labels
        if pitch_class_display:
            list_patches_text.append(ax.text(
                center_pos[0],
                center_pos[1],
                str(center),
                horizontalalignment='center',
                verticalalignment='center',
                size=size_text))
        else:
            list_patches_text.append(ax.text(
                center_pos[0],
                center_pos[1],
                a_center[0].replace('#', r'$\sharp$') \
                               .replace('b', r'$\flat$'),
                horizontalalignment='center',
                verticalalignment='center',
                size=size_text))
    
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

                    #get the # or b from the reference note
                    if pitch_class_display == False:
                        current_acc = df_pos[select_data].iat[0, 2]
                    
                    #get df for the note of reference from df_nei
                    df_nei_gr = df_nei.groupby('ref').get_group(df_pos[select_data].iat[0, 1])

                    #select the name of the note from the hexagone
                    select_data = df_nei_gr['pos'] == pos_ser_n 

                    #register the hexagons
                    if pitch_class_display:
                        current_note = df_nei_gr[select_data].iat[0, 2]
                        df_pos = df_pos.append(
                            {'pos':(pos[0], pos[1], pos[2]),
                                'note':current_note},
                            ignore_index=True)
                    else:
                        current_note = df_nei_gr[select_data].iat[0, 2]
                        current_acc = current_acc + df_nei_gr[select_data].iat[0, 3]
                        df_pos = df_pos.append(
                            {'pos':(pos[0], pos[1], pos[2]),
                                'note':current_note,
                                'acc':current_acc},
                            ignore_index=True)

                    #format current_note to display the # and b
                    if pitch_class_display == False:
                        current_acc = current_acc.astype(np.int64)
                        if current_acc > 0:
                            for l in range(current_acc):
                                current_note = current_note + '#'     
                        if current_acc < 0:
                            current_acc = abs(current_acc)
                            for l in range(current_acc):
                                current_note = current_note + 'b'

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
                    if show_hex:
                        #draw the hex
                        list_patches_text.append(patches.RegularPolygon(
                            center_pos,
                            6,
                            radius=length,
                            facecolor=default_facecolor,
                            edgecolor=edgecolor,
                            **kwargs))
                        
                        #put the name of the hex
                        if pitch_class_display:
                            list_patches_text.append(ax.text(
                                center_pos[0],
                                center_pos[1],
                                str(current_note),
                                horizontalalignment='center',
                                verticalalignment='center',
                                size=size_text))
                        else:
                            list_patches_text.append(ax.text(
                                center_pos[0],
                                center_pos[1],
                                current_note.replace('#', r'$\sharp$') \
                                            .replace('b', r'$\flat$'),
                                horizontalalignment='center',
                                verticalalignment='center',
                                size=size_text))
                        list_hex_show.append(True)
                    else:
                        list_patches_text.append(None)
                        list_patches_text.append(None)
                        list_hex_show.append(False)
                            
    #===================================================================================
    #function init and animate
    #===================================================================================
    #initiation function
    def init():
        return list_patches_text_init

    #animation function
    def animate(i):
        count_time.iat[0] = i/sampling_frequency
        #if pitch_class_display
        if is_pc[0]:
            if df_long[df_long.onset_seconds == count_time.iat[0]].shape[0] > 0:
                #for all the notes on this time
                for nb_onset in range(df_long[df_long.onset_seconds == count_time.iat[0]].shape[0]):
                    count_note.iat[0] = count_note.iat[0] + 1
                    #if pd.isnull(df_long.at[int(count_note.iat[0]), 'pc']) == False:
                    #find the note concerned in the reduce table
                    for j in range(df_short.shape[0]):
                        if df_short.at[j, 'pc'] == df_long.at[count_note.iat[0], 'pc']:
                            #give +1 to the note or + the duration of the note
                            if duration:
                                df_short.at[j, 'value'] = df_short.at[j, 'value'] + df_long.at[count_note.iat[0], 'duration']
                            else:
                                df_short.at[j, 'value'] = df_short.at[j, 'value'] + 1
                            break
                # update the norm, depending of the following characters:
                #   adaptive_scale, log and duration
                if adaptive_scale:
                    if log:
                        if duration:
                            if df_short['value'].max() > df_long['duration'].min():
                                norm = matplotlib.colors.LogNorm(vmin=df_long['duration'].min(), vmax=df_short['value'].max())
                            else:
                                norm = matplotlib.colors.LogNorm(vmin=df_long['duration'].min(), vmax=df_long['duration'].max())
                        else:
                            if df_short['value'].max() > 1:
                                norm = matplotlib.colors.LogNorm(vmin=1, vmax=df_short['value'].max())
                            else:
                                norm = matplotlib.colors.LogNorm(vmin=1, vmax=2)
                    else:
                        if duration:
                            norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['value'].max())
                        else:
                            norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['value'].max())
                else:
                    if log:
                        if duration:
                            norm = matplotlib.colors.LogNorm(vmin=df_long['duration'].min(), vmax=df_short['duration'].max())
                        else:
                            norm = matplotlib.colors.LogNorm(vmin=1, vmax=df_short['nb'].max())
                    else:
                        if duration:
                            norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['duration'].max())
                        else:
                            norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['nb'].max())
                #update the colorbar
                if colorbar:
                    ax2.clear()
                    cb1 = matplotlib.colorbar.ColorbarBase(ax2,cmap=cmap,norm=norm,orientation='vertical')
                #read every hexagons
                for j in range(df_pos.shape[0]):
                    if list_hex_show[j]:
                        #find the corresponding note and refresh the color of the hexagon
                        for k in range(df_short.shape[0]):
                            if df_pos.at[j, 'note'] == df_short.at[k, 'pc']:
                                if df_short.at[k, 'value'] != 0:
                                    list_patches_text[j*2].set_facecolor(cmap(norm(df_short.at[k, 'value'])))
        else:
            #if a note start on the current onset
            if df_long[df_long.onset_seconds == count_time.iat[0]].shape[0] > 0:
                #for all the notes on this time
                for nb_onset in range(df_long[df_long.onset_seconds == count_time.iat[0]].shape[0]):
                    count_note.iat[0] = count_note.iat[0] + 1
                    #if pd.isnull(df_long.at[int(count_note.iat[0]), 'tpc']) == False:
                    #find the note concerned in the reduce table
                    for j in range(df_short.shape[0]):
                        if df_short.at[j, 'step'] == df_long.at[count_note.iat[0], 'step'] and \
                        df_short.at[j, 'acc'] == df_long.at[count_note.iat[0], 'acc']:
                            #give +1 to the note
                            if duration:
                                df_short.at[j, 'value'] = df_short.at[j, 'value'] + df_long.at[count_note.iat[0], 'duration']
                            else:
                                df_short.at[j, 'value'] = df_short.at[j, 'value'] + 1
                            break
                # update the norm, depending of the following characters:
                #   adaptive_scale, log and duration
                if adaptive_scale:
                    if log:
                        if duration:
                            if df_short['value'].max() > df_long['duration'].min():
                                norm = matplotlib.colors.LogNorm(vmin=df_long['duration'].min(), vmax=df_short['value'].max())
                            else:
                                norm = matplotlib.colors.LogNorm(vmin=df_long['duration'].min(), vmax=df_long['duration'].max())
                        else:
                            if df_short['value'].max() > 1:
                                norm = matplotlib.colors.LogNorm(vmin=1, vmax=df_short['value'].max())
                            else:
                                norm = matplotlib.colors.LogNorm(vmin=1, vmax=2)
                    else:
                        if duration:
                            norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['value'].max())
                        else:
                            norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['value'].max())
                else:
                    if log:
                        if duration:
                            norm = matplotlib.colors.LogNorm(vmin=df_long['duration'].min(), vmax=df_short['duration'].max())
                        else:
                            norm = matplotlib.colors.LogNorm(vmin=1, vmax=df_short['nb'].max())
                    else:
                        if duration:
                            norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['duration'].max())
                        else:
                            norm = matplotlib.colors.Normalize(vmin=0, vmax=df_short['nb'].max())
                #update the colorbar
                if colorbar and adaptive_scale:
                    ax2.clear()
                    cb1 = matplotlib.colorbar.ColorbarBase(ax2,cmap=cmap,norm=norm,orientation='vertical')
                #read every hexagons
                for j in range(df_pos.shape[0]):
                    if list_hex_show[j]:
                        #find the corresponding note and refresh the color of the hexagon
                        for k in range(df_short.shape[0]):
                            if df_pos.at[j, 'note'] == df_short.at[k, 'step'] and \
                            df_pos.at[j, 'acc'] == df_short.at[k, 'acc']:
                                if df_short.at[k, 'value'] != 0:
                                    list_patches_text[j*2].set_facecolor(cmap(norm(df_short.at[k, 'value'])))
        return filter(None, list_patches_text)

    #add the patches to the ax
    for i in range(df_pos.shape[0]):
        if list_hex_show[i]:
            ax.add_patch(list_patches_text[i*2])
    
    anim = animation.FuncAnimation(fig,animate,init_func=init,frames=int((1+df_long['onset_seconds'].max())*sampling_frequency),interval=1/sampling_frequency,blit=True)
    if '.mp4' in filename:
        if audio:
            anim.save('pitchplots_image_only.mp4', writer=writer)
            my_clip = mpe.VideoFileClip('pitchplots_image_only.mp4')
            my_clip = my_clip.set_audio(soundtrack)
            my_clip.write_videofile(filename)
            os.remove('pitchplots_image_only.mp4')
        else:
            anim.save(filename, writer=writer)
    if '.gif' in filename:
        anim.save(filename, writer='imagemagick', fps=sampling_frequency)
    
    return anim