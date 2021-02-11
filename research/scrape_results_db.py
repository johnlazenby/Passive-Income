#!/usr/bin/env python3
import pandas as pd
import time
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.action_chains import ActionChains
from datetime import timedelta, date


#scrapes results DB for every date in date range specified by start_date and end_date
#results DB does not upload consistently. It's best to check manually which days have loaded
#and scrape in chunks of days at a time instead of daily with the other script.

def pad(num):
    if num < 10:
        return '0{}'.format(num)
    else:
        return '{}'.format(num)

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = date(2021, 2, 10)
end_date = date(2021, 2, 11)

for single_date in daterange(start_date, end_date):
    year = pad(single_date.year)
    month = pad(single_date.month)
    day = pad(single_date.day)


    url = 'https://rotogrinders.com/resultsdb/site/draftkings/date/{}-{}-{}/sport/nba'.format(year,month,day)
    driver = webdriver.Chrome('./chromedriver')
    driver.get(url)
    selector = "//*[contains(text(), 'Contests')]"
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, selector)))
    element = driver.find_element_by_xpath(selector)
    driver.execute_script("arguments[0].click();", element)
    #wait for cashlines to load
    time.sleep(15)
    text = driver.page_source
    soup = BeautifulSoup(text, "html.parser").find_all(class_="ant-table-tbody")[2]
    list_of_dicts = []
    for contest in soup.find_all('tr'):
        row = contest.find_all('td')
        contest_name = row[0].select_one('a').get_text().strip()
        contest_link = row[1].select_one('a')['href']
        prize_pool = row[2].get_text().replace(',', '').replace('$','')
        buy_in = row[3].get_text().replace(',', '').replace('$','')
        top_prize = row[4].get_text().replace(',', '').replace('$','')
        max_entries = row[5].get_text()
        entries = row[6].get_text()
        cash_line = row[7].get_text()
        winning_score = row[9].get_text()
        row_of_data = {"contest_name":contest_name,"contest_link":contest_link,"prize_pool":prize_pool,
        "buy_in":buy_in,"top_prize":top_prize,"max_entries":max_entries,"entries":entries,"cash_line":cash_line,
        "winning_score":winning_score}
        list_of_dicts.append(row_of_data)

    driver.quit()

    df = pd.DataFrame(list_of_dicts)
    #save copy

    file_name = 'research/export/contest_results/contest_results_{}_{}_{}.csv'.format(year,month,day)
    df.to_csv(file_name,index=False)
