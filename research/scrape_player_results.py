import requests
from bs4 import BeautifulSoup
from datetime import date
from datetime import timedelta 
    
#get yesterday's results

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


url = 'http://rotoguru1.com/cgi-bin/hyday.pl?mon={}&day={}&year={}&game=dk&scsv=1'.format(pad(month),pad(day),year)
page = requests.get(url)
soup = BeautifulSoup(page.text, "html.parser")
text = soup.select_one('body table tr td pre').get_text()
text_file = open("research/export/player_results/player_results_{}_{}_{}.txt".format(year,pad(month),pad(day)), "w")
text_file.write(text)
text_file.close()
