import pandas as pd
import numpy as np
from datetime import date
from mip import Model, xsum, maximize, BINARY, CBC

#takes template and predicted points, determines optimal lineup andcreates template .csv file that can be uploaded to DK
#saves copy of selected roster to specified location.

def merge_and_optimize(df, points_df):
    #merge template and predicted points
    df = df.merge(points_df, left_on=['Name','TeamAbbrev'], right_on=['name','team'],how='left')
    #we will miss some bad players. check max salary of players that did not merge
    #send error if a player with salary above $4,000 does not merge
    try:
        max_non_merge = df.loc[pd.isnull(df["points"]),'Salary'].max()
        problem_name = df.loc[df["Salary"] == max_non_merge,'Name']
        problem_salary = df.loc[df["Salary"] == max_non_merge,'Salary']
        max_non_merge < 4000
    except:
        raise Exception('non-trivial player did not merge ({}-{})'.format(problem_name,problem_salary))
    #drop those that do not merge
    df = df.loc[~pd.isnull(df["points"])]

    #create duplicates for each row to account for players who are eligible for many positions
    #helper function that creates position specific dataframe
    def switch_off_pos(df,pos):
        all_pos = ['pg','sg','sf','pf','c']
        all_pos.remove(pos)
        df_new = df.copy()
        for col in all_pos:
            df_new[col] = 0
        return df_new
    #create position specific dataframes and append
    dup_df = switch_off_pos(df,"pg").append(switch_off_pos(df,"sg"))
    dup_df = dup_df.append(switch_off_pos(df,"sf"))
    dup_df = dup_df.append(switch_off_pos(df,"pf"))
    dup_df = dup_df.append(switch_off_pos(df,"c"))
    df = dup_df
    #drop rows with no position
    df['total_positions'] = df['pg'] + df['sg'] + df['sf'] + df['pf'] + df['c']
    df = df[df['total_positions'] != 0]
    #create player dummy used to ensure no player is used twice despite duplicates
    df = pd.concat([df,pd.get_dummies(df['name'])],axis=1) 
    player_var_list = pd.get_dummies(df['name']).columns

    #select optimal lineup
    #num rows
    n = range(df.shape[0])
    #use free solver
    m = Model(solver_name=CBC)
    #n binary vars indicating if player is selected or not
    x = [m.add_var(var_type=BINARY) for i in n]
    #objective: maximize predicted points for players selected
    m.objective = maximize(xsum(df['points'].tolist()[i] * x[i] for i in n))
    #salary constraint
    m += xsum(df['Salary'].tolist()[i] * x[i] for i in n) <= 50000
    #position constraints. 1 of each position, 1 extra gaurd, 1 extra forward, 1 utility
    #pg
    m += xsum(df['pg'].tolist()[i] * x[i] for i in n) >= 1
    m += xsum(df['pg'].tolist()[i] * x[i] for i in n) <= 3
    #sg
    m += xsum(df['sg'].tolist()[i] * x[i] for i in n) >= 1
    m += xsum(df['sg'].tolist()[i] * x[i] for i in n) <= 3
    #g
    m += xsum((df['pg'].tolist()[i] + df['sg'].tolist()[i]) * x[i] for i in n) >= 3
    #sf
    m += xsum(df['sf'].tolist()[i] * x[i] for i in n) >= 1
    m += xsum(df['sf'].tolist()[i] * x[i] for i in n) <= 3
    #pf
    m += xsum(df['pf'].tolist()[i] * x[i] for i in n) >= 1
    m += xsum(df['pf'].tolist()[i] * x[i] for i in n) <= 3
    #f
    m += xsum((df['sf'].tolist()[i] + df['pf'].tolist()[i]) * x[i] for i in n) >= 3
    #c
    m += xsum(df['c'].tolist()[i] * x[i] for i in n) >= 1
    m += xsum(df['c'].tolist()[i] * x[i] for i in n) <= 2
    #total
    m += xsum(x[i] for i in n) == 8
    #player constraints - players appear only once
    for player in player_var_list:
        m += xsum(df[player].tolist()[i] * x[i] for i in n) <= 1, '{}'.format(player)
    #optimize
    m.optimize()

    #save copy of optimal lineup as record
    names = [df['Name'].to_list()[i] for i in n if x[i].x >= 0.99]
    points = [df['points'].to_list()[i] for i in n if x[i].x >= 0.99]
    with open( "export/lineups/lineup_{}.csv".format(date.today()), "w") as f:
        f.write("name,points\n")
        for i in range(len(names)):
            f.write("{},{}\n".format(names[i],points[i]))
        f.close()

    #order list of ids to conform with DK template
    #PG,SG,SF,PF,C,G,F,UTIL
    final_pos_list = [0 for i in range(8)]
    for pos in ["pg","sg","sf","pf","c"]:
        position_list = [df['ID'].to_list()[i] for i in n if x[i].x >= 0.99 and df[pos].to_list()[i] == 1]
        if pos == "pg":
            final_pos_list[0] = position_list[0]
        elif pos == "sg":
            final_pos_list[1] = position_list[0]
        elif pos == "sf":
            final_pos_list[2] = position_list[0]
        elif pos == "pf":
            final_pos_list[3] = position_list[0]
        elif pos == "c":
            final_pos_list[4] = position_list[0]
        if len(position_list) == 2:
            if pos in ["pg","sg"]:
                final_pos_list[5] = position_list[1]
            elif pos in ["sf","pf"]:
                final_pos_list[6] = position_list[1]
            elif pos == "c":
                final_pos_list[7] = position_list[1]
        if len(position_list) == 3:
            final_pos_list[7] = position_list[2]

    #write template to .csv file
    #PG,SG,SF,PF,C,G,F,UTIL
    with open("export/for_upload/lineup_{}.csv".format(date.today()), "w") as f:
        f.write("PG,SG,SF,PF,C,G,F,UTIL\n")
        for pos in final_pos_list:
            f.write("{}".format(pos))
            if pos != final_pos_list[len(final_pos_list)-1]: f.write(",") 
        f.close()