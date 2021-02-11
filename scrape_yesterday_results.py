import requests
from bs4 import BeautifulSoup
from datetime import date
from datetime import timedelta 
import pandas as pd
    
#get yesterday's results

def scrape_yesterday_results():
    #yesterday
    today = date.today()
    yesterday = today - timedelta(days = 1) 
    day = yesterday.day
    month = yesterday.month
    year = yesterday.year

    #format for naming of file
    def pad(num):
        if num < 10:
            return '0{}'.format(num)
        else:
            return '{}'.format(num)


    url = 'http://rotoguru1.com/cgi-bin/hyday.pl?mon={}&day={}&year={}&game=dk&scsv='.format(pad(month),pad(day),year)
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    rows = soup.select('[bgcolor="#E9E9E9"],[bgcolor="white"]')
    i = 0
    results = []
    for row in rows:
        cols = row.select('td')
        Pos = cols[0].text.strip()
        Name = cols[1].text.replace('^','').strip()
        pts = cols[2].text.strip()
        sal = cols[3].text.replace('$','').replace(',','').strip()
        team = cols[4].text.strip()
        if cols[5].text[0] == "v":
            home_away = 'H'
        elif cols[5].text[0] == "@":
            home_away = 'A'
        else:
            assert False
        opp = cols[5].text[2:].strip()
        t_score, o_score = cols[6].text.split('-')
        minutes = cols[7].text.strip()
        stats = cols[8].text.strip()
        results.append({'Date':'{}{}{}'.format(pad(year),pad(month),pad(day)), 'Pos':Pos, 'Name':Name, 'DK Pts':pts,
            'DK Salary':sal, 'Team':team, 'H/A':home_away, 'Team Score':t_score, 'Oppt Score':o_score,
            'Minutes':minutes, 'Stat Line':stats})
        
    
    pd.DataFrame(results).to_csv("research/export/player_results/player_results_{}_{}_{}.txt".format(pad(year),pad(month),pad(day)),
        index=None,sep=";")
    

if __name__ == '__main__':
    scrape_yesterday_results()
