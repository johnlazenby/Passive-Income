import pandas as pd
from datetime import timedelta, date
import sys

def pad(num):
    if num < 10:
        return '0{}'.format(num)
    else:
        return '{}'.format(num)

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


skip_list  = [date(2020, 12, 24), date(2020, 12, 25), date(2021, 1, 2), date(2021, 1, 12), date(2021, 1, 13), date(2021,1,20),
date(2021,1,21), date(2021,1,24), date(2021,1,26)]
start_date = date(2020, 12, 23)
end_date = date(2021, 1, 27)
for single_date in daterange(start_date, end_date):
    year = pad(single_date.year)
    month = pad(single_date.month)
    day = pad(single_date.day)

    #skip 
    if single_date in skip_list:
        continue
    print(year, month, day)

    #results
    df = pd.read_csv('research/export/player_results/player_results_{}_{}_{}.txt'.format(year,month,day), sep=";")
    df['Name'] = df['Name'].str.upper()
    df['Name'] = df['Name'].str.split(',', expand=True)[1] + " " + df['Name'].str.split(',', expand=True)[0]
    df['Name'] = df['Name'].str.strip()

    #fix bad merges
    #change to WENDELL CARTER JR. to WENDELL CARTER
    df.loc[df['Name']=='WENDELL CARTER JR.', 'Name'] = 'WENDELL CARTER'
    #change TIMOTHE LUWAWU to TIMOTHE LUWAWU-CABARROT
    df.loc[df['Name']=='TIMOTHE LUWAWU', 'Name'] = 'TIMOTHE LUWAWU-CABARROT'
    #change MARVIN BAGLEY to MARVIN BAGLEY III 
    df.loc[df['Name']=='MARVIN BAGLEY', 'Name'] = 'MARVIN BAGLEY III'

    #lineup
    df2 = pd.read_csv('export/lineups/lineup_{}-{}-{}.csv'.format(year,month,day))
    df2['name'] = df2['name'].str.strip()

    #merge
    merged = df.merge(df2,left_on='Name',right_on = 'name',how="right")
    points = merged['DK Pts'].sum()

    #results db
    df3 = pd.read_csv('research/export/contest_results/contest_results_{}_{}_{}.csv'.format(year,month,day))
    df3['contest_name'] = df3['contest_name'].str.upper()
    #to_filter = df3['contest_name'].str.contains('DOUBLE UP')
    to_filter = (df3['contest_name'] == 'NBA SINGLE ENTRY $5 DOUBLE UP') | (df3['contest_name'] == 'NBA GIANT SINGLE ENTRY $5 DOUBLE UP')
    cash_line = df3.loc[to_filter,'cash_line'].mean()
    
    #lineup
    print(merged[['name','DK Pts','points']])
    
    #result
    win = points > cash_line
    print('cash:{}, points:{},{}'.format(cash_line,points,win))
