import pandas as pd

def musical_read_file(
    location,
    convertTable,
    dataType):
    """Read a given file and put important elements in a dataFrame

    Function:
    Get a file location and read it to create a dataFrame with the following informations:
        pitch class value('pc'), number of appearences('nb'), total duration of the note('duration'),
        tpc format note('tpc'), sharps and flats('sup')
    Keyword arguments:
    location -- the absolute path to the .csv file containing the data
    dataType -- the type of data that contains the file (default 'tpc')
        (tpc:[A, B#, Gbbb, ...], pc (pitch class):[0, 3, 7, ...])
    convertTable -- the conversion table from pitch class to tpc(F#, A, ...) format,
        the position indicate the pitch class value (default [C, Db, D, Eb, E, F, Gb, G, Ab, A, Bb, B])
    """
    df_data = pd.read_csv(location)
    
    correct_format_tpc = False
    correct_format_duration = False
    correct_format_pc = False
    
    ok_tpc = False
    ok_duration = False
    ok_pc = False
    
    col_tpc = 'nan'
    col_duration = 'nan'
    col_pc = 'nan'
    
    s_tpc_values_1 = pd.Series(['F', 'C', 'G', 'D', 'A', 'E', 'B'])
    s_tpc_values_2 = pd.Series(['b', '#'])
    s_pc_values = pd.Series([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])

    if dataType == 'tpc':
        tpc = True
        pc = False
    if dataType == 'pc':
        tpc = False
        pc = True
        
    #===================================================================================
    #reading the file at Location
    #===================================================================================
    
    #read every columns
    for i in range(df_data.shape[1]):
        s_data = df_data.iloc[:, i]
        s_data.dropna(inplace=True)
        correct_format_tpc = True
        correct_format_duration = True
        correct_format_pc = True
        count = 0

        #read every rows
        for j in range(s_data.shape[0]):
            
            #do not check nan values
            if((s_data.isnull().iat[j]) == False):
                count = 0
                #pc check if it's a number from 0 to 11
                if isinstance(s_data.iat[j], int) or isinstance(s_data.iat[j], float):
                    if (s_data.iat[j] == s_pc_values).any() == False:
                        correct_format_pc = False
                else:
                    correct_format_pc = False
                
                #duration check if it's a number and in ]0;4]
                if isinstance(s_data.iat[j], int) or isinstance(s_data.iat[j], float):
                    if s_data.iat[j] <= 0 or s_data.iat[j] > 4:
                        correct_format_duration = False
                else:
                    correct_format_duration = False
                
                #tpc read every character of the strings
                for k in str(s_data.iat[j]):
                    count = count + 1

                    #check first character
                    if (count == 1): 
                        if (k == s_tpc_values_1).any() == False:
                            correct_format_tpc = False
                    
                    #check following characters
                    else: 
                        if (k == s_tpc_values_2).any() == False:
                            correct_format_tpc = False
                    if correct_format_tpc == False:
                        break

        #no error detected for pc
        if correct_format_pc == True and col_pc == 'nan':
            col_pc = i
            ok_pc = True
            
        #no error detected for tpc
        if correct_format_tpc == True and col_tpc == 'nan':
            col_tpc = i
            ok_tpc = True

        #no error detected for duration
        if correct_format_duration == True and col_duration == 'nan':
            col_duration = i
            ok_duration = True
            
    #===================================================================================
    #creating data Frame for tpc
    #===================================================================================
    if ok_tpc and tpc and pc == False:
        s_tpc = df_data.iloc[:, col_tpc]
        s_tpc = s_tpc.groupby(s_tpc).size()

        #the most current note first
        s_tpc.sort_values(inplace=True, ascending=False)

        df_tpc = pd.DataFrame(s_tpc)
        df_tpc.columns = ['nb']
        df_tpc.reset_index(inplace=True)
        df_tpc.columns = ['tpc', 'nb']
        
        #add the duration column
        if ok_duration:
            df_duration = pd.concat([
                    df_data[df_data.columns[col_tpc]],
                    df_data[df_data.columns[col_duration]]],
                axis=1,
                keys=['tpc', 'duration'])
            df_duration = (df_duration.groupby('tpc')).sum()
            df_tpc = pd.merge(df_tpc, df_duration, on=['tpc', 'tpc'])
        
        #add the sup column
        df_tpc['sup'] = pd.Series()
        df_tpc['sup'].fillna(0, inplace=True)
        for i in range(df_tpc.shape[0]):
            for j in df_tpc.at[i, 'tpc']:
                if j == '#':
                    df_tpc.at[i, 'sup'] = df_tpc.at[i, 'sup'] + 1
                if j == 'b':
                    df_tpc.at[i, 'sup'] = df_tpc.at[i, 'sup'] - 1
                if j != '#' and j != 'b':
                    carac = j

            #replace the values in tpc column, only A B C etc...
            df_tpc.at[i, 'tpc'] = carac
        
        #add the pitch class (pc) column
        df_tpc['pc'] = pd.Series()
        df_tpc['pc'].fillna(0, inplace=True)
        for i in range(df_tpc.shape[0]):
            if df_tpc.at[i, 'tpc'] == 'C': df_tpc.at[i, 'pc'] = 0
            if df_tpc.at[i, 'tpc'] == 'D': df_tpc.at[i, 'pc'] = 2
            if df_tpc.at[i, 'tpc'] == 'E': df_tpc.at[i, 'pc'] = 4
            if df_tpc.at[i, 'tpc'] == 'F': df_tpc.at[i, 'pc'] = 5
            if df_tpc.at[i, 'tpc'] == 'G': df_tpc.at[i, 'pc'] = 7
            if df_tpc.at[i, 'tpc'] == 'A': df_tpc.at[i, 'pc'] = 9
            if df_tpc.at[i, 'tpc'] == 'B': df_tpc.at[i, 'pc'] = 11

            df_tpc.at[i, 'pc'] = df_tpc.at[i, 'pc'] + df_tpc.at[i, 'sup']

            while df_tpc.at[i, 'pc'] < 0:
                df_tpc.at[i, 'pc'] = df_tpc.at[i, 'pc'] + 12
            while df_tpc.at[i, 'pc'] > 11:
                df_tpc.at[i, 'pc'] = df_tpc.at[i, 'pc'] - 12

        return df_tpc

    #===================================================================================
    #creating data Frame for pitch class
    #===================================================================================
    if ok_pc and pc and tpc == False:
        s_pc = df_data.iloc[:, col_pc]
        s_pc = s_pc.groupby(s_pc).size()

        #the most current note first
        s_pc.sort_values(inplace=True, ascending=False)

        df_pc = pd.DataFrame(s_pc)
        df_pc.columns = ['nb']
        df_pc.reset_index(inplace=True)
        df_pc.columns = ['pc', 'nb']
        
        #add the duration column
        if ok_duration:
            df_duration = pd.concat([
                    df_data[df_data.columns[col_pc]],
                    df_data[df_data.columns[col_duration]]],
                axis=1,
                keys=['pc', 'duration'])
            df_duration = (df_duration.groupby('pc')).sum()
            df_pc = pd.merge(df_pc, df_duration, on=['pc', 'pc'])

        #add the tpc column
        s_tpc_pc = []
        for i in range(df_pc.shape[0]):
            s_tpc_pc.append(convertTable[df_pc.at[i, 'pc']])

        df_pc['tpc'] = pd.Series(s_tpc_pc)

        #add the sup column
        df_pc['sup'] = pd.Series()
        df_pc['sup'].fillna(0, inplace=True)
        for i in range(df_pc.shape[0]):
            for j in df_pc.at[i, 'tpc']:
                if j == '#':
                    df_pc.at[i, 'sup'] = df_pc.at[i, 'sup'] + 1
                if j == 'b':
                    df_pc.at[i, 'sup'] = df_pc.at[i, 'sup'] - 1
                if j != '#' and j != 'b':
                    carac = j

            #replace the values in tpc column, only A B C etc...
            df_pc.at[i, 'tpc'] = carac
            
        return df_pc
