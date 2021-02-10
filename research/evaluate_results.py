import pandas as pd
from datetime import timedelta, date
import os
import subprocess
import matplotlib.pyplot as plt

def pad(num):
    if num < 10:
        return '0{}'.format(num)
    else:
        return '{}'.format(num)

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = date(2020, 12, 22)
end_date = date(2021, 2, 10)
pred_list = ['nf','sl','lu','nf_sl','sl_lu','nf_sl_lu']
merge_problems = []
zero_problems = []
results = []

for date in daterange(start_date,end_date):
    year = pad(date.year)
    month = pad(date.month)
    day = pad(date.day)

    #get contest results
    if not os.path.exists('research/export/contest_results/contest_results_{}_{}_{}.csv'.format(year,month,day)):
        print('skipped {} because no contest results'.format(date))
        continue
    contests = pd.read_csv('research/export/contest_results/contest_results_{}_{}_{}.csv'.format(year,month,day))
    contests['contest_name'] = contests['contest_name'].str.upper()
    #condition to select contests we want to include in the evaluation
    #to_filter = contests['contest_name'].str.contains('\$5 DOUBLE UP') & contests['contest_name'].str.contains('SINGLE ENTRY')
    #to_filter = contests['contest_name'].str.contains('DOUBLE UP') & contests['contest_name'].str.contains('SINGLE ENTRY')
    to_filter = contests['contest_name'].str.contains('DOUBLE UP') & contests['contest_name'].str.contains('SINGLE ENTRY') \
        & (contests['contest_name'].str.contains('\$5') | contests['contest_name'].str.contains('\$10') \
        | contests['contest_name'].str.contains('\$25'))
    #to_filter = contests['contest_name'].str.contains('DOUBLE UP')

    in_play = contests[to_filter]
    in_play = in_play.drop_duplicates(subset = ['contest_name','cash_line'])
    if in_play.shape[0] == 0:
        print('skipped {} because no contests of type specified on this date'.format(date))
        continue

    
    #get actual player results for the day and clean for merge
    if not os.path.exists('research/export/player_results/player_results_{}_{}_{}.txt'.format(year,month,day)):
        print('skipped {} because no player results'.format(date))
        continue
    #source for player results skipped key players this day (uncommon)
    if year == '2021' and month == '01' and day == '17':
        print('skipped because of flukey thing')
        continue
    players = pd.read_csv('research/export/player_results/player_results_{}_{}_{}.txt'.format(year,month,day), sep=";")
    players['Name'] = players['Name'].str.upper()
    players['Name'] = players['Name'].str.split(',', expand=True)[1] + " " + players['Name'].str.split(',', expand=True)[0]
    players['Name'] = players['Name'].str.replace("'","")
    players['Name'] = players['Name'].str.replace("JR\.","")
    players['Name'] = players['Name'].str.replace("\.","")
    players['Name'] = players['Name'].str.strip()
    #fix bad merges
    #change to WENDELL CARTER JR. to WENDELL CARTER
    players.loc[players['Name']=='WENDELL CARTER JR.', 'Name'] = 'WENDELL CARTER'
    #change TIMOTHE LUWAWU to TIMOTHE LUWAWU-CABARROT
    players.loc[players['Name']=='TIMOTHE LUWAWU', 'Name'] = 'TIMOTHE LUWAWU-CABARROT'
    #change MARVIN BAGLEY to MARVIN BAGLEY III 
    players.loc[players['Name']=='MARVIN BAGLEY', 'Name'] = 'MARVIN BAGLEY III'
    players.loc[players['Name']=='ISHMAEL SMITH', 'Name'] = 'ISH SMITH'
    
    for pred in pred_list:
        if not os.path.exists('export/lineups/lineup_{}_{}-{}-{}.csv'.format(pred,year,month,day)):
            print('skipped {} {} because no {} prediction'.format(date,pred,pred))
            continue
        lineup = pd.read_csv('export/lineups/lineup_{}_{}-{}-{}.csv'.format(pred,year,month,day))
        lineup['name'] = lineup['name'].str.replace("'","")
        lineup['name'] = lineup['name'].str.replace(".","")
        lineup['name'] = lineup['name'].str.strip()
        #fix bad merges
        lineup.loc[lineup['name'] == 'E HOLIDAY', 'name'] = 'JRUE HOLIDAY'

        #left merge on lineups
        merged = lineup.merge(players,left_on='name',right_on = 'Name',how="left")
        
        #collect merge problems
        bad_merges = merged.loc[merged['DK Pts'].isnull(),'name'].tolist()
        merge_problem = 0
        if len(bad_merges) > 0:
            merge_problem = 1
            merge_problems.append({'date':date, 'pred':pred, 'players':bad_merges})

        #collect zero problems
        zeros = merged.loc[merged['DK Pts'] == 0,'name'].tolist()
        zero_problem = 0
        if len(zeros) > 0:
            zero_problem = 1
            zero_problems.append({'date':date, 'pred':pred, 'players':zeros})
        
        #aggregate points
        points = merged['DK Pts'].sum()

        percent_wins = (points > in_play['cash_line']).mean()
        beat_median = points > in_play['cash_line'].median()
        avg_cash_line = in_play.loc[to_filter,'cash_line'].mean()
        median_cash_line = in_play.loc[to_filter,'cash_line'].median()
        avg_diff = points - avg_cash_line
        avg_diff_med = points - median_cash_line
        results.append({'date':date, 'pred':pred, 'percent_wins':percent_wins, 'beat_median':beat_median,
             'points':points, 'median_cash_line':median_cash_line,
            'avg_cash_line':avg_cash_line, 'avg_diff':avg_diff, 'zero_problem':zero_problem,
            'merge_problem':merge_problem, 'count':1})

#Print merge problems
if  len(merge_problems) > 0:
    print('merge problems!!!')
    print(merge_problems)
    exit()

#print zero problems from final five days
zero_problems = pd.DataFrame(zero_problems)
zero_last_five = zero_problems[zero_problems.date > zero_problems.date.max() - timedelta(5)]
if zero_last_five.shape[0] > 0:
    print('zero problems in last 5 days')
    print(zero_last_five)

#print results from last two days
df = pd.DataFrame(results)
results_last_two = df[df.date > df.date.max() - timedelta(2)]
print(results_last_two.to_string())

df.loc[df.zero_problem == 0,].groupby(by=['pred'])['beat_median'].mean().plot(kind='bar')
plt.title('percentage of times beat median (no zeros)')
plt.savefig('research/export/plots/temp1.png')
df.loc[df.zero_problem == 0,].groupby(by=['pred'])['percent_wins'].mean().plot(kind='bar')
plt.title('percentage of wins (no zeros)')
plt.savefig('research/export/plots/temp2.png')
df.loc[df.zero_problem == 0,].groupby(by=['pred'])['avg_diff'].mean().plot(kind='bar')
plt.title('average difference (no zeros)')
plt.savefig('research/export/plots/temp3.png')

for i in range(3):
    subprocess.call(['open', 'research/export/plots/temp{}.png'.format(i + 1)])
