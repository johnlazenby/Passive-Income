import pandas as pd
import time
from datetime import date
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.action_chains import ActionChains
import os

#takes a valid yahoo numberfire login and returns player-name-predicted points
#saves a copy of predictions as a .csv file in specified location

def scrape_numberfire(username,password):
    #url sometimes defaults to this page after sign in. In these cases just try again.
    url = "https://www.numberfire.com/"
    while url == "https://www.numberfire.com/":
        try:
            driver.quit()
        except:
            pass
        #open browser to projections url
        current_directory = os.path.dirname(os.path.realpath(__file__))
        driver_path = os.path.join(current_directory,'chromedriver')
        driver = webdriver.Chrome(driver_path)
        driver.get('https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections')
        #sign in
        selector = "//*[contains(text(), 'Sign Up With Yahoo')]"
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, selector)))
        element = driver.find_element_by_xpath(selector)
        driver.execute_script("arguments[0].click();", element)
        #type username
        selector = '.phone-no'
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        driver.find_element_by_css_selector(selector).send_keys(username)
        #click enter
        driver.find_element_by_css_selector('[id=login-signin]').click()
        #type password
        selector = '[id=login-passwd]'
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
        driver.find_element_by_css_selector(selector).send_keys(password)
        #click enter
        driver.find_element_by_css_selector('[id=login-signin]').click()
        url = driver.current_url

    #switch to draft kings numbers
    #click drop down
    selector = '.dfs-main__options__sections__indiv.platform .custom-drop i'
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    element = driver.find_element_by_css_selector(selector)
    driver.execute_script("arguments[0].click();", element)
    #select DK
    selector = '.dfs-main__options__sections__indiv.platform [data-value="4"]'
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    element = driver.find_element_by_css_selector(selector)
    driver.execute_script("arguments[0].click();", element)
    #wait to load then get html and close browser
    time.sleep(10)
    text = driver.page_source
    driver.quit()

    #parse html with beautiful soup
    soup = BeautifulSoup(text, "html.parser")
    #get table with data
    soup = soup.find(class_="stat-table__body")
    #get name, points, salary, and team
    list_of_dicts = []
    for player in soup.find_all('tr'):
        name = player.find('a', class_='full').get_text().strip()
        points = player.find('td', class_='fp active').get_text().strip()
        team = player.select('span.team-player__team.active')[0].get_text().strip()
        row_of_data = {"name":name,"points":points,"team":team}
        list_of_dicts.append(row_of_data)

    df = pd.DataFrame(list_of_dicts)
    #clean name for merge with template. name to upper case and remove JR. and SR.    
    df['name'] = df['name'].str.upper()
    df['name'] = df['name'].str.replace('JR.','')
    df['name'] = df['name'].str.replace('SR.','')
    df['name'] = df['name'].str.strip()

    #save copy
    file_name = 'export/predictions/numberfire_{}.csv'.format(date.today())
    df.to_csv(file_name,index=False)

    df['points'] = pd.to_numeric(df['points'])

    return df
