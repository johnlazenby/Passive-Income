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
import requests

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
        injury = player.select('.team-player__injury')
        risky = len(injury) > 0
        row_of_data = {"name":name,"points":points,"team":team,'risky':risky}
        list_of_dicts.append(row_of_data)

    df = pd.DataFrame(list_of_dicts)
    #clean name for merge with template. name to upper case and remove JR. and SR.    
    df['name'] = df['name'].str.upper()
    df['name'] = df['name'].str.replace('`','')
    df['name'] = df['name'].str.replace("'","")
    df['name'] = df['name'].str.replace(' III','')
    df['name'] = df['name'].str.replace(' II','')
    df['name'] = df['name'].str.replace('JR.','')
    df['name'] = df['name'].str.replace('SR.','')
    df['name'] = df['name'].str.replace('.','')

    df.loc[df['name'] == "PATRICK MILLS",'name'] = "PATTY MILLS"

    df['name'] = df['name'].str.strip()

    #save copy
    file_name = 'export/predictions/numberfire_{}.csv'.format(date.today())
    df.to_csv(file_name,index=False)

    df['points'] = pd.to_numeric(df['points'])

    return df

#gets DFS NBA projections and outputs them to pandas dataframe
def scrape_sportsline():
    url = 'https://www.sportsline.com/nba/expert-projections/simulation/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    soup = soup.find(class_="Table__TableBody-sc-1sgcl8o-9")
    results = []
    for row in soup.find_all('tr'):
        
        name = row.find_all('td')[0].text
        team = row.find_all('td')[2].text
        dk_points = row.find_all('td')[5].text
        row_dict ={'name':name, 'team':team, 'points':dk_points}
        results.append(row_dict)

    df = pd.DataFrame(results)
    df['name'] = df['name'].str.upper()
    df['name'] = df['name'].str.replace('`','')
    df['name'] = df['name'].str.replace("'","")
    df['name'] = df['name'].str.replace(' III','')
    df['name'] = df['name'].str.replace(' II','')
    df['name'] = df['name'].str.replace('JR.','')
    df['name'] = df['name'].str.replace('SR.','')
    df['name'] = df['name'].str.replace('.','')

    df.loc[df['name'] == 'CLINT NDUMBA-CAPELA','name'] = 'CLINT CAPELA'
    df.loc[df['name'] == 'LONNIE WALKER IV','name'] = 'LONNIE WALKER'
    df.loc[df['name'] == 'TAUREAN WALLER-PRINCE','name'] = 'TAUREAN PRINCE'
    df.loc[df['name'] == 'TIMOTHE LUWAWU','name'] = 'TIMOTHE LUWAWU-CABARROT'
    df.loc[df['name'] == 'SVI MYKHAILIUK','name'] = 'SVIATOSLAV MYKHAILIUK'
    
    df['name'] = df['name'].str.strip()

    #adjust teams
    df.loc[df['team'] == 'PHO','team'] = 'PHX'
    df.loc[df['team'] == 'UTA','team'] = 'UTAH'
    df.loc[df['team'] == 'WAS','team'] = 'WSH'

    #save copy
    file_name = 'export/predictions/sportsline_{}.csv'.format(date.today())
    df.to_csv(file_name,index=False)

    return df

