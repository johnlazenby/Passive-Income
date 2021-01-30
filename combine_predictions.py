import pandas as pd

#combine predictions from all three sources
def combine_predictions(nf, sl, lu, injuries, excluded_players):

    df = sl.merge(lu, on = ['name', 'team'], suffixes = ['_sl', '_lu'], how = 'outer')

    df['points_sl'] = pd.to_numeric(df['points_sl'])
    
    #outer merge. Only trust those in numberfire
    df = df.merge(nf, on = ['name', 'team'], how = 'outer')
    df = df.rename(columns={'points':'points_nf'})

    #create combinations
    df['points_nf_sl_lu'] = df[['points_nf','points_sl','points_lu']].mean(axis=1)
    df['points_nf_sl'] = df[['points_nf','points_sl']].mean(axis=1)
    df['points_nf_lu'] = df[['points_nf','points_lu']].mean(axis=1)
    df['points_sl_lu'] = df[['points_sl','points_lu']].mean(axis=1)

    #outer merge injuries
    df = df.merge(injuries,on = ['name', 'team'], how = 'outer')

    #check potential bad merges
    filter = ((df['status'] != 'Sidelined') & (df['points_nf'].isnull() | df['points_sl'].isnull() | df['points_lu'].isnull()) &
        (~df['points_nf'].isnull() | ~df['points_sl'].isnull() | ~df['points_lu'].isnull()) )
    print(sorted(df['team'].unique()))
    print(sorted(injuries['team'].unique()))
    print(sorted(sl['team'].unique()))
    print(sorted(lu['team'].unique()))
    print(sorted(nf['team'].unique()))
    max_non_merge = df.loc[filter,'points_nf_sl_lu'].max()


    try:
        assert max_non_merge < 20
    except:
        print(df[filter].to_string())
        raise Exception('non-trivial player did not merge')

    #flag to ID obs from this dataset
    df['predictions_flag'] = True
    
    return df

if __name__ == "__main__":
    nf = pd.read_csv('export/predictions/numberfire_2021-01-29.csv')
    lu = pd.read_csv('export/predictions/lineups_2021-01-29.csv')
    sl = pd.read_csv('export/predictions/sportsline_2021-01-29.csv')
    injuries = pd.read_csv('export/injuries/injuries_2021-01-29.csv')
    excluded_players = []
    combine_predictions(nf,sl,lu,injuries,excluded_players)

