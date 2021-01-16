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


skip_list  = [date(2020, 12, 24), date(2021, 1, 2), date(2021, 1, 12), date(2021, 1, 13)]
start_date = date(2020, 12, 22)
end_date = date(2021, 1, 15)
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
    print(merged[['name','DK Pts','points']])
    print(merged['DK Pts'].sum())