#get predictions from linups.com
def scrape_lineups(downloads_path):
    #open website
    current_directory = os.path.dirname(os.path.realpath(__file__))
    driver_path = os.path.join(current_directory,'chromedriver')
    driver = webdriver.Chrome(driver_path)
    driver.get('https://www.lineups.com/nba/nba-fantasy-basketball-projections')

    #switch to draft kings
    selector = '#ngb-dd-fantasy'
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    element = driver.find_element_by_css_selector(selector)
    driver.execute_script("arguments[0].click();", element)
    #click DK
    selector = '[for = "checkbox DraftKings"]'
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    element = driver.find_element_by_css_selector(selector)
    driver.execute_script("arguments[0].click();", element)

    #click largest player allowance
    selector = '#ngb-dd-items_per_page'
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    element = driver.find_element_by_css_selector(selector)
    driver.execute_script("arguments[0].click();", element)
    #get first dropdown
    selector = '#ngb-dd-items_per_page + div'
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    element = driver.find_element_by_css_selector(selector)
    #get last dropdown item (the biggest one)
    selector = '.dropdown-item'
    element = element.find_elements_by_css_selector(selector)[-1]
    #click biggest one
    selector = 'div label'
    element = element.find_element_by_css_selector(selector)
    driver.execute_script("arguments[0].click();", element)

    #remove file with same name from downloads
    #downloaded file will be named "nba-fantasy-baskeball-projections.csv".
    #remove this from downloads folder and wait until file is finished
    file_name = "nba-fantasy-basketball-projections.csv"
    try:
        os.remove(os.path.join(downloads_path,file_name))
    except:
        pass

    #download file
    selector = "//*[contains(text(), 'Download CSV')]"
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, selector)))
    element = driver.find_element_by_xpath(selector)
    driver.execute_script("arguments[0].click();", element)

    while not os.path.exists(os.path.join(downloads_path,file_name)):
        time.sleep(1)

    df = pd.read_csv(os.path.join(downloads_path,file_name))

    #remove file
    os.remove(os.path.join(downloads_path,file_name))


    df = df[['Name','Team','Projection']]
    df.columns = ['name','team','points']

    df['name'] = df['name'].str.upper()
    df['name'] = df['name'].str.replace('`','')
    df['name'] = df['name'].str.replace("'","")
    df['name'] = df['name'].str.replace(' III','')
    df['name'] = df['name'].str.replace(' II','')
    df['name'] = df['name'].str.replace('JR.','')
    df['name'] = df['name'].str.replace('SR.','')
    df['name'] = df['name'].str.replace('.','')

    df['name'] = df['name'].str.strip()

    #adjust teams
    df.loc[df['team'] == 'GSW','team'] = 'GS'
    df.loc[df['team'] == 'NOP','team'] = 'NO'
    df.loc[df['team'] == 'NYK','team'] = 'NY'
    df.loc[df['team'] == 'SAS','team'] = 'SA'
    df.loc[df['team'] == 'UTA','team'] = 'UTAH'
    df.loc[df['team'] == 'WAS','team'] = 'WSH'


    #adjust names
    df.loc[df['name'] == 'JAESEAN TATE','name'] = "JAE'SEAN TATE"

    #save copy
    file_name = 'export/predictions/lineups_{}.csv'.format(date.today())
    df.to_csv(file_name,index=False)

    #driver.quit()

    return df

def scrape_injuries():

    team_lookup = {
        'Atlanta': 'ATL',
        'Brooklyn': 'BKN',
        'Boston': 'BOS',
        'Charlotte': 'CHA',
        'Chicago': 'CHI',
        'Cleveland': 'CLE',
        'Dallas': 'DAL',
        'Denver': 'DEN',
        'Detroit': 'DET',
        'Golden State': 'GS',
        'Houston': 'HOU',
        'Indiana': 'IND',
        'Los Angeles': 'LAC',
        'Los Angeles': 'LAL',
        'Memphis': 'MEM',
        'Miami': 'MIA',
        'Milwaukee': 'MIL',
        'Minnesota': 'MIN',
        'New Orleans': 'NO',
        'New York': 'NY',
        'Oklahoma City': 'OKC',
        'Orlando': 'ORL',
        'Philadelphia': 'PHI',
        'Phoenix': 'PHX',
        'Portland': 'POR',
        'Sacramento': 'SAC',
        'San Antonio': 'SA',
        'Toronto': 'TOR',
        'Utah': 'UTAH',
        'Washington': 'WSH'
    }

    current_directory = os.path.dirname(os.path.realpath(__file__))
    driver_path = os.path.join(current_directory,'chromedriver')
    driver = webdriver.Chrome(driver_path)
    driver.get('https://www.rotoworld.com/basketball/nba/injury-report')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    teams = soup.find_all(class_='injuries__container')
    results = []
    for team in teams:
        team_name = team.find(class_='injuries__banner__name').text
        team_abbrev = team_lookup[team_name]
        table = team.find('tbody')
        if table is None:
            continue
        players = table.find_all('tr')
        for player in players:
            name = player.find_all('td')[0].find('span').text
            status = player.find_all('td')[2].text
            results.append({'team':team_abbrev, 'name':name, 'status':status})
    df = pd.DataFrame(results)
    df['name'] = df['name'].str.upper()
    df['name'] = df['name'].str.replace('`','')
    df['name'] = df['name'].str.replace("'","")
    df['name'] = df['name'].str.replace(' III','')
    df['name'] = df['name'].str.replace(' II','')
    df['name'] = df['name'].str.replace('JR.','')
    df['name'] = df['name'].str.replace('SR.','')
    df['name'] = df['name'].str.replace('.','')

    df['name'] = df['name'].str.strip()

    #save a copy
    file_name = 'export/injuries/injuries_{}.csv'.format(date.today())
    df.to_csv(file_name,index=False)

    return df

if __name__ == "__main__":
    scrape_injuries()
    #scrape_lineups('/Users/johnlazenby/Downloads')

