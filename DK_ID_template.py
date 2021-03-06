import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.action_chains import ActionChains

#takes Draft Kings username and password and downloads template for today's classic slate. returns template as pandas dataframe.

def DK_ID_template(username,password,downloads_path):
    #open browser
    current_directory = os.path.dirname(os.path.realpath(__file__))
    driver_path = os.path.join(current_directory,'chromedriver')
    driver = webdriver.Chrome(driver_path)
    driver.get('https://www.draftkings.com/lobby')
    #sign in
    selector = '[name="username"]'
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    driver.find_element_by_css_selector(selector).send_keys(username)
    driver.find_element_by_css_selector('[name="password"]').send_keys(password)
    driver.find_element_by_css_selector('[data-test-id="login-input"] span').click()
    #click lineups tab
    selector = '[alt="Lineups"]'
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    element = driver.find_element_by_css_selector(selector)
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.execute_script("arguments[0].click();", element)
    #switch to upload menu
    selector = "//*[contains(text(), 'Upload Lineups')]/parent::*"
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, selector)))
    element = driver.find_element_by_xpath(selector)
    driver.execute_script("arguments[0].click();", element)
    #switch to NBA
    #click dropdown
    selector = '.lineup-upload-left .inner [data-sports-dropdown="1"] .dropdown-toggle .icon-arrow-down'
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    element = driver.find_element_by_css_selector(selector)
    driver.execute_script("arguments[0].click();", element)
    #click NBA
    selector = '.lineup-upload-left .inner [data-sports-dropdown="1"] .dropdown-menu [data-sport="NBA"]'
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    element = driver.find_element_by_css_selector(selector)
    driver.execute_script("arguments[0].click();", element)
    #classic is the default
    #main slate should be default but will have to check this when there are more games available.
    selector = '.lineup-upload-left .inner .start-time.list-unstyled'
    #downloaded file will be named "DKSalaries.csv". remove this from downloads folder and wait until file is finished
    try:
        os.remove(os.path.join(downloads_path,"DKSalaries.csv"))
    except:
        pass
    #download template
    selector = '.lineup-upload-left .inner [data-download-template="1"]'
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    element = driver.find_element_by_css_selector(selector)
    driver.execute_script("arguments[0].click();", element)
    while not os.path.exists(os.path.join(downloads_path,"DKSalaries.csv")):
        time.sleep(1)

    #helper function to get latest downloaded file
    def newest(path):
        files = os.listdir(path)
        files = [filename for filename in files if filename.endswith(".csv")]
        paths = [os.path.join(path, basename) for basename in files]
        return max(paths, key=os.path.getctime)

    #read in downloaded template
    df = pd.read_csv(newest(downloads_path),skiprows=7) #first 7 rows are instructions
    time.sleep(5) #ensure file is read before deleting
    os.remove(newest(downloads_path)) #delete template
    #select relevant fields and create position dummies
    df = df[['Name','ID','Roster Position','Salary','TeamAbbrev']]
    df['pg'] = 0
    df.loc[df['Roster Position'].str.contains("PG"),'pg'] = 1
    df['sg'] = 0
    df.loc[df['Roster Position'].str.contains("SG"),'sg'] = 1
    df['sf'] = 0
    df.loc[df['Roster Position'].str.contains("SF"),'sf'] = 1
    df['pf'] = 0
    df.loc[df['Roster Position'].str.contains("PF"),'pf'] = 1
    df['c'] = 0
    df.loc[df['Roster Position'].str.contains("C"),'c'] = 1

    #Clean name for eventual merge to prediction. name to upper case and remove JR. and SR.
    df['Name'] = df['Name'].str.upper()
    df['Name'] = df['Name'].str.replace('`','')
    df['Name'] = df['Name'].str.replace("'","")
    df['Name'] = df['Name'].str.replace(' III','')
    df['Name'] = df['Name'].str.replace(' II','')
    df['Name'] = df['Name'].str.replace('JR.','')
    df['Name'] = df['Name'].str.replace('SR.','')
    df['Name'] = df['Name'].str.replace('.','')
    df['Name'] = df['Name'].str.strip()

    df.loc[df['Name'] == "LONNIE WALKER IV",'Name'] = "LONNIE WALKER"
    df.loc[df['Name'] == "JUANCHO HERNANGOMEZ",'Name'] = "JUAN HERNANGOMEZ"

    #teams
    df.loc[df['TeamAbbrev'] == 'UTA','TeamAbbrev'] = 'UTAH'
    df.loc[df['TeamAbbrev'] == 'WAS','TeamAbbrev'] = 'WSH'
    df.loc[df['TeamAbbrev'] == 'PHO','TeamAbbrev'] = 'PHX'

    #return pandas dataframe with ID, salary, and position for merge by name and team.
    #return driver for use in next piece
    return driver, df




