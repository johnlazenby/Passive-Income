import pandas as pd
import time
import os
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.action_chains import ActionChains
from datetime import timedelta, date

def scrape_yesterday_contests():
    
    def pad(num):
        if num < 10:
            return '0{}'.format(num)
        else:
            return '{}'.format(num)

    #yesterday
    today = date.today()
    yesterday = today - timedelta(days = 1) 
    day = pad(yesterday.day)
    month = pad(yesterday.month)
    year = pad(yesterday.year)

    url = 'https://rotogrinders.com/resultsdb/site/draftkings/date/{}-{}-{}'.format(year,month,day)
    current_directory = os.path.dirname(os.path.realpath(__file__))
    driver_path = os.path.join(current_directory,'chromedriver')
    driver = webdriver.Chrome(driver_path)
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
